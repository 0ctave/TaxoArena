"""cert_pc_k2_known.py: CERT-PC-K2-KNOWN, stage 0 (the pair scan and the TRAIN-only pair rule), the merged-pair site file, the
dry-run, the launch command and the READOUT of the merged-pair arm (SeparationNullBySizeTest `certKnownPair - ...`, gradle task
certKnownPair). ZERO calls.

REGISTRATION OF RECORD (it governs; this docstring restates it and never replaces it): docs/judge_v2_program.md
"## Registered 2026-10-03 (before any code or call) — CERT-PC-K2-KNOWN: does the site-null certificate certify a k = 2 declared
partition of KNOWN strength (two distinct declared MMLU-Pro categories merged into one site, chosen by a TRAIN-only rule stated
here) at G12's depth-1 site sizes (n 486, 441; 5 subsamples each), when the same pair certifies with margin at full size? (zero
calls; site-null runs, CPU)" (span L24036-L24052, commit 56093589); record docs/agents/results/CERT-PC-K2-KNOWN.json.
  PAIR RULE: unordered pairs of the 14 declared categories of the B0 MMLU_PRO_LB member (draw 5a3e756 TRAIN, 6,988 kept items),
  ELIGIBLE iff combined TRAIN ids >= 972 and each category >= 100. STAGE 0: the declared 2-way statistic of every eligible merged
  site at full size (no null), the whole table printed. STRONG = the largest statistic; MID = the eligible pair other than STRONG
  nearest 0.1078; EDGE = the eligible pair other than those two nearest 0.070; ties: the lexicographically smaller pair name; no
  pair replaced after stage 0.
  Per chosen pair: one FULL site and, at n 486 and 441, 5 subsamples stratified proportional to the two categories (draw seeds 1-5);
  each its own plain null (300 reps), C0 (300 size-matched 2-group relabellings) and the DEGENERATE / C0 gate first.
  G-KS (gate per pair): KNOWN-STRENGTH iff the FULL site certifies (k_d <= 14 of 300, C0 comparable, not DEGENERATE) AND its
  statistic minus its null p95 exceeds the SD of the declared statistic over the pair's five n-486 subsamples; else NOT-A-CONTROL.
  Per gated pair and size: CERTIFIED-AT-SIZE iff >= 4 of 5 certified; NOT-CERTIFIED-AT-SIZE iff <= 1; MIXED otherwise; NOT
  EVALUABLE gate first.
  KK1 (DECIDING, n 486): NO-CONTROL iff fewer than 2 pairs KNOWN-STRENGTH; K2-SENSITIVE iff every gated pair CERTIFIED-AT-SIZE;
  K2-SIZE-LIMIT iff at least one gated pair NOT-CERTIFIED-AT-SIZE; MIXED otherwise. KK2 the same at n 441. Q-K1's withholding rule.
  [Q-KK1 RULED 65e5c0d7 (registrar; programme L24046 / L24048 / L24050): KK1, KK2 and F-KK count STRONG and MID only; EDGE is
  descriptive (Support (f)).]
  P1 STRONG 0.20 [0.12, 0.35]; MID within 0.010 of 0.1078; EDGE within 0.010 of 0.070. P2 KNOWN-STRENGTH STRONG 0.90, MID 0.80,
  EDGE 0.30 (Brier). P3 KK1 K2-SENSITIVE 0.55 / MIXED 0.10 / K2-SIZE-LIMIT 0.15 / NO-CONTROL 0.20 (Brier). P4 merged-site null p95
  at n 486 (median over the chosen pairs' subsamples) 0.060 [0.045, 0.075]. P5 C0 comparable everywhere 0.85.
  F-KK fires iff KK1 reads K2-SIZE-LIMIT.

INSTRUMENT. The certPcSize / certPcK2 members, reused unchanged (pcsParseSites, pcsPopulation, pcsC0Seed, cpcDeclaredSite,
cpcRelabelNull, declaredSiteStatistic), driven by a NEW method certKnownPair (additions only; the only new check is kkpSiteError;
javap proof in the commit message). cert_pc_k2.py blob 38fb0dfc is IMPORTED unchanged (labels reader, TWINS, IDENTITY / PC1 pins,
subsample_status; through it cert_pc_size.py de39c648: draw, allocate, size_verdict), never copied. The registration said
"cert_pc_k2.py extended"; it is extended by import (a new file) so the blob of a VALID test's readout does not change (builder's
deviation KK-0). Labels: CERT-POSITIVE-CONTROL's label file of record (declared_labels.tsv, sha256 c0a20662...); snapshot
20261001_094311_Headless_Run_Auto_ge; config experiment_configs/rp12_r2/B0/g12_site_null.sitenull (slice 512, sepBar 0.0145,
dropTop 0, whiten false, 300 reps, 12 threads).

LAUNCH SEQUENCE (run-operator; a site null = a rule-7 heavy process: W1-W5, 12 JVM threads, never beside a construction, another
site null or a pool reader; the pool check in the B0-2 form first; run from the data root's checkout, e.g. the rp12-r2-run worktree
after merging this branch there, TAXOARENA_DATA_ROOT unset; nothing here is committed from the run):
  python tools/analysis/cert_pc_k2_known.py --selftest                 (never with python -O: refused)
  python tools/analysis/cert_pc_k2_known.py --mutants
  TAXOARENA_DATA_ROOT=<main checkout> python tools/analysis/v2_union_pool.py --dry-run   (rc 0; pool file sha256-lf16 79d48f4b36434a55)
  python tools/analysis/cert_pc_k2_known.py --dry-run [--data-root DIR] [--cpc-labels FILE]   STAGE 0 (the instrument check of the
        Python statistic first: IDENTITY 0.107803 and CERT-PC-K2's 30 K2 sites reproduced within 1e-9), the whole stage-0 table,
        the selection with its margins (= SELECTION), stage-0 and site-file sha256 (= the pins), overlaps, heap, wall, COMMAND;
        writes nothing
  python tools/analysis/cert_pc_k2_known.py --prepare [--cpc-labels FILE]   writes experiment_results/cert_pc_k2_known/stage0.tsv
        and site_labels.tsv (mode x); refuses unless the selection is SELECTION and the shas are STAGE0_SHA256 / SITES_SHA256
  python tools/analysis/cert_pc_k2_known.py --hashes before
  <the printed COMMAND: .\\gradlew.bat certKnownPair ...>   then  .\\gradlew.bat --stop
  python tools/analysis/cert_pc_k2_known.py --hashes after
  python tools/analysis/cert_pc_k2_known.py --analyze [--cpc-labels FILE]   outcome (write-once, mode x):
        experiment_results/cert_pc_k2_known/outcome.txt and kk_sites.csv; runs the selftest first; refuses a REFUSED / partial arm,
        a hash change, an IDENTITY failure, a stage-0 file or site file that is not the pinned one, a selection that the rule does
        not re-derive from the stage-0 file, a site file that the labels and the selection do not rebuild byte for byte, a full
        site whose arm statistic differs from its stage-0 statistic by more than 1e-9, an instrument or snapshot other than the
        registered, a missing / extra / wrong-size site.
Outputs are NEVER committed: pin them by sha256 and back them up to E:/TaxoArena_backup_<date>_<tag> with SHA256SUMS.txt (the
emb_hashes_before/after.json included).

BUILDER'S READINGS (each flagged to the registrar; printed in the outcome header):
  KK-0 cert_pc_k2.py extended by import, not edited (above). Stage 0 is computed in Python (numpy float64, the routine
       StatisticsUtils.chanceCorrectedSeparation on the first 512 floats, L2-normalised, as Embedding.projectTo) at --dry-run /
       --prepare, BEFORE any null, and pinned (SELECTION, STAGE0_SHA256, SITES_SHA256). The Python routine is an instrument copy, so
       it is checked three ways: (i) a fixed fixture whose value the Kotlin test CertKnownPairArmTest asserts too (XFIX); (ii) the
       dry-run reproduces IDENTITY's 0.10780301021353667 and the 30 K2 sites of CERT-PC-K2's arm within 1e-9; (iii) --analyze
       refuses unless each chosen pair's FULL site statistic printed by the arm equals its stage-0 value within 1e-9.
  KK-1 population: CERT-PC-K2's PK-1 on all 14 categories: the member root's TRAIN ids with a non-empty src (gold's join), the
       pinned stem-key twin dropped (the only stem-key group among the 6,993 ids, READY_cert_pc_k2 claim 3); refused unless the 14
       counts equal the registered class counts (sum 6,988). The dry-run recomputes the twins over all src-carrying ids.
  KK-2 pair name "a + b" with a < b (category names as in the label file); ties in the rule by that name. A selection whose margin
       (gap to the runner-up) is <= 1e-8 refuses: at that gap the Python and Kotlin statistics could order the pairs differently.
  KK-3 allocation and draw: CERT-PC-SIZE's PCS-1 (cert_pc_size.draw, imported) over the two categories; seeds 1-5 in every pair
       and size. Site file: IDENTITY first (CERT-PC-SIZE's rows), then per role STRONG, MID, EDGE: KK_<role>_n<N>_d0 (the FULL site,
       N = its size), KK_<role>_n486_d1..5, KK_<role>_n441_d1..5; each site's rows sorted by id; label = the category.
  KK-4 seeds: CERT-PC-SIZE's PCS-3 with the KK site name (plain null base 20260908, C0 cpcSeed(20261002, name, 0)); no deflated
       null (not registered; CERT-PC-K2 ran it beside, descriptive only). C0 "comparable" = C0 p95 < the plain null p95 (PCS-4).
  KK-5 the SD in G-KS is the sample SD (n - 1) of the five n-486 declared statistics; the population SD (n) is printed beside with
       whether the gate word would change (registration query Q-KK2 if it does).
  KK-6 KK1 / KK2 with a NOT EVALUABLE gated pair: Q-K1's withholding rule: the registered word is printed when every value the
       unevaluable pairs could take gives the same word; otherwise NOT EVALUABLE (F-KK not fired, P3 not scored).
  KK-7 REGISTRATION QUERY Q-KK1 (two verdicts on the same data; NOT resolved here): SUPPORT (f) and DESCRIPTIVE call EDGE
       "DESCRIPTIVE-ONLY ... whether gated or not", while G-KS gates every chosen pair, KK1 reads "every gated pair" and SUPPORT (a)
       counts "2-3 gated pairs". With EDGE gated, reading A (EDGE descriptive-only: KK1 over STRONG / MID) and reading B (EDGE
       enters KK1 when gated) can give different words (e.g. EDGE NOT-CERTIFIED-AT-SIZE: B K2-SIZE-LIMIT, A K2-SENSITIVE; or MID
       not gated: A NO-CONTROL, B evaluates). Both readings are printed; the deciding word is the one Q_KK1_RULING names; while it
       is None the word is printed only when A and B agree, otherwise KK WITHHELD (F-KK not fired, P3 not scored).
       RULED 65e5c0d7 (registrar; programme L24046 / L24048 / L24050): STRONG and MID only, EDGE descriptive = reading A;
       Q_KK1_RULING = "EDGE-DESCRIPTIVE" (READY_cert_pc_k2_known D-1). Reading B is still printed beside, descriptive.
  KK-8 IDENTITY (the instrument precondition of CERT-PC-SIZE / CERT-PC-K2) is kept: declared 0.107803, k_d 0, seed n00000001,
       n 6,993, plain null p95 / max = PC1's 0.041626 / 0.042414; refused otherwise.

STAGE 0 AT BUILD (the dry-run of 2026-10-03, data root rp12-r2-run, zero calls, no null): routine check IDENTITY |diff| 3.3e-16,
CERT-PC-K2's 30 K2 sites max |diff| 1.0e-15; 49 eligible pairs; STRONG = chemistry + law 0.119598 (margin 0.0141), MID =
engineering + law 0.105456 (margin 0.0113), EDGE = economics + physics 0.070390 (margin 8.95e-05); STRONG and MID share law.
DISCLOSED (KK-0): P1 is a prediction about stage 0, so it is DETERMINED by this build, before any null: STRONG 0.119598 lies
just below [0.12, 0.35] (the readout will print FAILED), MID within 0.010 of 0.1078 and EDGE within 0.010 of 0.070 (HELD).

SELFTEST (python tools/analysis/cert_pc_k2_known.py --selftest): every registered branch through the real entry points (analyze(),
main(["--analyze"]), stage0(), select(), build_site_bytes(), load_vectors(), check_routine()) on fixtures whose answer is known by
hand, asserting the printed VALUE; the case list is in selftest(). MUTANTS: --mutants runs the table MUTANTS below against
--selftest (temporary copies, removed); the result table is in the commit message.
"""
import argparse
import contextlib
import csv
import hashlib
import io
import itertools
import json
import math
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import ro as RO  # noqa: E402

TAG = "[PKK]"
_IN_SELFTEST = False
PK2_BLOB = "38fb0dfcde9be33be6f1087e5220e3fd295201c4"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _import_pinned(name, blob):
    got = RO.git_blob_lf(os.path.join(HERE, name + ".py"))
    if got != blob:
        refuse("%s.py is blob %s, not the pinned %s (imported, never copied)" % (name, got, blob))
    return __import__(name)


PK2 = _import_pinned("cert_pc_k2", PK2_BLOB)
PCS, CPC, G = PK2.PCS, PK2.CPC, PK2.G

OUT_REL = "experiment_results/cert_pc_k2_known"
CPC_LABELS_REL = PK2.CPC_LABELS_REL
LABELS_SHA = PK2.LABELS_SHA
SITES_NAME, STAGE0_NAME, ARM_NAME, OUTCOME_NAME, CSV_NAME = "site_labels.tsv", "stage0.tsv", "arm", "outcome.txt", "kk_sites.csv"
SITE_HEADER = PCS.SITE_HEADER
STAGE0_HEADER = "pair\tcat_a\tcat_b\tn_a\tn_b\tn\tstatistic\trole"
SNAPSHOT, ROOT_ID, N_ROOT = PK2.SNAPSHOT, PK2.ROOT_ID, PK2.N_ROOT
TWINS = PK2.TWINS
REG_COUNTS = {"math": 805, "physics": 778, "chemistry": 676, "engineering": 580, "law": 578, "other": 555, "economics": 504,
              "psychology": 476, "business": 467, "health": 410, "biology": 381, "philosophy": 298, "computer science": 242,
              "history": 238}                                   # the registration's class counts (MMLU-GOLD-GEOMETRY), sum 6,988
MIN_COMBINED, MIN_EACH = 972, 100
T_MID, T_EDGE = 0.1078, 0.070
ROLES = ("STRONG", "MID", "EDGE")
SIZES = (486, 441)
DECIDING = {486: "KK1", 441: "KK2"}
DRAWS = (1, 2, 3, 4, 5)
REPS, MCS, DEGENERATE_MIN = 300, 55, 20
BAR = Fraction(1, 20)
SLICE = 512
TOL = 1e-9                     # Python vs Kotlin statistic (float64, different summation order)
SEL_MARGIN_MIN = 1e-8          # KK-2
IDENTITY_DECLARED, IDENTITY_K = PK2.IDENTITY_DECLARED, PK2.IDENTITY_K
IDENTITY_FULL = 0.10780301021353667   # IDENTITY's declared statistic as the arms print it (CERT-PC-K2 arm sites.csv)
PC1_P95, PC1_MAX = PK2.PC1_P95, PK2.PC1_MAX
INSTRUMENT = {"arm": "certKnownPair", "reps": "300", "sliceDim": "512", "sepBar": "0.0145", "dropTop": "0", "whiten": "false",
              "minClusterSize": "55", "c0Seed": "20261002"}
P1_STRONG = (Fraction("0.12"), Fraction("0.35"))
P1_HALF = Fraction("0.010")
P2_P = {"STRONG": 0.90, "MID": 0.80, "EDGE": 0.30}
P3_PROBS = {"K2-SENSITIVE": 0.55, "MIXED": 0.10, "K2-SIZE-LIMIT": 0.15, "NO-CONTROL": 0.20}
P4_BAND = (0.045, 0.075)
P5_P = 0.85
Q_KK1_RULING = "EDGE-DESCRIPTIVE"   # KK-7 RULED 65e5c0d7, programme L24046 / L24048 / L24050 (KK1 / KK2 / F-KK: STRONG and MID
#   only; EDGE descriptive). Values: None (withhold on disagreement) | "EDGE-DESCRIPTIVE" | "EDGE-IN-IF-GATED"; the registrar's
PK2_WALL_S = 1503              # CERT-PC-K2's arm: emb_hashes_before 17:57:21 -> status.txt 18:22:24 (IDENTITY + 30 sites, SN+SND+C0)
# KK-0 pins, from the dry-run of 2026-10-03 (data root .claude/worktrees/rp12-r2-run); --prepare / --analyze refuse on a difference
SELECTION = {"STRONG": "chemistry + law", "MID": "engineering + law", "EDGE": "economics + physics"}
STAGE0_SHA256 = "0c32bb8139c934a44279764d8915c15955b9da65caab541a07dd65652be755aa"
SITES_SHA256 = "8e122edd42a044ad04d79bc2519ef78305bd976632473d98500b9021a4aa3b77"
# The routine on a fixed fixture (KK-0 (i)); CertKnownPairArmTest asserts the same value from the Kotlin routine.
XFIX = -0.04137677437400078
REG = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — CERT-PC-K2-KNOWN: ..." L24036-L24052 '
       '(as registered, 56093589)')

SENT_FKK_FIRED = ("F-KK: FIRED (KK1 K2-SIZE-LIMIT): the certificate fails, at G12's depth-1 sizes, a 2-way declared partition that "
                  "it certifies with margin at full size, so a k = 2 size-sensitivity limit is SHOWN; the k = 2 reading of CERT-PC-SIZE "
                  "W-2 ('0 of 60 not explained by n alone', shown for 14-way structure) is overturned and G12's 0 of 60 reads "
                  "'possibly a sensitivity limit at k = 2'. F-TAX N-1 and F2 stand.")
SENT_SENSITIVE = ("READING (KK1 K2-SENSITIVE): k = 2 sensitivity at n 441-486 is shown for declared structure at least as strong as "
                  "the weakest gated pair's statistic, and G12's 0 of 60 reads 'the tree's depth-1 splits are weaker than that' "
                  "(populations differ: routed anchor vs merged categories). F-TAX N-1 and F2 stand.")
SENT_NO_CONTROL = ("READING (KK1 NO-CONTROL): fewer than 2 chosen pairs are KNOWN-STRENGTH; a registered non-outcome: nothing about "
                   "the certificate.")
LIKE = ["LIKE WITH LIKE: | site | k | population | partition |",
        "  | CERT-PC-K2-KNOWN (this) | 2 | two declared categories merged | declared categories |",
        "  | CERT-PC-K2 (of record) | 2 | one category | declared source family |",
        "  | G12 TOP sites (of record) | 2-3 | one routed anchor | data-driven split |",
        "  | CERT-PC-SIZE (of record) | 14 | all categories | declared categories |",
        "  k- and size-matched to G12; the population (two distinct categories) is EASIER than a routed anchor's interior by design: "
        "this measures sensitivity to known structure, not whether anchors contain such structure"]
DOES_NOT_SHOW = ("DOES NOT SHOW: a certificate of any tree site; whether anchors contain certifiable 2-way structure; other members, "
                 "draws, slices or k; a mode test (MIX-LRT-SITE closed); sensitivity for structure weaker than the weakest gated pair")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def pair_name(a, b):
    a, b = sorted((a, b))
    return "%s + %s" % (a, b)


def site_names(selection_sizes):
    """selection_sizes: {role: full size} -> the KK site names in file order."""
    out = []
    for r in ROLES:
        out.append("KK_%s_n%d_d0" % (r, selection_sizes[r]))
        out.extend("KK_%s_n%d_d%d" % (r, n, d) for n in SIZES for d in DRAWS)
    return out


# ------------------------------------------------------------------------------------------------ the routine (KK-0)
def unit_rows(raw):
    """Embedding.projectTo(SLICE): the first SLICE floats as doubles, divided by their L2 norm (a zero row stays zero)."""
    x = np.asarray(raw, dtype=np.float32)[:, :SLICE].astype(np.float64)
    nrm = np.sqrt((x * x).sum(axis=1))
    nz = nrm > 0.0
    x[nz] = x[nz] / nrm[nz, None]
    return x


def declared_stat(groups):
    """StatisticsUtils.chanceCorrectedSeparation over the non-empty groups (each an (m, d) array of unit rows)."""
    groups = [g for g in groups if len(g) > 0]
    if not groups:
        return 0.0
    n = float(sum(len(g) for g in groups))
    if n < 2.0:
        return 0.0
    tot = np.zeros(groups[0].shape[1])
    w_within, pair_frac = 0.0, 0.0
    for g in groups:
        s = g.sum(axis=0)
        tot += s
        m = float(len(g))
        w_within += m * m - float(s @ s)
        pair_frac += m * (m - 1.0)
    w_total = n * n - float(tot @ tot)
    expected = w_total * pair_frac / (n * (n - 1.0))
    if expected <= 1e-10:
        return 0.0
    return 1.0 - w_within / expected


def site_stat(vec, labels):
    """labels {id: label} -> the declared statistic, groups in sorted-label order (pcsPopulation's)."""
    cats = sorted(set(labels.values()))
    return declared_stat([np.array([vec[q] for q in sorted(labels) if labels[q] == c]) for c in cats])


def fixture_vectors():
    """XFIX fixture: 12 ids x 600 floats, f[i][j] = ((31 i + 17 j) mod 101 - 50) / 50 (float32); groups ids 0-6 / 7-11."""
    raw = np.array([[((31 * i + 17 * j) % 101 - 50) / 50.0 for j in range(600)] for i in range(12)], dtype=np.float32)
    u = unit_rows(raw)
    return declared_stat([u[:7], u[7:]])


def load_vectors(db_path, ids):
    """{id: unit row} from the cache (SeparationNullBySizeTest.cpcLoadSliceFloats: queries JOIN embeddings on distilled_text,
    big-endian float32, the first SLICE floats). Refuses a missing id, a short vector or two different vectors for one id."""
    con = RO.open_ro(db_path) if not _IN_SELFTEST else sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
    raw, ids = {}, sorted(ids)
    try:
        for i in range(0, len(ids), 400):
            ch = ids[i:i + 400]
            for q, b in con.execute("SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text "
                                    "WHERE q.id IN (%s)" % ",".join("?" * len(ch)), ch):
                if b is None or len(b) // 4 < SLICE:
                    refuse("embedding of %s is shorter than %d floats" % (q, SLICE))
                v = struct.unpack(">%df" % SLICE, bytes(b[:4 * SLICE]))
                if q in raw and raw[q] != v:
                    refuse("two different vectors for %s" % q)
                raw[q] = v
    finally:
        con.close()
    miss = [q for q in ids if q not in raw]
    if miss:
        refuse("embedding cache miss: %d of %d ids (e.g. %s)" % (len(miss), len(ids), miss[:3]))
    u = unit_rows(np.array([raw[q] for q in ids], dtype=np.float32))
    return {q: u[i] for i, q in enumerate(ids)}


def check_routine(vec, cat, k2_sites=None, k2_arm=None, out=print):
    """KK-0 (ii): IDENTITY (all root ids, 14 categories) within TOL of IDENTITY_FULL; each CERT-PC-K2 site of its arm within TOL."""
    d0 = site_stat(vec, cat)
    out("%s ROUTINE CHECK IDENTITY: Python %.17g vs the arms' %.17g (|diff| %.2e; tolerance %.0e)" % (
        TAG, d0, IDENTITY_FULL, abs(d0 - IDENTITY_FULL), TOL))
    if not abs(d0 - IDENTITY_FULL) <= TOL:
        refuse("the Python routine gives IDENTITY %.17g, not the instrument's %.17g within %.0e" % (d0, IDENTITY_FULL, TOL))
    if k2_sites is None:
        refuse("CERT-PC-K2's site file and arm sites.csv are required for the routine check (KK-0 (ii))")
    worst, cnt = 0.0, 0
    for s, lab in k2_sites.items():
        if s == "IDENTITY":
            continue
        if s not in k2_arm:
            refuse("CERT-PC-K2 arm sites.csv has no row for %s" % s)
        d = site_stat(vec, lab)
        worst = max(worst, abs(d - k2_arm[s]))
        cnt += 1
    out("%s ROUTINE CHECK CERT-PC-K2: %d K2 sites, max |Python - arm| %.2e (tolerance %.0e)" % (TAG, cnt, worst, TOL))
    if cnt != 30 or not worst <= TOL:
        refuse("the Python routine does not reproduce CERT-PC-K2's %d K2 sites within %.0e (max %.2e)" % (cnt, TOL, worst))
    return d0, worst


# ------------------------------------------------------------------------------------------------ populations, stage 0, the rule
def find_twins(cat, src, text):
    """KK-1: among ALL src-carrying ids, ids sharing a stem key of their text; all but the smallest -> sorted list."""
    import split_side
    by = {}
    for q in sorted(q for q in cat if src[q]):
        by.setdefault(split_side.stem_key(text[q]), []).append(q)
    drop = []
    for v in by.values():
        drop.extend(v[1:])
    return sorted(drop)


def populations(cat, src, twins=TWINS, reg=None):
    """KK-1 -> {category: sorted ids}; refuses unless the 14 counts equal the registered class counts."""
    reg = REG_COUNTS if reg is None else reg
    tw = set(twins)
    pops = {}
    for q in sorted(cat):
        if src[q] and q not in tw:
            pops.setdefault(cat[q], []).append(q)
    got = {c: len(v) for c, v in pops.items()}
    if got != reg:
        bad = sorted(c for c in set(got) | set(reg) if got.get(c) != reg.get(c))
        refuse("category counts differ from the registered class counts: %s" % ", ".join(
            "%s %s (registered %s)" % (c, got.get(c), reg.get(c)) for c in bad))
    return pops


def eligible_pairs(pops):
    """-> sorted [(a, b)] with a < b, combined >= MIN_COMBINED and each >= MIN_EACH."""
    return [(a, b) for a, b in itertools.combinations(sorted(pops), 2)
            if len(pops[a]) + len(pops[b]) >= MIN_COMBINED and len(pops[a]) >= MIN_EACH and len(pops[b]) >= MIN_EACH]


def stage0(pops, vec):
    """-> [dict(pair, a, b, na, nb, stat)] for every eligible pair, sorted by pair name: the merged site's declared statistic."""
    rows = []
    for a, b in eligible_pairs(pops):
        st = declared_stat([np.array([vec[q] for q in pops[a]]), np.array([vec[q] for q in pops[b]])])
        rows.append(dict(pair=pair_name(a, b), a=a, b=b, na=len(pops[a]), nb=len(pops[b]), stat=float(st)))
    return sorted(rows, key=lambda r: r["pair"])


def _nearest(rows, key):
    best = min(rows, key=lambda r: (key(r), r["pair"]))
    rest = [key(r) for r in rows if r is not best]
    return best, (min(rest) - key(best)) if rest else float("inf")


def select(rows):
    """The registered rule -> ({role: row}, {role: margin to the runner-up}); refuses fewer than 3 eligible pairs and a margin
    <= SEL_MARGIN_MIN (KK-2)."""
    if len(rows) < 3:
        refuse("%d eligible pairs: the rule needs 3" % len(rows))
    strong, m_s = _nearest(rows, lambda r: -r["stat"])
    rest = [r for r in rows if r is not strong]
    mid, m_m = _nearest(rest, lambda r: abs(r["stat"] - T_MID))
    rest2 = [r for r in rest if r is not mid]
    edge, m_e = _nearest(rest2, lambda r: abs(r["stat"] - T_EDGE))
    sel, mar = {"STRONG": strong, "MID": mid, "EDGE": edge}, {"STRONG": m_s, "MID": m_m, "EDGE": m_e}
    for r in ROLES:
        if not mar[r] > SEL_MARGIN_MIN:
            refuse("%s: the margin to the runner-up is %.3g <= %.0e: the selection is not decided at the instrument's precision "
                   "(KK-2; a registrar's query)" % (r, mar[r], SEL_MARGIN_MIN))
    return sel, mar


def stage0_bytes(rows, sel):
    role_of = {sel[r]["pair"]: r for r in ROLES}
    lines = [STAGE0_HEADER] + ["%s\t%s\t%s\t%d\t%d\t%d\t%r\t%s" % (r["pair"], r["a"], r["b"], r["na"], r["nb"], r["na"] + r["nb"],
                                                                    r["stat"], role_of.get(r["pair"], "")) for r in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def parse_stage0(data):
    lines = data.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != STAGE0_HEADER:
        refuse("the stage-0 file's header is not %r" % STAGE0_HEADER)
    rows, roles = [], {}
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) != 8:
            refuse("malformed stage-0 row %r" % ln)
        r = dict(pair=p[0], a=p[1], b=p[2], na=int(p[3]), nb=int(p[4]), stat=float(p[6]))
        if p[7]:
            roles[p[7]] = r["pair"]
        rows.append(r)
    return rows, roles


def selection_pairs(sel):
    return {r: (sel[r]["a"], sel[r]["b"]) for r in ROLES}


def build_site_bytes(cat, src, pairs, twins=TWINS, reg=None):
    """-> (bytes, {site: sorted ids}, {site: {id: category}}, pops); IDENTITY first (CERT-PC-SIZE's rows), then per role the full
    site and the subsamples (KK-3)."""
    if len(set(cat.values())) != 14:
        refuse("%d declared categories, not 14" % len(set(cat.values())))
    pops = populations(cat, src, twins, reg)
    sites = {"IDENTITY": sorted(cat)}
    for r in ROLES:
        a, b = pairs[r]
        full = sorted(pops[a] + pops[b])
        sites["KK_%s_n%d_d0" % (r, len(full))] = full
        for n in SIZES:
            for d in DRAWS:
                sites["KK_%s_n%d_d%d" % (r, n, d)] = PCS.draw({a: pops[a], b: pops[b]}, n, d)
    labels = {s: {q: cat[q] for q in ids} for s, ids in sites.items()}
    rows = [SITE_HEADER]
    for s, ids in sites.items():
        rows.extend("%s\t%s\t%s" % (s, q, cat[q]) for q in ids)
    return ("\n".join(rows) + "\n").encode("utf-8"), sites, labels, pops


def overlap_lines(sites, pairs, pops):
    L = []
    for r in ROLES:
        a, b = pairs[r]
        N = len(pops[a]) + len(pops[b])
        parts = []
        for n in SIZES:
            ov = [len(set(sites["KK_%s_n%d_d%d" % (r, n, x)]) & set(sites["KK_%s_n%d_d%d" % (r, n, y)]))
                  for x in DRAWS for y in DRAWS if x < y]
            parts.append("n %d %d / %d (chance %.0f)" % (n, min(ov), max(ov), float(n) * n / N))
        L.append("OVERLAP %s (%s, population %d): 5 draws pairwise min / max: %s" % (r, pair_name(a, b), N, "; ".join(parts)))
    L.append("OVERLAP: the 5 draws of one pair and the two sizes are NOT independent replicates (CERT-PC-SIZE D-5)")
    shared = [(x, y) for x, y in itertools.combinations(ROLES, 2) if set(pairs[x]) & set(pairs[y])]
    L.append("OVERLAP: pairs sharing a category: %s" % (", ".join("%s / %s" % s for s in shared) if shared else "none"))
    return L


# ------------------------------------------------------------------------------------------------ dry-run / prepare / hashes
def cache_texts(data_root, ids):
    return PK2.cache_texts(data_root, ids)


def read_k2(data_root):
    """CERT-PC-K2's site file and its arm's declared statistics (KK-0 (ii)), from the data root."""
    sp = os.path.join(data_root, PK2.OUT_REL, PK2.SITES_NAME)
    ap = os.path.join(data_root, PK2.OUT_REL, PK2.ARM_NAME, "sites.csv")
    if not (os.path.isfile(sp) and os.path.isfile(ap)):
        return None, None
    if sha256_bytes(open(sp, "rb").read()) != PK2.SITES_SHA256:
        refuse("%s is not CERT-PC-K2's pinned site file" % sp)
    with open(ap, newline="", encoding="utf-8") as f:
        arm = {r["site_id"]: float(r["declared_stat"]) for r in csv.DictReader(f)}
    return PCS.parse_site_file(sp), arm


def assemble(data_root, cpc_labels, out=print):
    """Snapshot / root / labels pins (CERT-PC-SIZE's assemble), twins recomputed, populations, vectors, the routine check, stage 0,
    the selection, the stage-0 and site-file bytes."""
    cfg, sid, root, cat14, _d, _s = PCS.assemble(data_root, cpc_labels)
    cat, src = PK2.read_labels(cpc_labels, LABELS_SHA)
    if cat != cat14:
        refuse("the label file read twice differs")
    tw = find_twins(cat, src, cache_texts(data_root, [q for q in cat if src[q]]))
    if tuple(tw) != TWINS:
        refuse("stem-key twins among the src-carrying ids %s, not the pinned %s" % (tw, list(TWINS)))
    pops = populations(cat, src)
    vec = load_vectors(os.path.join(data_root, "embeddings_cache.db"), list(cat))
    k2s, k2a = read_k2(data_root)
    check_routine(vec, cat, k2s, k2a, out=out)
    rows = stage0(pops, vec)
    sel, mar = select(rows)
    s0 = stage0_bytes(rows, sel)
    data, sites, labels, _p = build_site_bytes(cat, src, selection_pairs(sel))
    return dict(cfg=cfg, sid=sid, root=root, cat=cat, src=src, pops=pops, rows=rows, sel=sel, mar=mar, s0=s0, data=data,
                sites=sites, labels=labels)


def command(cfg, heap):
    return ('.\\gradlew.bat certKnownPair --console=plain --offline --no-daemon -PjvmThreads=%d -PnullReps=%d '
            '"-DsnapshotId=%s" "-DsliceDim=%d" "-DsepBar=%s" "-DdropTop=%d" "-Dwhiten=%s" "-DsiteLabels=%s/%s" "-DoutDir=%s/%s"%s'
            % (cfg["jvmThreads"], cfg["nullReps"], SNAPSHOT, cfg["sliceDim"], repr(cfg["sepBar"]), cfg["dropTop"],
               str(cfg["whiten"]).lower(), OUT_REL, SITES_NAME, OUT_REL, ARM_NAME,
               "" if heap <= G.DEFAULT_HEAP_GB else ' "-DsiteNullHeap=%dg"' % heap))


def pin_word(got, pin):
    return "= the pin" if got == pin else ("NOT the pin %s" % pin if pin is not None else "NO PIN YET")


def dry_run(data_root, cpc_labels, out=print):
    out("pool: the B0-2 check is the operator's (v2_union_pool.py --dry-run); this mode opens no pool table")
    out("%s DRY RUN: zero calls, nothing written, no null replicate, no verdict" % TAG)
    CPC.heavy_check()
    A = assemble(data_root, cpc_labels, out=out)
    cfg, pops, rows, sel, mar = A["cfg"], A["pops"], A["rows"], A["sel"], A["mar"]
    out("%s member B0/mmlu_pro_lb = snapshot %s; root %s '%s' n = %d (TRAIN); CPC labels %s sha256 %s (= the pin)"
        % (TAG, A["sid"], A["root"]["id"], A["root"].get("label"), len(A["cat"]), cpc_labels, LABELS_SHA[:16]))
    out("%s stem-key twins dropped (KK-1): %s (= the pin; recomputed over all src-carrying ids)" % (TAG, list(TWINS)))
    out("%s populations (KK-1; = the registered class counts): %s" % (TAG, ", ".join(
        "%s %d" % (c, len(pops[c])) for c in sorted(pops, key=lambda c: (-len(pops[c]), c)))))
    out("%s STAGE 0: %d eligible pairs of %d (combined >= %d, each >= %d); the declared 2-way statistic at full size, no null:"
        % (TAG, len(rows), 91, MIN_COMBINED, MIN_EACH))
    role_of = {sel[r]["pair"]: r for r in ROLES}
    for r in sorted(rows, key=lambda r: (-r["stat"], r["pair"])):
        out("%s   %-32s n %4d (%3d / %3d)  stat %.6f  |-0.1078| %.6f  |-0.070| %.6f  %s" % (
            TAG, r["pair"], r["na"] + r["nb"], r["na"], r["nb"], r["stat"], abs(r["stat"] - T_MID), abs(r["stat"] - T_EDGE),
            role_of.get(r["pair"], "")))
    for r in ROLES:
        out("%s SELECTED %-6s = %s (n %d = %d + %d), stat %.6f; margin to the runner-up %.3g" % (
            TAG, r, sel[r]["pair"], sel[r]["na"] + sel[r]["nb"], sel[r]["na"], sel[r]["nb"], sel[r]["stat"], mar[r]))
    got_sel = {r: sel[r]["pair"] for r in ROLES}
    out("%s selection %s (%s)" % (TAG, json.dumps(got_sel), pin_word(got_sel, SELECTION)))
    s0sha, ssha = sha256_bytes(A["s0"]), sha256_bytes(A["data"])
    out("%s stage-0 file %s/%s: %d rows, sha256 %s (%s)" % (TAG, OUT_REL, STAGE0_NAME, len(rows), s0sha, pin_word(s0sha, STAGE0_SHA256)))
    pairs = selection_pairs(sel)
    for r in ROLES:
        a, b = pairs[r]
        for n in SIZES:
            q = PCS.allocate({a: len(pops[a]), b: len(pops[b])}, n)
            out("%s   %s n %d (%s): allocation %s %d / %s %d" % (TAG, r, n, DECIDING[n], a, q[a], b, q[b]))
    for ln in overlap_lines(A["sites"], pairs, pops):
        out("%s %s" % (TAG, ln))
    out("%s site file %s/%s: %d sites, %d rows, sha256 %s (%s)" % (
        TAG, OUT_REL, SITES_NAME, len(A["sites"]), A["data"].count(b"\n") - 1, ssha, pin_word(ssha, SITES_SHA256)))
    need, live, heap = G.heap_estimate(N_ROOT, cfg["sliceDim"], cfg["nullReps"], cfg["jvmThreads"])
    out("%s heap (g12_site_null's rule, the IDENTITY site n %d): live %d, peak %.2f GB -> %s" % (
        TAG, N_ROOT, live, need, "fits the 6g default" if heap <= G.DEFAULT_HEAP_GB else "-DsiteNullHeap=%dg" % heap))
    k2_cost = 2 * 30 * (466 ** 2)
    kk_cost = sum(len(A["sites"][s]) ** 2 for s in A["sites"] if s != "IDENTITY")
    out("%s wall: about %.0f min at %d threads (CERT-PC-K2's arm took %d s for IDENTITY + 30 sites x (plain + deflated) + C0; this "
        "arm runs IDENTITY + 33 sites x plain + C0, sum n^2 %d vs CERT-PC-K2's about %d; budget the window at about 40-70 min, "
        "the registration's)" % (TAG, PK2_WALL_S / 60.0 * max(1.0, kk_cost / float(k2_cost)), cfg["jvmThreads"], PK2_WALL_S,
                                  kk_cost, k2_cost))
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
    return dict(selection=got_sel, stage0_sha=s0sha, sites_sha=ssha, heap=heap, sites=len(A["sites"]))


def prepare(data_root, cpc_labels):
    if not CPC.same_checkout(data_root):
        refuse("--prepare writes the files into this checkout; the arm reads them from the data root's: run from %s" % data_root)
    CPC.heavy_check()
    A = assemble(data_root, cpc_labels)
    got_sel = {r: A["sel"][r]["pair"] for r in ROLES}
    if got_sel != SELECTION:
        refuse("the selection %s is not SELECTION %s" % (got_sel, SELECTION))
    if sha256_bytes(A["s0"]) != STAGE0_SHA256:
        refuse("the stage-0 file's sha256 %s is not STAGE0_SHA256 %s" % (sha256_bytes(A["s0"]), STAGE0_SHA256))
    if sha256_bytes(A["data"]) != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s" % (sha256_bytes(A["data"]), SITES_SHA256))
    d = os.path.join(ROOT, OUT_REL)
    os.makedirs(d, exist_ok=True)
    for name, data in ((STAGE0_NAME, A["s0"]), (SITES_NAME, A["data"])):
        with open(os.path.join(d, name), "xb") as f:
            f.write(data)
        print("%s wrote %s/%s (sha256 %s)" % (TAG, OUT_REL, name, sha256_bytes(data)))


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


# ------------------------------------------------------------------------------------------------ the rules
def sd_sample(xs):
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def sd_pop(xs):
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def gks(full_status, margin, sd):
    """G-KS: KNOWN-STRENGTH iff the full site CERTIFIED (k_d <= 14, C0 comparable, not DEGENERATE) and margin > sd."""
    return "KNOWN-STRENGTH" if (full_status == "CERTIFIED" and bool(margin > sd)) else "NOT-A-CONTROL"


def kk_definite(words):
    if all(w == "CERTIFIED-AT-SIZE" for w in words):
        return "K2-SENSITIVE"
    if any(w == "NOT-CERTIFIED-AT-SIZE" for w in words):
        return "K2-SIZE-LIMIT"
    return "MIXED"


def kk_word(words):
    """KK over the gated pairs' size verdicts: NO-CONTROL iff fewer than 2; KK-6 (Q-K1) for NOT EVALUABLE pairs."""
    if len(words) < 2:
        return "NO-CONTROL"
    ne = [i for i, w in enumerate(words) if w == "NOT EVALUABLE"]
    outs = set()
    for sub in itertools.product(("CERTIFIED-AT-SIZE", "NOT-CERTIFIED-AT-SIZE", "MIXED"), repeat=len(ne)):
        w = list(words)
        for i, v in zip(ne, sub):
            w[i] = v
        outs.add(kk_definite(w))
    return outs.pop() if len(outs) == 1 else "NOT EVALUABLE"


def kk_readings(gate, size_words, ruling=None):
    """KK-7: reading A (EDGE descriptive-only), reading B (EDGE in when gated) -> (A, B, deciding word)."""
    def over(roles):
        return kk_word([size_words[r] for r in roles if gate[r] == "KNOWN-STRENGTH"])
    a, b = over(("STRONG", "MID")), over(ROLES)
    if ruling == "EDGE-DESCRIPTIVE":
        return a, b, a
    if ruling == "EDGE-IN-IF-GATED":
        return a, b, b
    if ruling is not None:
        refuse("Q_KK1_RULING %r is not None / EDGE-DESCRIPTIVE / EDGE-IN-IF-GATED" % ruling)
    return a, b, (a if a == b else "WITHHELD")


def in_closed(x, lo, hi):
    v = Fraction(repr(x))
    return bool(lo <= v <= hi)


def median(xs):
    s = sorted(xs)
    return s[len(s) // 2]


# ------------------------------------------------------------------------------------------------ the readout
def analyze(arm_dir, out_dir, sites_path, stage0_path, labels_path, out=print):
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
    # stage 0 (KK-0): pinned file, the rule re-derived from it, the pinned selection
    s0bytes = open(stage0_path, "rb").read()
    if sha256_bytes(s0bytes) != STAGE0_SHA256:
        refuse("the stage-0 file's sha256 %s is not STAGE0_SHA256 %s" % (sha256_bytes(s0bytes), STAGE0_SHA256))
    cat, src = PK2.read_labels(labels_path, LABELS_SHA)
    pops = populations(cat, src)
    s0rows, s0roles = parse_stage0(s0bytes)
    want_pairs = [pair_name(a, b) for a, b in eligible_pairs(pops)]
    if [r["pair"] for r in s0rows] != want_pairs or any((r["na"], r["nb"]) != (len(pops[r["a"]]), len(pops[r["b"]])) for r in s0rows):
        refuse("the stage-0 file does not list exactly the %d eligible pairs at the labels' counts" % len(want_pairs))
    sel, mar = select(s0rows)
    got_sel = {r: sel[r]["pair"] for r in ROLES}
    if got_sel != s0roles or got_sel != SELECTION:
        refuse("the rule re-derives %s from the stage-0 file; the file's roles are %s, SELECTION %s" % (got_sel, s0roles, SELECTION))
    pairs = selection_pairs(sel)
    sbytes = open(sites_path, "rb").read()
    s_sha = sha256_bytes(sbytes)
    if st.get("sites_sha256") != s_sha:
        refuse("the arm read site file sha256 %s; %s is %s" % (st.get("sites_sha256"), sites_path, s_sha))
    if s_sha != SITES_SHA256:
        refuse("the site file's sha256 %s is not SITES_SHA256 %s" % (s_sha, SITES_SHA256))
    rebuilt, rsites, rlabels, _rp = build_site_bytes(cat, src, pairs)
    if rebuilt != sbytes:
        refuse("the site file is not the one the CPC labels (sha256 %s), TWINS and the stage-0 selection rebuild" % LABELS_SHA[:16])
    hb, ha = (os.path.join(out_dir, "emb_hashes_%s.json" % x) for x in ("before", "after"))
    if not (os.path.isfile(hb) and os.path.isfile(ha)):
        refuse("the embeddings_cache.db hashes before and after the arm are owed (--hashes before / after)")
    if json.load(open(hb)) != json.load(open(ha)):
        refuse("embeddings_cache.db changed during the arm (per-table hashes differ)")
    sizes = {r: len(pops[pairs[r][0]]) + len(pops[pairs[r][1]]) for r in ROLES}
    names = site_names(sizes)
    want = ["IDENTITY"] + names
    if list(rsites) != want:
        refuse("internal: the rebuilt site file lists %s" % list(rsites)[:5])

    say("%s CERT-PC-K2-KNOWN outcome (tools/analysis/cert_pc_k2_known.py blob %s; cert_pc_k2.py blob %s imported). Zero calls."
        % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), PK2_BLOB))
    say("registration: " + REG)
    say("arm: %s; snapshot %s; site file sha256 %s (= SITES_SHA256; rebuilt from the CPC labels sha256 %s, TWINS %s and the stage-0 "
        "selection: byte-identical); stage-0 file sha256 %s (= STAGE0_SHA256); reps %s; sliceDim %s; sepBar %s; dropTop %s; whiten "
        "%s; minClusterSize %s; C0 seed base %s; threads %s; embeddings_cache.db per-table hashes before == after" % (
            st["arm"], st["snapshot"], s_sha, LABELS_SHA[:16], list(TWINS), sha256_bytes(s0bytes), st["reps"], st["sliceDim"],
            st["sepBar"], st["dropTop"], st["whiten"], st["minClusterSize"], st["c0Seed"], st.get("threads")))
    say("builder's readings KK-0..KK-8 (docstring); registration query Q-KK1 (KK-7: EDGE in KK1 when gated?) ruling: %s"
        % ({"EDGE-DESCRIPTIVE": "EDGE-DESCRIPTIVE (registrar 65e5c0d7, programme L24046 / L24048 / L24050: KK1 / KK2 / F-KK count "
                                "STRONG and MID only; reading A decides, reading B descriptive)"}.get(Q_KK1_RULING, Q_KK1_RULING)
           or "NONE (the deciding word is printed only where readings A and B agree)"))
    say("STAGE 0 (the TRAIN-only pair rule, re-derived from the pinned stage-0 file): %d eligible pairs (combined >= %d, each >= %d)"
        % (len(s0rows), MIN_COMBINED, MIN_EACH))
    for r in sorted(s0rows, key=lambda r: (-r["stat"], r["pair"])):
        say("  stage0 %-32s n %4d  stat %.6f%s" % (r["pair"], r["na"] + r["nb"], r["stat"],
                                                  "  <- %s" % next(x for x in ROLES if got_sel[x] == r["pair"])
                                                  if r["pair"] in got_sel.values() else ""))
    for r in ROLES:
        say("SELECTED %s = %s (n %d), stage-0 stat %.6f, margin to the runner-up %.3g" % (
            r, sel[r]["pair"], sizes[r], sel[r]["stat"], mar[r]))

    with open(os.path.join(arm_dir, "sites.csv"), newline="", encoding="utf-8") as f:
        rows = {r["site_id"]: r for r in csv.DictReader(f)}
    if list(rows) != want:
        refuse("sites.csv holds %s, not IDENTITY + the 33 KK sites in order" % list(rows)[:20])
    reps = {}
    with open(os.path.join(arm_dir, "replicates.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            reps.setdefault((r["site_id"], r["arm"]), []).append((int(r["rep"]), float(r["stat"])))
    for key, xs in reps.items():
        if [i for i, _x in xs] != list(range(REPS)):
            refuse("replicates %s: reps %d, not 0..%d in order (a partial file)" % (key, len(xs), REPS - 1))
    R = {k: [x for _i, x in v] for k, v in reps.items()}
    for s in want:
        for a_ in (("SN",) if s == "IDENTITY" else ("SN", "C0")):
            if (s, a_) not in R:
                refuse("replicates: %s's %s arm is missing" % (s, a_))

    # IDENTITY (KK-8)
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
    say("SUPPORT (a) per chosen pair 1 full site + 2 sizes x 5 subsamples, %d null replicates each; DECIDING units: 5 subsamples per "
        "gated pair at n 486 (KK1; KK2 at n 441); (b) DEFF 1.0 by construction (each p_d is a permutation-null count; no item "
        "resampling; a tree-arm DEFF per D-PR-1 does not apply); (c) n_eff = %d replicates per site; (d) SE of p_d at the bar "
        "sqrt(0.05 x 0.95 / %d) = %.4f; (e) MDE80 = 2.8 x SE = %.4f per site (a site with true p_d <= %.3f certifies with >= 80%%); "
        "(f) SCOREABLE for STRONG and MID (p_d about 1/301 = %.4f), EDGE DESCRIPTIVE-ONLY (Q-KK1); (g) floor 1/301 << 0.05; "
        "NULL-INFEASIBLE below n %d, DEGENERATE below %d reached replicates" % (
            REPS, REPS, REPS, se, 2.8 * se, 0.05 - 2.8 * se, 1 / 301.0, 2 * MCS, DEGENERATE_MIN))
    say("SUPPORT: no matches and no questions: wrong(established), the tie conventions A / B and a question-clustered bootstrap "
        "are N/A to a null exceedance count")
    for ln in LIKE:
        say(ln)
    for ln in overlap_lines(rsites, pairs, pops):
        say(ln)

    res, out_rows = {}, []
    for s in names:
        role = s.split("_")[1]
        n_reg = int(s.split("_")[2][1:])
        r = rows[s]
        n = int(r["n"])
        a, b = pairs[role]
        lab = rlabels[s]
        gs = "%d/%d" % (sum(1 for v in lab.values() if v == a), sum(1 for v in lab.values() if v == b))
        if n != len(rsites[s]) or n != n_reg or int(r["groups"]) != 2 or r["group_sizes"] != gs:
            refuse("sites.csv: %s n %s groups %s sizes %s (the site file holds %d, %s/%s %s; want n %d, 2 groups)"
                   % (s, r["n"], r["groups"], r["group_sizes"], len(rsites[s]), a, b, gs, n_reg))
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
        status = PK2.subsample_status(n, k, comparable, reached)
        res[s] = dict(role=role, n=n, d=d, k=k, np95=np95, c0p95=c0p95, comparable=comparable, reached=reached, status=status)
        say("  %-20s n %4d (%s/%s %s): declared %.6f; null min %.6f / p95 %.6f / max %.6f; k_d %3d of %d, p_d %d/301 = %.6f; "
            "C0 p95 %.6f (%s); reached %d -> %s" % (
                s, n, a, b, gs, d, sn[0], np95, sn[-1], k, REPS, k + 1, float(CPC.p_of(k)), c0p95,
                "comparable" if comparable else "FAILS: reaches the null p95", reached, status))
        out_rows.append([s, role, pair_name(a, b), n, gs, "%.6f" % d, k, "%d/301" % (k + 1), "%.6f" % sn[0], "%.6f" % np95,
                         "%.6f" % sn[-1], "%.6f" % c0p95, str(comparable).lower(), reached, status])
    # stage 0 reproduced by the instrument (KK-0 (iii))
    for role in ROLES:
        f = res["KK_%s_n%d_d0" % (role, sizes[role])]
        diff = abs(f["d"] - sel[role]["stat"])
        if not diff <= TOL:
            refuse("%s: the arm's full-site statistic %.17g differs from its stage-0 value %.17g by %.2e > %.0e (KK-0 (iii))"
                   % (role, f["d"], sel[role]["stat"], diff, TOL))
    say("STAGE 0 REPRODUCED: each chosen pair's full-site statistic printed by the arm equals its stage-0 value within %.0e" % TOL)

    gate, size_words = {}, {n: {} for n in SIZES}
    for role in ROLES:
        f = res["KK_%s_n%d_d0" % (role, sizes[role])]
        d486 = [res["KK_%s_n486_d%d" % (role, dd)]["d"] for dd in DRAWS]
        sd1, sd0 = sd_sample(d486), sd_pop(d486)
        margin = f["d"] - f["np95"]
        gate[role] = gks(f["status"], margin, sd1)
        alt = gks(f["status"], margin, sd0)
        say("G-KS %s (%s): %s; full site n %d %s (k_d %d, C0 %s, reached %d); statistic - null p95 = %.6f - %.6f = %.6f vs SD over "
            "the five n-486 subsamples %.6f (sample, n - 1; KK-5); population SD %.6f -> %s" % (
                role, pair_name(*pairs[role]), gate[role], f["n"], f["status"], f["k"],
                "comparable" if f["comparable"] else "FAILS", f["reached"], f["d"], f["np95"], margin, sd1, sd0,
                "the gate word is unchanged" if alt == gate[role] else "the gate word WOULD CHANGE to %s (Q-KK2)" % alt))
    for n in SIZES:
        for role in ROLES:
            sts = [res["KK_%s_n%d_d%d" % (role, n, dd)]["status"] for dd in DRAWS]
            c = sum(1 for x in sts if x == "CERTIFIED")
            nc = sum(1 for x in sts if x == "NOT CERTIFIED")
            ne_c0 = sum(1 for x in sts if x == "NOT EVALUABLE (C0)")
            ne_all = sum(1 for x in sts if x.startswith("NOT EVALUABLE"))
            size_words[n][role] = PCS.size_verdict(sts)
            ds = [res["KK_%s_n%d_d%d" % (role, n, dd)]["d"] for dd in DRAWS]
            ns = [res["KK_%s_n%d_d%d" % (role, n, dd)]["np95"] for dd in DRAWS]
            say("PAIR %s n %d: %s (%s); certified %d, not certified %d, NOT EVALUABLE %d (C0 %d, degenerate / infeasible %d) of 5 "
                "(gate first); median declared %.6f vs median null p95 %.6f" % (
                    role, n, size_words[n][role], gate[role], c, nc, ne_all, ne_c0, ne_all - ne_c0, median(ds), median(ns)))
    kk = {}
    for n in SIZES:
        ra, rb, word = kk_readings(gate, size_words[n], Q_KK1_RULING)
        kk[n] = word
        ng_a = sum(1 for r in ("STRONG", "MID") if gate[r] == "KNOWN-STRENGTH")
        ng_b = sum(1 for r in ROLES if gate[r] == "KNOWN-STRENGTH")
        say("%s (n %d) reading A (EDGE descriptive-only; %d gated of STRONG / MID): %s; reading B (EDGE in when gated; %d gated of "
            "3): %s" % (DECIDING[n], n, ng_a, ra, ng_b, rb))
        say("%s (n %d): %s%s" % (DECIDING[n], n, word, "" if word != "WITHHELD" else
                                  " (readings A and B differ; registration query Q-KK1 unruled: no deciding word)"))
    kk1 = kk[486]
    if kk1 == "K2-SIZE-LIMIT":
        say(SENT_FKK_FIRED)
    else:
        say("F-KK: NOT FIRED (KK1 %s). F-TAX N-1 and F2 stand." % kk1)
        if kk1 == "K2-SENSITIVE":
            say(SENT_SENSITIVE)
        elif kk1 == "NO-CONTROL":
            say(SENT_NO_CONTROL)
        else:
            say("READING: none (KK1 %s: %s; no sentence)" % (kk1, {"MIXED": "a registered MIXED",
                                                                  "NOT EVALUABLE": "not evaluable (KK-6)",
                                                                  "WITHHELD": "Q-KK1 unruled (KK-7)"}[kk1]))
    # predictions
    p1 = [("STRONG", in_closed(sel["STRONG"]["stat"], *P1_STRONG), "[0.12, 0.35]"),
          ("MID", in_closed(sel["MID"]["stat"], Fraction("0.1078") - P1_HALF, Fraction("0.1078") + P1_HALF), "0.1078 +/- 0.010"),
          ("EDGE", in_closed(sel["EDGE"]["stat"], Fraction("0.070") - P1_HALF, Fraction("0.070") + P1_HALF), "0.070 +/- 0.010")]
    for role, held, band in p1:
        say("P1 %s stage-0 statistic %.6f in %s: %s" % (role, sel[role]["stat"], band, "HELD" if held else "FAILED"))
    for role in ROLES:
        e = bool(gate[role] == "KNOWN-STRENGTH")
        say("P2 %s KNOWN-STRENGTH (p %.2f): event %s, Brier %.4f" % (role, P2_P[role], "yes" if e else "no",
                                                                   (P2_P[role] - (1.0 if e else 0.0)) ** 2))
    if kk1 in P3_PROBS:
        b3 = sum((p - (1.0 if v == kk1 else 0.0)) ** 2 for v, p in P3_PROBS.items())
        say("P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome %s, Brier (4-way sum) %.4f"
            % (kk1, b3))
    else:
        say("P3 KK1 readings: NOT SCORED (KK1 %s)" % kk1)
    p4v = [res["KK_%s_n486_d%d" % (role, dd)]["np95"] for role in ROLES for dd in DRAWS]
    p4 = median(p4v)
    say("P4 merged-site null p95 at n 486, median over the %d subsamples of the 3 chosen pairs: %.6f in [0.045, 0.075]: %s" % (
        len(p4v), p4, "HELD" if bool(P4_BAND[0] <= p4 <= P4_BAND[1]) else "FAILED"))
    allc = sum(1 for s in names if res[s]["comparable"])
    e5 = bool(allc == len(names))
    say("P5 C0 comparable on every site (p 0.85): event %s (%d of %d comparable), Brier %.4f" % (
        "yes" if e5 else "no", allc, len(names), (P5_P - (1.0 if e5 else 0.0)) ** 2))
    say("DESCRIPTIVE: EDGE (%s) G-KS %s, n 486 %s, n 441 %s (reported whether gated or not)" % (
        pair_name(*pairs["EDGE"]), gate["EDGE"], size_words[486]["EDGE"], size_words[441]["EDGE"]))
    say(DOES_NOT_SHOW)

    os.makedirs(out_dir, exist_ok=True)
    with open(outcome_p, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_p, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["site", "role", "pair", "n", "group_sizes", "declared", "k_d", "p_d", "null_min", "null_p95", "null_max",
                    "c0_p95", "c0_comparable", "reached", "status"])
        w.writerows(out_rows)
    out("%s wrote %s and %s (write-once)" % (TAG, outcome_p, csv_p))
    return dict(kk=kk, gate=gate, size_words=size_words, res=res, sel=got_sel, fired=bool(kk1 == "K2-SIZE-LIMIT"), lines=L)


# ------------------------------------------------------------------------------------------------ selftest
FX_SEL = {"STRONG": ("law", "math"), "MID": ("chemistry", "physics"), "EDGE": ("biology", "math")}


def _labels_fixture():
    """6,993 ids: the 14 categories at the registered counts with src, the pinned twin (math, with src), 3 math + 1 computer
    science ids without src (as the record's label file)."""
    cat, src, i = {}, {}, 0

    def add(c, s, qid=None):
        nonlocal i
        q = qid or "q_%05d" % i
        i += 1
        cat[q], src[q] = c, s
    for c in sorted(REG_COUNTS):
        for _j in range(REG_COUNTS[c]):
            add(c, "ori_mmlu-x")
    add("math", "scibench-stat", TWINS[0])
    for c in ("math", "math", "math", "computer science"):
        add(c, "")
    return cat, src


def _write_labels(path, cat, src):
    data = (CPC.LABEL_HEADER + "\n" + "".join("%s\t%s\t%s\n" % (q, cat[q], src[q]) for q in sorted(cat))).encode("utf-8")
    open(path, "wb").write(data)
    return sha256_bytes(data)


def _stage0_rows(pops, stats=None, chosen=None):
    """Synthetic stage-0 rows: every eligible pair 0.030 + 0.0001 x index, the chosen pairs at the given statistics."""
    stats = stats or {}
    chosen = chosen or {"STRONG": 0.30, "MID": 0.1078, "EDGE": 0.070}
    by_pair = {pair_name(*FX_SEL[r]): chosen[r] for r in ROLES}
    rows = []
    for i, (a, b) in enumerate(eligible_pairs(pops)):
        nm = pair_name(a, b)
        rows.append(dict(pair=nm, a=a, b=b, na=len(pops[a]), nb=len(pops[b]),
                         stat=stats.get(nm, by_pair.get(nm, 0.030 + 0.0001 * i))))
    return rows


def _fx(tmp, spec=None, chosen=None, status="COMPLETE", hashes_equal=True, partial=False, site_sha_bad=False, sepbar="0.0145",
        arm="certKnownPair", snapshot=SNAPSHOT, ident_d=0.10780301, ident_k=0, ident_seed="n00000001", ident_n=6993,
        ident_p95=0.041626, ident_max=0.042414, drop_site=None, n_bad=None, k_lie=None, c0_lie=None, gs_lie=None,
        tamper_site=None, drop_reps_arm=None, full_shift=None, stage0_role_lie=False, stage0_drop_first=False):
    """spec[site-key] (site-key = "<ROLE>_full" or the KK name without the full size) = dict(k=, d=None, c0=small|equal|below,
    reached=None|int). SN = i x sc (i = 0..299) with sc = d / (300 - k) (d default (300 - k) / 1000; the full site's d = its stage-0
    statistic), so exactly k replicates are >= d; null p95 = 284 sc. Returns (arm, out, sites, stage0, labels, pins)."""
    spec = spec or {}
    arm_d, outd = os.path.join(tmp, "arm"), os.path.join(tmp, "out")
    os.makedirs(arm_d)
    os.makedirs(outd)
    cat, src = _labels_fixture()
    lp = os.path.join(tmp, "declared_labels.tsv")
    lsha = _write_labels(lp, cat, src)
    pops = populations(cat, src)
    rows = _stage0_rows(pops, chosen=chosen)
    sel, _m = select(rows)
    assert selection_pairs(sel) == FX_SEL, selection_pairs(sel)
    s0 = stage0_bytes(rows, sel)
    if stage0_role_lie:                                     # the first pair (not the rule's MID) claims MID; the rule's MID none
        lines = [(ln.rsplit("\t", 1)[0] + "\t") if ln.endswith("\tMID") else ln for ln in s0.decode().split("\n")]
        lines[1] = lines[1].rsplit("\t", 1)[0] + "\tMID"
        s0 = "\n".join(lines).encode()
    if stage0_drop_first:                                   # a filler pair (not chosen) missing from the stage-0 table
        lines = s0.decode().split("\n")
        s0 = "\n".join(lines[:1] + lines[2:]).encode()
    s0p = os.path.join(outd, STAGE0_NAME)
    open(s0p, "wb").write(s0)
    data, sites, labels, _p = build_site_bytes(cat, src, FX_SEL)
    pins = (lsha, sha256_bytes(s0), sha256_bytes(data), {r: sel[r]["pair"] for r in ROLES})
    sp = os.path.join(outd, SITES_NAME)
    if tamper_site:          # swap one row's id for another id of the same category outside the site: not the registered file
        q0 = sites[tamper_site][0]
        repl = next(q for q in sorted(cat) if cat[q] == cat[q0] and src[q] and q not in sites[tamper_site] and q not in TWINS)
        old = ("%s\t%s\t%s\n" % (tamper_site, q0, cat[q0])).encode()
        data = data.replace(old, ("%s\t%s\t%s\n" % (tamper_site, repl, cat[q0])).encode(), 1)
    open(sp, "wb").write(data)
    sha = sha256_bytes(data if not site_sha_bad else b"x")
    with open(os.path.join(arm_d, "status.txt"), "w") as f:
        f.write("%s\narm=%s\nsnapshot=%s\nsites_sha256=%s\nreps=300\nsliceDim=512\nsepBar=%s\ndropTop=0\nwhiten=false\n"
                "minClusterSize=55\nc0Seed=20261002\nthreads=12\n" % (status, arm, snapshot, sha, sepbar))
    names = ["IDENTITY"] + [s for s in sites if s != "IDENTITY"]
    if drop_site:
        names = [s for s in names if not s.endswith(drop_site)]
    stat_of = {r: sel[r]["stat"] for r in ROLES}
    srows, rep_lines = [], []
    for s in names:
        if s == "IDENTITY":
            sn = [i / 100000.0 for i in range(284)] + [ident_p95] * 15 + [ident_max]
            if ident_k:
                sn[-1] = ident_d + 1e-9
            srows.append('IDENTITY,"IDENTITY",%d,14,,%r,%d,,,,,%s,300' % (ident_n, ident_d, ident_k, ident_seed))
            rep_lines += ['"IDENTITY",SN,%d,%r' % (i, x) for i, x in enumerate(sn[:150] if partial else sn)]
            continue
        role = s.split("_")[1]
        key = "%s_full" % role if s.endswith("_d0") else s
        sp_ = dict(k=0, d=None, c0="small", reached=None)
        sp_.update(spec.get(key, {}))
        k_ = sp_["k"]
        if s.endswith("_d0"):
            d = stat_of[role] + (full_shift if (full_shift and role == "MID") else 0.0)
        else:
            d = sp_["d"] if sp_["d"] is not None else (300 - k_) / 1000.0
        sc = d / (300 - k_) if k_ < 300 else d / 300.0
        sn = [i * sc for i in range(300)]
        if k_ >= 300:
            sn = [d + 1.0 + i * sc for i in range(300)]
        if sp_["reached"] is not None:
            sn = [0.0] * (300 - sp_["reached"]) + [0.5 * sc + j * sc for j in range(sp_["reached"])]
            d = 1000.0 * sc if not s.endswith("_d0") else d
        n = len(sites[s]) + (1 if n_bad == s else 0)
        a, b = FX_SEL[role]
        gs = "%d/%d" % (sum(1 for v in labels[s].values() if v == a), sum(1 for v in labels[s].values() if v == b))
        if gs_lie == s:
            gs = "1/%d" % (n - 1)
        c0 = {"small": [i * sc * 0.001 for i in range(300)], "equal": list(sn), "below": [x - 1e-12 for x in sn]}[sp_["c0"]]
        k_arm = sum(1 for x in sn if x >= d) + (1 if k_lie == s else 0)
        c0p = CPC.pctl(sorted(c0), 0.95) + (1e-6 if c0_lie == s else 0.0)
        srows.append('KK,"%s",%d,2,%s,%r,%d,,,%r,123,%s,300' % (s, n, gs, d, k_arm, c0p, s))
        for arm_, xs in (("SN", sn), ("C0", c0)):
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
    return arm_d, outd, sp, s0p, lp, pins, sites


@contextlib.contextmanager
def _pins(lsha, s0sha, ssha, sel, ruling="keep"):
    global LABELS_SHA, STAGE0_SHA256, SITES_SHA256, SELECTION, Q_KK1_RULING
    saved = (LABELS_SHA, STAGE0_SHA256, SITES_SHA256, SELECTION, Q_KK1_RULING)
    LABELS_SHA, STAGE0_SHA256, SITES_SHA256, SELECTION = lsha, s0sha, ssha, sel
    if ruling != "keep":
        Q_KK1_RULING = ruling
    try:
        yield
    finally:
        LABELS_SHA, STAGE0_SHA256, SITES_SHA256, SELECTION, Q_KK1_RULING = saved


def _ks(role, size, ks, **kw):
    return {"KK_%s_n%d_d%d" % (role, size, i + 1): dict(k=k, **kw) for i, k in enumerate(ks)}


def _sizes():
    cat, src = _labels_fixture()
    pops = populations(cat, src)
    return {r: len(pops[FX_SEL[r][0]]) + len(pops[FX_SEL[r][1]]) for r in ROLES}


def selftest():
    global _IN_SELFTEST
    _IN_SELFTEST = True
    if not __debug__:
        refuse("python -O strips the selftest's asserts: run without -O")
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="pkkst_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:            # noqa: BLE001
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(tmp, ruling="keep", **kw):
        arm, outd, sp, s0p, lp, pins, _s = _fx(tmp, **kw)
        lines = []
        with _pins(*pins, ruling=ruling):
            r = analyze(arm, outd, sp, s0p, lp, out=lines.append)
        return r, lines, outd

    def refused(tmp, needle, pins_override=None, **kw):
        arm, outd, sp, s0p, lp, pins, _s = _fx(tmp, **kw)
        try:
            with _pins(*(pins_override(pins) if pins_override else pins)):
                analyze(arm, outd, sp, s0p, lp, out=lambda s: None)
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

    SZ = _sizes()

    def full(role):
        return "KK_%s_n%d_d0" % (role, SZ[role])

    def all_sensitive(tmp):
        r, L, outd = run(tmp)
        assert r["kk"] == {486: "K2-SENSITIVE", 441: "K2-SENSITIVE"} and r["fired"] is False, r["kk"]
        assert r["gate"] == {"STRONG": "KNOWN-STRENGTH", "MID": "KNOWN-STRENGTH", "EDGE": "KNOWN-STRENGTH"}, r["gate"]
        has(L, "KK1 (n 486) reading A (EDGE descriptive-only; 2 gated of STRONG / MID): K2-SENSITIVE; reading B (EDGE in when gated; "
               "3 gated of 3): K2-SENSITIVE")
        has(L, "KK1 (n 486): K2-SENSITIVE")
        has(L, "KK2 (n 441): K2-SENSITIVE")
        has(L, "F-KK: NOT FIRED (KK1 K2-SENSITIVE). F-TAX N-1 and F2 stand.")
        has(L, SENT_SENSITIVE)
        has(L, "SELECTED STRONG = law + math (n %d), stage-0 stat 0.300000, margin to the runner-up 0.192" % SZ["STRONG"])
        has(L, "SELECTED MID = chemistry + physics (n %d), stage-0 stat 0.107800, margin to the runner-up 0.0378" % SZ["MID"])
        has(L, "SELECTED EDGE = biology + math (n %d), stage-0 stat 0.070000, margin to the runner-up 0.0352" % SZ["EDGE"])
        # MID full: d 0.1078, k 0 -> null p95 = 284 x 0.1078 / 300; subsample d = 0.3 exactly for all -> SD 0
        has(L, "G-KS MID (chemistry + physics): KNOWN-STRENGTH; full site n %d CERTIFIED (k_d 0, C0 comparable, reached 299); "
               "statistic - null p95 = 0.107800 - 0.102051 = 0.005749 vs SD over the five n-486 subsamples 0.000000 (sample, n - 1; "
               "KK-5); population SD 0.000000 -> the gate word is unchanged" % SZ["MID"])
        has(L, "PAIR STRONG n 486: CERTIFIED-AT-SIZE (KNOWN-STRENGTH); certified 5, not certified 0, NOT EVALUABLE 0 (C0 0, degenerate "
               "/ infeasible 0) of 5 (gate first); median declared 0.300000 vs median null p95 0.284000")
        has(L, "P1 STRONG stage-0 statistic 0.300000 in [0.12, 0.35]: HELD")
        has(L, "P1 MID stage-0 statistic 0.107800 in 0.1078 +/- 0.010: HELD")
        has(L, "P1 EDGE stage-0 statistic 0.070000 in 0.070 +/- 0.010: HELD")
        has(L, "P2 STRONG KNOWN-STRENGTH (p 0.90): event yes, Brier 0.0100")
        has(L, "P2 EDGE KNOWN-STRENGTH (p 0.30): event yes, Brier 0.4900")
        has(L, "P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome K2-SENSITIVE, Brier "
               "(4-way sum) 0.2750")
        has(L, "P4 merged-site null p95 at n 486, median over the 15 subsamples of the 3 chosen pairs: 0.284000 in [0.045, 0.075]: "
               "FAILED")
        has(L, "P5 C0 comparable on every site (p 0.85): event yes (33 of 33 comparable), Brier 0.0225")
        has(L, "DESCRIPTIVE: EDGE (biology + math) G-KS KNOWN-STRENGTH, n 486 CERTIFIED-AT-SIZE, n 441 CERTIFIED-AT-SIZE (reported "
               "whether gated or not)")
        has(L, "STAGE 0 REPRODUCED: each chosen pair's full-site statistic printed by the arm equals its stage-0 value within 1e-09")
        has(L, "IDENTITY: REPRODUCED (precondition held; null p95 / max equal PC1's)")
        has(L, DOES_NOT_SHOW)
        assert any(l.startswith("SUPPORT (a) per chosen pair 1 full site") and "0.0126" in l and "0.0352" in l for l in L), L
        assert sum(1 for l in L if l.startswith("  stage0 ")) == 49, "the stage-0 table is not printed whole"
        has(L, "  stage0 law + math                       n 1383  stat 0.300000  <- STRONG")
        has(L, "  %-20s n %4d (law/math 578/805): declared 0.300000; null min 0.000000 / p95 0.284000 / max 0.299000; k_d   0 of 300, "
               "p_d 1/301 = 0.003322; C0 p95 0.000284 (comparable); reached 299 -> CERTIFIED" % (full("STRONG"), SZ["STRONG"]))
        has(L, "  KK_EDGE_n441_d1      n  441 (biology/math 142/299): declared 0.300000; null min 0.000000 / p95 0.284000 / max "
               "0.299000; k_d   0 of 300, p_d 1/301 = 0.003322; C0 p95 0.000284 (comparable); reached 299 -> CERTIFIED")
        txt = open(os.path.join(outd, OUTCOME_NAME), encoding="utf-8").read()
        assert txt.startswith("pool: none (no DB opened)\n") and "\nKK1 (n 486): K2-SENSITIVE\n" in txt
        rows = list(csv.DictReader(open(os.path.join(outd, CSV_NAME), encoding="utf-8")))
        assert len(rows) == 33 and rows[0]["site"] == full("STRONG") and rows[0]["p_d"] == "1/301" and \
            rows[0]["status"] == "CERTIFIED" and rows[0]["group_sizes"] == "578/805", rows[0]
        try:
            with _pins(*_fx(sub(tmp, 9))[5]):
                analyze(os.path.join(tmp, "arm"), outd, os.path.join(outd, SITES_NAME), os.path.join(outd, STAGE0_NAME),
                        os.path.join(tmp, "declared_labels.tsv"), out=lambda s: None)
            raise AssertionError("second analyze not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e

    def size_limit(tmp):
        # MID NOT-CERTIFIED at 486 (k 15 on 4 of 5) -> K2-SIZE-LIMIT under both readings; F-KK fires
        sp_ = _ks("MID", 486, [14, 15, 15, 15, 15])
        r, L, _o = run(sub(tmp, 0), spec=sp_)
        assert r["kk"] == {486: "K2-SIZE-LIMIT", 441: "K2-SENSITIVE"} and r["fired"] is True, r["kk"]
        has(L, "PAIR MID n 486: NOT-CERTIFIED-AT-SIZE (KNOWN-STRENGTH); certified 1, not certified 4, NOT EVALUABLE 0 (C0 0, "
               "degenerate / infeasible 0) of 5 (gate first); median declared 0.285000 vs median null p95 0.284000")
        has(L, "KK1 (n 486): K2-SIZE-LIMIT")
        has(L, SENT_FKK_FIRED)
        assert not any(l.startswith("READING") or l.startswith("F-KK: NOT FIRED") for l in L), L
        has(L, "P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome K2-SIZE-LIMIT, Brier "
               "(4-way sum) 1.0750")
        # boundaries at the pair level: 4 / 3 / 2 / 1 certified (k 14 certifies, k 15 does not)
        for i, (ks, v, word) in enumerate((([14, 14, 14, 14, 15], "CERTIFIED-AT-SIZE", "K2-SENSITIVE"),
                                           ([14, 14, 14, 15, 15], "MIXED", "MIXED"),
                                           ([14, 14, 15, 15, 15], "MIXED", "MIXED"),
                                           ([14, 15, 15, 15, 15], "NOT-CERTIFIED-AT-SIZE", "K2-SIZE-LIMIT"))):
            r, L, _o = run(sub(tmp, 1 + i), spec=_ks("STRONG", 486, ks))
            assert r["size_words"][486]["STRONG"] == v and r["kk"][486] == word, (ks, r["size_words"][486], r["kk"])
        has(L, "  KK_STRONG_n486_d1    n  486 (law/math 203/283): declared 0.286000; null min 0.000000 / p95 0.284000 / max "
               "0.299000; k_d  14 of 300, p_d 15/301 = 0.049834; C0 p95 0.000284 (comparable); reached 299 -> CERTIFIED")
        has(L, "  KK_STRONG_n486_d2    n  486 (law/math 203/283): declared 0.285000; null min 0.000000 / p95 0.284000 / max "
               "0.299000; k_d  15 of 300, p_d 16/301 = 0.053156; C0 p95 0.000284 (comparable); reached 299 -> NOT CERTIFIED")
        # MIXED: STRONG MIXED, MID certified -> KK MIXED; READING none
        r, L, _o = run(sub(tmp, 6), spec=_ks("STRONG", 486, [14, 14, 14, 15, 15]))
        has(L, "KK1 (n 486): MIXED")
        has(L, "F-KK: NOT FIRED (KK1 MIXED). F-TAX N-1 and F2 stand.")
        has(L, "READING: none (KK1 MIXED: a registered MIXED; no sentence)")
        # KK2 from n 441 only, KK1 from n 486 only
        sp2 = _ks("STRONG", 441, [100] * 5)
        r, L, _o = run(sub(tmp, 7), spec=sp2)
        assert r["kk"] == {486: "K2-SENSITIVE", 441: "K2-SIZE-LIMIT"} and r["fired"] is False, r["kk"]
        has(L, "KK2 (n 441): K2-SIZE-LIMIT")
        # every gated pair's verdict is read, not the first only: the LAST role failing
        r, L, _o = run(sub(tmp, 8), spec=_ks("EDGE", 486, [100] * 5), ruling="EDGE-IN-IF-GATED")
        assert r["kk"][486] == "K2-SIZE-LIMIT" and r["fired"] is True, r["kk"]

    def gate_gks(tmp):
        # full site k 15 -> NOT certified -> NOT-A-CONTROL; MID out -> reading A NO-CONTROL, reading B evaluates (STRONG, EDGE)
        r, L, _o = run(sub(tmp, 0), spec={"MID_full": dict(k=15)}, ruling=None)
        assert r["gate"]["MID"] == "NOT-A-CONTROL" and r["kk"][486] == "WITHHELD" and r["fired"] is False, (r["gate"], r["kk"])
        has(L, "KK1 (n 486) reading A (EDGE descriptive-only; 1 gated of STRONG / MID): NO-CONTROL; reading B (EDGE in when gated; "
               "2 gated of 3): K2-SENSITIVE")
        has(L, "KK1 (n 486): WITHHELD (readings A and B differ; registration query Q-KK1 unruled: no deciding word)")
        has(L, "READING: none (KK1 WITHHELD: Q-KK1 unruled (KK-7); no sentence)")
        has(L, "P3 KK1 readings: NOT SCORED (KK1 WITHHELD)")
        has(L, "P2 MID KNOWN-STRENGTH (p 0.80): event no, Brier 0.6400")
        # full k 14 certifies (p 15/301 <= 0.05)
        r, L, _o = run(sub(tmp, 1), spec={"MID_full": dict(k=14)})
        assert r["gate"]["MID"] == "KNOWN-STRENGTH", r["gate"]
        # full C0 fails -> NOT-A-CONTROL; full DEGENERATE -> NOT-A-CONTROL
        r, L, _o = run(sub(tmp, 2), spec={"STRONG_full": dict(c0="equal")})
        assert r["gate"]["STRONG"] == "NOT-A-CONTROL", r["gate"]
        has(L, "P5 C0 comparable on every site (p 0.85): event no (32 of 33 comparable), Brier 0.7225")
        r, L, _o = run(sub(tmp, 3), spec={"STRONG_full": dict(reached=19)})
        assert r["gate"]["STRONG"] == "NOT-A-CONTROL", r["gate"]
        # margin vs SD: MID margin 0.005749; subsample d spread with sample SD > margin -> NOT-A-CONTROL
        spread = {"KK_MID_n486_d%d" % (i + 1): dict(k=0, d=v) for i, v in enumerate([0.29, 0.30, 0.31, 0.30, 0.30])}
        r, L, _o = run(sub(tmp, 4), spec=spread)            # sample SD 0.0070711 > 0.005749
        assert r["gate"]["MID"] == "NOT-A-CONTROL", r["gate"]
        assert any(l.startswith("G-KS MID (chemistry + physics): NOT-A-CONTROL;") and "vs SD over the five n-486 subsamples "
                   "0.007071 (sample, n - 1; KK-5); population SD 0.006325 -> the gate word is unchanged" in l for l in L), L
        spread2 = {"KK_MID_n486_d%d" % (i + 1): dict(k=0, d=v) for i, v in enumerate([0.296, 0.30, 0.304, 0.30, 0.30])}
        r, L, _o = run(sub(tmp, 5), spec=spread2)           # sample SD 0.0028284 < 0.005749
        assert r["gate"]["MID"] == "KNOWN-STRENGTH", r["gate"]
        # sample vs population SD straddling the margin: the KK-5 flag line
        spread4 = {"KK_MID_n486_d%d" % (i + 1): dict(k=0, d=v) for i, v in enumerate([0.2914, 0.30, 0.3086, 0.30, 0.30])}
        r, L, _o = run(sub(tmp, 7), spec=spread4)           # sample SD 0.006081 > margin 0.005749 > population SD 0.005439
        assert r["gate"]["MID"] == "NOT-A-CONTROL" and any("the gate word WOULD CHANGE to KNOWN-STRENGTH (Q-KK2)" in l for l in L), L
        # equality: gks uses a strict '>'
        assert gks("CERTIFIED", 0.01, 0.01) == "NOT-A-CONTROL" and gks("CERTIFIED", 0.0100001, 0.01) == "KNOWN-STRENGTH"
        assert gks("NOT CERTIFIED", 1.0, 0.0) == "NOT-A-CONTROL" and gks("NOT EVALUABLE (C0)", 1.0, 0.0) == "NOT-A-CONTROL"
        assert abs(sd_sample([1, 2, 3, 4, 5]) - math.sqrt(2.5)) < 1e-15 and abs(sd_pop([1, 2, 3, 4, 5]) - math.sqrt(2.0)) < 1e-15
        # NO-CONTROL under both readings: STRONG and MID out, EDGE gated -> A 0, B 1 -> NO-CONTROL; sentence; P3 scored
        r, L, _o = run(sub(tmp, 8), spec={"STRONG_full": dict(k=100), "MID_full": dict(k=100)})
        assert r["kk"] == {486: "NO-CONTROL", 441: "NO-CONTROL"} and r["fired"] is False, r["kk"]
        has(L, "KK1 (n 486): NO-CONTROL")
        has(L, SENT_NO_CONTROL)
        has(L, "P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome NO-CONTROL, Brier "
               "(4-way sum) 0.9750")
        # a NOT-A-CONTROL pair that fails at size does not decide: MID out and NOT-CERTIFIED at 486 -> reading B over STRONG, EDGE
        sp9 = {"MID_full": dict(k=100)}
        sp9.update(_ks("MID", 486, [100] * 5))
        r, L, _o = run(sub(tmp, 9), spec=sp9, ruling="EDGE-IN-IF-GATED")
        assert r["kk"][486] == "K2-SENSITIVE", r["kk"]

    def q_kk1(tmp):
        # EDGE gated and NOT-CERTIFIED at 486, STRONG / MID certified: A K2-SENSITIVE, B K2-SIZE-LIMIT
        sp_ = _ks("EDGE", 486, [100] * 5)
        r, L, _o = run(sub(tmp, 0), spec=sp_, ruling=None)
        assert r["kk"][486] == "WITHHELD" and r["fired"] is False, r["kk"]
        has(L, "KK1 (n 486) reading A (EDGE descriptive-only; 2 gated of STRONG / MID): K2-SENSITIVE; reading B (EDGE in when gated; "
               "3 gated of 3): K2-SIZE-LIMIT")
        r, L, _o = run(sub(tmp, 1), spec=sp_, ruling="EDGE-DESCRIPTIVE")
        assert r["kk"][486] == "K2-SENSITIVE" and r["fired"] is False, r["kk"]
        has(L, "builder's readings KK-0..KK-8 (docstring); registration query Q-KK1 (KK-7: EDGE in KK1 when gated?) ruling: "
               "EDGE-DESCRIPTIVE (registrar 65e5c0d7, programme L24046 / L24048 / L24050: KK1 / KK2 / F-KK count STRONG and MID only; "
               "reading A decides, reading B descriptive)")
        r, L, _o = run(sub(tmp, 2), spec=sp_, ruling="EDGE-IN-IF-GATED")
        assert r["kk"][486] == "K2-SIZE-LIMIT" and r["fired"] is True, r["kk"]
        has(L, SENT_FKK_FIRED)
        # EDGE not gated: A and B agree whatever EDGE does at size
        sp2 = dict(sp_)
        sp2["EDGE_full"] = dict(k=100)
        r, L, _o = run(sub(tmp, 3), spec=sp2, ruling=None)
        assert r["kk"][486] == "K2-SENSITIVE" and r["gate"]["EDGE"] == "NOT-A-CONTROL", (r["kk"], r["gate"])
        try:
            kk_readings({r_: "KNOWN-STRENGTH" for r_ in ROLES}, {r_: "CERTIFIED-AT-SIZE" for r_ in ROLES}, "EDGE")
            raise AssertionError("a bad ruling accepted")
        except SystemExit as e:
            assert "Q_KK1_RULING 'EDGE'" in str(e), e

    def q_kk1_ruled_default(tmp):
        # the module default is the registrar's ruling (65e5c0d7): never WITHHELD
        assert Q_KK1_RULING == "EDGE-DESCRIPTIVE", Q_KK1_RULING
        # (a) EDGE passes G-KS, then fails at n 486; STRONG / MID certified -> KK1 K2-SENSITIVE (A), F-KK NOT FIRED, P3 scored
        r, L, _o = run(sub(tmp, 0), spec=_ks("EDGE", 486, [100] * 5))
        assert r["gate"]["EDGE"] == "KNOWN-STRENGTH" and r["size_words"][486]["EDGE"] == "NOT-CERTIFIED-AT-SIZE", (r["gate"], r["size_words"])
        assert r["kk"] == {486: "K2-SENSITIVE", 441: "K2-SENSITIVE"} and r["fired"] is False, r["kk"]
        has(L, "KK1 (n 486) reading A (EDGE descriptive-only; 2 gated of STRONG / MID): K2-SENSITIVE; reading B (EDGE in when gated; "
               "3 gated of 3): K2-SIZE-LIMIT")
        has(L, "KK1 (n 486): K2-SENSITIVE")
        has(L, "F-KK: NOT FIRED (KK1 K2-SENSITIVE). F-TAX N-1 and F2 stand.")
        has(L, SENT_SENSITIVE)
        has(L, "P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome K2-SENSITIVE, Brier "
               "(4-way sum) 0.2750")
        has(L, "DESCRIPTIVE: EDGE (biology + math) G-KS KNOWN-STRENGTH, n 486 NOT-CERTIFIED-AT-SIZE, n 441 CERTIFIED-AT-SIZE "
               "(reported whether gated or not)")
        assert not any("WITHHELD" in l for l in L), [l for l in L if "WITHHELD" in l]
        # (b) the converse: MID NOT-A-CONTROL with EDGE gated and certified -> KK1 NO-CONTROL (A), never rescued by EDGE
        r, L, _o = run(sub(tmp, 1), spec={"MID_full": dict(k=15)})
        assert r["gate"]["MID"] == "NOT-A-CONTROL" and r["gate"]["EDGE"] == "KNOWN-STRENGTH", r["gate"]
        assert r["kk"] == {486: "NO-CONTROL", 441: "NO-CONTROL"} and r["fired"] is False, r["kk"]
        has(L, "KK1 (n 486) reading A (EDGE descriptive-only; 1 gated of STRONG / MID): NO-CONTROL; reading B (EDGE in when gated; "
               "2 gated of 3): K2-SENSITIVE")
        has(L, "KK1 (n 486): NO-CONTROL")
        has(L, SENT_NO_CONTROL)
        has(L, "P3 KK1 readings (K2-SENSITIVE 0.55, MIXED 0.10, K2-SIZE-LIMIT 0.15, NO-CONTROL 0.20): outcome NO-CONTROL, Brier "
               "(4-way sum) 0.9750")
        assert not any("WITHHELD" in l for l in L), [l for l in L if "WITHHELD" in l]
        # (c) EDGE certified cannot rescue a failing STRONG: STRONG NOT-CERTIFIED at 486 -> K2-SIZE-LIMIT, F-KK fires
        r, L, _o = run(sub(tmp, 2), spec=_ks("STRONG", 486, [100] * 5))
        assert r["kk"][486] == "K2-SIZE-LIMIT" and r["fired"] is True, r["kk"]
        has(L, SENT_FKK_FIRED)

    def not_evaluable(tmp):
        ne = dict(c0="equal")
        # MID NOT EVALUABLE at 486 (2 C0), STRONG certified: A -> NE could change the word -> NOT EVALUABLE
        sp_ = {k: v for k, v in _ks("MID", 486, [0] * 5).items()}
        sp_["KK_MID_n486_d4"].update(ne)
        sp_["KK_MID_n486_d5"].update(ne)
        r, L, _o = run(sub(tmp, 0), spec=sp_, ruling="EDGE-DESCRIPTIVE")
        assert r["size_words"][486]["MID"] == "NOT EVALUABLE" and r["kk"][486] == "NOT EVALUABLE" and r["fired"] is False, r["kk"]
        has(L, "PAIR MID n 486: NOT EVALUABLE (KNOWN-STRENGTH); certified 3, not certified 0, NOT EVALUABLE 2 (C0 2, degenerate / "
               "infeasible 0) of 5 (gate first); median declared 0.300000 vs median null p95 0.284000")
        has(L, "READING: none (KK1 NOT EVALUABLE: not evaluable (KK-6); no sentence)")
        has(L, "P3 KK1 readings: NOT SCORED (KK1 NOT EVALUABLE)")
        has(L, "P5 C0 comparable on every site (p 0.85): event no (31 of 33 comparable), Brier 0.7225")
        # MID NOT EVALUABLE, STRONG NOT-CERTIFIED: K2-SIZE-LIMIT whatever MID would read -> the word stands, F-KK fires
        sp2 = dict(sp_)
        sp2.update(_ks("STRONG", 486, [100] * 5))
        r, L, _o = run(sub(tmp, 1), spec=sp2, ruling="EDGE-DESCRIPTIVE")
        assert r["kk"][486] == "K2-SIZE-LIMIT" and r["fired"] is True, r["kk"]
        # one C0 failure of 5 leaves the pair evaluable (4 certified -> CERTIFIED-AT-SIZE)
        sp3 = _ks("MID", 486, [0] * 5)
        sp3["KK_MID_n486_d5"].update(ne)
        r, L, _o = run(sub(tmp, 2), spec=sp3)
        assert r["size_words"][486]["MID"] == "CERTIFIED-AT-SIZE" and r["kk"][486] == "K2-SENSITIVE", r["size_words"][486]
        # DEGENERATE 19 / 20
        sp4 = _ks("STRONG", 441, [0] * 5)
        sp4["KK_STRONG_n441_d1"]["reached"] = 19
        r, L, _o = run(sub(tmp, 3), spec=sp4)
        assert r["res"]["KK_STRONG_n441_d1"]["status"] == "NOT EVALUABLE (DEGENERATE)", r["res"]["KK_STRONG_n441_d1"]
        sp4["KK_STRONG_n441_d1"]["reached"] = 20
        r, L, _o = run(sub(tmp, 4), spec=sp4)
        assert r["res"]["KK_STRONG_n441_d1"]["status"] == "CERTIFIED", r["res"]["KK_STRONG_n441_d1"]
        # C0 one step below the null p95 is comparable
        r, L, _o = run(sub(tmp, 5), spec=_ks("MID", 441, [0] * 5, c0="below"))
        assert all(r["res"]["KK_MID_n441_d%d" % i]["comparable"] for i in DRAWS)
        assert [kk_word(w) for w in (["CERTIFIED-AT-SIZE"], [], ["NOT EVALUABLE", "NOT EVALUABLE"],
                                     ["CERTIFIED-AT-SIZE", "MIXED", "NOT EVALUABLE"],
                                     ["NOT-CERTIFIED-AT-SIZE", "NOT EVALUABLE", "NOT EVALUABLE"],
                                     ["CERTIFIED-AT-SIZE", "MIXED"], ["CERTIFIED-AT-SIZE", "CERTIFIED-AT-SIZE", "CERTIFIED-AT-SIZE"])] == \
            ["NO-CONTROL", "NO-CONTROL", "NOT EVALUABLE", "NOT EVALUABLE", "K2-SIZE-LIMIT", "MIXED", "K2-SENSITIVE"]

    def predictions(tmp):
        # P1 boundaries (closed intervals, decimal-exact): STRONG 0.12 held, 0.1199 failed; MID 0.1178 held, 0.1179 failed; EDGE 0.060
        assert in_closed(0.12, *P1_STRONG) and not in_closed(0.1199, *P1_STRONG) and in_closed(0.35, *P1_STRONG) and \
            not in_closed(0.3501, *P1_STRONG)
        lo, hi = Fraction("0.1078") - P1_HALF, Fraction("0.1078") + P1_HALF
        assert in_closed(0.1178, lo, hi) and not in_closed(0.1179, lo, hi) and in_closed(0.0978, lo, hi) and not in_closed(0.0977, lo, hi)
        r, L, _o = run(sub(tmp, 0), chosen={"STRONG": 0.36, "MID": 0.1179, "EDGE": 0.060})
        has(L, "P1 STRONG stage-0 statistic 0.360000 in [0.12, 0.35]: FAILED")
        has(L, "P1 MID stage-0 statistic 0.117900 in 0.1078 +/- 0.010: FAILED")
        has(L, "P1 EDGE stage-0 statistic 0.060000 in 0.070 +/- 0.010: HELD")
        # P4: median of the 15 n-486 null p95 values; FAILED in the default fixture (0.284), HELD when the subsample d's give 0.060
        sp_ = {}
        for role in ROLES:
            sp_.update({"KK_%s_n486_d%d" % (role, i + 1): dict(k=0, d=v) for i, v in
                        enumerate([0.0633803, 0.0633803, 0.0633803, 0.0633803, 0.0633803])})
        r, L, _o = run(sub(tmp, 1), spec=sp_)
        assert any(l.startswith("P4 merged-site null p95 at n 486, median over the 15 subsamples of the 3 chosen pairs: 0.060000 "
                                "in [0.045, 0.075]: HELD") for l in L), [l for l in L if l.startswith("P4")]
        # P4 median, not min / max: 7 low, 8 high -> the 8th value
        sp2 = {}
        vals = [0.04] * 7 + [0.0633803] * 1 + [0.09] * 7
        i = 0
        for role in ROLES:
            for dd in DRAWS:
                sp2["KK_%s_n486_d%d" % (role, dd)] = dict(k=0, d=vals[i])
                i += 1
        r, L, _o = run(sub(tmp, 2), spec=sp2)
        assert any(l.startswith("P4 merged-site null p95 at n 486, median over the 15 subsamples of the 3 chosen pairs: 0.060000")
                   for l in L), [l for l in L if l.startswith("P4")]

    def identity(tmp):
        refused(sub(tmp, 0), "IDENTITY FAILED: declared 0.107804 k_d 0", ident_d=0.1078041)
        refused(sub(tmp, 1), "IDENTITY FAILED: declared 0.107803 k_d 1", ident_k=1)
        refused(sub(tmp, 2), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6993 seed PS_x", ident_seed="PS_x")
        refused(sub(tmp, 3), "IDENTITY FAILED: declared 0.107803 k_d 0 n 6992 seed n00000001", ident_n=6992)
        refused(sub(tmp, 4), "p95 0.041627 max 0.042414", ident_p95=0.041627)
        refused(sub(tmp, 5), "p95 0.041626 max 0.042415", ident_max=0.042415)

    def refusals(tmp):
        for i, (needle, kw) in enumerate([
                ("the arm's status is 'REFUSED: x'", dict(status="REFUSED: x")),
                ("a partial file", dict(partial=True)),
                ("embeddings_cache.db changed during the arm", dict(hashes_equal=False)),
                ("the arm read site file sha256", dict(site_sha_bad=True)),
                ("instrument: the arm ran sepBar='0.025'", dict(sepbar="0.025")),
                ("instrument: the arm ran arm='certPcK2'", dict(arm="certPcK2")),
                ("the arm read snapshot 'OTHER'", dict(snapshot="OTHER")),
                ("sites.csv holds", dict(drop_site="KK_MID_n441_d3")),
                ("sites.csv: KK_EDGE_n441_d2 n 442", dict(n_bad="KK_EDGE_n441_d2")),
                ("sites.csv: KK_MID_n486_d4 n 486 groups 2 sizes 1/485", dict(gs_lie="KK_MID_n486_d4")),
                ("KK_MID_n486_d3: k_d recount 0 != the arm's 1", dict(k_lie="KK_MID_n486_d3")),
                ("KK_STRONG_n441_d5: C0 p95 recount", dict(c0_lie="KK_STRONG_n441_d5")),
                ("replicates: KK_EDGE_n486_d2's C0 arm is missing", dict(drop_reps_arm=("KK_EDGE_n486_d2", "C0"))),
                ("MID: the arm's full-site statistic", dict(full_shift=2e-9))]):
            refused(sub(tmp, i), needle, **kw)
        # full shift below the tolerance passes
        r, L, _o = run(sub(tmp, 15), full_shift=5e-10)
        assert r["kk"][486] == "K2-SENSITIVE", r["kk"]
        # the pins: site file, stage-0 file, labels, selection; the rebuild (pin overridden) and the stage-0 roles
        refused(sub(tmp, 20), "is not SITES_SHA256", tamper_site="KK_MID_n486_d3")
        refused(sub(tmp, 21), "the site file is not the one the CPC labels", tamper_site="KK_MID_n486_d3",
                pins_override=lambda p: (p[0], p[1], sha256_bytes(open(os.path.join(tmp, "s21", "out", SITES_NAME), "rb").read()), p[3]))
        refused(sub(tmp, 22), "not CERT-POSITIVE-CONTROL's label file of record", pins_override=lambda p: ("0" * 64, p[1], p[2], p[3]))
        refused(sub(tmp, 23), "is not STAGE0_SHA256", pins_override=lambda p: (p[0], "0" * 64, p[2], p[3]))
        refused(sub(tmp, 24), "the rule re-derives", pins_override=lambda p: (p[0], p[1], p[2], dict(p[3], MID="biology + physics")))
        refused(sub(tmp, 26), "the stage-0 file does not list exactly the 49 eligible pairs", stage0_drop_first=True,
                pins_override=lambda p: (p[0], sha256_bytes(open(os.path.join(tmp, "s26", "out", STAGE0_NAME), "rb").read()), p[2], p[3]))
        refused(sub(tmp, 25), "the rule re-derives", stage0_role_lie=True,
                pins_override=lambda p: (p[0], sha256_bytes(open(os.path.join(tmp, "s25", "out", STAGE0_NAME), "rb").read()), p[2], p[3]))

    def rule(tmp):
        cat, src = _labels_fixture()
        pops = populations(cat, src)
        el = eligible_pairs(pops)
        assert len(el) == 49 and el[0] == ("biology", "chemistry") and ("computer science", "math") in el and \
            ("history", "philosophy") not in el, (len(el), el[:3])
        # eligibility boundaries: 972 in, 971 out; each >= 100
        fake = {"a": list(range(486)), "b": list(range(486)), "c": list(range(485)), "d": list(range(900)), "e": list(range(99))}
        fe = eligible_pairs(fake)
        assert ("a", "b") in fe and ("a", "c") not in fe and ("b", "c") not in fe and ("d", "e") not in fe and ("c", "d") in fe, fe
        fake2 = {"x": list(range(100)), "y": list(range(872))}
        assert eligible_pairs(fake2) == [("x", "y")]
        R_ = lambda nm, s: dict(pair=nm, a=nm.split(" + ")[0], b=nm.split(" + ")[1], na=1, nb=1, stat=s)
        # STRONG = max; MID nearest 0.1078 other than STRONG; EDGE nearest 0.070 other than both
        rows = [R_("a + b", 0.20), R_("a + c", 0.11), R_("a + d", 0.105), R_("b + c", 0.071), R_("b + d", 0.0685), R_("c + d", 0.01)]
        sel, mar = select(rows)
        assert {r: sel[r]["pair"] for r in ROLES} == {"STRONG": "a + b", "MID": "a + c", "EDGE": "b + c"}, sel
        assert abs(mar["MID"] - 0.0006) < 1e-12 and abs(mar["STRONG"] - 0.09) < 1e-12 and abs(mar["EDGE"] - 0.0005) < 1e-12, mar
        # STRONG would be nearest 0.1078 too -> MID is the next; MID nearest 0.070 too -> EDGE is the next
        rows2 = [R_("a + b", 0.1078), R_("a + c", 0.1000), R_("a + d", 0.0701), R_("b + c", 0.0500), R_("b + d", 0.0300)]
        sel2, _m = select(rows2)
        assert {r: sel2[r]["pair"] for r in ROLES} == {"STRONG": "a + b", "MID": "a + c", "EDGE": "a + d"}, sel2
        rows3 = [R_("a + b", 0.30), R_("a + c", 0.0701), R_("a + d", 0.0699), R_("b + c", 0.01)]
        sel3, _m = select(rows3)                       # MID = a + c (|0.0377| < |0.0379|); EDGE = a + d
        assert {r: sel3[r]["pair"] for r in ROLES} == {"STRONG": "a + b", "MID": "a + c", "EDGE": "a + d"}, sel3
        # ties -> the lexicographically smaller name; a tie refuses (KK-2) because the margin is 0
        try:
            select([R_("a + b", 0.3), R_("a + c", 0.3), R_("a + d", 0.1), R_("b + c", 0.07)])
            raise AssertionError("a tie accepted")
        except SystemExit as e:
            assert "STRONG: the margin to the runner-up is 0" in str(e), e
        best, m = _nearest([R_("b + c", 0.3), R_("a + c", 0.3)], lambda r: -r["stat"])
        assert best["pair"] == "a + c" and m == 0.0
        try:
            select([R_("a + b", 0.3), R_("a + c", 0.1)])
            raise AssertionError("2 pairs accepted")
        except SystemExit as e:
            assert "2 eligible pairs" in str(e), e
        # stage-0 bytes: round trip; roles written; repr precision kept
        rr = _stage0_rows(pops)
        s, _m = select(rr)
        b = stage0_bytes(rr, s)
        back, roles = parse_stage0(b)
        assert [x["stat"] for x in back] == [x["stat"] for x in rr] and roles == {r: s[r]["pair"] for r in ROLES}, roles
        assert b.startswith((STAGE0_HEADER + "\nbiology + chemistry\tbiology\tchemistry\t381\t676\t1057\t0.03\t\n").encode()), b[:120]

    def routine(tmp):
        # the statistic: hand values
        e1, e2 = np.eye(4)[0], np.eye(4)[1]
        g1, g2 = np.array([e1, e1, e1]), np.array([e2, e2])
        assert declared_stat([g1, g2]) == 1.0, declared_stat([g1, g2])          # perfect partition
        assert declared_stat([np.vstack([g1, g2])]) == 0.0                      # k = 1
        assert declared_stat([g1[:1]]) == 0.0 and declared_stat([]) == 0.0
        # W(S): n=5, ||sum||^2 = 9 + 4 = 13 -> W = 12; within: (9-9) + (4-4) = 0; anti: groups {e1,e2},{e1,e2},{e1}
        anti = declared_stat([np.array([e1, e2]), np.array([e1, e2]), np.array([e1])])
        # within = (4-2) + (4-2) + (1-1) = 4; pairFrac = 2+2+0 = 4; E = 12 x 4 / 20 = 2.4 -> 1 - 4/2.4 = -0.6667
        assert abs(anti - (1 - 4 / 2.4)) < 1e-15, anti
        # projectTo: the first SLICE floats, normalised; a 600-float row
        raw = np.zeros((1, 600), dtype=np.float32)
        raw[0, 0], raw[0, 1], raw[0, 599] = 3.0, 4.0, 100.0
        u = unit_rows(raw)
        assert u.shape == (1, SLICE) and abs(u[0, 0] - 0.6) < 1e-15 and abs(u[0, 1] - 0.8) < 1e-15
        # the fixture value the Kotlin test asserts (KK-0 (i))
        x = fixture_vectors()
        assert XFIX is not None and abs(x - XFIX) <= 1e-15, (x, XFIX)
        # load_vectors: big-endian float32 from a fixture cache (queries JOIN embeddings on the distilled text)
        db = os.path.join(tmp, "emb.db")
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE queries (id TEXT, distilled_text TEXT)")
        con.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
        con.execute("INSERT INTO queries VALUES ('q1','t1'),('q2','t2'),('q3','t3')")
        v1 = [3.0, 4.0] + [0.0] * 598
        con.execute("INSERT INTO embeddings VALUES ('t1', ?), ('t2', ?), ('t3', ?)",
                    (struct.pack(">600f", *v1), struct.pack(">512f", *([1.0] * 512)), struct.pack(">511f", *([1.0] * 511))))
        con.commit()
        con.close()
        vec = load_vectors(db, ["q1", "q2"])
        assert abs(vec["q1"][0] - 0.6) < 1e-15 and abs(vec["q1"][1] - 0.8) < 1e-15 and abs(vec["q2"][7] - 1 / math.sqrt(512)) < 1e-15
        for ids, needle in ((["q1", "q3"], "shorter than 512"), (["q1", "q9"], "embedding cache miss: 1 of 2")):
            try:
                load_vectors(db, ids)
                raise AssertionError("not refused: " + needle)
            except SystemExit as e:
                assert needle in str(e), e
        le = os.path.join(tmp, "le.db")                 # a little-endian blob reads as a different vector: the IDENTITY check guards
        con = sqlite3.connect(le)
        con.execute("CREATE TABLE queries (id TEXT, distilled_text TEXT)")
        con.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
        con.execute("INSERT INTO queries VALUES ('q1','t1')")
        con.execute("INSERT INTO embeddings VALUES ('t1', ?)", (struct.pack("<600f", *v1),))
        con.commit()
        con.close()
        assert abs(load_vectors(le, ["q1"])["q1"][0] - 0.6) > 0.1
        # check_routine: IDENTITY and the K2 sites against the arm values, both refusals
        cat = {"a%d" % i: ("c%d" % (i % 2)) for i in range(6)}
        rng = np.random.default_rng(0)
        vv = {q: unit_rows(rng.standard_normal((1, 600)).astype(np.float32))[0] for q in cat}
        d_id = site_stat(vv, cat)
        k2s = {"IDENTITY": cat}
        k2a = {}
        for j in range(30):
            nm = "K2_x_n4_d%d" % j
            k2s[nm] = {q: ("f%d" % ((i + j) % 2)) for i, q in enumerate(sorted(cat)[:4])}
            k2a[nm] = site_stat(vv, k2s[nm])
        global IDENTITY_FULL
        saved = IDENTITY_FULL
        try:
            IDENTITY_FULL = d_id + 5e-10
            lines = []
            check_routine(vv, cat, k2s, k2a, out=lines.append)
            assert lines[1].startswith("[PKK] ROUTINE CHECK CERT-PC-K2: 30 K2 sites, max |Python - arm| 0.00e+00"), lines
            IDENTITY_FULL = d_id + 2e-9
            try:
                check_routine(vv, cat, k2s, k2a, out=lambda s: None)
                raise AssertionError("IDENTITY off by 2e-9 accepted")
            except SystemExit as e:
                assert "not the instrument's" in str(e), e
            IDENTITY_FULL = d_id
            bad = dict(k2a)
            bad["K2_x_n4_d7"] += 2e-9
            for a_, needle in ((bad, "does not reproduce CERT-PC-K2's 30 K2 sites"), (None, "are required for the routine check")):
                try:
                    check_routine(vv, cat, k2s if a_ is not None else None, a_, out=lambda s: None)
                    raise AssertionError("not refused: " + needle)
                except SystemExit as e:
                    assert needle in str(e), e
            short = {k: v for k, v in list(k2s.items())[:30]}
            try:
                check_routine(vv, cat, short, k2a, out=lambda s: None)
                raise AssertionError("29 K2 sites accepted")
            except SystemExit as e:
                assert "does not reproduce CERT-PC-K2's 29 K2 sites" in str(e), e
        finally:
            IDENTITY_FULL = saved
        # stage0() on vectors: the merged pair's statistic = site_stat over its labels
        pops = {"c0": sorted(q for q in cat if cat[q] == "c0"), "c1": sorted(q for q in cat if cat[q] == "c1")}
        global MIN_COMBINED, MIN_EACH
        sv = (MIN_COMBINED, MIN_EACH)
        try:
            MIN_COMBINED, MIN_EACH = 6, 3
            rows = stage0(pops, vv)
            assert len(rows) == 1 and rows[0]["pair"] == "c0 + c1" and rows[0]["stat"] == site_stat(vv, cat), rows
        finally:
            MIN_COMBINED, MIN_EACH = sv

    def site_file(tmp):
        cat, src = _labels_fixture()
        assert len(cat) == N_ROOT and len(set(cat.values())) == 14
        data, sites, labels, pops = build_site_bytes(cat, src, FX_SEL)
        assert list(sites) == ["IDENTITY"] + site_names(SZ) and len(sites["IDENTITY"]) == N_ROOT
        assert {c: len(v) for c, v in pops.items()} == REG_COUNTS
        assert TWINS[0] not in set().union(*[set(sites[s]) for s in sites if s != "IDENTITY"]), "the pinned twin was drawn"
        nosrc = [q for q in cat if not src[q]]
        assert len(nosrc) == 4 and not (set(nosrc) & set(sites[full("STRONG")])), "a no-src id entered a full site"
        for role in ROLES:
            a, b = FX_SEL[role]
            f = sites[full(role)]
            assert f == sorted(pops[a] + pops[b]) and len(f) == SZ[role]
            for n in SIZES:
                for d in DRAWS:
                    s = "KK_%s_n%d_d%d" % (role, n, d)
                    assert len(sites[s]) == n and set(sites[s]) <= set(f) and set(labels[s].values()) == {a, b}, s
        cnt = lambda s, a: sum(1 for v in labels[s].values() if v == a)
        # allocation (PCS-1): law 578 / math 805 at n 486 -> 203.1 / 282.9 -> 203 / 283
        assert (cnt("KK_STRONG_n486_d1", "law"), cnt("KK_STRONG_n486_d1", "math")) == (203, 283)
        assert (cnt("KK_EDGE_n441_d1", "biology"), cnt("KK_EDGE_n441_d1", "math")) == (142, 299)
        pdata, psites = PCS.build_site_bytes(cat)
        assert psites["IDENTITY"] == sites["IDENTITY"] and pdata.split(b"\nPS_")[0] == data.split(b"\nKK_")[0]
        assert sites["KK_MID_n486_d1"] != sites["KK_MID_n486_d2"]
        d2, s2, _l2, _p2 = build_site_bytes(dict(cat), dict(src), dict(FX_SEL))
        assert d2 == data and s2 == sites, "the draw is not deterministic"
        assert sha256_bytes(data) == "%s" % SITE_FIXTURE_SHA, sha256_bytes(data)
        # the draw seed is the registered 1..5 (cert_pc_size.draw with seed d)
        assert sites["KK_MID_n441_d2"] == PCS.draw({"chemistry": pops["chemistry"], "physics": pops["physics"]}, 441, 2)
        try:
            populations(cat, src, twins=())
            raise AssertionError("the twin kept and accepted")
        except SystemExit as e:
            assert "math 806 (registered 805)" in str(e), e
        try:
            build_site_bytes({q: ("biology" if c == "business" else c) for q, c in cat.items()}, src, FX_SEL)
            raise AssertionError("13 categories accepted")
        except SystemExit as e:
            assert "13 declared categories, not 14" in str(e), e
        # twins over ALL src-carrying ids (not only three anchors), smallest id kept; no-src ids ignored
        text = {q: "text %s" % q for q in cat}
        law = sorted(q for q in cat if cat[q] == "law")
        text[law[1]] = text[law[0]]
        first_math = min(q for q in cat if cat[q] == "math" and src[q] and q not in TWINS)
        text[TWINS[0]] = text[first_math]
        text[nosrc[0]] = text[law[0]]
        assert find_twins(cat, src, text) == sorted([law[1], TWINS[0]]), find_twins(cat, src, text)
        assert find_twins(cat, src, {q: "text %s" % q for q in cat}) == []
        L = overlap_lines(sites, FX_SEL, pops)
        assert L[-1] == "OVERLAP: pairs sharing a category: STRONG / EDGE" and L[0].startswith(
            "OVERLAP STRONG (law + math, population 1383): 5 draws pairwise min / max: n 486 "), L

    def helpers(tmp):
        cfg = G.load_config(os.path.join(ROOT, PCS.CONFIG_REL))
        assert command(cfg, 6) == (
            '.\\gradlew.bat certKnownPair --console=plain --offline --no-daemon -PjvmThreads=12 -PnullReps=300 '
            '"-DsnapshotId=20261001_094311_Headless_Run_Auto_ge" "-DsliceDim=512" "-DsepBar=0.0145" "-DdropTop=0" "-Dwhiten=false" '
            '"-DsiteLabels=experiment_results/cert_pc_k2_known/site_labels.tsv" "-DoutDir=experiment_results/cert_pc_k2_known/arm"'), \
            command(cfg, 6)
        assert command(cfg, 8).endswith(' "-DsiteNullHeap=8g"')
        assert median([5, 1, 4, 2, 3]) == 3 and median(list(range(15))) == 7
        for fn_, arg in ((prepare, (tmp, "x")), (hashes, ("before", tmp))):
            try:
                fn_(*arg)
                raise AssertionError("%s from another data root not refused" % fn_.__name__)
            except SystemExit as e:
                assert tmp in str(e), e
        assert pin_word("a", "a") == "= the pin" and pin_word("a", None) == "NO PIN YET" and pin_word("a", "b") == "NOT the pin b"

    def main_analyze(tmp):
        global OUT_REL
        arm, outd, sp, s0p, lp, pins, _s = _fx(tmp, spec=_ks("STRONG", 486, [14, 15, 15, 15, 15]))
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
        assert "\nKK1 (n 486): K2-SIZE-LIMIT\n" in txt and "\n" + SENT_FKK_FIRED + "\n" in txt and "\nKK2 (n 441): K2-SENSITIVE\n" in txt, txt[-900:]

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
                   ("all gated and certified: every printed line, write-once", all_sensitive),
                   ("K2-SIZE-LIMIT / MIXED / pair boundaries 4-1 of 5; KK2 441 only; last role read", size_limit),
                   ("G-KS: full k 14 / 15, C0, DEGENERATE, margin vs SD (strict, sample vs population), NO-CONTROL", gate_gks),
                   ("Q-KK1: readings A / B, WITHHELD, both rulings, EDGE not gated", q_kk1),
                   ("Q-KK1 ruled (65e5c0d7) as the default: EDGE gated-then-fails, MID out with EDGE gated, never WITHHELD",
                    q_kk1_ruled_default),
                   ("NOT EVALUABLE pairs (KK-6), C0 1 / 2, DEGENERATE 19 / 20", not_evaluable),
                   ("P1 bands (closed, exact), P4 median", predictions),
                   ("IDENTITY refusals (incl. PC1 p95 / max)", identity),
                   ("refusals (pins, rebuild, stage-0 roles, KK-0 (iii) tolerance)", refusals),
                   ("the pair rule: eligibility 972 / 100, STRONG / MID / EDGE, exclusions, ties, stage-0 file", rule),
                   ("the routine: hand values, projectTo, XFIX, big-endian load, refusals, check_routine, stage0()", routine),
                   ("labels, populations, twins, allocation, site file", site_file), ("helpers", helpers)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


SITE_FIXTURE_SHA = "e2c579da3ab93c529f420d826d6307c6ed31a8a2f52b7c6d8d19c35c98bc94a3"

MUTANTS = [
    ("M0 control (no-op; must SURVIVE)", "TAG = \"[PKK]\"", "TAG = \"[PKK]\""),
    ("M1 k_d counts > (not >=)", "        k = CPC.kcount(R[(s, \"SN\")], d)", "        k = sum(1 for x in R[(s, \"SN\")] if x > d)"),
    ("M2 G-KS: a NOT CERTIFIED full site passes", "    return \"KNOWN-STRENGTH\" if (full_status == \"CERTIFIED\"",
     "    return \"KNOWN-STRENGTH\" if (full_status in (\"CERTIFIED\", \"NOT CERTIFIED\")"),
    ("M3 size verdict with the K2 anchor words", "            size_words[n][role] = PCS.size_verdict(sts)", "            size_words[n][role] = PK2.anchor_verdict(sts)"),
    ("M4 G-KS margin >= (not >)", "and bool(margin > sd))", "and bool(margin >= sd))"),
    ("M5 G-KS ignores the full-site certification", "(full_status == \"CERTIFIED\" and bool(margin > sd))", "(bool(margin > sd))"),
    ("M6 G-KS with the population SD", "        gate[role] = gks(f[\"status\"], margin, sd1)", "        gate[role] = gks(f[\"status\"], margin, sd0)"),
    ("M7 G-KS SD over the n-441 subsamples", "        d486 = [res[\"KK_%s_n486_d%d\" % (role, dd)][\"d\"] for dd in DRAWS]",
     "        d486 = [res[\"KK_%s_n441_d%d\" % (role, dd)][\"d\"] for dd in DRAWS]"),
    ("M8 G-KS margin without the null p95", "        margin = f[\"d\"] - f[\"np95\"]", "        margin = f[\"d\"]"),
    ("M9 G-KS full site read from the first subsample", "        f = res[\"KK_%s_n%d_d0\" % (role, sizes[role])]\n        d486",
     "        f = res[\"KK_%s_n486_d1\" % role]\n        d486"),
    ("M10 KK SENSITIVE on any certified", "    if all(w == \"CERTIFIED-AT-SIZE\" for w in words):", "    if any(w == \"CERTIFIED-AT-SIZE\" for w in words):"),
    ("M11 KK SIZE-LIMIT only if all fail", "    if any(w == \"NOT-CERTIFIED-AT-SIZE\" for w in words):", "    if all(w == \"NOT-CERTIFIED-AT-SIZE\" for w in words):"),
    ("M12 NO-CONTROL iff < 1", "    if len(words) < 2:\n        return \"NO-CONTROL\"", "    if len(words) < 1:\n        return \"NO-CONTROL\""),
    ("M13 NO-CONTROL iff < 3", "    if len(words) < 2:\n        return \"NO-CONTROL\"", "    if len(words) < 3:\n        return \"NO-CONTROL\""),
    ("M14 KK-6 ignores NOT EVALUABLE pairs", "    ne = [i for i, w in enumerate(words) if w == \"NOT EVALUABLE\"]", "    ne = []"),
    ("M15 KK-6 NOT EVALUABLE on any NE pair", "    return outs.pop() if len(outs) == 1 else \"NOT EVALUABLE\"",
     "    return outs.pop() if not ne else \"NOT EVALUABLE\""),
    ("M16 reading A includes EDGE", "    a, b = over((\"STRONG\", \"MID\")), over(ROLES)", "    a, b = over(ROLES), over(ROLES)"),
    ("M17 unruled: reading B decides", "    return a, b, (a if a == b else \"WITHHELD\")", "    return a, b, b"),
    ("M18 ruling EDGE-DESCRIPTIVE returns B", "    if ruling == \"EDGE-DESCRIPTIVE\":\n        return a, b, a", "    if ruling == \"EDGE-DESCRIPTIVE\":\n        return a, b, b"),
    ("M19 bad ruling accepted", "    if ruling is not None:\n        refuse(", "    if False:\n        refuse("),
    ("M20 ungated pairs decide", "        return kk_word([size_words[r] for r in roles if gate[r] == \"KNOWN-STRENGTH\"])",
     "        return kk_word([size_words[r] for r in roles])"),
    ("M21 KK1 from the n-441 verdict", "    kk1 = kk[486]", "    kk1 = kk[441]"),
    ("M22 pair verdicts from the first draw only", "            sts = [res[\"KK_%s_n%d_d%d\" % (role, n, dd)][\"status\"] for dd in DRAWS]",
     "            sts = [res[\"KK_%s_n%d_d%d\" % (role, n, 1)][\"status\"] for dd in DRAWS]"),
    ("M23 F-KK on MIXED too", "    if kk1 == \"K2-SIZE-LIMIT\":\n        say(SENT_FKK_FIRED)", "    if kk1 in (\"K2-SIZE-LIMIT\", \"MIXED\"):\n        say(SENT_FKK_FIRED)"),
    ("M24 SENSITIVE sentence on any not-fired", "        if kk1 == \"K2-SENSITIVE\":\n            say(SENT_SENSITIVE)", "        if kk1 != \"NO-CONTROL\":\n            say(SENT_SENSITIVE)"),
    ("M25 P3 scored when withheld", "    if kk1 in P3_PROBS:", "    if True:"),
    ("M26 P2 event on NOT-A-CONTROL", "        e = bool(gate[role] == \"KNOWN-STRENGTH\")", "        e = True"),
    ("M27 P1 bands half-open", "    return bool(lo <= v <= hi)", "    return bool(lo < v <= hi)"),
    ("M28 P1 half-width 0.011", "P1_HALF = Fraction(\"0.010\")", "P1_HALF = Fraction(\"0.011\")"),
    ("M29 P4 min (not median)", "    p4 = median(p4v)", "    p4 = min(p4v)"),
    ("M30 P4 over n 441", "    p4v = [res[\"KK_%s_n486_d%d\" % (role, dd)][\"np95\"] for role in ROLES for dd in DRAWS]",
     "    p4v = [res[\"KK_%s_n441_d%d\" % (role, dd)][\"np95\"] for role in ROLES for dd in DRAWS]"),
    ("M31 P5 over the subsamples only", "    allc = sum(1 for s in names if res[s][\"comparable\"])\n    e5 = bool(allc == len(names))",
     "    allc = sum(1 for s in names if \"_d0\" not in s and res[s][\"comparable\"])\n    e5 = bool(allc == 30)"),
    ("M32 C0 reaches strict", "        comparable = not bool(c0p95 >= np95)", "        comparable = not bool(c0p95 > np95)"),
    ("M33 C0 not a precondition", "        comparable = not bool(c0p95 >= np95)", "        comparable = True"),
    ("M34 degenerate check removed", "        reached = sum(1 for x in R[(s, \"SN\")] if x > 0.0)", "        reached = REPS"),
    ("M35 STRONG = the smallest statistic", "    strong, m_s = _nearest(rows, lambda r: -r[\"stat\"])", "    strong, m_s = _nearest(rows, lambda r: r[\"stat\"])"),
    ("M36 MID may be STRONG", "    rest = [r for r in rows if r is not strong]", "    rest = list(rows)"),
    ("M37 EDGE may be MID", "    rest2 = [r for r in rest if r is not mid]", "    rest2 = list(rest)"),
    ("M38 MID nearest 0.070", "    mid, m_m = _nearest(rest, lambda r: abs(r[\"stat\"] - T_MID))", "    mid, m_m = _nearest(rest, lambda r: abs(r[\"stat\"] - T_EDGE))"),
    ("M39 ties to the larger name", "    best = min(rows, key=lambda r: (key(r), r[\"pair\"]))",
     "    best = min(rows, key=lambda r: (key(r), [-ord(c) for c in r[\"pair\"]]))"),
    ("M40 KK-2 margin guard removed", "        if not mar[r] > SEL_MARGIN_MIN:", "        if False:"),
    ("M41 eligibility 972 -> 970", "MIN_COMBINED, MIN_EACH = 972, 100", "MIN_COMBINED, MIN_EACH = 970, 100"),
    ("M42 eligibility each >= 100 dropped", " and len(pops[a]) >= MIN_EACH and len(pops[b]) >= MIN_EACH]", "]"),
    ("M43 stage-0 pin not checked", "    if sha256_bytes(s0bytes) != STAGE0_SHA256:", "    if False:"),
    ("M44 rule re-derivation not checked", "    if got_sel != s0roles or got_sel != SELECTION:", "    if False:"),
    ("M45 stage-0 roles not checked", "    if got_sel != s0roles or got_sel != SELECTION:", "    if got_sel != SELECTION:"),
    ("M46 stage-0 eligible list not checked", "    if [r[\"pair\"] for r in s0rows] != want_pairs or", "    if False and"),
    ("M47 site pin not checked", "    if s_sha != SITES_SHA256:", "    if False:"),
    ("M48 site rebuild not checked", "    if rebuilt != sbytes:", "    if False:"),
    ("M49 arm-read sha not checked", "    if st.get(\"sites_sha256\") != s_sha:", "    if False:"),
    ("M50 hash check removed", "    if json.load(open(hb)) != json.load(open(ha)):", "    if False:"),
    ("M51 KK-0 (iii) removed", "        if not diff <= TOL:", "        if False:"),
    ("M52 KK-0 (iii) tolerance x10", "        diff = abs(f[\"d\"] - sel[role][\"stat\"])", "        diff = abs(f[\"d\"] - sel[role][\"stat\"]) / 10.0"),
    ("M53 IDENTITY gate removed", "    if not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K", "    if False and not (\"%.6f\" % d0 == IDENTITY_DECLARED and k0 == IDENTITY_K"),
    ("M54 IDENTITY p95 / max not checked", "\n            and p95_0 == PC1_P95 and max_0 == PC1_MAX):", "):"),
    ("M55 write-once pre-check removed", "        if os.path.exists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)"),
    ("M56 partial replicates accepted", "        if [i for i, _x in xs] != list(range(REPS)):", "        if False:"),
    ("M57 instrument check removed", "        if st.get(k) != v:\n            refuse(\"instrument", "        if False:\n            refuse(\"instrument"),
    ("M58 snapshot check removed", "    if st.get(\"snapshot\") != SNAPSHOT:", "    if False:"),
    ("M59 sites.csv list check removed", "    if list(rows) != want:", "    if False:"),
    ("M60 k recount check removed", "        if k != int(r[\"k_declared\"]):", "        if False:"),
    ("M61 C0 recount check removed", "        if c0p95 != float(r[\"c0_p95\"]):", "        if False:"),
    ("M62 group sizes not checked", " or int(r[\"groups\"]) != 2 or r[\"group_sizes\"] != gs:", " or int(r[\"groups\"]) != 2:"),
    ("M63 missing arm not checked", "            if (s, a_) not in R:", "            if False:"),
    ("M64 twins not dropped", "        if src[q] and q not in tw:", "        if src[q]:"),
    ("M65 twin keeps the largest id", "        drop.extend(v[1:])", "        drop.extend(v[:-1])"),
    ("M66 registered counts not checked", "    if got != reg:", "    if False:"),
    ("M67 no-src ids enter", "        if src[q] and q not in tw:", "        if q not in tw:"),
    ("M68 draw seed shifted (d + 1)", "PCS.draw({a: pops[a], b: pops[b]}, n, d)", "PCS.draw({a: pops[a], b: pops[b]}, n, d + 1)"),
    ("M69 routine: no 512 slice", "    x = np.asarray(raw, dtype=np.float32)[:, :SLICE].astype(np.float64)", "    x = np.asarray(raw, dtype=np.float32).astype(np.float64)"),
    ("M70 routine: no normalisation", "    x[nz] = x[nz] / nrm[nz, None]", "    x[nz] = x[nz]"),
    ("M71 routine: pairs n^2", "        pair_frac += m * (m - 1.0)", "        pair_frac += m * m"),
    ("M72 load: little-endian", "                v = struct.unpack(\">%df\" % SLICE", "                v = struct.unpack(\"<%df\" % SLICE"),
    ("M73 routine check IDENTITY removed", "    if not abs(d0 - IDENTITY_FULL) <= TOL:", "    if False:"),
    ("M74 routine check: 30 sites not required", "    if cnt != 30 or not worst <= TOL:", "    if not worst <= TOL:"),
    ("M75 routine check: K2 values not compared", "    if cnt != 30 or not worst <= TOL:", "    if cnt != 30:"),
    ("M76 labels pin bypassed", "    cat, src = PK2.read_labels(labels_path, LABELS_SHA)", "    cat, src = PK2.read_labels(labels_path, sha256_bytes(open(labels_path, \"rb\").read()))"),
    ("M77 selftest gate in main removed", "    if not _IN_SELFTEST and selftest() != 0:", "    if False:"),
    ("M78 full site drops an item", "        full = sorted(pops[a] + pops[b])", "        full = sorted(pops[a] + pops[b][:-1])"),
    ("M79 default ruling None (READY D-1)", "Q_KK1_RULING = \"EDGE-DESCRIPTIVE\"   # KK-7 RULED", "Q_KK1_RULING = None   # KK-7 RULED"),
    ("M80 default ruling EDGE-IN-IF-GATED", "Q_KK1_RULING = \"EDGE-DESCRIPTIVE\"   # KK-7 RULED", "Q_KK1_RULING = \"EDGE-IN-IF-GATED\"   # KK-7 RULED"),
]


def mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    t0 = src.index("\nMUTANTS = [\n")
    t1 = src.index("\n]\n", t0) + 3
    head, table, tail = src[:t0], src[t0:t1], src[t1:]        # never mutate the table's own text
    rows = []
    for name, old, new in MUTANTS:
        if old in head:
            mut = head.replace(old, new, 1) + table + tail
        elif old in tail:
            mut = head + table + tail.replace(old, new, 1)
        else:
            rows.append((name, "NOT APPLIED (pattern absent)"))
            continue
        tmp = os.path.join(HERE, "_pkk_mutant_%d.py" % os.getpid())
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(mut)
            r = subprocess.run([sys.executable, tmp, "--selftest"], capture_output=True, text=True, timeout=1800)
            rows.append((name, "KILLED" if r.returncode != 0 else "SURVIVED"))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    for n, v in rows:
        print("  %-64s %s" % (n, v))
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
    analyze(os.path.join(d, ARM_NAME), d, os.path.join(d, SITES_NAME), os.path.join(d, STAGE0_NAME), cpc_labels)
    return 0


if __name__ == "__main__":
    sys.exit(main())
