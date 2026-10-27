"""gap_fix.py: GAP-FIX -- can the anchor-free tree's partition gap to a flat vMF mixture be closed cheaply: (a) by a few Lloyd
(nearest-centroid) passes on the leaves of af_clean_s42 (DECIDING) and the three re-draws, within parent and globally, re-read with
the FLAT-MIX-MMLU instrument against V0; (b) by filing AF-U's union EVAL items only within their own source's leaves (DESCRIPTIVE)?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU readout.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — GAP-FIX: can the anchor-free tree's partition gap
  to a flat vMF mixture be closed cheaply: ..." L24842-L24854 (_as_of 9bff7e39, the commit that wrote it, parent 4c764a1e); the
  registrar's record L24808-L24812. GF1 (the ONE deciding criterion), Support (a)-(g), P1-P7, F-GF, WILL-NOT-SHOW.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or anywhere with --data-root <main checkout>; ONE single-threaded python
process; both parts are POOL READERS (rule 7): never beside a construction or a JVM; busy.ps1 must exit 1 first):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix.py --selftest    # synthetic only (replicas on E:)
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix.py --mutants     # each mutant must be KILLED
  python tools/analysis/gap_fix.py --dry-run [--part a|b]   # POOL line first; pins, denominators, cost; NO label of the
                                                            #   held-out side, NO key read, NO statistic; writes nothing
  python tools/analysis/gap_fix.py --run --part a           # (a): about 30-60 CPU-min; the outcome of record, WRITE-ONCE:
                                                            #   experiment_results/gap_fix/gap_fix_a_outcome.txt (+ _a_arms.csv)
  python tools/analysis/gap_fix.py --run --part b           # (b): about 60-80 CPU-min (RESP-PROFILE-INFO's 3PL two-stage);
                                                            #   launch DETACHED (Start-Process) and poll; WRITE-ONCE:
                                                            #   experiment_results/gap_fix/gap_fix_b_outcome.txt (+ gap_fix_b.READ_STARTED)
  Outputs are never committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_gap_fix with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar.

THE INSTRUMENT (the registration: "importing flat_mix_mmlu.py (blob 555ae3ac), flat_generality.py (d16f1042), key_info_v2.py
(37f5935c), resp_profile_info.py (1817ec8a), union_route_common.py (d5473976), union_af_route.py (bf3f17db) unchanged"): every file
is blob-verified (LF) when its part is imported; parts (a) and (b) import their modules lazily and run in separate processes (the
selftest runs each part in its own child), because flat_mix_mmlu installs a connect guard (four DBs) that union_af_route's import
removes; neither part ever runs with the other's modules loaded.

(a) LLOYD REFINEMENT (deciding on af_clean_s42 at T = 5; the three re-draws descriptive, id-disjoint only)
  DATA      per tree: its fit set (FM.fit_set: the snapshot's root-region texts, ASSERTED counts 8,125 / 8,126 / 8,130 / 8,133),
            the routing slice 256, unit rows (FM.fit_matrix); its held-out / EVAL side and the label set through FG.tree_pool +
            FG.corpus_for (af_clean_s42: the 3,445 judgeable questions of p2dca21ab5f4ef3ae, content-closed under stem_key at norm-v1
            for this tree; the re-draws on their own pools); FG.hygiene REFUSES a fit text equal to an EVAL text. Held-out items never
            enter a centroid; labels only in M1's scorer (AF.score_cells via FM.m1_block); keys only in M2 (FM.m2_block, F6).
  V         V0-V4 are READ, never refitted: FLAT-MIX-MMLU's state (af_clean_s42) and FLAT-GENERALITY's (re-draws), each part file
            sha256-pinned below (a changed file REFUSES); V0 is the comparator of record, V1-V4 give spread_V.
  REFINE    R-A1 the start z_0 = the tree's flatLeaf assignment of its fit set (AF.route: nearest leaf vmfMu at the slice, unit rows):
                 "the tree's leaf memberships on its TRAIN fit set, at the routing slice and renormalisation with which FLAT-MIX-MMLU
                 files T" (FM.fit_partition's T: lab = AF.route(tree, X)). The graph membership is printed beside (descriptive).
            R-A2 one pass t = 1, 2, ...: C_t = renormalised mean of the current members of each leaf (an emptied leaf KEEPS its last
                 centroid, the as-built vmfMu before pass 1; count printed); every fit item moves to the nearest C_t among its allowed
                 leaves (cosine; numpy argmax, the lower leaf index on a tie). LLOYD-WP (deciding): the allowed leaves are the leaves of
                 the subtree of the parent of the item's CURRENT leaf (the registration's words "ITS CURRENT LEAF'S PARENT'S
                 SUBTREE", read per pass: an item that moved into a deeper branch is bound by its new leaf's parent from the next
                 pass on; a leaf with two parents REFUSES). LLOYD-GL (descriptive): all leaves. READING CHECK (descriptive, NOT a
                 registered arm): WP-A, the parent of the item's AS-BUILT leaf fixed for every pass (the other reading of "current";
                 printed at T = 5 so the reviewer sees whether the reading matters).
            R-A3 the refined leaf centroids after T passes = the renormalised means of the members after pass T (emptied: the last
                 centroid); held-out items, the label set and the keyed questions are filed to the nearest refined centroid among
                 ALL leaves (flatLeaf). T = 0 (recentring without any move) is printed descriptive.
            R-A4 passes are run to T = 10 and on to convergence (no item changes leaf in a pass; cap 300, printed); M1 / M2 at T = 0
                 (descriptive), 1, 2, 5 (DECIDING for WP on af_clean_s42), 10 and convergence.
  READOUTS  on af_clean_s42 at T = 5: D_R = M1(T-WP) - M1(V0); D_T = M1(T) - M1(V0) (the recorded -0.0430 [-0.0557, -0.0293]: an
            IDENTITY PRECONDITION, refused otherwise, with T 0.727 [0.712, 0.741] / 2504, V0 2652 of 3445, M2(T) +12.785, spread_V
            0.0305); I_R = M1(T-WP) - M1(T); paired 95% intervals = FLAT-MIX-MMLU C1's held-out interval (FM.twin_boot_ci: 1,000
            whole stem_key twin-group resamples, seed 20260926, percentile). M2 differences with F6's boot_mean_ci (descriptive).
  GF1       (the registration's one clause) CLOSED iff the 95% upper bound of D_R >= 0 AND I_R > 0 with its 95% lower bound > 0; OPEN
            iff the 95% upper bound of D_R < 0 AND |D_R| > max(MDE80 0.0186, spread_V 0.0305) = 0.0305; PARTIAL otherwise (exhaustive
            and exclusive). FAILS (rule 8): CLOSED refuted by D_R's upper bound < 0 or I_R's lower bound <= 0. F-GF fires iff CLOSED.
  PREDICTIONS P1-P6 as registered (bands HELD iff the point lies in the CLOSED interval; outcome probabilities by Brier). Readings
            (stated): P1 uses the held-out leaf-change share of T-WP / T-GL against T as built; P4 is D(GL) = M1(T-GL) - M1(V0) at
            T = 5; P5 "the refined M2 gap closes by less than half of -1.534e-3" = (M2(T-WP) - M2(V0)) < D_T,M2 / 2 with D_T,M2 the
            measured M2(T) - M2(V0) (T = 5, WP); P6 "WP raises M1 at the point on all three re-draws" = I_R(T = 5) > 0 on each.
  Not applicable (stated): no judge verdict enters (no wrong(established), no tie conventions A / B); no call cache, --pilot or
  truncation guard (zero calls).

(b) SOURCE-GATED FILING (descriptive in full; the own-source subset was SEEN)
  OBJECTS   the union objects of record (union_route_common / resp_structure_common THE OBJECTS: pool pv2_1575de61bb20e977, B0-2
            pool line first; EVAL 5,907 / 5,404; 18 models; AF-U as built, inputs manifest 53021e26...; frozen TRAIN policy
            8d68018c...; K_s seeds 0-4; two-stage B 2,000, default_rng(42)).
  GATING    R-B1 every EVAL-side item (the side export) with an AF-U routing row is filed to the nearest AF-U leaf (cosine of its 256-d
            unit vector, union_af_route._TV, the reader K_s was filed with, against the member snapshots' leaf vmfMu) among the leaves
            of its OWN declared source(s) (union_af_route.item_sources of the routing rows: the rule K_s is filed by, R3); a one-cell
            member's item keeps its one cell (it is filed by source already); TRAIN items are NOT re-filed (the registration: "TRAIN
            policies unchanged"). R-B2 IDENTITY: the ungated nearest leaf over all grafted leaves must equal AF-U's recorded cell for
            every gated item (REFUSED otherwise); the number of EVAL items whose cell changes is printed beside R-KI1's 191.
  READERS   on the ONE TRAIN key and the ONE EVAL key read (resp_structure_common.read_train, union_cells_io.eval_set with this test's
            B1 marker), D is built twice by v2_declared_cells.build_ud (as built; gated). Ungated IDENTITY (refused otherwise): B3 and
            C1 / G_AF at the point (resp_structure_common.b3_identity); KI1 D -0.024800 [-0.043451, -0.006149], spread_K 0.017640;
            U2 D_K -0.45pp [-1.31pp, +0.41pp], spread_K +0.58pp (one run_boot with KEY-INFO-V2's hook); RP2 D -0.004423, spread_K
            0.000861 (point). Gated: KI1 (key_info_v2.ki_terms on run_boot's TRAIN multiplicities / EVAL weights; interval
            union_route_common.interval; F6 cross-check on AF-U gated), RP2 (resp_profile_info.point_stats / boot / iid_D: every
            replicate re-fits the 3PL), U2 (union_af_route.u_stats); each with its registered interval form and spread_K, its word
            by its own function (ki1_verdict / rp2_word / u2_verdict), printed DESCRIPTIVE (not a registered verdict); P7.

SELFTEST (--selftest; each part in its own child process; replicas under scratch_dir's E: dir; NO DB of record is opened):
  (a) A-PURE masks / Lloyd against an independent loop; A-BRANCH every GF1 / F-GF / FAILS / P1-P6 / Support print branch by value with
      the edges (UB exactly 0, |D_R| exactly 0.0305, I_R's lower bound exactly 0); A-NAIVE a twin-group fixture where an i.i.d. interval
      reads CLOSED and the registered twin-group interval reads PARTIAL; A-E2E --dry-run (labels forbidden) and --run on
      flat_generality's replica, every deciding number against an independent recomputation; A-VERDICT three planted replicas whose
      GF1 is known by construction (CLOSED: V0 = the refined partition, a junk tree; PARTIAL: a fixed-point tree, V0 = the same
      partition; OPEN: the fixed-point tree against a better V0); A-REFUSE write-once, identity, V-state pin, fit/EVAL overlap.
  (b) B-GATE gate_core by value (moves, one-cell, identity refusal, mixed sources, missing vector); B-E2E run_b on resp_structure_common's
      sealed fixture with a planted gating: the gated KI / RP2 / U2 points and the KI two-stage interval against independent loops,
      the ungated identity from the same loops; refusals (identity, a re-filed TRAIN item, write-once); B-DRY no key read; B-BRANCH.
MUTANTS (MUTANTS at the end; --mutants runs each on a copy under scratch_dir's E: dir, the named selftest cases in a child; 2026-10-06,
build of record): 46 of 46 KILLED.
  X01 GF1 UB >= 0 -> > 0 (A-BRANCH, A-VERDICT) | X02 LB(I_R) leg dropped (A-NAIVE) | X03 I_R point leg dropped | X04 OPEN > -> >= | X05 OPEN
  without UB < 0 | X06 OPEN on the signed D_R | X07 FAILS <= -> < | X08 D_R against T | X09 I_R against V0 (A-E2E) | X10 i.i.d. interval in
  the deciding path (A-NAIVE) | X11 deciding T 5 -> 10 | X12 deciding WP -> GL (A-VERDICT) | X13 WP mask = all | X14 WP mask from the
  as-built leaf | X15 emptied leaf to zero | X16 filing centroids = pass-T centroids | X17 root-parent leaf only itself (A-PURE) | X18
  held-out share from TRAIN (A-E2E) | X19 P1 edges exclusive | X20 P5 inverted | X21 P6 any | X22 F-GF on PARTIAL | X23 identity removed |
  X24 V-state pin removed | X25 write-once x -> w (A-PURE) | X26 hygiene removed (A-OVERLAP) | X27 dry-run reads labels | X28 P4 from WP |
  X29 P3 Brier ignores the outcome | X30 run_a's existence pre-check removed | X31 refinement fitted on the label set, not the fit set |
  Y01 gating without the source restriction | Y02 R-B2 identity removed | Y03 TRAIN items re-filed (B-GATE) | Y04 KI1 against K0 only |
  Y05 KI1 interval from i.i.d. | Y06 RP2 on the as-built D | Y07 U2 from the as-built replicates | Y08 identity (b) removed | Y09 TRAIN-cell
  check removed | Y10 KI spread min/max | Y11 gated KI on as-built replicates | Y12 P7 word from another value | Y13 / Y15 KI1 / RP2 word
  line omitted | Y14 U2 word on another spread (B-E2E).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import sys           # noqa: E402
import io            # noqa: E402
import csv           # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import tempfile      # noqa: E402
import contextlib    # noqa: E402
import subprocess    # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.environ.get("GAPFIX_TOOLS_DIR") or os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import scratch_dir   # noqa: E402,F401  (TEMP-SPRAWL: tempfile on E:, removed at exit)

TAG = "[GAP-FIX]"
TEST_ID = "GAP-FIX"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — GAP-FIX: can the anchor-free tree\'s'
            ' partition gap to a flat vMF mixture be closed cheaply: ..." L24842-L24854 (_as_of 9bff7e39, parent 4c764a1e)')
IMPORT_PINS = {"flat_mix_mmlu.py": "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2",
               "flat_generality.py": "d16f104244450013746079d8bb9aab9d3e9092c8",
               "key_info_v2.py": "37f5935c7e64d95110193cce575b25b128529f53",
               "resp_profile_info.py": "1817ec8ad607bb3b3d0abfb0116b5b2c27dd2d02",
               "union_route_common.py": "d54739769d38a3a402e2deaab9e45109cd86de4e",
               "union_af_route.py": "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"}
PART_FILES = {"a": ("flat_mix_mmlu.py", "flat_generality.py"),
              "b": ("key_info_v2.py", "resp_profile_info.py", "union_route_common.py", "union_af_route.py")}
OUT_REL = "experiment_results/gap_fix"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _lf(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def pins_of(path):
    d = _lf(path)
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest(), lf16=hashlib.sha256(d).hexdigest()[:16],
                crlf16=hashlib.sha256(d.replace(b"\n", b"\r\n")).hexdigest()[:16])


def fmt_pins(p):
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"][:8], p["lf16"], p["crlf16"])


def verify_imports(part):
    """The registration's imports, unchanged: the LF blob of each file the part imports, or nothing runs."""
    out = []
    for f in PART_FILES[part]:
        got = pins_of(os.path.join(HERE, f))["blob"]
        if got != IMPORT_PINS[f]:
            refuse("tools/analysis/%s is blob:%s, not the registered blob:%s" % (f, got[:8], IMPORT_PINS[f][:8]))
        out.append("[PIN] tools/analysis/%s blob:%s (registered; verified)" % (f, got[:8]))
    return out


def script_pins():
    return pins_of(os.path.abspath(__file__))


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_once(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def in_band(x, band):
    return bool(band[0] <= x <= band[1])


def brier_multi(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def brier_event(p, happened):
    return float((p - (1.0 if bool(happened) else 0.0)) ** 2)


def hw(x, band):
    return "HELD" if in_band(x, band) else "FAILED"


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# (a) LLOYD REFINEMENT
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
TREES_A = ("af_clean_s42", "af_s137", "af_s2048", "af_s42_o1")
DECIDING_TREE = "af_clean_s42"
REG_A = dict(
    t_steps=(1, 2, 5, 10), t_decide=5, t_cap=300,
    bar_open=0.0305, mde_dr=0.0186, spread_v=0.0305, se_dr=0.00663, se_ir=0.00539, mde_ir=0.0151, disc_ir_decl=0.10, disc_dr=0.1533,
    n_decide=3445, d_t_m2_rec=-1.534e-3,
    identity={"af_clean_s42": dict(n=3445, t_hits=2504, v0_hits=2652, spread="0.0305", m1="0.727 [0.712, 0.741]", m2="+12.785",
                                   d_t="-0.0430 [-0.0557, -0.0293]"),
              "af_s137": dict(n=3448, t_hits=2480, v0_hits=2553, spread="0.0133"),
              "af_s2048": dict(n=3446, t_hits=2559, v0_hits=2594, spread="0.0165"),
              "af_s42_o1": dict(n=3437, t_hits=2459, v0_hits=2587, spread="0.0177")},
    v_state={"af_clean_s42": ("experiment_results/flat_mix_mmlu/state", (
                 "8792a8f40a46a57ad938e01781ae61368c2619c23ddbb531af29dd0be567dd7e", "dbb4940be355d8b7b01f408b2844535afc6bdf6ae85ff4e070c5d7a681342de1",
                 "5a67d5c19c00b098273bf998403148859579bb2e55aca5a5cbb861f2b4f8139d", "445d384323d3fd690dd6a68bf13c5a7be33de8736ba71d6df666b874656318a2",
                 "fdd6aa33572018cf2ded13bb202c336320a39fc8abb47b46d7254675398c98ed")),
             "af_s137": ("experiment_results/flat_generality/state/af_s137", (
                 "2f0e8392d047680ec19e3da097270c4169ed68b052db7ae3dc9b3fdbee15f79f", "4d82dc70f0de65bb3a25da5ecba3ba421bc7ee078c10bdd122eefd23e2478071",
                 "9d096e1879ca82bc0d8235bf8a307e7b336f0473f70c7f9bc88a9bebde01d95b", "9ee0891afad1d19b2f85935a947e415bc42b8ce01311faa7482a92107d5941d1",
                 "6ef482fc314018e1efa6f274dd2c5fd5eae7440501d5a58f0bf0e55c681599fa")),
             "af_s2048": ("experiment_results/flat_generality/state/af_s2048", (
                 "c8a1ca52c3fb05493cad1f82e546ce14bf099e76150a1a5b072a7bdf679af820", "cb02ebd9e7038f5807458d4f744e10622769785a18809e6df666c975f5d3471b",
                 "37c24ffdaedfb51dc5a51c6b846022d8516dabcaf4edc80599fd69d381821cf2", "6bfc28120146c859b36bca81979278ccbad98f2086639e623004847441e0241a",
                 "0117223c5e5d97ba7330fcdb349f59c6054e5368f16dc0562576618cada418d8")),
             "af_s42_o1": ("experiment_results/flat_generality/state/af_s42_o1", (
                 "4785ba7eb1d18a6f014f8b82f20ff2b4be3ed5ba1ea5758d3aec77aa14aac5cf", "3e013ef728900cb74406ad1581b2f890727c48169111f5b17b1815ca5c2a4679",
                 "6d968bf42051ffddd9ec05ac5a8729af6e4f7dafed5c369e0d83cc37d79d1784", "9a182f9820aed4970708b98cdd9c0e04dfef73e1729ab96ecb473d92b555de96",
                 "7b88c7c8b35da00ae1e714d4d08887795fa2b75d134640e16857ab93ef0b527d"))},
    outcome="gap_fix_a_outcome.txt", arms_csv="gap_fix_a_arms.csv",
)
_REGA = [REG_A]
PRED_A = dict(P1_wp=(0.04, 0.25), P1_gl=(0.08, 0.35), P2_dr=(-0.045, -0.012), P2_ir=(0.000, 0.030),
              P3=(("CLOSED", 0.10), ("PARTIAL", 0.50), ("OPEN", 0.40)), P4=(-0.035, 0.005), P5=0.65, P6=0.60)
FM = FG = AF = F = None                       # set by _a_mods() (lazy: part (a) only)


def RA():
    return _REGA[0]


def _a_mods():
    """Part (a)'s imports, blob-verified first (flat_generality verifies flat_mix_mmlu's blob again and imports it)."""
    global FM, FG, AF, F
    if FG is None:
        verify_imports("a")
        import flat_generality as _FG          # noqa: E402  (pins flat_mix_mmlu; FM installs its connect guard)
        FG, FM, AF, F = _FG, _FG.FM, _FG.AF, _FG.F
    return FG


# ── pure: the tree's parent masks and the Lloyd passes (no data access) ─────────────────────────────────────────────────────
def leaf_parent_masks(byid, leaf_ids):
    """-> (mask k x k bool: mask[j] = the leaves of the subtree of leaf j's parent; parent id per leaf; root id). A leaf with no
    parent or with two parents REFUSES (the registration's 'parent' needs exactly one)."""
    parents = {}
    for nid, n in byid.items():
        for c in n.get("childIds") or []:
            parents.setdefault(c, []).append(nid)
    roots = [nid for nid in byid if not parents.get(nid)]
    idx = {l: i for i, l in enumerate(leaf_ids)}
    k = len(leaf_ids)
    mask = np.zeros((k, k), dtype=bool)
    par = []
    sub = {}
    for j, l in enumerate(leaf_ids):
        ps = parents.get(l, [])
        if len(ps) != 1:
            refuse("leaf %s has %d parents (within-parent refinement needs exactly one)" % (l, len(ps)))
        p = ps[0]
        par.append(p)
        if p not in sub:
            out, stack, seen = [], [p], set()
            while stack:
                cur = stack.pop()
                if cur in seen:
                    continue
                seen.add(cur)
                if cur in idx:
                    out.append(idx[cur])
                for c in byid[cur].get("childIds") or []:
                    if c in byid:
                        stack.append(c)
            sub[p] = out
        mask[j, sub[p]] = True
        if not mask[j, j]:
            refuse("leaf %s is not in its own parent's subtree" % l)
    return mask, par, roots


def centroids(X, z, k, prev):
    """Renormalised mean of each leaf's current members; a leaf without members keeps prev's row (its last centroid)."""
    S = np.zeros((k, X.shape[1]))
    np.add.at(S, z, X)
    cnt = np.bincount(z, minlength=k)
    C = np.array(prev, dtype=np.float64, copy=True)
    live = cnt > 0
    C[live] = S[live] / np.linalg.norm(S[live], axis=1, keepdims=True)
    return C, cnt


def lloyd_step(X, C, allowed):
    """Every row to the nearest centroid among its allowed leaves (allowed: n x k bool); numpy argmax (lower index on a tie)."""
    S = X @ C.T
    S[~allowed] = -np.inf
    return np.argmax(S, axis=1)


def refine(X, z0, mu0, mask, variant, t_keep, t_cap):
    """The Lloyd passes of one variant: 'WP' (the CURRENT leaf's parent's subtree, per pass), 'GL' (all leaves), 'WPA' (the AS-BUILT
    leaf's parent's subtree; the reading check). -> dict(t -> dict(z, C (filing centroids), empty), t_conv, converged, moves)."""
    k = mu0.shape[0]
    full = np.ones((len(z0), k), dtype=bool)
    z = np.array(z0, dtype=np.int64)
    C_prev = np.array(mu0, dtype=np.float64)
    out = {}
    Cf, cnt = centroids(X, z, k, C_prev)
    out[0] = dict(z=z.copy(), C=Cf, empty=int((cnt == 0).sum()))
    t_conv, conv, moves = None, False, []
    need = max(t_keep)
    for t in range(1, t_cap + 1):
        C_t, _c = centroids(X, z, k, C_prev)
        if variant == "WP":
            allowed = mask[z]
        elif variant == "WPA":
            allowed = mask[z0]
        elif variant == "GL":
            allowed = full
        else:
            refuse("unknown variant %r" % variant)
        zn = lloyd_step(X, C_t, allowed)
        moves.append(int((zn != z).sum()))
        changed = bool((zn != z).any())
        z, C_prev = zn, C_t
        if t in t_keep or (not changed and t_conv is None):
            Cf, cnt = centroids(X, z, k, C_prev)
            rec = dict(z=z.copy(), C=Cf, empty=int((cnt == 0).sum()))
            if t in t_keep:
                out[t] = rec
            if not changed and t_conv is None:
                t_conv, conv = t, True
                out["conv"] = rec
        if conv and t >= need:
            break
    if not conv:
        Cf, cnt = centroids(X, z, k, C_prev)
        out["conv"] = dict(z=z.copy(), C=Cf, empty=int((cnt == 0).sum()))
        t_conv = t_cap
    for t in t_keep:                          # converged before t: the partition no longer changes
        if t not in out:
            out[t] = out["conv"]
    return dict(steps=out, t_conv=t_conv, converged=conv, moves=moves)


# ── the deciding clause and its readout (pure) ──────────────────────────────────────────────────────────────────────────────
def gf1(dr, dr_hi, ir, ir_lo, bar):
    """GF1, the registration's one clause: CLOSED iff UB(D_R) >= 0 AND I_R > 0 AND LB(I_R) > 0; OPEN iff UB(D_R) < 0 AND |D_R| >
    bar (= max(MDE80 0.0186, spread_V 0.0305)); PARTIAL otherwise."""
    if bool(dr_hi >= 0) and bool(ir > 0) and bool(ir_lo > 0):
        return "CLOSED"
    if bool(dr_hi < 0) and bool(abs(dr) > bar):
        return "OPEN"
    return "PARTIAL"


def gf1_refuted(dr_hi, ir_lo):
    """FAILS (rule 8): CLOSED is refuted at the planned n by D_R's upper bound < 0 or by I_R's lower bound <= 0."""
    return bool(dr_hi < 0) or bool(ir_lo <= 0)


def paired_m1(per_a, per_b, groups):
    """a minus b per held-out question; FLAT-MIX-MMLU C1's interval (whole stem_key twin groups, seed 20260926)."""
    d = np.asarray(per_a, dtype=np.float64) - np.asarray(per_b, dtype=np.float64)
    lo, hi = FM.twin_boot_ci(d, groups)
    return dict(d=float(d.mean()), lo=float(lo), hi=float(hi), disc=float(np.mean(d != 0)))


def paired_m2(per2_a, per2_b, ci=True):
    common = [q for q in per2_a if q in per2_b]
    d = np.array([per2_a[q] - per2_b[q] for q in common])
    if not ci:
        return dict(d=float(d.mean()), lo=None, hi=None, n=len(common))
    lo, hi = F.boot_mean_ci(d)
    return dict(d=float(d.mean()), lo=float(lo), hi=float(hi), n=len(common))


def decide(arms, groups, key_wp, bar):
    """The deciding quantities from the per-question arms (run_a calls this; the selftest calls it on planted arms too)."""
    dr = paired_m1(arms[key_wp]["per1"], arms["V0"]["per1"], groups)
    ir = paired_m1(arms[key_wp]["per1"], arms["T"]["per1"], groups)
    dt = paired_m1(arms["T"]["per1"], arms["V0"]["per1"], groups)
    word = gf1(dr["d"], dr["hi"], ir["d"], ir["lo"], bar)
    return dict(dr=dr, ir=ir, dt=dt, word=word, refuted=gf1_refuted(dr["hi"], ir["lo"]), bar=bar)


def f4(x):
    return "%+.4f" % x


def ci4(p):
    return "%s [%s, %s]" % (f4(p["d"]), f4(p["lo"]), f4(p["hi"]))


GF1_TEXT = {
    "CLOSED": "GF1: CLOSED: the 95%% upper bound of D_R %s >= 0 and I_R %s > 0 with its 95%% lower bound %s > 0: the loss is no longer "
              "shown and the refinement moved it",
    "OPEN": "GF1: OPEN: the 95%% upper bound of D_R %s < 0 and |D_R| %s > %s (max(MDE80 0.0186, spread_V 0.0305)): FLAT-MIX-MMLU's L1 "
            "rule on M1 still fires after five within-parent passes",
    "PARTIAL": "GF1: PARTIAL: neither CLOSED (upper bound of D_R %s >= 0 with I_R %s and its lower bound %s > 0) nor OPEN (upper bound "
               "< 0 with |D_R| %s > %s) holds",
}


def gf1_lines(dec):
    dr, ir, bar = dec["dr"], dec["ir"], dec["bar"]
    w = dec["word"]
    L = []
    if w == "CLOSED":
        L.append(GF1_TEXT["CLOSED"] % (f4(dr["hi"]), f4(ir["d"]), f4(ir["lo"])))
    elif w == "OPEN":
        L.append(GF1_TEXT["OPEN"] % (f4(dr["hi"]), "%.4f" % abs(dr["d"]), "%.4f" % bar))
    else:
        L.append(GF1_TEXT["PARTIAL"] % (f4(dr["hi"]), f4(ir["d"]), f4(ir["lo"]), "%.4f" % abs(dr["d"]), "%.4f" % bar))
    if dec["refuted"]:
        L.append("FAILS (rule 8): CLOSED is REFUTED at the planned n (%s)" % "; ".join(
            x for x in ("upper bound of D_R %s < 0" % f4(dr["hi"]) if dr["hi"] < 0 else "",
                        "lower bound of I_R %s <= 0" % f4(ir["lo"]) if ir["lo"] <= 0 else "") if x))
    else:
        L.append("FAILS (rule 8): CLOSED is not refuted (upper bound of D_R %s >= 0 and lower bound of I_R %s > 0)" % (f4(dr["hi"]), f4(ir["lo"])))
    if w == "CLOSED":
        L.append("FALSIFIER F-GF FIRES (GF1 CLOSED): five nearest-centroid passes within parent, topology kept, remove FLAT-MIX-MMLU's "
                 "purity loss; the reading that the loss is a property of the tree as a partition (T-4 open) is overturned and the loss is "
                 "relocated in the leaf boundaries; FLAT-MIX-MMLU's LIMITATION sentence takes the bracket 'removed by a within-parent "
                 "Lloyd refinement (GAP-FIX)'; a refinement step becomes a candidate engine change for a NEW registration with its own "
                 "go (never from this result alone)")
    else:
        L.append("FALSIFIER F-GF NOT FIRED (GF1 %s): the gap is not closed by refinement at T 5; T-4's mechanism stays unidentified" % w)
    return L


def predictions_a(st):
    """P1-P6 by value. st: dict with share_wp, share_gl, dr, ir, word, d_gl, m2_wp_v0, m2_t_v0, ir_redraws (list or None)."""
    L = []
    L.append("  P1 held-out leaf-change share at T 5: WP %.4f, band [0.04, 0.25] -> %s; GL %.4f, band [0.08, 0.35] -> %s" % (
        st["share_wp"], hw(st["share_wp"], PRED_A["P1_wp"]), st["share_gl"], hw(st["share_gl"], PRED_A["P1_gl"])))
    L.append("  P2 D_R (WP) %s, band [-0.045, -0.012] -> %s; I_R %s, band [0.000, +0.030] -> %s" % (
        f4(st["dr"]), hw(st["dr"], PRED_A["P2_dr"]), f4(st["ir"]), hw(st["ir"], PRED_A["P2_ir"])))
    L.append("  P3 GF1: CLOSED 0.10, PARTIAL 0.50, OPEN 0.40: observed %s -> Brier %.4f" % (st["word"], brier_multi(PRED_A["P3"], st["word"])))
    L.append("  P4 (descriptive) D (GL) %s, band [-0.035, +0.005] -> %s" % (f4(st["d_gl"]), hw(st["d_gl"], PRED_A["P4"])))
    e5 = bool(st["m2_wp_v0"] < st["m2_t_v0"] / 2.0)
    L.append("  P5 (descriptive) the refined M2 gap closes by less than half (M2(T-WP) - M2(V0) %+.3f < D_T,M2 / 2 = %+.3f, x1e-3), "
             "probability 0.65: %s -> %s; Brier %.4f" % (1000 * st["m2_wp_v0"], 500 * st["m2_t_v0"], "yes" if e5 else "no",
                                                        "HELD" if e5 else "FAILED", brier_event(PRED_A["P5"], e5)))
    if st.get("ir_redraws") is None or len(st["ir_redraws"]) != 3:
        L.append("  P6 (descriptive) WP raises M1 at the point on all three re-draws, probability 0.60: NOT SCOREABLE (re-draws read: %s)"
                 % (0 if st.get("ir_redraws") is None else len(st["ir_redraws"])))
    else:
        e6 = bool(all(x > 0 for x in st["ir_redraws"]))
        L.append("  P6 (descriptive) WP raises M1 at the point on all three re-draws (I_R %s), probability 0.60: %d of 3 -> %s; Brier %.4f" % (
            " / ".join(f4(x) for x in st["ir_redraws"]), sum(1 for x in st["ir_redraws"] if x > 0), "HELD" if e6 else "FAILED",
            brier_event(PRED_A["P6"], e6)))
    return L


def support_lines_a(n, mbar, dec):
    r = RA()
    dr, ir = dec["dr"], dec["ir"]
    se_dr_m, se_ir_m = math.sqrt(dr["disc"] / n), math.sqrt(ir["disc"] / n)
    bs_dr, bs_ir = (dr["hi"] - dr["lo"]) / (2 * 1.96), (ir["hi"] - ir["lo"]) / (2 * 1.96)
    return [
        "SUPPORT (registered beside measured):",
        "  (a) DECIDING denominator: %d held-out questions (registered %d; FLAT-MIX-MMLU C1; one item per question); one tree, one V0 (seed of record)" % (n, r["n_decide"]),
        "  (b) DEFF 1.0 declared (FLAT-MIX-MMLU); measured Kish mean twin-group size %.4f (DEFF upper bound at rho = 1)" % mbar,
        "  (c) n_eff = %d / %.4f = %.0f" % (n, mbar, n / mbar),
        "  (d) SE(D_R): registered %.5f (FLAT-MIX-MMLU's realised C1 analytic SE, discordance %.4f); measured discordance T-WP vs V0 %.4f -> "
        "sqrt(%.4f / %d) = %.5f; twin-bootstrap half-width / 1.96 %.5f | SE(I_R): registered %.5f (declared discordance %.2f); measured "
        "discordance T-WP vs T %.4f -> %.5f; twin-bootstrap %.5f" % (r["se_dr"], r["disc_dr"], dr["disc"], dr["disc"], n, se_dr_m, bs_dr,
                                                                    r["se_ir"], r["disc_ir_decl"], ir["disc"], se_ir_m, bs_ir),
        "  (e) MDE80: D_R registered %.4f, measured 2.8 x %.5f = %.4f | I_R registered %.4f, measured 2.8 x %.5f = %.4f" % (
            r["mde_dr"], se_dr_m, 2.8 * se_dr_m, r["mde_ir"], se_ir_m, 2.8 * se_ir_m),
        "  (f) VERDICT LINE (registered): CLOSED vs not SCOREABLE (predicted D_R -0.030 lies 0.030 from the bar 0, beyond 0.0186); OPEN vs "
        "PARTIAL DESCRIPTIVE-ONLY (predicted |D_R| 0.030 lies 0.0005 from the bar 0.0305); I_R DESCRIPTIVE-ONLY (predicted +0.013 short of 0.0151)",
        "  (g) STRUCTURAL: CLOSED is reachable at infinite budget; OPEN's bar keeps V's seed spread 0.0305 at any n; WP is bounded by the "
        "parent constraint, and in the GL limit a refinement is a warm-started flat k-means",
        "NOT APPLICABLE (stated): no judge verdict enters (no wrong(established), no tie conventions A / B); zero calls (no cache, pilot or "
        "truncation guard)",
    ]


WILL_NOT_SHOW_A = ("WHAT THIS RESULT WILL NOT SHOW (registered): anything about the engine's construction itself (a post-hoc refinement); "
                   "content-closed re-draw results (id-disjoint only); that V is a better taxonomy; a key-information claim (M2 "
                   "descriptive); a second embedder or corpus.")


# ── data-bound (a) ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def spec_of(tree):
    return FG.IDENTITY if tree == DECIDING_TREE else FG.TREES[tree]


def out_paths_a():
    d = os.path.join(FM.DATA_ROOT, *OUT_REL.split("/"))
    return os.path.join(d, RA()["outcome"]), os.path.join(d, RA()["arms_csv"])


def v_parts(tree):
    """V0-V4 of the tree, READ from the state of record; every part file's sha256 must equal its pin (REFUSED otherwise)."""
    rel, shas = RA()["v_state"][tree]
    d = os.path.join(FM.DATA_ROOT, *rel.split("/"))
    parts, lines = {}, []
    for s, want in enumerate(shas):
        p = os.path.join(d, "part_V%d.json" % s)
        if not os.path.isfile(p):
            refuse("%s: V state %s is absent" % (tree, p))
        got = sha256_file(p)
        if got != want:
            refuse("%s: V state %s is sha256 %s, not the pinned %s (V is read, never refitted)" % (tree, p, got, want))
        with open(p, encoding="utf-8") as f:
            b = json.load(f)
        if b.get("partition") != "V%d" % s:
            refuse("%s: %s holds partition %r, not V%d" % (tree, p, b.get("partition"), s))
        parts["V%d" % s] = b
        lines.append("[PIN] %s/part_V%d.json sha256 %s (= the pin; rule %s)" % (rel, s, got[:16], b.get("rule")))
    return parts, lines


def eval_texts_only(ids):
    """The EVAL side's TEXTS (eval_question_link; no category, no key) for the dry-run's hygiene and twin-group counts."""
    import pool_guard
    con = pool_guard.open_ro(os.path.join(FM.DATA_ROOT, "mmlu_pro_dataset_cache_v2.db"))
    try:
        link = {q: t for q, t in con.execute("SELECT question_id, question_text FROM eval_question_link") if q in ids}
    finally:
        con.close()
    if set(link) != set(ids):
        refuse("%d EVAL ids have no eval_question_link text" % len(set(ids) - set(link)))
    return [link[q] for q in sorted(ids)]


def tree_data(tree, labels=True):
    """Fit set, matrix, tree, masks, pool; with labels=True also the label set and the held-out side (FG.corpus_for)."""
    spec = spec_of(tree)
    texts, g, ids, text = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])
    pid, eval_ids = FG.tree_pool(spec)
    tr = FG.load_tree(tree, spec)
    mask, par, roots = leaf_parent_masks(tr["byid"], tr["leaf_ids"])
    out = dict(spec=spec, texts=texts, graph=g, ids=ids, text=text, pid=pid, eval_ids=eval_ids, tree=tr, mask=mask, par=par, roots=roots)
    if labels:
        train, heldout, _cs = FG.corpus_for(spec, eval_ids)
        FG.hygiene(texts, [t for t, _ in heldout])          # REFUSES if an EVAL text of this tree is in its fit set
        out.update(train=train, heldout=heldout)
    return out


def graph_agreement(td_, z0):
    """Descriptive: share of fit texts whose flatLeaf leaf (z0) holds the text in the snapshot graph's leaf region."""
    tr, g, text = td_["tree"], td_["graph"], td_["text"]
    tpos = {t: i for i, t in enumerate(td_["texts"])}
    inleaf = {}
    for j, l in enumerate(tr["leaf_ids"]):
        node = g["byid"].get(l)
        for q in (node or {}).get("queryIds") or []:
            if q in text and text[q] in tpos:
                inleaf.setdefault(tpos[text[q]], set()).add(j)
    agree = sum(1 for i, j in enumerate(z0) if j in inleaf.get(i, ()))
    return agree, len(inleaf), len(z0)


def arm_from_centroids(name, C, leaf_ids, ctx):
    fn = (lambda C_: (lambda Q: [leaf_ids[i] for i in FM.nearest_assign(Q, C_)]))(C)
    sc, hits, kh = FM.m1_block(fn, ctx["Qt"], ctx["Qh"], ctx["train"], ctx["heldout"])
    m2 = FM.m2_block(fn, ctx["keyed"], ctx["veck"])
    return dict(name=name, m1=sc["acc"], m1_lo=sc["lo"], m1_hi=sc["hi"], hits=sc["hits"], sc=sc, per1=hits, m2=m2["mean"],
                per2=m2["per_q"], per4=None, m4=None, filed=np.asarray(FM.nearest_assign(ctx["Qh"], C)))


def run_tree_a(tree, keyed, veck, say):
    """Everything of one tree: identity, the refinement arms, the paired quantities. -> result dict."""
    r = RA()
    td_ = tree_data(tree, labels=True)
    tr, mask, spec = td_["tree"], td_["mask"], td_["spec"]
    k = len(tr["leaf_ids"])
    X = FM.fit_matrix(td_["texts"], dim=FG.DIM)
    train, heldout = td_["train"], td_["heldout"]
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    Qt, Qh = AF.sliced(vec, [t for t, _ in train], FG.DIM), AF.sliced(vec, [t for t, _ in heldout], FG.DIM)
    ctx = dict(Qt=Qt, Qh=Qh, train=train, heldout=heldout, keyed=keyed, veck=veck)
    parts, plines = v_parts(tree)
    for ln in plines:
        say("  " + ln)
    heldout_ids = sorted(td_["eval_ids"])
    arms = FM.measures(parts, train, heldout, heldout_ids, vec, keyed, veck, names=tuple("V%d" % s for s in range(5)), dim=FG.DIM)
    arms["T"] = arm_from_centroids("T", tr["leaf_mu"], tr["leaf_ids"], ctx)
    z0 = np.asarray(AF.route(tr, X))
    ref = {v: refine(X, z0, tr["leaf_mu"], mask, v, r["t_steps"], r["t_cap"]) for v in ("WP", "GL", "WPA")}
    tkeys = (0,) + tuple(r["t_steps"]) + ("conv",)
    share = {}
    for v in ("WP", "GL"):
        for t in tkeys:
            st = ref[v]["steps"][t]
            nm = "%s_%s" % (v, t)
            arms[nm] = arm_from_centroids(nm, st["C"], tr["leaf_ids"], ctx)
            share[nm] = dict(train=float(np.mean(st["z"] != z0)), heldout=float(np.mean(arms[nm]["filed"] != arms["T"]["filed"])),
                             empty=st["empty"], sizes=np.bincount(st["z"], minlength=k))
    st = ref["WPA"]["steps"][r["t_decide"]]
    nm = "WPA_%d" % r["t_decide"]
    arms[nm] = arm_from_centroids(nm, st["C"], tr["leaf_ids"], ctx)
    share[nm] = dict(train=float(np.mean(st["z"] != z0)), heldout=float(np.mean(arms[nm]["filed"] != arms["T"]["filed"])),
                     empty=st["empty"], sizes=np.bincount(st["z"], minlength=k))
    groups, G = FM.twin_groups([t for t, _ in heldout])
    spread_v = FM.spread([arms["V%d" % s]["m1"] for s in range(5)])
    # IDENTITY (a failed precondition otherwise): T and V0 through this path are the recorded ones
    idn = r["identity"][tree]
    dt = paired_m1(arms["T"]["per1"], arms["V0"]["per1"], groups)
    got = dict(n=len(heldout), t_hits=int(arms["T"]["hits"]), v0_hits=int(arms["V0"]["hits"]), spread="%.4f" % spread_v)
    if tree == DECIDING_TREE:
        got.update(m1=FM.fmt_m1(arms["T"]["sc"]), m2="%+.3f" % (1000 * arms["T"]["m2"]), d_t=ci4(dt))
    bad = [kk for kk in idn if got.get(kk) != idn[kk]]
    if bad:
        refuse("[GF-IDENTITY] %s: %s are not the recorded %s" % (tree, {kk: got.get(kk) for kk in bad}, {kk: idn[kk] for kk in bad}))
    say("  IDENTITY %s: %s -> REPRODUCED" % (tree, ", ".join("%s %s" % (kk, got[kk]) for kk in sorted(got))))
    ga = graph_agreement(td_, z0)
    paired = {}
    for nm in [a for a in arms if a[:3] in ("WP_", "GL_", "WPA")]:
        full = nm.endswith("_%d" % r["t_decide"])
        paired[nm] = dict(v0=paired_m1(arms[nm]["per1"], arms["V0"]["per1"], groups), t=paired_m1(arms[nm]["per1"], arms["T"]["per1"], groups),
                          m2_v0=paired_m2(arms[nm]["per2"], arms["V0"]["per2"], ci=full), m2_t=paired_m2(arms[nm]["per2"], arms["T"]["per2"], ci=full))
    paired["T"] = dict(v0=dt, m2_v0=paired_m2(arms["T"]["per2"], arms["V0"]["per2"], ci=True))
    dec = decide(arms, groups, "WP_%d" % r["t_decide"], r["bar_open"])
    return dict(tree=tree, spec=spec, k=k, n=len(heldout), G=G, mbar=FM.kish_mbar(groups), fit_n=len(td_["texts"]), arms=arms,
                share=share, paired=paired, dec=dec, spread_v=spread_v, ref={v: dict(t_conv=ref[v]["t_conv"], converged=ref[v]["converged"],
                moves=ref[v]["moves"][:12]) for v in ref}, graph=ga, allowed=Counter(int(x) for x in mask.sum(axis=1)),
                root_parent=sum(1 for p in td_["par"] if p in td_["roots"]), z0_sizes=np.bincount(z0, minlength=k), groups=groups)


def sizes_txt(s):
    s = np.asarray(s)
    return "min %d, median %.0f, max %d, empty %d" % (int(s.min()), float(np.median(s)), int(s.max()), int((s == 0).sum()))


def render_a(res):
    r = RA()
    L = ["=== GAP-FIX (a) outcome (%s; zero calls) ===" % REG_TEXT]
    L.append("script %s" % res["script"])
    for t in res["order"]:
        R = res["trees"][t]
        sp = R["spec"]
        L.append("")
        L.append("[%s] pool %s (%s); held-out / EVAL side %d questions in %d stem_key twin groups (Kish %.4f); k %d; fit set %d; keyed %d" % (
            t, sp["pool"], sp["split_word"], R["n"], R["G"], R["mbar"], R["k"], R["fit_n"], len(R["arms"]["T"]["per2"])))
        L.append("  structure: allowed leaves per leaf (WP) %s; leaves whose parent is the root %d; flatLeaf start agrees with the graph's "
                 "leaf region for %d of %d graph-filed fit texts (fit set %d; descriptive)" % (
                     ", ".join("%d: %d" % kv for kv in sorted(R["allowed"].items())), R["root_parent"], R["graph"][0], R["graph"][1], R["graph"][2]))
        L.append("  passes: WP converged %s at t %d; GL converged %s at t %d; WP-A converged %s at t %d; moves per pass (WP) %s" % (
            R["ref"]["WP"]["converged"], R["ref"]["WP"]["t_conv"], R["ref"]["GL"]["converged"], R["ref"]["GL"]["t_conv"],
            R["ref"]["WPA"]["converged"], R["ref"]["WPA"]["t_conv"], R["ref"]["WP"]["moves"]))
        L.append("  leaf sizes on the fit set: as built (flatLeaf) %s; WP T5 %s; GL T5 %s" % (
            sizes_txt(R["z0_sizes"]), sizes_txt(R["share"]["WP_%d" % r["t_decide"]]["sizes"]), sizes_txt(R["share"]["GL_%d" % r["t_decide"]]["sizes"])))
        L.append("  arm      M1 [Wilson 95%]         hits      M2 x1e3   M1 - M1(V0) [twin 95%]       M1 - M1(T) [twin 95%]        "
                 "TRAIN moved  held-out moved  empty")
        for a in ("T",) + tuple("V%d" % s for s in range(5)):
            m = R["arms"][a]
            extra = "  %s" % ci4(R["paired"]["T"]["v0"]) if a == "T" else ""
            L.append("  %-8s %.3f [%.3f, %.3f]  %4d/%d  %+8.3f%s" % (a, m["m1"], m["m1_lo"], m["m1_hi"], m["hits"], R["n"], 1000 * m["m2"], extra))
        for v in ("WP", "GL"):
            for tt in (0,) + tuple(r["t_steps"]) + ("conv",):
                a = "%s_%s" % (v, tt)
                m, p, s = R["arms"][a], R["paired"][a], R["share"][a]
                tag = " (DECIDING)" if (v == "WP" and tt == r["t_decide"] and t == DECIDING_TREE) else ""
                L.append("  %-8s %.3f [%.3f, %.3f]  %4d/%d  %+8.3f  %s  %s  %.4f       %.4f          %d%s" % (
                    a, m["m1"], m["m1_lo"], m["m1_hi"], m["hits"], R["n"], 1000 * m["m2"], ci4(p["v0"]), ci4(p["t"]), s["train"], s["heldout"],
                    s["empty"], tag))
        a = "WPA_%d" % r["t_decide"]
        m, p, s = R["arms"][a], R["paired"][a], R["share"][a]
        L.append("  READING CHECK (not registered; descriptive) %s: M1 %.3f (%d/%d), M1 - M1(V0) %s, M1 - M1(T) %s; TRAIN moved %.4f, "
                 "held-out moved %.4f" % (a, m["m1"], m["hits"], R["n"], ci4(p["v0"]), ci4(p["t"]), s["train"], s["heldout"]))
        wp = R["paired"]["WP_%d" % r["t_decide"]]
        L.append("  M2 at T 5 (descriptive; F6 boot_mean_ci): WP - V0 %+.3f [%+.3f, %+.3f], WP - T %+.3f [%+.3f, %+.3f]; T - V0 %+.3f [%+.3f, %+.3f] x1e-3" % (
            1000 * wp["m2_v0"]["d"], 1000 * wp["m2_v0"]["lo"], 1000 * wp["m2_v0"]["hi"], 1000 * wp["m2_t"]["d"], 1000 * wp["m2_t"]["lo"],
            1000 * wp["m2_t"]["hi"], 1000 * R["paired"]["T"]["m2_v0"]["d"], 1000 * R["paired"]["T"]["m2_v0"]["lo"], 1000 * R["paired"]["T"]["m2_v0"]["hi"]))
        L.append("  spread_V (M1, V0-V4) %.4f" % R["spread_v"])
        if t != DECIDING_TREE:
            d = R["dec"]
            L.append("  DESCRIPTIVE (id-disjoint only; this tree's own V0 and spread_V %.4f): D_R %s, I_R %s, D_T %s; the GF1 rule would read %s "
                     "(not a verdict)" % (R["spread_v"], ci4(d["dr"]), ci4(d["ir"]), ci4(d["dt"]), d["word"]))
    D = res["trees"][DECIDING_TREE]
    dec = D["dec"]
    L.append("")
    L.append("== GF1 (THE ONE DECIDING CRITERION; af_clean_s42, LLOYD-WP, T = 5; points and intervals jointly) ==")
    L.append("  DENOMINATOR: %d held-out questions (p2dca21ab5f4ef3ae judgeable) in %d twin groups" % (D["n"], D["G"]))
    L.append("  D_T = M1(T) - M1(V0) = %s (the recorded -0.0430 [-0.0557, -0.0293])" % ci4(dec["dt"]))
    L.append("  D_R = M1(T-WP) - M1(V0) = %s" % ci4(dec["dr"]))
    L.append("  I_R = D_R - D_T = M1(T-WP) - M1(T) = %s" % ci4(dec["ir"]))
    L.append("  bar for OPEN = max(MDE80 %.4f, spread_V %.4f) = %.4f" % (r["mde_dr"], r["spread_v"], dec["bar"]))
    for ln in gf1_lines(dec):
        L.append(ln)
    L.append("")
    L.append("PREDICTIONS (blind for the refined arms):")
    k5 = "WP_%d" % r["t_decide"]
    pst = dict(share_wp=D["share"][k5]["heldout"], share_gl=D["share"]["GL_%d" % r["t_decide"]]["heldout"], dr=dec["dr"]["d"], ir=dec["ir"]["d"],
               word=dec["word"], d_gl=D["paired"]["GL_%d" % r["t_decide"]]["v0"]["d"], m2_wp_v0=D["paired"][k5]["m2_v0"]["d"],
               m2_t_v0=D["paired"]["T"]["m2_v0"]["d"],
               ir_redraws=[res["trees"][t]["dec"]["ir"]["d"] for t in res["order"] if t != DECIDING_TREE] or None)
    L.extend(predictions_a(pst))
    L.append("")
    L.extend(support_lines_a(D["n"], D["mbar"], dec))
    L.append(WILL_NOT_SHOW_A)
    return L, dec["word"]


def arms_csv_a(res):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["tree", "arm", "M1", "M1_lo", "M1_hi", "hits", "n", "M2_x1000", "d_v0", "d_v0_lo", "d_v0_hi", "d_t", "d_t_lo", "d_t_hi",
                "train_moved", "heldout_moved", "empty", "sizes"])
    for t in res["order"]:
        R = res["trees"][t]
        for a, m in R["arms"].items():
            p, s = R["paired"].get(a, {}), R["share"].get(a)
            pv, pt = p.get("v0"), p.get("t")
            w.writerow([t, a, repr(m["m1"]), repr(m["m1_lo"]), repr(m["m1_hi"]), m["hits"], R["n"], repr(1000 * m["m2"]),
                        "" if pv is None else repr(pv["d"]), "" if pv is None else repr(pv["lo"]), "" if pv is None else repr(pv["hi"]),
                        "" if pt is None else repr(pt["d"]), "" if pt is None else repr(pt["lo"]), "" if pt is None else repr(pt["hi"]),
                        "" if s is None else repr(s["train"]), "" if s is None else repr(s["heldout"]), "" if s is None else s["empty"],
                        "" if s is None else " ".join(str(int(x)) for x in s["sizes"])])
    return buf.getvalue()


def header_a():
    _a_mods()
    FG.header()                               # the pool line FIRST (pool_guard.assert_pool_of_record p2dca21ab5f4ef3ae)
    print("[SCRIPT] tools/analysis/gap_fix.py %s" % fmt_pins(script_pins()))
    for ln in verify_imports("a"):
        print(ln)
    print("[REGISTRATION] %s" % REG_TEXT)


def dry_run_a():
    header_a()
    print("[MODE] --dry-run (a): pins, denominators, structure and cost; NO label of the held-out side, NO measure, nothing written")
    t0 = time.perf_counter()
    pins = FM.table_pins(**FG.pin_kw())
    for kk, v in pins.items():
        print("[PIN table/row/file] %s %s" % (kk, v))
    print("[PIN] %.1f s (taken before and after --run)" % (time.perf_counter() - t0))
    for tree in TREES_A:
        _parts, plines = v_parts(tree)
        td_ = tree_data(tree, labels=False)
        tr = td_["tree"]
        etx = eval_texts_only(td_["eval_ids"])
        exact, stem = FG.hygiene(td_["texts"], etx)
        groups, G = FM.twin_groups(etx)
        print("TREE %s: %s | %d leaves, depth %d, slice %d; pool %s (%d judgeable, registered %d; %s)" % (
            tree, tr["name"], len(tr["leaf_ids"]), tr["depth"], tr["dim"], td_["pid"], len(td_["eval_ids"]), td_["spec"]["eval_n"],
            td_["spec"]["split_word"]))
        print("  FIT SET %d root texts (ASSERTED %d); fit texts equal to an EVAL text %d (asserted 0); sharing an EVAL stem_key %d; "
              "EVAL texts %d in %d stem_key twin groups (Kish %.4f)" % (len(td_["texts"]), td_["spec"]["fit_n"], exact, stem, len(etx), G,
                                                                       FM.kish_mbar(groups)))
        print("  WP allowed leaves per leaf: %s; leaves whose parent is the root %d" % (
            ", ".join("%d: %d" % kv for kv in sorted(Counter(int(x) for x in td_["mask"].sum(axis=1)).items())),
            sum(1 for p in td_["par"] if p in td_["roots"])))
        for ln in plines:
            print("  " + ln)
    keyed = F.keyed_questions()
    print("KEYED (F6): %d questions, %d models (M2's unit)" % (len(keyed[4]), len(keyed[0])))
    r = RA()
    print("PLAN: per tree, V0-V4 READ from their pinned state; T as built; LLOYD-WP and LLOYD-GL at T = 0, %s and convergence (cap %d); "
          "WP-A at T %d (reading check); M1 / M2 per arm through flat_mix_mmlu (m1_block, m2_block); twin-group intervals (B %d, seed %d); "
          "F6 CI at T %d (B %d, seed 42)" % (", ".join(str(x) for x in r["t_steps"]), r["t_cap"], r["t_decide"], FM.BOOT_B, FM.BOOT_SEED,
                                             r["t_decide"], F.B))
    rng = np.random.default_rng(1)
    Xs = FM.unit_rows(rng.standard_normal((8125, FG.DIM)))
    mu = FM.unit_rows(rng.standard_normal((82, FG.DIM)))
    z0 = np.argmax(Xs @ mu.T, axis=1)
    t0 = time.process_time()
    refine(Xs, z0, mu, np.ones((82, 82), dtype=bool), "GL", (1, 2, 5), 5)
    per = (time.process_time() - t0) / 5
    print("COST (SYNTHETIC timing, n 8125 x %d, k 82): %.3f CPU-s per pass -> <= %.1f CPU-min for 3 variants x 4 trees at the cap %d "
          "(convergence is expected far below it); plus about 18 arms x 4 trees through m1_block / m2_block and the bootstraps "
          "(registered: CPU under 1 h)" % (FG.DIM, per, per * 3 * 4 * r["t_cap"] / 60, r["t_cap"]))
    print("%s dry-run (a) complete: zero measures on real data, nothing written" % TAG)
    return 0


def run_a():
    header_a()
    outp, csvp = out_paths_a()
    for p in (outp, csvp):
        if os.path.exists(p):
            refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    before = FM.table_pins(**FG.pin_kw())
    for kk, v in before.items():
        print("[PIN before] %s %s" % (kk, v))
    keyed = F.keyed_questions()
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), FG.DIM)
    res = dict(order=list(TREES_A), trees={}, script=fmt_pins(script_pins()))
    for tree in TREES_A:
        print("%s tree %s ..." % (TAG, tree))
        res["trees"][tree] = run_tree_a(tree, keyed, veck, print)
    L, word = render_a(res)
    txt = "\n".join(L) + "\n"
    FM.check_pins_after(before, **FG.pin_kw())
    sh = write_once(outp, txt)
    sh2 = write_once(csvp, arms_csv_a(res))
    print(txt)
    print("%s wrote %s (sha256 %s) and %s (sha256 %s), write-once; never committed: back up to E:/TaxoArena_backup_<date>_gap_fix with "
          "SHA256SUMS.txt" % (TAG, outp, sh, csvp, sh2))
    LAST_A.clear()
    LAST_A.update(res=res, word=word, text=txt)
    return 0


LAST_A = {}


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# (b) SOURCE-GATED FILING (descriptive)
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
REG_B = dict(
    B=2000, seed=42, moved_rec=191,
    identity=dict(ki_d="-0.024800", ki_lo="-0.043451", ki_hi="-0.006149", ki_spread="0.017640",
                  u2_dk="-0.45pp", u2_lo="-1.31pp", u2_hi="+0.41pp", u2_spread="+0.58pp",
                  rp_d="-0.004423", rp_spread="0.000861"),
    outcome="gap_fix_b_outcome.txt", marker="gap_fix_b.READ_STARTED",
)
_REGB = [REG_B]
PRED_B = dict(ki=(-0.020, -0.005), rp=(-0.0035, -0.0005), u2=(-0.0080, 0.0010))
RSC = RPI = KI = URC = UAR = V = UCI = None   # set by _b_mods() (lazy: part (b) only)


def RB():
    return _REGB[0]


def _b_mods():
    global RSC, RPI, KI, URC, UAR, V, UCI
    if RPI is None:
        verify_imports("b")
        import key_info_v2 as _KI              # noqa: E402  (pins union_route_common -> escalation_rc, union_cells_io, union_af_route)
        import resp_profile_info as _RPI       # noqa: E402  (pins resp_structure_common -> union_cells_io, cell_flips, ...)
        KI, RPI = _KI, _RPI
        URC, RSC = _KI.U, _RPI.RSC
        UAR, V, UCI = URC.UAR, URC.V, _RPI.U
    return RPI


def f6_(x):
    return "%+.6f" % x


def gate_core(af, eval_items, vec, leaf_ids, M, leaf_src, item_srcs, single_cells, no_row=()):
    """R-B1 / R-B2: {item: cell} with every EVAL item re-filed to its nearest leaf among its OWN declared source(s)' leaves; TRAIN
    and other items unchanged. single_cells {source: cell} (one-cell members, filed by source already). -> (gated, counts)."""
    gated = dict(af)
    cnt = Counter()
    single_of = {c: s for s, c in single_cells.items()}
    leaf_src = np.asarray(leaf_src)
    for it in sorted(eval_items):
        cell = af.get(it)
        if cell is None or cell in no_row:
            cnt["no_row"] += 1
            continue
        ss = item_srcs.get(it)
        if not ss:
            refuse("[GF-GATE] EVAL item %s has no declared source in the routing rows" % it)
        if cell in single_of:
            if set(ss) != {single_of[cell]}:
                refuse("[GF-GATE] EVAL item %s sits in the one-cell %s but declares %s" % (it, cell, ss))
            cnt["one_cell"] += 1
            continue
        if any(s in single_cells for s in ss):
            refuse("[GF-GATE] EVAL item %s declares a one-cell source beside a multi-leaf one (%s): no centroid for the one cell" % (it, ss))
        if it not in vec:
            refuse("[GF-GATE] EVAL item %s has a routing row but no vector" % it)
        s_all = M @ vec[it]
        j_all = int(np.argmax(s_all))
        if leaf_ids[j_all] != cell:
            refuse("[GF-IDENTITY-FILING] EVAL item %s: the nearest leaf over all grafted leaves is %s, AF-U recorded %s" % (it, leaf_ids[j_all], cell))
        allowed = np.isin(leaf_src, list(ss))
        if not allowed.any():
            refuse("[GF-GATE] EVAL item %s: its declared source(s) %s have no leaf" % (it, ss))
        j = int(np.flatnonzero(allowed)[np.argmax(s_all[allowed])])
        gated[it] = leaf_ids[j]
        cnt["gated"] += 1
        if gated[it] != cell:
            cnt["moved"] += 1
            cnt["moved:" + "+".join(ss)] += 1
    return gated, cnt


def eval_side_items(af, side):
    """The items re-filed: EVAL side (the side export) AND an AF-U cell row; TRAIN and GATE never."""
    return sorted(it for it, (_c, s) in side.items() if s == "EVAL" and it in af)


def afu_gate(af, say):
    """The real gating: AF-U's member snapshots (leaf vmfMu), the routing rows' declared sources, union_af_route._TV vectors."""
    c = UAR.reg()
    _pairs, val, _ksrc, _commit, single = UAR.afu_state(say)
    ids, mus, srcs = [], [], []
    for m, s in c["members"]:
        if s in single:
            continue
        snap = UAR.GB.last_snapshot(UAR.P("%s/%s/seed_42/dag_snapshots.jsonl" % (c["afu"], m)))
        for n in snap["nodes"]:
            if n.get("isLeaf"):
                if len(n["vmfMu"]) != c["dim"]:
                    refuse("[GF-GATE] leaf %s:%s vmfMu has %d dims, not %d" % (s, n["id"], len(n["vmfMu"]), c["dim"]))
                ids.append("%s:%s" % (s, n["id"]))
                mus.append(n["vmfMu"])
                srcs.append(s)
    M = np.asarray(mus, dtype=np.float64)
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    single_cells = {s: e["cell"] for s, e in single.items()}
    vdir = UAR.input_paths()["merged"] if single else val
    rows = UAR.RP.read_rows(os.path.join(UAR.P(vdir), UAR.RP.QUERIES)) + UAR.RP.read_rows(os.path.join(UAR.P(vdir), UAR.RP.TRAIN))
    item_srcs = UAR.item_sources(rows)
    side, smeta = UAR._SIDES[0]()
    evi = eval_side_items(af, side)
    need = [it for it in evi if af[it] not in (UAR.NO_ROW, UAR.UNROUTED) and af[it] not in single_cells.values()]
    vec = UAR._TV[0](need, c["dim"])
    gated, cnt = gate_core(af, evi, vec, ids, M, srcs, item_srcs, single_cells, no_row=(UAR.NO_ROW, UAR.UNROUTED))
    say("%s GATING (R-B1): %d grafted leaves from the member snapshots (%s) + one-cell %s; %d EVAL-side items with an AF-U row (side "
        "export %s); re-filed within own source %d, one-cell kept %d, no row %d; ungated nearest leaf == AF-U's recorded cell for every "
        "re-filed item (R-B2 IDENTITY); cells changed %d (%s)" % (
            TAG, len(ids), ", ".join("%s %d" % (s, srcs.count(s)) for s in sorted(set(srcs))), sorted(single_cells.values()), len(evi),
            smeta.get("sha256_lf", "?")[:16], cnt["gated"], cnt["one_cell"], cnt["no_row"], cnt["moved"],
            ", ".join("%s %d" % (k_[6:], v) for k_, v in sorted(cnt.items()) if k_.startswith("moved:")) or "none"))
    return gated, cnt


def out_paths_b(root, out_dir=None):
    d = out_dir if out_dir is not None else os.path.join(root, *OUT_REL.split("/"))
    return os.path.join(d, RB()["outcome"]), os.path.join(d, RB()["marker"])


def ki_boot(D):
    """run_boot (G14's two-stage reader, B, seed) with KEY-INFO-V2's hook: per replicate every arm's KI on the replicate's TRAIN
    multiplicities and EVAL component weights. -> (bt, {arm: [KI_b]}, groupings)."""
    arms = [("AF-U", "tree")] + [("K_s %s" % nm, "x:" + nm) for nm in URC.KNAMES]
    G_ = {name: D.groupings[key] for name, key in arms}
    AT, AE = D.A[D.T], D.A[D.E]
    rec = {name: [] for name, _k in arms}

    def hook(D_, wt, v):
        v = np.asarray(v, dtype=np.float64)
        wtt = wt[D_.T]
        for name, _k in arms:
            g, ng = G_[name]
            t, _p, _m = KI.ki_terms(AT, g[D_.T], wtt, AE, g[D_.E], ng)
            rec[name].append(float(v @ t) / v.sum())
    bt = V.run_boot(D, RB()["B"], RB()["seed"], hook=hook)
    return bt, rec, G_


def ki_stats(D, rec, G_):
    """KI1's form (key_info_v2 R1 / R3): D = KI(AF-U) - mean_s KI(K_s) at the point (ki_terms, unit TRAIN weights); interval
    union_route_common.interval(point, two-stage, i.i.d.); spread_K = max - min of the five K_s points."""
    AT, AE = D.A[D.T], D.A[D.E]
    ones = np.ones(len(D.T))
    terms = {}
    for name, (g, ng) in G_.items():
        t, _p, _m = KI.ki_terms(AT, g[D.T], ones, AE, g[D.E], ng)
        terms[name] = t
    kn = ["K_s %s" % nm for nm in URC.KNAMES]
    dt = terms["AF-U"] - np.mean([terms[k] for k in kn], axis=0)
    two = np.asarray(rec["AF-U"]) - np.mean([rec[k] for k in kn], axis=0)
    iid = [float(v @ dt) / v.sum() for v in URC.iid_weights(RB()["seed"], len(D.E), RB()["B"])]
    d = URC.interval(float(dt.mean()), two, iid, len(D.E))
    kk = [float(terms[k].mean()) for k in kn]
    return dict(d=d, spread=max(kk) - min(kk), ki={name: float(t.mean()) for name, t in terms.items()}, terms=terms, two=two)


def rp_point(D, I, arms):
    pt, _sh, _x = RPI.point_stats(D, I, arms)
    ks = [pt[k]["r2"] for k in RSC.KNAMES]
    return dict(d=pt["AF-U"]["r2"] - float(np.mean(ks)), spread=float(max(ks) - min(ks)), pt=pt)


def identity_b(ki0, u0, rp0):
    got = dict(ki_d=f6_(ki0["d"]["point"]), ki_lo=f6_(ki0["d"]["lo"]), ki_hi=f6_(ki0["d"]["hi"]), ki_spread="%.6f" % ki0["spread"],
               u2_dk=UAR.pp(u0["DK"]["point"]), u2_lo=UAR.pp(u0["DK"]["lo"]), u2_hi=UAR.pp(u0["DK"]["hi"]), u2_spread=UAR.pp(u0["spread_K"]),
               rp_d=f6_(rp0["d"]), rp_spread="%.6f" % rp0["spread"])
    want = RB()["identity"]
    bad = [k for k in want if got[k] != want[k]]
    return (not bad), got, bad


def render_b(st):
    L = ["=== GAP-FIX (b) SOURCE-GATED FILING (DESCRIPTIVE in full; %s; zero calls) ===" % REG_TEXT]
    L.append("DENOMINATOR: %d EVAL items in %d components (Kish %.3f); %d models; TRAIN %d scored items; B %d two-stage replicates "
             "(default_rng(%d))" % (st["n"], st["comp"], st["kish"], st["m"], st["n_train"], RB()["B"], RB()["seed"]))
    L.append("GATED FILING: %d of the %d scored EVAL items change cell (R-KI1 recorded %d cross-source filings: %s); by source %s; TRAIN cells "
             "unchanged (checked)" % (st["moved"], st["n"], RB()["moved_rec"], "equal" if st["moved"] == RB()["moved_rec"] else "DIFFERENT",
                                      st["moved_by_src"]))
    k, u, r = st["ki"], st["u2"], st["rp"]
    L.append("KI1 re-read (KEY-INFO-V2's form; DESCRIPTIVE): D = KI(AF-U gated) - mean_s KI(K_s) = %s | two-stage 95%% [%s, %s]; spread_K "
             "%.6f; SE_2stage %.6f, DEFF %.3f, n_eff %.0f, MDE80 %.6f; KI(AF-U gated) %+.6f (as built %+.6f)" % (
                 f6_(k["d"]["point"]), f6_(k["d"]["lo"]), f6_(k["d"]["hi"]), k["spread"], k["d"]["se2"], k["d"]["deff"], k["d"]["n_eff"],
                 k["d"]["mde"], k["ki"]["AF-U"], st["ki0"]["ki"]["AF-U"]))
    L.append("  KI1's rule would read %s (descriptive; not a registered verdict)" % KI.ki1_verdict(k["d"], k["spread"]))
    L.append("RP2 re-read (RESP-PROFILE-INFO's form; DESCRIPTIVE): D = R2_int(AF-U gated) - mean R2_int(K_s) = %s | two-stage 95%% [%s, %s] "
             "(SE %.6f; each replicate re-fits the 3PL; non-converged replicates %d of %d); spread_K %.6f; DEFF %.3f; R2_int(AF-U gated) %s "
             "(as built %s)" % (f6_(r["d"]), f6_(r["lo"]), f6_(r["hi"]), r["se2"], r["nonconv"], r["fits"], r["spread"], r["deff"],
                                f6_(r["pt"]["AF-U"]["r2"]), f6_(st["rp0"]["pt"]["AF-U"]["r2"])))
    L.append("  RP2's rule would read %s (descriptive; not a registered verdict)" % RPI.rp2_word(r["d"], r["lo"], r["hi"], r["spread"]))
    L.append("U2 re-read (UNION-AF-ROUTE's form; DESCRIPTIVE): D_K = G_AF(gated) - G_K = %s | two-stage [%s, %s]; spread_K %s; MDE80 %s; "
             "G_AF(gated) %s [%s, %s] (as built %s); without BBH D_K %s [%s, %s]" % (
                 UAR.pp(u["DK"]["point"]), UAR.pp(u["DK"]["lo"]), UAR.pp(u["DK"]["hi"]), UAR.pp(u["spread_K"]), UAR.pp(u["DK"]["mde"]),
                 UAR.pp(u["G"]["point"]), UAR.pp(u["G"]["lo"]), UAR.pp(u["G"]["hi"]), UAR.pp(st["u0"]["G"]["point"]),
                 UAR.pp(st["dk_nobbh"]["point"]), UAR.pp(st["dk_nobbh"]["lo"]), UAR.pp(st["dk_nobbh"]["hi"])))
    L.append("  U2's rule would read %s (descriptive; not a registered verdict)" % UAR.u2_verdict(u["DK"], u["spread_K"]))
    L.append("PREDICTION P7 (descriptive, (b); informed by seen subsets, scored and not credited as blind):")
    L.append("  gated KI1 D %s, band [-0.020, -0.005] -> %s" % (f6_(k["d"]["point"]), hw(k["d"]["point"], PRED_B["ki"])))
    L.append("  gated RP2 D %s, band [-0.0035, -0.0005] -> %s" % (f6_(r["d"]), hw(r["d"], PRED_B["rp"])))
    L.append("  gated U2 D_K %s, band [-0.80pp, +0.10pp] -> %s" % (UAR.pp(u["DK"]["point"]), hw(u["DK"]["point"], PRED_B["u2"])))
    L.append("LIKE WITH LIKE: AF-U gated [SC] (legitimate only when the source is known at query time) | K_s [SC], filed by source as "
             "registered; the D-4 filing asymmetry is removed by construction here. Never a label-free filing.")
    L.append("WHAT THIS RESULT WILL NOT SHOW (registered): any registered verdict (seen subset data); a label-free filing; routing beyond U2.")
    return L


def header_b(root, say, dry, outs):
    _b_mods()
    pol, af, kx = RSC.prelude(root, say, TAG, TEST_ID + " (b)", REG_TEXT, [os.path.abspath(__file__)], outs, dry)   # POOL line first
    for ln in verify_imports("b"):
        say("%s %s" % (TAG, ln))
    return pol, af, kx


def dry_run_b(root, out_dir=None, out=print, gate_fn=None):
    outp, mark = out_paths_b(root, out_dir)
    pol, af, kx = header_b(root, out, True, [outp, mark])
    gated, _cnt = (gate_fn or afu_gate)(af, out)
    _models, _ntr, E = RSC.dry_structure(root, out, TAG, pol, gated, kx)
    moved = sum(1 for i in E["items"] if gated.get(i) != af.get(i))
    out("%s DRY-RUN (b): gated cells of the %d-item EVAL set (structure only): %d change cell (R-KI1 recorded %d); no key column selected "
        "(both tripwires sealed); no statistic; nothing written. PLANNED: one TRAIN key read, one EVAL key read (B1 marker %s), two "
        "run_boot (B %d, default_rng(%d)) with KEY-INFO-V2's hook (as built: the identity; gated), RESP-PROFILE-INFO's boot on the gated "
        "D (the 3PL re-fitted per replicate: about 1 CPU-h, launch detached)" % (TAG, len(E["items"]), moved, RB()["moved_rec"], mark,
                                                                                RB()["B"], RB()["seed"]))
    return 0


def run_b(root, out_dir=None, out=print, gate_fn=None):
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    outp, mark = out_paths_b(root, out_dir)
    pol, af, kx = header_b(root, say, False, [outp, mark])
    gated, _gcnt = (gate_fn or afu_gate)(af, say)                # cells fixed BEFORE any key is read
    models, tmeta, cstr, K_tr, _n = RSC.read_train(root, say, TAG, pol["roster"], True)
    E = UCI.eval_set(root, say, TAG, roster=pol["roster"], key=True, marker=mark)
    D0 = RSC.build(models, tmeta, E, K_tr, cstr, af, kx, pol, TAG)
    D1 = RSC.build(models, tmeta, E, K_tr, cstr, gated, kx, pol, TAG)
    if D0.items != D1.items or not np.array_equal(D0.A, D1.A):
        refuse("[GF-D] the gated D's items or key differ from the as-built D's")
    c0 = [D0.tree_keys[D0.g_tree[k_]] for k_ in range(D0.n)]
    c1 = [D1.tree_keys[D1.g_tree[k_]] for k_ in range(D1.n)]
    tbad = [D0.items[k_] for k_ in D0.T if c0[k_] != c1[k_]]
    if tbad:
        refuse("[GF-TRAIN] %d TRAIN item(s) changed cell under the gating (first %s): TRAIN policies must be unchanged" % (len(tbad), tbad[:3]))
    moved_pos = [k_ for k_ in D0.E if c0[k_] != c1[k_]]
    by_src = Counter(D0.src[k_] for k_ in moved_pos)
    RSC.b3_identity(D0, pol, say, TAG)
    I = RSC.irt_point(D0, say, TAG)
    arms0, arms1 = RSC.arms_of(D0), RSC.arms_of(D1)
    bt0, rec0, G0 = ki_boot(D0)
    ki0 = ki_stats(D0, rec0, G0)
    u0 = UAR.u_stats(bt0, D0, None)
    rp0 = rp_point(D0, I, arms0)
    ok, got, bad = identity_b(ki0, u0, rp0)
    if not ok:
        refuse("[GF-IDENTITY-B] as built: %s are not the recorded %s" % ({k_: got[k_] for k_ in bad}, {k_: RB()["identity"][k_] for k_ in bad}))
    say("%s IDENTITY (as built, the same readers): KI1 D %s [%s, %s] spread_K %s; U2 D_K %s [%s, %s] spread_K %s; RP2 D %s spread_K %s "
        "-> REPRODUCED" % (TAG, got["ki_d"], got["ki_lo"], got["ki_hi"], got["ki_spread"], got["u2_dk"], got["u2_lo"], got["u2_hi"],
                           got["u2_spread"], got["rp_d"], got["rp_spread"]))
    bt1, rec1, G1 = ki_boot(D1)
    ki1 = ki_stats(D1, rec1, G1)
    f6 = KI.ki_f6(D1, G1["AF-U"][0])
    if abs(f6 - ki1["ki"]["AF-U"]) > 1e-9:
        refuse("[GF-F6] gated AF-U: ki_terms %+.9f differs from free_tests_f4_f7.loo_imp x M %+.9f" % (ki1["ki"]["AF-U"], f6))
    u1 = UAR.u_stats(bt1, D1, None)
    nk = len(D1.xnames)
    wd = {V.TREE + 1 + i: -1.0 / nk for i in range(nk)}
    wd[V.TREE] = 1.0
    dk_nobbh = UAR.lin(bt1, D1, "NON_BBH", wd)
    rp1 = rp_point(D1, I, arms1)
    btr, recr = RPI.boot(D1, I, arms1)
    if not np.array_equal(btr["two"], bt1["two"]):
        refuse("[GF-BOOT] RESP-PROFILE-INFO's run_boot replicates differ from KEY-INFO-V2's on the same gated D (same B, seed)")
    two = np.asarray(recr["D"])
    iid = RPI.iid_D(D1, I, arms1)
    v2, vi = V._var(two), V._var(iid)
    se2 = math.sqrt(v2)
    rp1.update(lo=rp1["d"] - 1.96 * se2, hi=rp1["d"] + 1.96 * se2, se2=se2, deff=(v2 / vi) if vi > 0 else float("nan"),
               nonconv=recr["nonconv"], fits=recr["fits"], two=two)
    st = dict(n=len(D1.E), comp=D1.eval_units["n_units"], kish=URC.kish_eval(D1), m=len(D1.models), n_train=len(D1.T), moved=len(moved_pos),
              moved_by_src=", ".join("%s %d" % kv for kv in sorted(by_src.items())) or "none", ki=ki1, ki0=ki0, u2=u1, u0=u0, rp=rp1, rp0=rp0,
              dk_nobbh=dk_nobbh)
    for ln in render_b(st):
        say(ln)
    text = "\n".join(lines) + "\n"
    sh = write_once(outp, text)
    out("%s OUTCOME written write-once: %s (sha256 %s; never committed)" % (TAG, outp, sh))
    LAST_B.clear()
    LAST_B.update(st=st, text=text, D0=D0, D1=D1, bt1=bt1)
    return st, text


LAST_B = {}


# ══ SELFTEST (fixtures and independent oracles; the mutants edit only the code ABOVE this line) ══════════════════════════
class Checks(object):
    def __init__(self, quiet=False):
        self.n, self.quiet = 0, quiet

    def ok(self, cond, what):
        self.n += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not self.quiet:
            print("  ok  " + what)


def _refused(fn, needle):
    try:
        fn()
    except SystemExit as e:
        return needle in str(e), str(e)
    return False, "no refusal"


def _capture(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            r = fn(*a, **k)
        except SystemExit as e:
            r = "SystemExit: %s" % e
    return r, buf.getvalue()


def _line(text, prefix):
    for ln in text.splitlines():
        if ln.startswith(prefix):
            return ln
    raise AssertionError("no line starting with %r" % prefix)


# ── (a) oracles: plain loops, written without refine / centroids / lloyd_step / m1_block / score_cells ─────────────────────
def o_parent_sets(nodes, leaf_ids):
    byid = {n["id"]: n for n in nodes}
    par = {}
    for n in nodes:
        for c in n.get("childIds") or []:
            par[c] = n["id"]

    def leaves_under(v):
        n = byid[v]
        if n.get("isLeaf"):
            return [v]
        out = []
        for c in n.get("childIds") or []:
            out += leaves_under(c)
        return out
    return [set(leaf_ids.index(x) for x in leaves_under(par[l])) for l in leaf_ids]


def o_mean_dir(rows):
    s = np.zeros(len(rows[0]))
    for r in rows:
        s = s + r
    return s / np.linalg.norm(s)


def o_lloyd(X, z0, mu0, psets, variant, T):
    n, k = X.shape[0], len(mu0)
    z, C = list(int(v) for v in z0), [np.array(m, dtype=np.float64) for m in mu0]

    def recentre(z_, C_):
        out = []
        for j in range(k):
            mem = [X[i] for i in range(n) if z_[i] == j]
            out.append(o_mean_dir(mem) if mem else C_[j])
        return out
    for _t in range(T):
        C = recentre(z, C)
        zn = []
        for i in range(n):
            allowed = range(k) if variant == "GL" else (psets[z[i]] if variant == "WP" else psets[int(z0[i])])
            best, bs = None, None
            for j in sorted(allowed):
                s = float(X[i] @ C[j])
                if bs is None or s > bs:
                    best, bs = j, s
            zn.append(best)
        z = zn
    return z, np.array(recentre(z, C))


def o_nearest(Q, C):
    C = np.asarray(C, dtype=np.float64)
    C = C / np.linalg.norm(C, axis=1, keepdims=True)
    return [int(np.argmax(C @ q)) for q in Q]


def o_score(cell_t, cell_h, train, heldout):
    counts = {}
    for c, (_t, lab) in zip(cell_t, train):
        counts.setdefault(c, {})
        counts[c][lab] = counts[c].get(lab, 0) + 1
    major = {}
    for c, d in counts.items():
        best, bc = None, -1
        for lab, v in d.items():
            if v > bc:
                best, bc = lab, v
        major[c] = best
    return np.array([1.0 if major.get(c) == lab else 0.0 for c, (_t, lab) in zip(cell_h, heldout)])


def _write_tree(rd, nodes):
    with open(os.path.join(rd, "dag_snapshots.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(dict(iteration=1, nodes=nodes)) + "\n")


def _leaf(i, mu, parent, depth):
    return dict(id="L%d" % i, depth=depth, isLeaf=True, vmfMu=[float(x) for x in mu], sliceDim=len(mu), childIds=[], label="leaf %d" % i,
                parentIds=[parent])


def _inner(nid, children, parent, depth, dim):
    return dict(id=nid, depth=depth, isLeaf=False, vmfMu=[1.0] + [0.0] * (dim - 1), sliceDim=dim, childIds=children, label=nid,
                parentIds=[] if parent is None else [parent])


def _nearest_body(X, C, name="V0"):
    C = FM.unit_rows(np.asarray(C, dtype=np.float64))
    lab = FM.nearest_assign(X, C)
    return dict(FM.m4_refit(X, lab, len(C)), rule="nearest", centers=C.tolist(), partition=name, script=script_pins())


@contextlib.contextmanager
def _a_env(td, rep):
    saved = dict(TREES=FG.TREES, IDENTITY=FG.IDENTITY, DIM=FG.DIM, DR=FM.DATA_ROOT, B=F.B, REG=_REGA[0])
    try:
        FG.TREES, FG.IDENTITY, FG.DIM = {t: dict(s) for t, s in rep["trees"].items()}, dict(rep["identity"]), 16
        FM.DATA_ROOT, F.B = td, 200
        with FG._replica_env(td, rep):
            yield
    finally:
        FG.TREES, FG.IDENTITY, FG.DIM, FM.DATA_ROOT, F.B, _REGA[0] = (saved["TREES"], saved["IDENTITY"], saved["DIM"], saved["DR"],
                                                                     saved["B"], saved["REG"])


def _a_data(tree):
    spec = spec_of(tree)
    texts = FM.fit_set(snapshot=spec["snapshot"], fit_n=spec["fit_n"])[0]
    X = FM.fit_matrix(texts, dim=FG.DIM)
    _pid, ids = FG.tree_pool(spec)
    train, heldout, _c = FG.corpus_for(spec, ids)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    Qt, Qh = AF.sliced(vec, [t for t, _ in train], FG.DIM), AF.sliced(vec, [t for t, _ in heldout], FG.DIM)
    return dict(spec=spec, X=X, texts=texts, train=train, heldout=heldout, Qt=Qt, Qh=Qh, groups=FM.twin_groups([t for t, _ in heldout])[0])


def _a_variant_tree(td, variant, A):
    """Rewrite af_clean_s42's run-dir tree for a verdict fixture. -> (V0 centres, the tree's nodes)."""
    spec = FG.IDENTITY
    rd = os.path.join(td, spec["run"])
    X, d = A["X"], FG.DIM
    if variant == "closed":
        # junk leaves (all near one direction) under a three-level tree with a leaf directly under the root
        u = FM.unit_rows(np.random.default_rng(5).standard_normal((1, d)))[0]
        mus = FM.unit_rows(u[None, :] + 1e-3 * np.random.default_rng(6).standard_normal((6, d)))
        nodes = [_inner("R", ["D0", "L3", "D1"], None, 0, d), _inner("D0", ["L0", "N1"], "R", 1, d), _inner("N1", ["L1", "L2"], "D0", 2, d),
                 _inner("D1", ["L4", "L5"], "R", 1, d), _leaf(0, mus[0], "D0", 2), _leaf(1, mus[1], "N1", 3), _leaf(2, mus[2], "N1", 3),
                 _leaf(3, mus[3], "R", 1), _leaf(4, mus[4], "D1", 2), _leaf(5, mus[5], "D1", 2)]
        _write_tree(rd, nodes)
        spec["leaves"] = 6
        tr = FG.load_tree(DECIDING_TREE, spec)
        z0 = o_nearest(X, tr["leaf_mu"])
        _z, Cf = o_lloyd(X, z0, tr["leaf_mu"], o_parent_sets(nodes, tr["leaf_ids"]), "WP", RA()["t_decide"])
        return Cf, nodes
    # PARTIAL / OPEN: a two-leaf tree at its own Lloyd fixed point (both leaves under the root)
    rng = np.random.default_rng(9)
    C = FM.kmeanspp(X, 2, rng)
    z = o_nearest(X, C)
    for _ in range(200):
        C = np.array([o_mean_dir([X[i] for i in range(len(X)) if z[i] == j]) for j in range(2)])
        z2 = o_nearest(X, C)
        if z2 == z:
            break
        z = z2
    nodes = [_inner("R", ["L0", "L1"], None, 0, d), _leaf(0, C[0], "R", 1), _leaf(1, C[1], "R", 1)]
    _write_tree(rd, nodes)
    spec["leaves"] = 2
    if variant == "partial":
        return C, nodes
    # OPEN: V0 = the replica's nine latent themes (the theme is in the replica text), a far purer partition than two cells
    import re
    th = [int(re.search(r"on theme (\d+)\?", t).group(1)) for t in A["texts"]]
    return np.array([o_mean_dir([X[i] for i in range(len(X)) if th[i] == c]) for c in sorted(set(th))]), nodes


def _a_states(td, variant):
    """V0-V4 state files for every tree (EM through flat_mix_mmlu.fit_partition at the tree's k; V0 replaced in a verdict variant),
    their pins and the identity constants (oracle). -> (reg swap, per-tree oracle inputs)."""
    vs, idn, info = {}, {}, {}
    for tree in TREES_A:
        A = _a_data(tree)
        nodes, v0c = None, None
        if tree == DECIDING_TREE and variant != "default":
            v0c, nodes = _a_variant_tree(td, variant, A)
        spec = spec_of(tree)
        bodies = [FM.fit_partition("V%d" % s, A["X"], k=spec["leaves"]) for s in range(5)]
        if v0c is not None:
            bodies[0] = _nearest_body(A["X"], v0c)
        rel = "vstate/%s" % tree
        os.makedirs(os.path.join(td, rel), exist_ok=True)
        shas = []
        for s, b in enumerate(bodies):
            p = os.path.join(td, rel, "part_V%d.json" % s)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(b, sort_keys=True))
            shas.append(sha256_file(p))
        vs[tree] = (rel, tuple(shas))
        tr = FG.load_tree(tree, spec)
        hT = o_score(o_nearest(A["Qt"], tr["leaf_mu"]), o_nearest(A["Qh"], tr["leaf_mu"]), A["train"], A["heldout"])
        hV = [o_score(FM.partition_assign(b, A["Qt"]), FM.partition_assign(b, A["Qh"]), A["train"], A["heldout"]) for b in bodies]
        n = len(A["heldout"])
        accs = [h.mean() for h in hV]
        d = dict(n=n, t_hits=int(hT.sum()), v0_hits=int(hV[0].sum()), spread="%.4f" % (max(accs) - min(accs)))
        if tree == DECIDING_TREE:
            from t3_routing_inflation import wilson
            lo, hi = wilson(int(hT.sum()), n)
            d["m1"] = "%.3f [%.3f, %.3f]" % (hT.mean(), lo, hi)
            fn = (lambda tr_: (lambda Q: [tr_["leaf_ids"][i] for i in o_nearest(Q, tr_["leaf_mu"])]))(tr)
            keyed = F.keyed_questions()
            veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), FG.DIM)
            d["m2"] = "%+.3f" % (1000 * FM.m2_block(fn, keyed, veck)["mean"])
            dd = hT - hV[0]
            lo_, hi_ = FM.twin_boot_ci(dd, A["groups"])
            d["d_t"] = "%+.4f [%+.4f, %+.4f]" % (dd.mean(), lo_, hi_)
        idn[tree] = d
        info[tree] = dict(A=A, tr=tr, hT=hT, hV=hV, nodes=nodes, bodies=bodies)
    return dict(RA(), v_state=vs, identity=idn), info


def _a_oracle_decide(info, t=None):
    """GF1's inputs by the oracle on af_clean_s42: WP at T (default 5), GL at T, held-out shares, D_R / I_R / D_T with intervals."""
    t = RA()["t_decide"] if t is None else t
    I = info[DECIDING_TREE]
    A, tr = I["A"], I["tr"]
    nodes = I["nodes"]
    if nodes is None:
        with open(os.path.join(FM.DATA_ROOT, FG.IDENTITY["run"], "dag_snapshots.jsonl"), encoding="utf-8") as f:
            nodes = json.loads([ln for ln in f if ln.strip()][-1])["nodes"]
    ps = o_parent_sets(nodes, tr["leaf_ids"])
    z0 = o_nearest(A["X"], tr["leaf_mu"])
    out = {}
    for v in ("WP", "GL"):
        z, Cf = o_lloyd(A["X"], z0, tr["leaf_mu"], ps, v, t)
        h = o_score(o_nearest(A["Qt"], Cf), o_nearest(A["Qh"], Cf), A["train"], A["heldout"])
        moved_h = float(np.mean(np.array(o_nearest(A["Qh"], Cf)) != np.array(o_nearest(A["Qh"], tr["leaf_mu"]))))
        out[v] = dict(h=h, moved_h=moved_h, moved_t=float(np.mean(np.array(z) != np.array(z0))))

    def ci(d):
        lo, hi = FM.twin_boot_ci(d, A["groups"])
        return dict(d=float(np.mean(d)), lo=float(lo), hi=float(hi))
    hW, hT, hV = out["WP"]["h"], I["hT"], I["hV"][0]
    dr, ir, dt = ci(hW - hV), ci(hW - hT), ci(hT - hV)
    word = ("CLOSED" if (dr["hi"] >= 0 and ir["d"] > 0 and ir["lo"] > 0) else
            "OPEN" if (dr["hi"] < 0 and abs(dr["d"]) > 0.0305) else "PARTIAL")
    return dict(dr=dr, ir=ir, dt=dt, word=word, wp=out["WP"], gl=out["GL"], d_gl=float(np.mean(out["GL"]["h"] - hV)))


def _a_run(td, variant="default"):
    """One replica, one variant: states, then --dry-run (labels forbidden) and --run end to end. -> dict of outputs."""
    rep = FG._replica_fg(td, np.random.default_rng(20261006))
    out = {}
    with _a_env(td, rep):
        reg, info = _a_states(td, variant)
        _REGA[0] = dict(reg, outcome="o_%s.txt" % variant, arms_csv="a_%s.csv" % variant)
        out["info"], out["reg"] = info, _REGA[0]
        out["oracle"] = _a_oracle_decide(info)
        if variant == "closed":
            out["oracle10"] = _a_oracle_decide(info, t=10)
        saved = (AF.corpus, FG.corpus_for)

        def _forbid(*a, **k):
            raise AssertionError("the dry-run read the held-out side's labels")
        AF.corpus, FG.corpus_for = _forbid, _forbid
        try:
            out["dry"] = _capture(dry_run_a)
        except AssertionError as e:
            out["dry"] = ("AssertionError: %s" % e, "")
        finally:
            AF.corpus, FG.corpus_for = saved
        out["run"] = _capture(run_a)
        op, cp = out_paths_a()
        out["text"] = open(op, encoding="utf-8").read() if os.path.exists(op) else ""
        out["csv"] = open(cp, encoding="utf-8").read().splitlines() if os.path.exists(cp) else []
        out["again"] = _capture(run_a)
        if variant == "default":
            good = _REGA[0]
            bad = dict(good, identity=dict(good["identity"], **{DECIDING_TREE: dict(good["identity"][DECIDING_TREE], d_t="+0.9999 [+0.9, +1.0]")}),
                       outcome="o_bad.txt", arms_csv="a_bad.csv")
            _REGA[0] = bad
            out["idref"] = _capture(run_a)
            out["idref_written"] = os.path.exists(out_paths_a()[0])
            _REGA[0] = dict(good, outcome="o_pin.txt", arms_csv="a_pin.csv")
            rel, _sh = good["v_state"]["af_s137"]
            p = os.path.join(td, rel, "part_V1.json")
            b = json.load(open(p, encoding="utf-8"))
            b["iters"] = int(b.get("iters", 0)) + 1
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(b, sort_keys=True))
            out["pinref"] = _capture(run_a)
            _REGA[0] = good
    return out


def st_a_pure(chk):
    d = 4
    nodes = [_inner("R", ["D0", "L3", "D1"], None, 0, d), _inner("D0", ["L0", "N1"], "R", 1, d), _inner("N1", ["L1", "L2"], "D0", 2, d),
             _inner("D1", ["L4", "L5"], "R", 1, d)] + [_leaf(i, np.eye(d)[i % d], p, dp) for i, p, dp in
                                                        ((0, "D0", 2), (1, "N1", 3), (2, "N1", 3), (3, "R", 1), (4, "D1", 2), (5, "D1", 2))]
    byid = {n["id"]: n for n in nodes}
    ids = ["L%d" % i for i in range(6)]
    mask, par, roots = leaf_parent_masks(byid, ids)
    want = [{0, 1, 2}, {1, 2}, {1, 2}, {0, 1, 2, 3, 4, 5}, {4, 5}, {4, 5}]
    chk.ok([set(np.flatnonzero(mask[j]).tolist()) for j in range(6)] == want and roots == ["R"] and par[3] == "R",
           "A-PURE masks: the parent's subtree of every leaf (deep branch, sibling pair, a leaf under the root = all leaves)")
    chk.ok([set(np.flatnonzero(mask[j]).tolist()) for j in range(6)] == o_parent_sets(nodes, ids), "A-PURE masks equal the oracle's parent sets")
    two = dict(byid, D1=dict(byid["D1"], childIds=["L4", "L5", "L1"]))
    chk.ok(_refused(lambda: leaf_parent_masks(two, ids), "has 2 parents")[0], "A-PURE a leaf with two parents REFUSES")
    rng = np.random.default_rng(20)
    X = np.abs(rng.standard_normal((90, d)) + 2.0 * np.eye(d)[rng.integers(0, d, 90)])       # the positive orthant
    X = X / np.linalg.norm(X, axis=1, keepdims=True)
    mu0 = np.abs(rng.standard_normal((6, d)))
    mu0[5] = -np.ones(d)                                              # a leaf no item reaches: it must keep its centroid
    mu0 = mu0 / np.linalg.norm(mu0, axis=1, keepdims=True)
    z0 = np.argmax(X @ mu0.T, axis=1)
    ps = o_parent_sets(nodes, ids)
    agree = True
    for v in ("WP", "GL", "WPA"):
        r = refine(X, z0, mu0, mask, v, (1, 2, 5), 300)
        for t in (1, 2, 5):
            zo, Co = o_lloyd(X, z0, mu0, ps, v, t)
            agree = agree and list(r["steps"][t]["z"]) == zo and bool(np.allclose(r["steps"][t]["C"], Co, atol=1e-12))
        zc, _Cc = o_lloyd(X, z0, mu0, ps, v, r["t_conv"])
        zc1, _ = o_lloyd(X, z0, mu0, ps, v, r["t_conv"] + 1)
        agree = agree and bool(r["converged"]) and list(r["steps"]["conv"]["z"]) == zc == zc1
    chk.ok(agree, "A-PURE refine() WP / GL / WP-A at T 1, 2, 5 and at convergence equal the oracle loop (partitions and filing centroids)")
    r5 = refine(X, z0, mu0, mask, "WP", (5,), 300)["steps"][5]
    chk.ok(r5["empty"] >= 1 and bool(np.allclose(r5["C"][5], mu0[5])), "A-PURE a never-reached leaf keeps its last centroid (%d empty)" % r5["empty"])
    rw, rg, ra = (refine(X, z0, mu0, mask, v, (5,), 300)["steps"][5]["z"] for v in ("WP", "GL", "WPA"))
    chk.ok(bool((rw != rg).any()) and bool((rw != ra).any()), "A-PURE WP differs from GL and from WP-A on this fixture (the constraint binds)")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        p = os.path.join(td, "o.txt")
        write_once(p, "first")
        try:
            write_once(p, "second")
            second = "no error"
        except FileExistsError:
            second = "FileExistsError"
        chk.ok(second == "FileExistsError" and open(p, encoding="utf-8").read() == "first",
               "A-PURE write_once opens mode x: a second write raises and leaves the first content")
    zt = np.array(z0)
    C1, _ = centroids(X, zt, 6, mu0)
    zz = lloyd_step(X, C1, mask[zt])
    chk.ok(all(mask[zt[i], zz[i]] for i in range(len(zz))), "A-PURE a WP step never leaves the current parent's subtree")


def st_a_branch(chk):
    bar = 0.0305
    chk.ok(gf1(0.0, 0.0, 0.01, 0.001, bar) == "CLOSED", "GF1 CLOSED at UB(D_R) exactly 0 with I_R and its lower bound > 0")
    chk.ok(gf1(0.0, -1e-9, 0.01, 0.001, bar) == "PARTIAL", "GF1 UB(D_R) just below 0 and |D_R| small: PARTIAL")
    chk.ok(gf1(0.01, 0.02, 0.01, 0.0, bar) == "PARTIAL", "GF1 I_R lower bound exactly 0: not CLOSED (PARTIAL)")
    chk.ok(gf1(0.01, 0.02, 0.0, 0.001, bar) == "PARTIAL", "GF1 I_R point 0 with a positive lower bound (impossible in data; the point leg): PARTIAL")
    chk.ok(gf1(-0.0305, -0.02, 0.01, 0.001, bar) == "PARTIAL", "GF1 |D_R| exactly 0.0305 with UB < 0: not OPEN (strict), PARTIAL")
    chk.ok(gf1(-0.0306, -0.02, 0.01, 0.001, bar) == "OPEN", "GF1 |D_R| 0.0306 with UB < 0: OPEN")
    chk.ok(gf1(-0.05, 0.0, 0.0, -0.01, bar) == "PARTIAL", "GF1 large |D_R| but UB exactly 0 (not < 0): PARTIAL")
    chk.ok(gf1(-0.05, -0.01, 0.02, 0.01, bar) == "OPEN", "GF1 OPEN even with a positive I_R when UB(D_R) < 0 and |D_R| > bar")
    chk.ok(gf1(0.05, 0.06, 0.0, -0.01, bar) == "PARTIAL", "GF1 a large positive D_R is never OPEN")
    chk.ok(gf1_refuted(-0.001, 0.01) and gf1_refuted(0.01, 0.0) and not gf1_refuted(0.0, 0.0001), "FAILS rule 8: UB < 0 or LB(I_R) <= 0")
    mk = lambda dr, ir, w, ref: dict(dr=dict(d=dr[0], lo=dr[1], hi=dr[2]), ir=dict(d=ir[0], lo=ir[1], hi=ir[2]), word=w, refuted=ref, bar=bar)  # noqa: E731
    Lc = gf1_lines(mk((0.0, -0.01, 0.0), (0.03, 0.01, 0.05), "CLOSED", False))
    chk.ok(Lc[0].startswith("GF1: CLOSED: the 95% upper bound of D_R +0.0000 >= 0 and I_R +0.0300 > 0 with its 95% lower bound +0.0100")
           and Lc[1].startswith("FAILS (rule 8): CLOSED is not refuted") and Lc[2].startswith("FALSIFIER F-GF FIRES (GF1 CLOSED)"),
           "GF1 CLOSED lines by value: the clause, FAILS not refuted, F-GF FIRES")
    Lo = gf1_lines(mk((-0.04, -0.05, -0.03), (0.003, -0.002, 0.008), "OPEN", True))
    chk.ok(Lo[0].startswith("GF1: OPEN: the 95% upper bound of D_R -0.0300 < 0 and |D_R| 0.0400 > 0.0305")
           and "upper bound of D_R -0.0300 < 0; lower bound of I_R -0.0020 <= 0" in Lo[1] and Lo[2].startswith("FALSIFIER F-GF NOT FIRED (GF1 OPEN)"),
           "GF1 OPEN lines by value: the clause, FAILS refuted on both legs, F-GF NOT FIRED")
    Lp = gf1_lines(mk((-0.01, -0.02, 0.001), (0.0, 0.0, 0.0), "PARTIAL", True))
    chk.ok(Lp[0].startswith("GF1: PARTIAL: neither CLOSED (upper bound of D_R +0.0010 >= 0 with I_R +0.0000 and its lower bound +0.0000 > 0)")
           and Lp[1] == "FAILS (rule 8): CLOSED is REFUTED at the planned n (lower bound of I_R +0.0000 <= 0)" and "NOT FIRED (GF1 PARTIAL)" in Lp[2],
           "GF1 PARTIAL lines by value; FAILS on the I_R leg only; F-GF NOT FIRED")
    st = dict(share_wp=0.04, share_gl=0.36, dr=-0.012, ir=0.0, word="OPEN", d_gl=-0.035, m2_wp_v0=-0.8e-3, m2_t_v0=-1.534e-3,
              ir_redraws=[0.01, 0.0, 0.02])
    L = predictions_a(st)
    chk.ok("WP 0.0400, band [0.04, 0.25] -> HELD; GL 0.3600, band [0.08, 0.35] -> FAILED" in L[0], "P1 inclusive lower edge HELD; GL above FAILED")
    chk.ok("D_R (WP) -0.0120, band [-0.045, -0.012] -> HELD; I_R +0.0000, band [0.000, +0.030] -> HELD" in L[1], "P2 both inclusive edges HELD")
    chk.ok(L[2].endswith("observed OPEN -> Brier %.4f" % (0.1 ** 2 + 0.5 ** 2 + 0.6 ** 2)), "P3 Brier on OPEN = 0.01 + 0.25 + 0.36")
    chk.ok("D (GL) -0.0350, band [-0.035, +0.005] -> HELD" in L[3], "P4 inclusive edge")
    chk.ok("< D_T,M2 / 2 = -0.767" in L[4] and ("yes -> HELD; Brier %.4f" % (0.35 ** 2)) in L[4], "P5 -0.800 < -0.767: closes by less than half, HELD")
    chk.ok(("2 of 3 -> FAILED; Brier %.4f" % (0.6 ** 2)) in L[5] and "I_R +0.0100 / +0.0000 / +0.0200" in L[5], "P6 needs all three (+0.0000 is not > 0)")
    st2 = dict(st, m2_wp_v0=-0.7e-3, ir_redraws=[0.01, 0.001, 0.02], word="CLOSED")
    L2 = predictions_a(st2)
    chk.ok(("no -> FAILED; Brier %.4f" % (0.65 ** 2)) in L2[4] and ("3 of 3 -> HELD; Brier %.4f" % (0.4 ** 2)) in L2[5]
           and L2[2].endswith("Brier %.4f" % (0.9 ** 2 + 0.5 ** 2 + 0.4 ** 2)), "P5 FAILED, P6 HELD, P3 Brier on CLOSED")
    L3 = predictions_a(dict(st, ir_redraws=None))
    chk.ok("NOT SCOREABLE (re-draws read: 0)" in L3[5], "P6 not scoreable without the three re-draws")
    _a_mods()
    dsup = mk((-0.03, -0.043, -0.017), (0.013, 0.002, 0.024), "PARTIAL", False)
    dsup["dr"]["disc"], dsup["ir"]["disc"] = 0.1533, 0.10
    sl = support_lines_a(3445, 1.0, dsup)
    chk.ok(any("sqrt(0.1533 / 3445) = 0.00667" in x and "discordance T-WP vs T 0.1000 -> 0.00539" in x for x in sl)
           and any("D_R registered 0.0186, measured 2.8 x 0.00667 = 0.0187" in x for x in sl),
           "Support (d)/(e) measured SE and MDE80 from the discordances by value (0.00667 / 0.00539; MDE 0.0187)")
    chk.ok(any("n_eff = 3445 / 1.0000 = 3445" in x for x in sl) and any("VERDICT LINE (registered)" in x for x in sl)
           and any("NOT APPLICABLE (stated)" in x for x in sl), "Support (a)-(g) lines and the not-applicable line are printed")


def st_a_naive(chk):
    """A twin-group fixture on decide(), the function run_a calls: all of I_R sits in ONE stem_key twin group of 40 questions."""
    _a_mods()
    n = 400
    groups = np.concatenate([np.zeros(40, dtype=np.int64), np.arange(1, 361)])
    rng = np.random.default_rng(1)
    base = (rng.uniform(size=n) < 0.7).astype(float)
    wp, t = base.copy(), base.copy()
    wp[:40], t[:40] = 1.0, 0.0
    arms = {"WP_5": dict(per1=wp), "V0": dict(per1=wp.copy()), "T": dict(per1=t)}
    good = decide(arms, groups, "WP_5", 0.0305)
    naive = decide(arms, np.arange(n), "WP_5", 0.0305)
    chk.ok(naive["word"] == "CLOSED" and naive["ir"]["lo"] > 0, "A-NAIVE an i.i.d. interval (every question its own group) reads CLOSED "
           "(I_R %s)" % ci4(naive["ir"]))
    chk.ok(good["word"] == "PARTIAL" and good["ir"]["lo"] <= 0 and abs(good["ir"]["d"] - 0.1) < 1e-12 and good["dr"]["hi"] == 0.0,
           "A-NAIVE the registered whole-twin-group interval reads PARTIAL (I_R %s; D_R upper bound 0)" % ci4(good["ir"]))


def st_a_e2e(chk):
    _a_mods()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        o = _a_run(td, "default")
    txt, orc = o["text"], o["oracle"]
    chk.ok(o["dry"][0] == 0 and "dry-run (a) complete: zero measures" in o["dry"][1] and o["dry"][1].splitlines()[0].startswith("pool "),
           "A-E2E --dry-run completes with the pool line first and NO label read (AF.corpus / corpus_for forbidden) (%s)" % (o["dry"][0],))
    chk.ok(o["run"][0] == 0 and bool(txt) and len(o["csv"]) == 1 + 4 * (5 + 1 + 2 * 6 + 1), "A-E2E --run writes the outcome and the arms "
           "CSV (4 trees x 19 arms) (%s)" % (o["run"][0] if o["run"][0] != 0 else len(o["csv"])))
    chk.ok(_line(txt, "  D_R = M1(T-WP) - M1(V0) = ").endswith(ci4(orc["dr"])), "A-E2E D_R %s = the oracle" % ci4(orc["dr"]))
    chk.ok(_line(txt, "  I_R = D_R - D_T = M1(T-WP) - M1(T) = ").endswith(ci4(orc["ir"])), "A-E2E I_R %s = the oracle" % ci4(orc["ir"]))
    chk.ok(_line(txt, "  D_T = M1(T) - M1(V0) = ").startswith("  D_T = M1(T) - M1(V0) = " + ci4(orc["dt"])), "A-E2E D_T = the oracle")
    chk.ok(_line(txt, "GF1: ").startswith("GF1: %s" % orc["word"]), "A-E2E GF1 word %s = the hand rule on the oracle's numbers" % orc["word"])
    p1 = _line(txt, "  P1 held-out leaf-change share at T 5: ")
    chk.ok(("WP %.4f," % orc["wp"]["moved_h"]) in p1 and ("GL %.4f," % orc["gl"]["moved_h"]) in p1, "A-E2E P1 held-out shares (WP %.4f, GL "
           "%.4f) = the oracle" % (orc["wp"]["moved_h"], orc["gl"]["moved_h"]))
    row = [ln for ln in txt.splitlines() if ln.startswith("  WP_5 ") and "(DECIDING)" in ln]
    chk.ok(len(row) == 1 and (" %.4f       %.4f " % (orc["wp"]["moved_t"], orc["wp"]["moved_h"])) in row[0],
           "A-E2E the deciding row's TRAIN and held-out moved shares = the oracle")
    chk.ok(_line(txt, "  P4 (descriptive) D (GL) ").startswith("  P4 (descriptive) D (GL) %s" % f4(orc["d_gl"])), "A-E2E P4 D(GL) = the oracle")
    chk.ok("IDENTITY af_clean_s42:" in o["run"][1] and "-> REPRODUCED" in o["run"][1], "A-E2E the identity precondition printed REPRODUCED")
    chk.ok(isinstance(o["again"][0], str) and "WRITE-ONCE" in o["again"][0], "A-E2E a second --run REFUSES (write-once)")
    chk.ok(isinstance(o["idref"][0], str) and "[GF-IDENTITY]" in o["idref"][0] and not o["idref_written"],
           "A-REFUSE a recorded D_T that this path does not reproduce REFUSES; no outcome written")
    chk.ok(isinstance(o["pinref"][0], str) and "is sha256" in o["pinref"][0], "A-REFUSE a tampered V state file REFUSES (pin)")
    chk.ok("WP converged True" in txt and "GL converged True" in txt, "A-E2E WP and GL converged; the convergence step is printed")


def st_a_verdict(chk):
    _a_mods()
    for variant, want in (("closed", "CLOSED"), ("partial", "PARTIAL"), ("open", "OPEN")):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
            o = _a_run(td, variant)
            orc, txt = o["oracle"], o["text"]
            chk.ok(orc["word"] == want, "A-VERDICT %s fixture: the oracle reads %s by construction (D_R %s, I_R %s)" % (
                variant, want, ci4(orc["dr"]), ci4(orc["ir"])))
            chk.ok(o["run"][0] == 0 and _line(txt, "GF1: ").startswith("GF1: %s" % want), "A-VERDICT %s: --run prints GF1 %s" % (variant, want))
            chk.ok(_line(txt, "  D_R = M1(T-WP) - M1(V0) = ").endswith(ci4(orc["dr"])) and
                   _line(txt, "  I_R = D_R - D_T = M1(T-WP) - M1(T) = ").endswith(ci4(orc["ir"])), "A-VERDICT %s: D_R and I_R = the oracle" % variant)
            fl = _line(txt, "FALSIFIER F-GF ")
            chk.ok(fl.startswith("FALSIFIER F-GF FIRES") == (want == "CLOSED"), "A-VERDICT %s: F-GF %s" % (variant, "FIRES" if want == "CLOSED" else "NOT FIRED"))
            if variant == "closed":
                orc10 = o["oracle10"]
                chk.ok(abs(orc10["ir"]["d"] - orc["ir"]["d"]) > 1e-9 or abs(orc10["wp"]["moved_t"] - orc["wp"]["moved_t"]) > 1e-9,
                       "A-VERDICT closed: T 5 and T 10 differ on this fixture (a wrong deciding T is visible)")
                chk.ok(abs(orc["gl"]["moved_t"] - orc["wp"]["moved_t"]) > 1e-9, "A-VERDICT closed: WP and GL differ on this fixture")


def st_a_overlap(chk):
    _a_mods()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        rep = FG._replica_fg(td, np.random.default_rng(20261006), overlap=True)
        with _a_env(td, rep):
            res = _capture(lambda: tree_data("af_s137", labels=True))
    chk.ok(isinstance(res[0], str) and "fit texts are EVAL texts" in res[0], "A-REFUSE a fit text equal to an EVAL text REFUSES in tree_data (run_a's path)")


# ── (b) oracles and fixture ─────────────────────────────────────────────────────────────────────────────────────────────────
FX_B = dict(REG_B, B=24, seed=42)


def _b_plant(X):
    """A planted gating on resp_structure_common's fixture: every scored EVAL item of BBH:n00000001 -> BBH:n00000004 and of
    MMLU_PRO_LB:n00000007 -> MMLU_PRO_LB:n00000010 (TRAIN untouched)."""
    mv = {"BBH:n00000001": "BBH:n00000004", "MMLU_PRO_LB:n00000007": "MMLU_PRO_LB:n00000010"}

    def fn(af, say):
        g = dict(af)
        n = 0
        for r in X["rows"]:
            if r["side"] == "EVAL" and r.get("scored", True) and r["af"] in mv:
                g[r["id"]] = mv[r["af"]]
                n += 1
        say("%s GATING (selftest plant): %d EVAL items moved" % (TAG, n))
        return g, Counter(moved=n)
    return fn, mv


def _b_oracle(cellf, mats, wt=None, v=None):
    """KI (sum over models of the Brier gain) and routed accuracy per arm, by plain loops on the fixture rows."""
    tr, ev, YT, YE = mats
    m = YT.shape[1]
    wt = np.ones(len(tr)) if wt is None else wt
    v = np.ones(len(ev)) if v is None else v
    out = {}
    tot = np.zeros(m)
    for i in range(len(tr)):
        tot = tot + wt[i] * YT[i]
    marg = tot / wt.sum()
    gb = int(np.argmax(tot))
    for name, f in cellf.items():
        S, W = {}, {}
        for i, r in enumerate(tr):
            c = f(r)
            S[c] = S.get(c, np.zeros(m)) + wt[i] * YT[i]
            W[c] = W.get(c, 0.0) + wt[i]
        ki = acc = 0.0
        for i, r in enumerate(ev):
            c = f(r)
            p = S[c] / W[c] if W.get(c, 0) > 0 else marg
            ki += v[i] * float(((marg - YE[i]) ** 2 - (p - YE[i]) ** 2).sum())
            pick = int(np.argmax(S[c])) if W.get(c, 0) >= 1 else gb
            acc += v[i] * YE[i][pick]
        out[name] = (ki / v.sum(), acc / v.sum())
    return out


def _b_expected(X, gate_mv, D0):
    """The as-built identity constants and the gated values, by the loops (points) and the loops on run_boot's own draws (intervals)."""
    mats = RSC.fx_matrices(X["rows"])
    ev = mats[1]

    def arms(gated):
        f = {"AF": (lambda r: gate_mv.get(r["af"], r["af"]) if (gated and r["side"] == "EVAL") else r["af"])}
        for s in RSC.KSEEDS:
            f["K%d" % s] = (lambda r, s=s: X["kcells"][s][r["id"]])
        return f
    B, seed = RB()["B"], RB()["seed"]
    rng = np.random.default_rng(seed)
    draws = []
    for _b in range(B):
        wt = np.zeros(D0.n, dtype=np.int64)
        wt[D0.T] = V.draw_units(rng, D0.train_units)
        v = V.draw_units(rng, D0.eval_units).astype(np.float64)
        draws.append((wt[D0.T].astype(np.float64), v))
    O = RSC.fx_irt(X["rows"])
    sh = RPI.R()["shrink"]

    def r2loop(cf):
        sums, cnt = {}, {}
        for i, r in enumerate(O["tr"]):
            c = cf(r)
            cnt[c] = cnt.get(c, 0) + 1
            sums[c] = sums.get(c, np.zeros(O["eT"].shape[1])) + O["eT"][i]
        num = den = 0.0
        for i, r in enumerate(O["ev"]):
            c = cf(r)
            eb = sums[c] / (cnt[c] + sh) if c in cnt else np.zeros(O["eE"].shape[1])
            num += ((O["eE"][i] - eb) ** 2).sum()
            den += (O["eE"][i] ** 2).sum()
        return 1.0 - num / den
    res = {}
    kn = ["K%d" % s for s in RSC.KSEEDS]
    for gated in (False, True):
        f = arms(gated)
        pt = _b_oracle(f, mats)
        ki_d = pt["AF"][0] - np.mean([pt[k][0] for k in kn])
        dk = pt["AF"][1] - np.mean([pt[k][1] for k in kn])
        two_ki, two_dk = [], []
        for wt, v in draws:
            o = _b_oracle(f, mats, wt=wt, v=v)
            two_ki.append(o["AF"][0] - np.mean([o[k][0] for k in kn]))
            two_dk.append(o["AF"][1] - np.mean([o[k][1] for k in kn]))
        se_ki, se_dk = float(np.std(two_ki, ddof=1)), float(np.std(two_dk, ddof=1))
        rk = [r2loop(f[k]) for k in kn]
        res[gated] = dict(ki_d=ki_d, ki_lo=ki_d - 1.96 * se_ki, ki_hi=ki_d + 1.96 * se_ki,
                          ki_spread=max(pt[k][0] for k in kn) - min(pt[k][0] for k in kn),
                          dk=dk, dk_lo=dk - 1.96 * se_dk, dk_hi=dk + 1.96 * se_dk, dk_spread=max(pt[k][1] for k in kn) - min(pt[k][1] for k in kn),
                          rp_d=r2loop(f["AF"]) - float(np.mean(rk)), rp_spread=max(rk) - min(rk),
                          moved=sum(1 for r in ev if gate_mv.get(r["af"]) is not None))
    return res


def _b_identity_from(e):
    return dict(ki_d=f6_(e["ki_d"]), ki_lo=f6_(e["ki_lo"]), ki_hi=f6_(e["ki_hi"]), ki_spread="%.6f" % e["ki_spread"], u2_dk=UAR.pp(e["dk"]),
                u2_lo=UAR.pp(e["dk_lo"]), u2_hi=UAR.pp(e["dk_hi"]), u2_spread=UAR.pp(e["dk_spread"]), rp_d=f6_(e["rp_d"]),
                rp_spread="%.6f" % e["rp_spread"])


def _b_D0(root, X):
    """The fixture's as-built D, read the way resp_profile_info's selftest reads it (the unit structure of run_boot's draws)."""
    with RSC.patched(X):
        pol, af, kx = RSC.prelude(root, lambda s: None, TAG, TEST_ID, REG_TEXT, [], [os.path.join(root, "nx")], True)
        models, tmeta, cstr, K_tr, _n = RSC.read_train(root, lambda s: None, TAG, pol["roster"], True)
        tw, esha = V.open_tw("eval", "route", UCI.P(root, UCI.C()["eval_rel"]), UCI.C()["eval_sha"], "eval_view", lambda s: None)
        tw.unseal("selftest: the oracle's unit structure")
        E = UCI._eval_set_open(tw, esha, UCI.P(root, UCI.C()["eval_rel"]), root, lambda s: None, TAG, pol["roster"], False, None)
        K_ev, _k = V.read_key(tw, "response", UCI.C()["cv"], models, E["meta"], True, UCI.C()["rule"])
        tw.close()
        E["K"] = K_ev
        return RSC.build(models, tmeta, E, K_tr, cstr, af, kx, pol, TAG)


def st_b_gate(chk):
    _b_mods()
    leaf_ids = ["A:1", "A:2", "B:1", "B:2"]
    M = np.array([[1, 0, 0], [0.8, 0.6, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    M = M / np.linalg.norm(M, axis=1, keepdims=True)
    src = ["A", "A", "B", "B"]
    vec = {"e1": np.array([0, 1.0, 0]), "e2": np.array([1.0, 0.1, 0]), "e3": np.array([0, 0.2, 1.0]), "t1": np.array([0, 1.0, 0])}
    af = {"e1": "B:1", "e2": "A:1", "e3": "B:2", "e4": "S:1", "t1": "B:1", "e5": "<no-routing-row>"}
    srcs = {"e1": ["A"], "e2": ["A"], "e3": ["B"], "e4": ["S"], "t1": ["A"]}
    g, cnt = gate_core(af, ["e1", "e2", "e3", "e4", "e5"], vec, leaf_ids, M, src, srcs, {"S": "S:1"}, no_row=("<no-routing-row>",))
    chk.ok(g["e1"] == "A:2" and g["e2"] == "A:1" and g["e3"] == "B:2" and g["e4"] == "S:1" and g["t1"] == "B:1" and g["e5"] == "<no-routing-row>",
           "B-GATE a cross-source item moves to its own source's nearest leaf; own-source items stay; one-cell kept; TRAIN untouched")
    chk.ok(cnt["moved"] == 1 and cnt["gated"] == 3 and cnt["one_cell"] == 1 and cnt["no_row"] == 1 and cnt["moved:A"] == 1, "B-GATE counts by value")
    bad = dict(af, e2="A:2")
    chk.ok(_refused(lambda: gate_core(bad, ["e2"], vec, leaf_ids, M, src, srcs, {}), "[GF-IDENTITY-FILING]")[0],
           "B-GATE an item whose recorded cell is not the ungated nearest leaf REFUSES (R-B2)")
    chk.ok(_refused(lambda: gate_core(af, ["e1"], {}, leaf_ids, M, src, srcs, {}), "no vector")[0], "B-GATE a missing vector REFUSES")
    chk.ok(_refused(lambda: gate_core(af, ["e1"], vec, leaf_ids, M, src, dict(srcs, e1=["A", "S"]), {"S": "S:1"}), "one-cell source beside")[0],
           "B-GATE a one-cell source beside a multi-leaf source REFUSES")
    chk.ok(_refused(lambda: gate_core(af, ["e4"], vec, leaf_ids, M, src, dict(srcs, e4=["A"]), {"S": "S:1"}), "sits in the one-cell")[0],
           "B-GATE an item in a one-cell cell that declares another source REFUSES")
    g2, _c = gate_core(af, ["e1"], vec, leaf_ids, M, src, dict(srcs, e1=["A", "B"]), {})
    chk.ok(g2["e1"] == "B:1", "B-GATE an item of two declared sources is filed among both sources' leaves (K_s's rule)")
    side = {"e1": ("c", "EVAL"), "t1": ("c", "TRAIN"), "g1": ("c", "GATE"), "e9": ("c", "EVAL")}
    chk.ok(eval_side_items({"e1": 1, "t1": 1, "g1": 1}, side) == ["e1"], "B-GATE only EVAL-side items with an AF-U row are re-filed")


def st_b_e2e(chk):
    _b_mods()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        root, X = RSC.build_fixture(tmp, "planted")
        fn, mv = _b_plant(X)
        old = _REGB[0]
        try:
            _REGB[0] = dict(FX_B)
            D0 = _b_D0(root, X)
            with RSC.patched(X), RPI._swap(RPI.FX_RP):
                exp = _b_expected(X, mv, D0)
            _REGB[0] = dict(FX_B, identity=_b_identity_from(exp[False]), moved_rec=exp[True]["moved"])
            od = os.path.join(tmp, "out")
            with RSC.patched(X), RPI._swap(RPI.FX_RP):
                dry = _capture(dry_run_b, root, od, print, fn)
                chk.ok(dry[0] == 0 and dry[1].splitlines()[0].startswith(TAG + " POOL pv_fx") and "no key column selected" in dry[1]
                       and not os.path.exists(os.path.join(od, RB()["marker"])) and not os.path.exists(os.path.join(od, RB()["outcome"])),
                       "B-DRY the dry-run prints the POOL line first, reads no key, writes nothing (%s)" % (dry[0],))
                r = _capture(run_b, root, od, print, fn)
                chk.ok(isinstance(r[0], tuple), "B-E2E run_b completes on the fixture (%s)" % (r[0] if not isinstance(r[0], tuple) else "ok"))
                text = r[0][1]
                g = exp[True]
                chk.ok("-> REPRODUCED" in text and ("KI1 D %s" % f6_(exp[False]["ki_d"])) in _line(text, TAG + " IDENTITY (as built"),
                       "B-E2E the as-built identity equals the oracle's loops (KI1 D %s, U2 D_K %s, RP2 D %s)" % (
                           f6_(exp[False]["ki_d"]), UAR.pp(exp[False]["dk"]), f6_(exp[False]["rp_d"])))
                kl = _line(text, "KI1 re-read")
                chk.ok(("= %s | two-stage 95%% [%s, %s]; spread_K %.6f" % (f6_(g["ki_d"]), f6_(g["ki_lo"]), f6_(g["ki_hi"]), g["ki_spread"])) in kl,
                       "B-E2E gated KI1 D %s [%s, %s], spread_K %.6f = the oracle (points and the two-stage interval on run_boot's draws)" % (
                           f6_(g["ki_d"]), f6_(g["ki_lo"]), f6_(g["ki_hi"]), g["ki_spread"]))
                rl = _line(text, "RP2 re-read")
                chk.ok(("= %s |" % f6_(g["rp_d"])) in rl and ("spread_K %.6f" % g["rp_spread"]) in rl, "B-E2E gated RP2 D %s, spread_K %.6f = the oracle"
                       % (f6_(g["rp_d"]), g["rp_spread"]))
                ul = _line(text, "U2 re-read")
                chk.ok(("D_K = G_AF(gated) - G_K = %s | two-stage [%s, %s]; spread_K %s" % (UAR.pp(g["dk"]), UAR.pp(g["dk_lo"]), UAR.pp(g["dk_hi"]),
                                                                                            UAR.pp(g["dk_spread"]))) in ul,
                       "B-E2E gated U2 D_K %s [%s, %s] = the oracle" % (UAR.pp(g["dk"]), UAR.pp(g["dk_lo"]), UAR.pp(g["dk_hi"])))
                chk.ok(abs(g["ki_d"] - exp[False]["ki_d"]) > 1e-6 and abs(g["dk"] - exp[False]["dk"]) > 1e-6 and abs(g["rp_d"] - exp[False]["rp_d"]) > 1e-6,
                       "B-E2E the plant changes every gated value (an as-built reading in place of the gated one is visible)")
                chk.ok(_line(text, "GATED FILING: ").startswith("GATED FILING: %d of the %d scored EVAL items change cell" % (
                    g["moved"], len(RSC.fx_matrices(X["rows"])[1]))), "B-E2E the moved count = the plant (%d)" % g["moved"])
                kw = "AF-BETTER" if (g["ki_d"] > g["ki_spread"] and g["ki_lo"] > 0) else ("K0-BETTER" if (g["ki_d"] < -g["ki_spread"] and g["ki_hi"] < 0) else "NEITHER")
                chk.ok(_line(text, "  KI1's rule would read ").startswith("  KI1's rule would read %s " % kw), "B-E2E KI1's word %s from the oracle's numbers" % kw)
                uw = "FIRES" if (g["dk_lo"] > 0 and g["dk"] > g["dk_spread"]) else ("REVERSE" if (g["dk_hi"] < 0 and g["dk"] < -g["dk_spread"]) else "NOT FIRED")
                chk.ok(_line(text, "  U2's rule would read ").startswith("  U2's rule would read %s " % uw), "B-E2E U2's word %s from the oracle's numbers" % uw)
                import re
                mm = re.search(r"= ([-+0-9.]+) \| two-stage 95% \[([-+0-9.]+), ([-+0-9.]+)\].*spread_K ([0-9.]+);", rl)
                rd_, rlo, rhi, rsp = (float(x) for x in mm.groups())
                rw_ = "AF-BETTER" if (rlo > 0 and rd_ > rsp) else ("K0-BETTER" if (rhi < 0 and rd_ < -rsp) else "NEITHER")
                chk.ok(_line(text, "  RP2's rule would read ").startswith("  RP2's rule would read %s " % rw_), "B-E2E RP2's word %s from its printed numbers" % rw_)
                pk = _line(text, "  gated KI1 D ")
                chk.ok(pk.endswith(hw(g["ki_d"], PRED_B["ki"])), "B-E2E P7 KI line's word from the value")
                again = _capture(run_b, root, od, print, fn)
                chk.ok(isinstance(again[0], str) and "write-once" in again[0], "B-E2E a second run REFUSES (write-once)")
                od2 = os.path.join(tmp, "out2")
                _REGB[0] = dict(_REGB[0], identity=dict(_REGB[0]["identity"], ki_d="+9.999999"))
                bad = _capture(run_b, root, od2, print, fn)
                chk.ok(isinstance(bad[0], str) and "[GF-IDENTITY-B]" in bad[0] and not os.path.exists(os.path.join(od2, RB()["outcome"])),
                       "B-REFUSE an as-built value that differs from the record REFUSES; no outcome")
                _REGB[0] = dict(FX_B, identity=_b_identity_from(exp[False]))
                tr_id = [r["id"] for r in X["rows"] if r["side"] == "TRAIN" and r.get("scored", True)][0]

                def fn_bad(af, say):
                    gg, c = fn(af, say)
                    gg[tr_id] = "BBH:n00000002" if af[tr_id] != "BBH:n00000002" else "BBH:n00000003"
                    return gg, c
                od3 = os.path.join(tmp, "out3")
                bad2 = _capture(run_b, root, od3, print, fn_bad)
                chk.ok(isinstance(bad2[0], str) and "[GF-TRAIN]" in bad2[0], "B-REFUSE a gating that re-files a TRAIN item REFUSES")
        finally:
            _REGB[0] = old


def st_b_branch(chk):
    _b_mods()
    chk.ok(hw(-0.020, PRED_B["ki"]) == "HELD" and hw(-0.005, PRED_B["ki"]) == "HELD" and hw(-0.0049, PRED_B["ki"]) == "FAILED",
           "P7 KI band inclusive at both edges")
    chk.ok(hw(-0.0035, PRED_B["rp"]) == "HELD" and hw(-0.0005, PRED_B["rp"]) == "HELD" and hw(-0.00049, PRED_B["rp"]) == "FAILED", "P7 RP band")
    chk.ok(hw(-0.0080, PRED_B["u2"]) == "HELD" and hw(0.0010, PRED_B["u2"]) == "HELD" and hw(0.00101, PRED_B["u2"]) == "FAILED", "P7 U2 band (pp as fractions)")


PARTS = {"a": (("A-PURE", st_a_pure), ("A-BRANCH", st_a_branch), ("A-NAIVE", st_a_naive), ("A-E2E", st_a_e2e), ("A-VERDICT", st_a_verdict),
               ("A-OVERLAP", st_a_overlap)),
         "b": (("B-GATE", st_b_gate), ("B-BRANCH", st_b_branch), ("B-E2E", st_b_e2e))}


def selftest_part(part, only=None, quiet=False):
    if part == "a":
        _a_mods()
    else:
        _b_mods()
    chk = Checks(quiet)
    chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "THREADS the three thread variables are 1")
    for name, fn in PARTS[part]:
        if only and name not in only:
            continue
        t0 = time.perf_counter()
        fn(chk)
        if not quiet:
            print("  -- %s done (%.1f s)" % (name, time.perf_counter() - t0))
    print("%s SELFTEST part (%s): %d checks passed" % (TAG, part, chk.n))
    return 0


def _child(args, env_extra=None, src=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    cmd = [sys.executable, src or os.path.abspath(__file__)] + args
    p = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def selftest(only=None):
    rc_all = 0
    for part in ("a", "b"):
        names = [n for n, _f in PARTS[part]]
        sel = [n for n in (only or names) if n in names]
        if not sel:
            continue
        rc, out = _child(["--selftest-part", part, "--only"] + sel)
        sys.stdout.write(out)
        print("%s selftest part (%s) child rc %d" % (TAG, part, rc))
        rc_all = rc_all or rc
    if rc_all:
        raise SystemExit("%s SELFTEST FAILED" % TAG)
    print("%s SELFTEST: both parts passed" % TAG)
    return 0


# ── mutants: (id, part, selftest cases, old, new); each must make that part's selftest fail ──────────────────────────────────
NL = "\n"
MUTANTS = (
    ("X01 GF1 UB(D_R) >= 0 -> > 0", "a", ("A-BRANCH", "A-VERDICT"), "if bool(dr_hi >= 0) and bool(ir > 0)", "if bool(dr_hi > 0) and bool(ir > 0)"),
    ("X02 GF1 lower bound of I_R dropped", "a", ("A-BRANCH", "A-NAIVE"), "and bool(ir > 0) and bool(ir_lo > 0):", "and bool(ir > 0):"),
    ("X03 GF1 I_R point leg dropped", "a", ("A-BRANCH",), "if bool(dr_hi >= 0) and bool(ir > 0) and bool(ir_lo > 0):", "if bool(dr_hi >= 0) and bool(ir_lo > 0):"),
    ("X04 GF1 OPEN |D_R| > bar -> >=", "a", ("A-BRANCH",), "bool(abs(dr) > bar)", "bool(abs(dr) >= bar)"),
    ("X05 GF1 OPEN without UB < 0", "a", ("A-BRANCH",), "if bool(dr_hi < 0) and bool(abs(dr) > bar):", "if bool(abs(dr) > bar):"),
    ("X06 GF1 OPEN on the signed D_R", "a", ("A-BRANCH", "A-VERDICT"), "bool(abs(dr) > bar)", "bool(dr > bar)"),
    ("X07 FAILS rule 8 LB(I_R) <= 0 -> < 0", "a", ("A-BRANCH",), "return bool(dr_hi < 0) or bool(ir_lo <= 0)", "return bool(dr_hi < 0) or bool(ir_lo < 0)"),
    ("X08 D_R against T instead of V0", "a", ("A-E2E",), 'dr = paired_m1(arms[key_wp]["per1"], arms["V0"]["per1"], groups)', 'dr = paired_m1(arms[key_wp]["per1"], arms["T"]["per1"], groups)'),
    ("X09 I_R against V0 instead of T", "a", ("A-E2E",), 'ir = paired_m1(arms[key_wp]["per1"], arms["T"]["per1"], groups)', 'ir = paired_m1(arms[key_wp]["per1"], arms["V0"]["per1"], groups)'),
    ("X10 i.i.d. interval (twin groups ignored) in the deciding path", "a", ("A-NAIVE",), "    lo, hi = FM.twin_boot_ci(d, groups)" + NL + "    return dict(d=float(d.mean()), lo=float(lo), hi=float(hi), disc",
     "    lo, hi = FM.twin_boot_ci(d, np.arange(len(d)))" + NL + "    return dict(d=float(d.mean()), lo=float(lo), hi=float(hi), disc"),
    ("X11 the deciding T 5 -> 10", "a", ("A-VERDICT",), 'dec = decide(arms, groups, "WP_%d" % r["t_decide"], r["bar_open"])', 'dec = decide(arms, groups, "WP_10", r["bar_open"])'),
    ("X12 the deciding variant WP -> GL", "a", ("A-VERDICT",), 'dec = decide(arms, groups, "WP_%d" % r["t_decide"], r["bar_open"])', 'dec = decide(arms, groups, "GL_%d" % r["t_decide"], r["bar_open"])'),
    ("X13 WP mask = all leaves (GL)", "a", ("A-PURE",), "        if variant == \"WP\":" + NL + "            allowed = mask[z]", "        if variant == \"WP\":" + NL + "            allowed = full"),
    ("X14 WP mask from the as-built leaf (WP-A)", "a", ("A-PURE",), "        if variant == \"WP\":" + NL + "            allowed = mask[z]", "        if variant == \"WP\":" + NL + "            allowed = mask[z0]"),
    ("X15 an emptied leaf drops to zero (no last centroid)", "a", ("A-PURE",), "    C = np.array(prev, dtype=np.float64, copy=True)", "    C = np.zeros_like(np.asarray(prev, dtype=np.float64))"),
    ("X16 filing centroids = the pass-T centroids", "a", ("A-PURE",), "        if t in t_keep or (not changed and t_conv is None):" + NL + "            Cf, cnt = centroids(X, z, k, C_prev)",
     "        if t in t_keep or (not changed and t_conv is None):" + NL + "            Cf, cnt = C_prev, np.bincount(z, minlength=k)"),
    ("X17 root-parent leaf allowed only itself", "a", ("A-PURE",), "        mask[j, sub[p]] = True", "        mask[j, sub[p] if p not in roots else [j]] = True"),
    ("X18 held-out share measured on TRAIN", "a", ("A-E2E",), 'share[nm] = dict(train=float(np.mean(st["z"] != z0)), heldout=float(np.mean(arms[nm]["filed"] != arms["T"]["filed"])),' + NL + '                             empty=st["empty"], sizes=np.bincount(st["z"], minlength=k))' + NL + '    st = ref',
     'share[nm] = dict(train=float(np.mean(st["z"] != z0)), heldout=float(np.mean(st["z"] != z0)),' + NL + '                             empty=st["empty"], sizes=np.bincount(st["z"], minlength=k))' + NL + '    st = ref'),
    ("X19 P1 band edges exclusive", "a", ("A-BRANCH",), "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])"),
    ("X20 P5 event inverted", "a", ("A-BRANCH",), 'e5 = bool(st["m2_wp_v0"] < st["m2_t_v0"] / 2.0)', 'e5 = bool(st["m2_wp_v0"] > st["m2_t_v0"] / 2.0)'),
    ("X21 P6 any instead of all", "a", ("A-BRANCH",), 'e6 = bool(all(x > 0 for x in st["ir_redraws"]))', 'e6 = bool(any(x > 0 for x in st["ir_redraws"]))'),
    ("X22 F-GF fires on PARTIAL too", "a", ("A-BRANCH", "A-VERDICT"), "    if w == \"CLOSED\":" + NL + "        L.append(\"FALSIFIER F-GF FIRES", "    if w != \"OPEN\":" + NL + "        L.append(\"FALSIFIER F-GF FIRES"),
    ("X23 identity precondition removed", "a", ("A-E2E",), "    if bad:" + NL + "        refuse(\"[GF-IDENTITY]", "    if False:" + NL + "        refuse(\"[GF-IDENTITY]"),
    ("X24 V-state pin check removed", "a", ("A-E2E",), "        if got != want:" + NL + "            refuse(\"%s: V state", "        if False:" + NL + "            refuse(\"%s: V state"),
    ("X25 write-once mode x -> w", "a", ("A-PURE",), '    with open(path, "x", encoding="utf-8", newline="\\n") as f:', '    with open(path, "w", encoding="utf-8", newline="\\n") as f:'),
    ("X30 run_a's existence pre-check removed", "a", ("A-E2E",), "    for p in (outp, csvp):" + NL + "        if os.path.exists(p):" + NL + "            refuse(\"%s exists: outcome files of record are WRITE-ONCE\" % p)",
     "    for p in (outp, csvp):" + NL + "        if False:" + NL + "            refuse(\"%s exists: outcome files of record are WRITE-ONCE\" % p)"),
    ("X31 the refinement fitted on the label set, not the fit set", "a", ("A-E2E",), '    ref = {v: refine(X, z0, tr["leaf_mu"], mask, v, r["t_steps"], r["t_cap"]) for v in ("WP", "GL", "WPA")}',
     '    ref = {v: refine(Qt, np.asarray(AF.route(tr, Qt)), tr["leaf_mu"], mask, v, r["t_steps"], r["t_cap"]) for v in ("WP", "GL", "WPA")}'),
    ("X26 hygiene (fit / EVAL overlap) not checked", "a", ("A-OVERLAP",), "        FG.hygiene(texts, [t for t, _ in heldout])          # REFUSES", "        (lambda *a: None)(texts, [t for t, _ in heldout])          # REFUSES"),
    ("X27 dry-run reads the labels (corpus_for)", "a", ("A-E2E",), "        td_ = tree_data(tree, labels=False)", "        td_ = tree_data(tree, labels=True)"),
    ("X28 P4 reads WP instead of GL", "a", ("A-E2E",), 'd_gl=D["paired"]["GL_%d" % r["t_decide"]]["v0"]["d"]', 'd_gl=D["paired"]["WP_%d" % r["t_decide"]]["v0"]["d"]'),
    ("X29 P3 Brier observed outcome ignored", "a", ("A-BRANCH",), 'brier_multi(PRED_A["P3"], st["word"])', 'brier_multi(PRED_A["P3"], "PARTIAL")'),
    ("Y01 gating without the source restriction", "b", ("B-GATE",), "        allowed = np.isin(leaf_src, list(ss))", "        allowed = np.ones(len(leaf_src), dtype=bool)"),
    ("Y02 gating identity (R-B2) removed", "b", ("B-GATE",), "        if leaf_ids[j_all] != cell:" + NL + "            refuse(\"[GF-IDENTITY-FILING]", "        if False:" + NL + "            refuse(\"[GF-IDENTITY-FILING]"),
    ("Y03 TRAIN-side items re-filed too", "b", ("B-GATE",), 'if s == "EVAL" and it in af)', 'if s in ("EVAL", "TRAIN") and it in af)'),
    ("Y04 KI1 D against K0 only", "b", ("B-E2E",), '    dt = terms["AF-U"] - np.mean([terms[k] for k in kn], axis=0)', '    dt = terms["AF-U"] - terms[kn[0]]'),
    ("Y05 KI1 interval from the i.i.d. replicates", "b", ("B-E2E",), "    d = URC.interval(float(dt.mean()), two, iid, len(D.E))", "    d = URC.interval(float(dt.mean()), iid, iid, len(D.E))"),
    ("Y06 RP2 point on the as-built D", "b", ("B-E2E",), "    rp1 = rp_point(D1, I, arms1)", "    rp1 = rp_point(D0, I, arms0)"),
    ("Y07 U2 from the as-built replicates", "b", ("B-E2E",), "    u1 = UAR.u_stats(bt1, D1, None)", "    u1 = UAR.u_stats(bt0, D0, None)"),
    ("Y08 identity (b) removed", "b", ("B-E2E",), "    if not ok:" + NL + "        refuse(\"[GF-IDENTITY-B]", "    if False:" + NL + "        refuse(\"[GF-IDENTITY-B]"),
    ("Y09 TRAIN-cell check removed", "b", ("B-E2E",), "    if tbad:" + NL + "        refuse(\"[GF-TRAIN]", "    if False:" + NL + "        refuse(\"[GF-TRAIN]"),
    ("Y10 KI spread min/max swapped", "b", ("B-E2E",), '    return dict(d=d, spread=max(kk) - min(kk),', '    return dict(d=d, spread=min(kk) - max(kk),'),
    ("Y11 the gated KI reads the as-built replicates", "b", ("B-E2E",), "    bt1, rec1, G1 = ki_boot(D1)" + NL + "    ki1 = ki_stats(D1, rec1, G1)", "    bt1, rec1, G1 = ki_boot(D1)" + NL + "    ki1 = ki_stats(D0, rec0, G0)"),
    ("Y13 KI1 word line omitted", "b", ("B-E2E",), """    L.append("  KI1's rule would read %s""", """    (lambda *a: None)("  KI1's rule would read %s"""),
    ("Y14 U2 word on the as-built spread", "b", ("B-E2E",), 'UAR.u2_verdict(u["DK"], u["spread_K"]))', 'UAR.u2_verdict(u["DK"], st["u0"]["spread_K"] + 1.0))'),
    ("Y15 RP2 word line omitted", "b", ("B-E2E",), """    L.append("  RP2's rule would read %s""", """    (lambda *a: None)("  RP2's rule would read %s"""),
    ("Y12 P7 KI word from another value", "b", ("B-E2E",), 'hw(k["d"]["point"], PRED_B["ki"])))', 'hw(st["ki0"]["d"]["point"] + 1.0, PRED_B["ki"])))'),
)


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("# ══ SELFTEST (fixtures and independent oracles")
    rows = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        for mid, part, cases, old, new in MUTANTS:
            if only and mid.split()[0] not in only:
                continue
            head = src[:cut]
            if head.count(old) != 1:
                rows.append((mid, "BAD-MUTANT (old text found %d times above the selftest line)" % head.count(old)))
                print("  %-70s %s" % (mid, rows[-1][1]), flush=True)
                continue
            mut = head.replace(old, new) + src[cut:]
            p = os.path.join(td, "gap_fix_%s.py" % mid.split()[0])
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(mut)
            rc, out = _child(["--selftest-part", part, "--only"] + list(cases) + ["--quiet"], env_extra={"GAPFIX_TOOLS_DIR": HERE}, src=p)
            rows.append((mid, "KILLED" if rc != 0 else "SURVIVED"))
            print("  %-70s %s" % (mid, rows[-1][1]), flush=True)
    killed = sum(1 for _m, r in rows if r == "KILLED")
    print("%s MUTANTS: %d of %d killed" % (TAG, killed, len(rows)))
    return 0 if killed == len(rows) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--selftest-part", choices=("a", "b"))
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--part", choices=("a", "b", "all"), default=None)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--data-root", default=None, help="the checkout whose DBs, results and run dirs are read (set before any import)")
    a = ap.parse_args(argv)
    if a.data_root:
        os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(a.data_root)
        os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(a.data_root)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.selftest:
        return selftest(only=a.only)
    if a.selftest_part:
        return selftest_part(a.selftest_part, only=a.only, quiet=a.quiet)
    if a.mutants:
        return run_mutants(only=a.only)
    part = a.part or ("all" if a.dry_run else None)
    if a.run and part not in ("a", "b"):
        refuse("--run needs --part a or --part b (one part per process: their imports must not meet)")
    root = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
    if a.dry_run and part == "all":
        rc = 0
        for p_ in ("a", "b"):
            r_, out = _child(["--dry-run", "--part", p_] + (["--data-root", a.data_root] if a.data_root else []))
            sys.stdout.write(out)
            rc = rc or r_
        return rc
    if part == "a":
        return dry_run_a() if a.dry_run else run_a()
    if a.dry_run:
        return dry_run_b(root)
    run_b(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
