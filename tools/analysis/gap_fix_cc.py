"""gap_fix_cc.py: GAP-FIX-CC -- GAP-FIX re-run, its criteria words unchanged, on the three content-closed MMLU-Pro re-draw trees
Q_e1sd1-3 (qwen3; DECIDING, GF1-CC) and on the nomic_raw trees N-raw (af_clean_s42's split), N_e1sd2, N_e1sd3 (second embedder;
GF1-N, SCORED SECONDARY, never joined); N_e1sd1 DESCRIPTIVE. Do five within-parent Lloyd passes close each tree's purity gap to a
flat vMF mixture at its own k? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU readout.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — GAP-FIX-CC: GAP-FIX re-run with its criteria words
  unchanged on the three content-closed MMLU-Pro re-draw trees ..." L25029-L25041 (_as_of e83b59d5, the commit that wrote it, parent
  d8ab39fa); the registrar's record L24950-L24956. GF1 (per tree), GF1-CC (DECIDING), GF1-N (scored secondary), Support (a)-(g),
  P1-P6, F-GFC, WHAT THIS RESULT WILL NOT SHOW. The registration governs; this docstring restates.
  RULINGS APPLIED (pre-data, the registrar's): C-1 / B-3 (L25147-L25157: F-GFC is scored from the printed 'LB(I_P) > 0 on m of c'
  line, FIRES iff m >= 2; the tool's own FIRES / NOT FIRED line is the all-c reading and NOT of record; no code change); P-1 option (b)
  ("## Registrar's record 2026-10-08 (insertion only; zero calls; nothing run; pre-data) — rulings GAP-FIX-CC P-1 (seed replacement),
  the R1 twin rule ..." L25212-L25219, _as_of 6098f22f, parent 8daf8220), with the owed P-2 / P-3 of docs/reviews/POSTRUN_gap-fix-cc.md
  (443cf9ff) and C-2 of docs/reviews/READY_gap-fix-cc.md (3968447d): built in the 2026-10-08 delta (see RULING P-1 below).
  PILOT DISCLOSURE (the registration's): no 2026-10-07 exploratory number concerns GAP-FIX or these trees' flat mixtures; the files
  E:/TaxoArena_tmp/cert_split (results.json, VERIFIED_HEADLINE.txt), E:/TaxoArena_tmp/hier_tests (granularity_free, nesting,
  test3_fair_backoff + review dirs) and E:/TaxoArena_tmp/scpb/review_v3_synthesis.md were SEEN (pilot role only, never evidence).
  This script opens none of them.

LAUNCH SEQUENCE (the run-operator; ONE single-threaded python process; a POOL READER (rule 7): never beside a construction, a site
null or a JVM; E:/TaxoArena_tmp/busy.ps1 must exit 1 immediately before --dry-run and --run; from the main checkout, or from anywhere
with --data-root <main checkout>):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --selftest   # synthetic only; no DB opened
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gap_fix_cc.py --mutants    # every mutant must be KILLED
  python tools/analysis/gap_fix_cc.py --dry-run --nomic-leg <e1-guard|not-run>   # pool lines FIRST (e1_split_draws.load_real);
        # pins, splits, builds, guards, hygiene, fit / held-out counts, WP structure, cost; NO M1, NO hit, NO statistic; writes nothing
  python tools/analysis/gap_fix_cc.py --run --nomic-leg <e1-guard|not-run>       # about 10-20 CPU-min; WRITE-ONCE outcome of record:
        # experiment_results/gap_fix_cc/gap_fix_cc_outcome.txt and gap_fix_cc_arms.csv (both refused before any work if present)
  --nomic-leg is REQUIRED with --dry-run / --run (no default): the READY review rules which (the registration's EMBEDDER GATE):
  e1-guard = the nomic leg runs through the E1 readout's own-embedder path with its [EMB-GUARD] vmfMu check (e1_split_draws.check_tree:
  embedder_guard.guard through e1_readout.text_join_guard, both discriminators must REFUSE); not-run = GF1-N prints NOT RUN.
  Outputs are never committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_gap_fix_cc with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar.

THE INSTRUMENT. tools/analysis/gap_fix.py (blob 7c0691e8, GAP-FIX's instrument of record) is IMPORTED UNCHANGED and blob-verified:
its refine / centroids / lloyd_step / leaf_parent_masks (LLOYD-WP exactly as GAP-FIX: the operative clause, per-pass parent of the
item's CURRENT leaf; an emptied leaf keeps its last centroid; held-out filed flatLeaf to the refined centroids), gf1 / gf1_refuted
(GF1's one clause) and paired_m1 (FLAT-MIX-MMLU C1's twin-group interval: 1,000 whole stem_key group resamples, seed 20260926,
percentile). BUILDER DECLARATION B-1: "gap_fix.py extended by a delta" is built as this separate driver importing gap_fix.py
unchanged, so GAP-FIX's blob of record (its outcome's pin) stays valid; the delta is this file.
  WORLD (data). e1_split_draws.py (blob 0414b8fa; its own import pins e1_readout 88f7990c, e1sd_split_draw 0c12e9b8, e1sd_launch
  bdbb3fc6) load_real(): pool lines first, the three e1sd splits re-derived byte-equal (held-out = the split's EVAL texts 3,598 /
  3,522 / 3,500; label set = every other distinct corpus text), the six builds, the E1 identity world (p2dca held-out 3,445 and
  readout train 8,324; af_clean_s42; N-raw), vectors BY TEXT in each tree's own embedder (qwen3_raw in place; nomic_raw only through
  embedder_arms.open_arm_reader), the 256 slice renormalised (e1_readout.unit). No new reader.
  GUARDS / HYGIENE per tree: e1_split_draws.check_tree (run-dir leaves == snapshot graph leaves; [EMB-GUARD] ADMIT on its own
  vectors; both discriminators REFUSE) then, for e1sd trees, e1_split_draws.hygiene (fit texts all TRAIN of the split, no held-out
  text, no shared stem_key: all 0); for N-raw and af_clean_s42 (p2dca): fit texts outside the label set 0, fit texts equal to a
  held-out text 0 (REFUSED otherwise; FLAT-MIX-MMLU's rule), fit texts sharing a held-out stem_key printed. A qwen3 guard refusal
  REFUSES the run; a nomic refusal makes the whole nomic leg NOT RUN (printed with the reason; the gate is the leg's).
  FIT SET per tree = the snapshot graph's root-region member ids -> corpus texts (e1_split_draws' text join), sorted, its own
  embedder, 256 slice, unit rows (the rows FM.fit_set / FM.fit_matrix build for af_clean_s42; identity I-2 below proves it).
  V0..V4 = flat vMF mixtures at the tree's own leaf count, seeds 0-4, FITTED HERE on that fit set (FLAT-MIX-MMLU's fitter
  flat_mix_mmlu.vmf_em unchanged: k-means++ seeding, hard step, soft EM, Banerjee kappa, max_iter 200, tol 1e-6; ruling B6: a
  degenerate seed is B6-VOID, see RULING P-1); assignment MAP. V0 (seed 0, or its rule replacement) is the comparator; V1-V4 give
  spread_V.
  RULING P-1 (option (b)), fit_v_rule: slot Vj starts at seed j; a B6-VOID seed is replaced IN ITS SLOT by the lowest seed of 5..9
  not yet used on that tree (a seed tried and found VOID counts as used; the pool is shared by the five slots of one tree, slots in
  order V0..V4); each slot prints 'VFIT <tree> V<j>: seed s B6 OK (...)' or 'VFIT <tree> V<j>: seed s B6-VOID -> seed t OK REPLACED
  (ruling P-1) (...)'; if 5..9 are exhausted the slot prints '... -> VOID-TREE', no further slot is fitted, and the tree drops out:
  no statistic, '[<tree>] leg ...: VOID-TREE (...)' in the outcome, a VOID-TREE row in its leg that is NOT GAP-SHOWN (GF1-CC / GF1-N
  keep the registered words: the word on >= 2 of the GAP-SHOWN trees, NOT EVALUABLE if fewer than 2). BUILDER DECLARATION B-7: a
  seed is B6-VOID iff flat_mix_mmlu.vmf_em (unchanged) refuses it with its own text citing ruling B6 (FM.B6): the one-member /
  degenerate cell of record, a k-means++ seed owning no point, a component losing all responsibility; any other refusal stops the run
  naming tree, slot and seed. BUILDER DECLARATION B-8 (for the registrar; no registered word changes): a VOID-TREE qwen3 tree is not
  GAP-SHOWN in P1, is printed 'VOID-TREE NOT SCORED' in P2 / P3 (tally 'k of <scored> HELD (n VOID-TREE not scored: ...)'), and does
  not count towards P5's '>= 2 of 3'.
  P-2: --dry-run fits V0..V4 on the real fit sets (label-free; no M1), prints every VFIT line, any VOID-TREE, and 'V FITS (P-2,
  label-free): <n> slots fitted, <r> by a ruling P-1 replacement; VOID-TREE <v>; CPU <s>'. P-3: every refusal raised while a tree is
  processed (--run: V fits, arms, identity I-1, statistics; --dry-run: structure, V fits; a qwen3 guard) reads
  '[GAP-FIX-CC] REFUSED on tree <name>: ...'. Labels only in M1's scorer; held-out never
  enters a centroid or a V fit. M2 NOT RUN (registered; printed as such).
  ARMS per tree: T (as built, flatLeaf), V0-V4, LLOYD-WP and LLOYD-GL at T = 0, 1, 2, 5, 10 and convergence (cap 300). M1 =
  flat_mix_mmlu.m1_block (anchor_free_readout.score_cells: majority category of the label set per cell; held-out hit iff equal).
  READOUTS per tree: D_T = M1(T) - M1(V0); D_R = M1(T-WP 5) - M1(V0); I_R = D_R - D_T = M1(T-WP 5) - M1(T); NEW (W-2): I_0 =
  M1(WP_0) - M1(T) (the re-centring) and I_P = M1(WP_5) - M1(WP_0) (the passes); each with its twin-group 95% interval (B 1,000,
  seed 20260926); D(GL 5) descriptive. bar = max(MDE80, spread_V) with the tree's OWN spread_V (max - min M1 over V0..V4) and its OWN
  MDE80 = 2.80 x sqrt(discordance(T-WP 5 vs V0) / n) (BUILDER DECLARATION B-2: "its own MDE80 from its measured discordance" read as
  GAP-FIX's Support (e) measured form; Kish printed beside, never multiplied in: the registered DEFF is 1.0).
  GF1 per tree (GAP-FIX's words): CLOSED iff UB(D_R) >= 0 AND I_R > 0 with LB(I_R) > 0; OPEN iff UB(D_R) < 0 AND |D_R| > bar; PARTIAL
  otherwise. PRECONDITION: GAP-SHOWN iff UB(D_T) < 0; otherwise NO-GAP, not counted. Each condition is printed with 'holds' or
  'fails' beside it (GAP-FIX D-3). A CLOSED tree whose I_P interval contains 0 is printed 'CLOSED by re-centring, not by the passes'.
  FAILS (rule 8) per tree: CLOSED refuted by UB(D_R) < 0 or LB(I_R) <= 0.
  GF1-CC (DECIDING; Q_e1sd1-3): the GF1 word that holds on >= 2 of the GAP-SHOWN qwen3 trees; NOT EVALUABLE if fewer than 2 are
  GAP-SHOWN; MIXED if no word holds on 2. FAILS: GF1-CC CLOSED refuted by 2 GAP-SHOWN trees not CLOSED.
  GF1-N (SCORED SECONDARY; N-raw, N_e1sd2, N_e1sd3): the same rule; never joined with GF1-CC (S4); NOT RUN if the gate is not met.
  N_e1sd1 (28 leaves): its GF1 rule printed DESCRIPTIVE only, never counted.
  F-GFC fires iff GF1-CC reads CLOSED with LB(I_P) > 0 on those trees. BUILDER DECLARATION B-3 (for the registrar): "those trees"
  read as EVERY GAP-SHOWN qwen3 tree that reads CLOSED (the trees carrying GF1-CC's word); the count "LB(I_P) > 0 on m of c CLOSED
  trees" is printed beside so the other reading (>= 2) is visible; they differ only when 3 trees read CLOSED and exactly 2 have
  LB(I_P) > 0.
  PREDICTIONS P1-P6 as registered: bands HELD iff the point lies in the CLOSED interval (per tree; the count printed); words by Brier.
  BUILDER DECLARATION B-4: P6's lumped class "NOT EVALUABLE / MIXED / NOT RUN" (0.25) is one Brier class OTHER.
  IDENTITY PRECONDITIONS (a failed precondition otherwise; nothing of the trees is printed before they hold):
  I-1 every tree's T arm reproduces its recorded flatLeaf top-1 (E1-SPLIT-DRAWS outcome: Q 0.7268 / 0.7354 / 0.7297, N 0.5545 /
      0.6860 / 0.6503; E1: N-raw 0.6813), its leaf count and its held-out n.
  I-2 (BUILDER DECLARATION B-5, not registered: GAP-FIX's own practice) af_clean_s42 through THIS path (text-joined fit set 8,125, the
      E1 qwen3 vectors, gap_fix.refine, V0 READ from FLAT-MIX-MMLU's pinned state via gap_fix.v_parts) reproduces GAP-FIX's outcome:
      hits T 2504 / V0 2652 / WP_0 2535 / WP_5 2550 of 3445, D_T -0.0430 [-0.0557, -0.0293], D_R -0.0296 [-0.0412, -0.0168], I_R
      +0.0134 [+0.0046, +0.0218], I_0 +0.0090 [+0.0015, +0.0163]; I_P printed beside the POSTRUN's +0.0044 [+0.0000, +0.0087].
  NOT APPLICABLE (stated in the outcome): no judge verdict (no wrong(established), no tie conventions A / B); zero calls (no call
  cache, pilot or truncation guard); M2 not run; LLOYD-WP-A not run (GAP-FIX's reading check, not registered here).
  GAP-FIX's carried defects: D-1 (the OPEN bar band MDE80 < |D_R| <= spread_V untested) -> C-PLANT's band cases and mutant M05;
  D-3 ('fails' beside each failed GF1 condition) -> gf1_condition_lines; D-4 (stdout cp1252 crash) -> main() reconfigures stdout and
  stderr to utf-8, C-MAIN runs a child under PYTHONIOENCODING=cp1252; D-5 (resp_structure_common.py:144 alpha overflow) NOT
  APPLICABLE: this path imports no 3PL / resp_structure code, and editing that file would break the blob pins of other records
  (BUILDER DECLARATION B-6, a deviation for the registrar).

SELFTEST (--selftest; synthetic worlds built in memory, scratch on E: via scratch_dir; NO DB is opened, the real loader never runs):
  C-PURE aggregate() / gfc_fires() / predictions by value, every branch and order; C-PLANT tree_stats + render on planted per-question
  arms with exact interval edges (all-zero differences give [0, 0]); C-E2E run_core() on three fixture worlds (each tree its own
  split; within-parent arcs of three clusters) whose words are known by construction, every printed point against an independent
  oracle (plain loops: gap_fix's o_lloyd / o_nearest / o_score / o_parent_sets, an own MAP loop), the outcome write-once; C-NOMIC the
  gate (not-run, a nomic guard refusal, a qwen3 guard refusal); C-DRY the dry-run computes no measure and writes nothing; C-REFUSE
  identity I-1 / I-2, leaf count, held-out n, fit / held-out overlap, outputs present; C-VSEED ruling P-1 by value (the slot seeds and
  the exact seed sequence tried, through a patched FM.vmf_em raising FLAT-MIX-MMLU's own B6 text: none VOID, 0, 0+5, 0+5+2, V3, V1+V3,
  4+5..8 -> 9, 0+5..9 -> VOID-TREE, a pool exhausted across slots, a non-B6 refusal; the REAL fitter on cells of identical points ->
  VOID-TREE and on a regular set -> seeds 0-4); C-RENDER render_all on planted per-tree words (C-2: R2 a NO-GAP CLOSED tree with
  LB(I_P) <= 0 beside GF1-CC CLOSED -> 'LB(I_P) > 0 on 2 of 2', FIRES; R5 the GF1-N FAILS line from the N rows in both directions;
  VOID-TREE rows in GF1-CC / GF1-N / P1 / P2 / P5); C-E2E-VOID run_core and dry_core end to end on the fixture worlds with VOID seeds
  (the replacement printed, V0 hits / word / D_R / bar equal to the oracle fitted at seed 5, GF1-CC equal to an oracle aggregate, a
  VOID-TREE dropped (CC, N, N1), the arms CSV, P-2's dry-run lines and summary by value, P-3 on --run and --dry-run); C-MAIN the CLI
  (--nomic-leg required, unknown value fatal, cp1252 stdout). MUTANTS: the table in MUTANTS below; --mutants runs each on a copy under scratch_dir's E: dir, the named
  selftest cases in a child; the results are in the commit message.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import sys           # noqa: E402
import io            # noqa: E402
import csv           # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import tempfile      # noqa: E402
import contextlib    # noqa: E402
import subprocess    # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

if "--data-root" in sys.argv[:-1]:             # BEFORE any import that fixes DATA_ROOT (flat_mix_mmlu / pool_guard read it on import)
    _dr = os.path.abspath(sys.argv[sys.argv.index("--data-root") + 1])
    os.environ["TAXOARENA_DATA_ROOT"] = _dr
    os.environ["TAXOARENA_RESULTS_ROOT"] = _dr
HERE = os.environ.get("GAPFIXCC_TOOLS_DIR") or os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import scratch_dir   # noqa: E402,F401  (TEMP-SPRAWL: tempfile on E:, removed at exit)

TAG = "[GAP-FIX-CC]"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — GAP-FIX-CC: GAP-FIX re-run with its '
            'criteria words unchanged on the three content-closed MMLU-Pro re-draw trees ..." L25029-L25041 (_as_of e83b59d5, parent '
            'd8ab39fa)')
IMPORT_PINS = {"gap_fix.py": "7c0691e8444848f3669e46d33adbfa2b7af31a20",          # GAP-FIX's instrument of record (imported unchanged)
               "e1_split_draws.py": "0414b8fa6816ba0cf11765cad1ce5b2bc260400c"}   # the e1sd world loader (real mode only)
OUT_REL = "experiment_results/gap_fix_cc"
OUTCOME = "gap_fix_cc_outcome.txt"
ARMS_CSV = "gap_fix_cc_arms.csv"
NOMIC_LEGS = ("e1-guard", "not-run")


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


def verify_pin(name):
    got = pins_of(os.path.join(HERE, name))["blob"]
    if got != IMPORT_PINS[name]:
        refuse("tools/analysis/%s is blob:%s, not the pinned blob:%s" % (name, got[:8], IMPORT_PINS[name][:8]))
    return "[PIN] tools/analysis/%s blob:%s (pinned; verified)" % (name, got[:8])


verify_pin("gap_fix.py")
import gap_fix as GF   # noqa: E402  (GAP-FIX's instrument, unchanged)
GF._a_mods()           # blob-verifies flat_generality / flat_mix_mmlu and imports them (no DB is opened by an import)
FM = GF.FM
SDR = None             # e1_split_draws, imported by the real loader only


def write_once(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def say(L, s=""):
    print(s)
    L.append(s)


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# registered constants
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
REG = dict(t_steps=(1, 2, 5, 10), t_decide=5, t_cap=300, seeds=(0, 1, 2, 3, 4), v_pool=(5, 6, 7, 8, 9),
           se_dr=0.00630, se_ir=0.00433, mde_dr=0.0176, mde_ir=0.0121, disc_dr=0.1388, disc_ir=0.0656, n_plan=3500, mde_k=2.8)
WORDS = ("CLOSED", "PARTIAL", "OPEN")
PRED = dict(P1=0.55, P2=(-0.055, -0.005), P3=(-0.040, 0.002),
            P4=(("PARTIAL", 0.45), ("CLOSED", 0.20), ("NOT EVALUABLE", 0.15), ("OPEN", 0.10), ("MIXED", 0.10)),
            P5=0.75, P6=(("PARTIAL", 0.40), ("CLOSED", 0.20), ("OPEN", 0.15), ("OTHER", 0.25)))
LEGS = {"CC": "DECIDING (GF1-CC; qwen3)", "N": "SCORED SECONDARY (GF1-N; nomic_raw)", "N1": "DESCRIPTIVE ONLY (never counted)"}
REAL_TREES = (
    dict(name="Q_e1sd1", leg="CC", arm="Q", split=1, leaves=80, n=3598, top1="0.7268"),
    dict(name="Q_e1sd2", leg="CC", arm="Q", split=2, leaves=87, n=3522, top1="0.7354"),
    dict(name="Q_e1sd3", leg="CC", arm="Q", split=3, leaves=72, n=3500, top1="0.7297"),
    dict(name="N-raw", leg="N", arm="N", split=0, leaves=84, n=3445, top1="0.6813"),
    dict(name="N_e1sd2", leg="N", arm="N", split=2, leaves=80, n=3522, top1="0.6860"),
    dict(name="N_e1sd3", leg="N", arm="N", split=3, leaves=71, n=3500, top1="0.6503"),
    dict(name="N_e1sd1", leg="N1", arm="N", split=1, leaves=28, n=3598, top1="0.5545"),
)
GAPFIX_ID = dict(name="af_clean_s42", leaves=82, n=3445, fit_n=8125, hits=dict(T=2504, V0=2652, WP_0=2535, WP_5=2550),
                 ci=dict(D_T="-0.0430 [-0.0557, -0.0293]", D_R="-0.0296 [-0.0412, -0.0168]", I_R="+0.0134 [+0.0046, +0.0218]",
                         I_0="+0.0090 [+0.0015, +0.0163]"),
                 ip_postrun="+0.0044 [+0.0000, +0.0087]")
WILL_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): anything about the engine's construction (a post-hoc refinement); a "
                 "joined qwen3 + nomic word (S4); anything about af_clean_s42's qwen3 tree beyond GAP-FIX; a key-information claim (M2 "
                 "not run); GAP-FIX's part (b) (not re-run); a corpus other than MMLU-Pro.")
FGFC_FIRES = ("FALSIFIER F-GFC FIRES (GF1-CC CLOSED with LB(I_P) > 0 on those trees): the passes, not the re-centring, remove the gap "
              "on content-closed re-draws; GAP-FIX's reading (PARTIAL; the passes not shown > 0, W-2) is overturned as the general "
              "case; FLAT-MIX-MMLU's LIMITATION sentence takes the bracket 'removed by a within-parent Lloyd refinement on >= 2 of 3 "
              "content-closed re-draws (GAP-FIX-CC)'; a refinement step becomes a candidate engine change for a new registration with "
              "its own go")
VERDICT_F = ("(f) VERDICT LINE (registered): at GAP-FIX's D_R (-0.030) as the prediction, CLOSED vs not is SCOREABLE (0.030 > 0.0176); "
             "OPEN vs PARTIAL is DESCRIPTIVE-ONLY whenever |D_R| lies within 0.0176 of the tree's own bar; I_R and I_P DESCRIPTIVE-ONLY; "
             "a tree with D_T near 0 makes GF1 uninformative there (the precondition)")
STRUCT_G = ("(g) STRUCTURAL (registered, as GAP-FIX): CLOSED reachable; OPEN's bar keeps spread_V at any n; WP bounded by the parent "
            "constraint")


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# pure: words, aggregation, falsifier, predictions
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def in_band(x, band):
    return bool(band[0] <= x <= band[1])


def hw(x, band):
    return "HELD" if in_band(x, band) else "FAILED"


def brier_multi(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def brier_event(p, happened):
    return float((p - (1.0 if bool(happened) else 0.0)) ** 2)


def f4(x):
    return "%+.4f" % x


def ci4(p):
    return "%s [%s, %s]" % (f4(p["d"]), f4(p["lo"]), f4(p["hi"]))


def aggregate(rows):
    """rows: [(name, gap_shown, word)] -> (word, counted words). The GF1 word on >= 2 GAP-SHOWN trees; NOT EVALUABLE if fewer than 2
    trees are GAP-SHOWN; MIXED if no word holds on 2 (unique: at most one word can hold on 2 of <= 3 trees)."""
    counted = [w for _n, g, w in rows if bool(g)]
    if len(counted) < 2:
        return "NOT EVALUABLE", counted
    for w in WORDS:
        if sum(1 for x in counted if x == w) >= 2:
            return w, counted
    return "MIXED", counted


def closed_refuted(rows):
    """FAILS (rule 8): the aggregate CLOSED is refuted by 2 GAP-SHOWN trees not CLOSED."""
    return bool(sum(1 for _n, g, w in rows if bool(g) and w != "CLOSED") >= 2)


def gfc_fires(word, closed_stats):
    """F-GFC: GF1-CC CLOSED with LB(I_P) > 0 on every GAP-SHOWN tree that reads CLOSED (B-3). closed_stats: [I_P dict] of those trees.
    -> (fires, m with LB > 0, c CLOSED trees)."""
    m = sum(1 for ip in closed_stats if bool(ip["lo"] > 0))
    c = len(closed_stats)
    return bool(word == "CLOSED" and c > 0 and m == c), m, c


def gf1_condition_lines(R):
    """GF1 per tree with 'holds' / 'fails' beside each condition (GAP-FIX D-3)."""
    dr, ir, bar = R["dr"], R["ir"], R["bar"]

    def hf(c):
        return "holds" if bool(c) else "fails"
    return [
        "    CLOSED needs: UB(D_R) %s >= 0 [%s]; I_R %s > 0 [%s]; LB(I_R) %s > 0 [%s]" % (
            f4(dr["hi"]), hf(dr["hi"] >= 0), f4(ir["d"]), hf(ir["d"] > 0), f4(ir["lo"]), hf(ir["lo"] > 0)),
        "    OPEN needs:   UB(D_R) %s < 0 [%s]; |D_R| %.4f > bar %.4f [%s]" % (
            f4(dr["hi"]), hf(dr["hi"] < 0), abs(dr["d"]), bar, hf(abs(dr["d"]) > bar)),
    ]


def tree_word_line(R):
    w = R["word"]
    extra = ""
    if w == "CLOSED" and bool(R["ip"]["lo"] <= 0 <= R["ip"]["hi"]):
        extra = " -- CLOSED by re-centring, not by the passes (I_P %s contains 0)" % ci4(R["ip"])
    return "    GF1 (this tree): %s%s%s" % (w, extra, "" if R["gap"] else " -- NO-GAP: UB(D_T) %s >= 0, NOT COUNTED" % f4(R["dt"]["hi"]))


def predictions(cc, word_cc, word_n):
    """P1-P6 by value. cc: the three qwen3 tree stats (in order); a VOID-TREE (ruling P-1) carries void=True and no number: it is not
    GAP-SHOWN (P1), NOT SCORED in P2 / P3 (the tally names it) and does not count towards P5 (BUILDER DECLARATION B-8)."""
    L = []
    live = [R for R in cc if not R.get("void")]
    vnote = "" if len(live) == len(cc) else " (%d VOID-TREE not scored: %s)" % (
        len(cc) - len(live), ", ".join(R["name"] for R in cc if R.get("void")))
    gs = sum(1 for R in cc if R["gap"])
    e1 = bool(gs == 3)
    L.append("  P1 GAP-SHOWN on 3 of 3 qwen3 trees, probability 0.55: %d of 3 -> %s; Brier %.4f" % (
        gs, "occurred" if e1 else "did not occur", brier_event(PRED["P1"], e1)))
    def per(key, band):
        out, hs = [], []
        for R in cc:
            if R.get("void"):
                out.append("%s VOID-TREE NOT SCORED" % R["name"])
                continue
            h = in_band(R[key]["d"], band)
            hs.append(h)
            out.append("%s %s %s" % (R["name"], f4(R[key]["d"]), "HELD" if h else "FAILED"))
        return out, hs
    t2, h2 = per("dt", PRED["P2"])
    L.append("  P2 D_T per qwen3 tree, band [-0.055, -0.005]: %s -> %d of %d HELD%s" % ("; ".join(t2), sum(h2), len(h2), vnote))
    t3, h3 = per("dr", PRED["P3"])
    L.append("  P3 D_R per qwen3 tree, band [-0.040, +0.002]: %s -> %d of %d HELD%s" % ("; ".join(t3), sum(h3), len(h3), vnote))
    L.append("  P4 GF1-CC (PARTIAL 0.45, CLOSED 0.20, NOT EVALUABLE 0.15, OPEN 0.10, MIXED 0.10): observed %s -> Brier (5-class) %.4f" % (
        word_cc, brier_multi(PRED["P4"], word_cc)))
    k5 = sum(1 for R in live if bool(R["i0"]["d"] > R["ip"]["d"]))
    e5 = bool(k5 >= 2)
    L.append("  P5 I_0 > I_P at the point on >= 2 of 3 qwen3 trees, probability 0.75: %d of 3 (%s) -> %s; Brier %.4f" % (
        k5, "; ".join("%s VOID-TREE" % R["name"] if R.get("void") else "%s I_0 %s vs I_P %s" % (R["name"], f4(R["i0"]["d"]), f4(R["ip"]["d"]))
                      for R in cc),
        "occurred" if e5 else "did not occur", brier_event(PRED["P5"], e5)))
    cls = word_n if word_n in WORDS else "OTHER"
    L.append("  P6 GF1-N (PARTIAL 0.40, CLOSED 0.20, OPEN 0.15, NOT EVALUABLE / MIXED / NOT RUN 0.25 as one class OTHER, B-4): observed "
             "%s (class %s) -> Brier (4-class) %.4f" % (word_n, cls, brier_multi(PRED["P6"], cls)))
    return L, dict(p1=e1, p2=h2, p3=h3, p5=e5, k5=k5, p6_class=cls)


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# per tree: arms, statistics
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
_LABELS = [False]      # M1 (labels) is admitted in run_core only; the dry-run never sets it


def mat(space, texts):
    return np.stack([np.asarray(space[t], dtype=np.float64) for t in texts])


def cent_fn(C, leaf_ids):
    C = np.asarray(C, dtype=np.float64)
    return lambda Q: [leaf_ids[i] for i in FM.nearest_assign(Q, C)]


def map_fn(body):
    mu, ka, pi = np.asarray(body["mu"]), np.asarray(body["kappa"]), np.asarray(body["pi"])
    return lambda Q: ["c%03d" % i for i in FM.map_assign(Q, mu, ka, pi)]


def m1(fn, e):
    if not _LABELS[0]:
        refuse("[GFC-LABELS] a held-out / label-set measure was requested outside --run (the dry-run computes no measure)")
    if "Qt" not in e:
        e["Qt"] = mat(e["space"], [t for t, _ in e["train"]])
        e["Qh"] = mat(e["space"], [t for t, _ in e["heldout"]])
    sc, hits, _kh = FM.m1_block(fn, e["Qt"], e["Qh"], e["train"], e["heldout"])
    return dict(m1=float(sc["acc"]), hits=int(sc["hits"]), per1=hits)


def is_b6_void(ex):
    """A V seed is B6-VOID iff FLAT-MIX-MMLU's fitter (unchanged) refused it citing ruling B6 (BUILDER DECLARATION B-7: every refusal
    vmf_em raises carries FM.B6: the one-member / degenerate cell of record, a seed owning no point, a component losing all
    responsibility); any other refusal is not a VOID and stops the run, naming the tree (P-3)."""
    return bool(FM.B6 in str(ex))


def fit_v_rule(X, k, name):
    """V0..V4 under ruling P-1 (option (b)). Slot j starts at seed j (REG seeds); a B6-VOID seed is replaced IN ITS SLOT by the lowest
    seed of 5..9 not yet used on this tree (a seed tried and found VOID counts as used); if 5..9 are exhausted the tree is VOID-TREE.
    -> (V by slot or None, printed lines, void reason or None). Label-free (the fit set only)."""
    out, lines = {}, []
    used = set(REG["seeds"])
    for j, s0 in enumerate(REG["seeds"]):
        chain, s = [], s0
        while True:
            try:
                r = FM.vmf_em(X, k, s)
            except SystemExit as ex:
                if not is_b6_void(ex):
                    raise SystemExit("%s REFUSED: [GFC-VFIT] tree %s V%d seed %d (not a B6 VOID): %s" % (TAG, name, j, s, ex))
                chain.append("seed %d B6-VOID" % s)
                free = [t for t in REG["v_pool"] if t not in used]
                if not free:
                    why = "VOID-TREE (ruling P-1: slot V%d %s; seeds %d-%d exhausted; the tree drops out under the registered words)" % (
                        j, " -> ".join(chain), REG["v_pool"][0], REG["v_pool"][-1])
                    lines.append("VFIT %s V%d: %s -> VOID-TREE" % (name, j, " -> ".join(chain)))
                    return None, lines, why
                s = free[0]
                used.add(s)
                continue
            break
        out["V%d" % j] = dict(rule="map", mu=r["mu"], kappa=r["kappa"], pi=r["pi"], iters=int(r["iters"]), converged=bool(r["converged"]),
                              mean_ll=float(r["mean_ll"]), seed=int(s))
        lines.append("VFIT %s V%d: %s%s%s (converged %s, iters %d, mean ll %.4f)" % (
            name, j, "".join(c + " -> " for c in chain), "seed %d OK" % s if chain else "seed %d B6 OK" % s,
            " REPLACED (ruling P-1)" if chain else "", bool(r["converged"]), int(r["iters"]), float(r["mean_ll"])))
    return out, lines, None


def v_fit_entry(e, L):
    """The V fits of one admitted tree on ITS fit set (label-free; --dry-run (P-2) and --run). Prints the VFIT lines."""
    Xv = mat(e["space"], e["fit"])               # the fit set only (never the label set, never held-out)
    V, lines, void = fit_v_rule(Xv, len(e["tree"]["leaf_ids"]), e["name"])
    for ln in lines:
        say(L, ln)
    return V, void


def named(name, ex):
    """P-3: every refusal raised while one tree is processed names that tree."""
    return SystemExit("%s REFUSED on tree %s: %s" % (TAG, name, ex))


def tree_arms(e, vparts=None, identity_only=False):
    """Every arm of one admitted tree. vparts given (I-2): V read, never fitted. -> (arms, info)."""
    tr = e["tree"]
    leaf_ids = list(tr["leaf_ids"])
    k = len(leaf_ids)
    X = mat(e["space"], e["fit"])
    mask, par, roots = GF.leaf_parent_masks(tr["byid"], leaf_ids)
    z0 = np.argmax(X @ np.asarray(tr["leaf_mu"]).T, axis=1)          # anchor_free_readout.route (flatLeaf, the fit set)
    if vparts is None:
        refuse("[GFC-VFIT] tree %s: tree_arms needs its V fits (v_fit_entry / I-2's read V0)" % e["name"])
    V = vparts
    t_keep = REG["t_steps"]
    variants = ("WP",) if identity_only else ("WP", "GL")
    ref = {v: GF.refine(X, z0, tr["leaf_mu"], mask, v, t_keep, REG["t_cap"]) for v in variants}
    arms = {"T": m1(cent_fn(tr["leaf_mu"], leaf_ids), e)}
    for nm in sorted(V):
        arms[nm] = m1(map_fn(V[nm]), e)
    tk = (0, REG["t_decide"]) if identity_only else (0,) + tuple(t_keep) + ("conv",)
    moved = {}
    for v in variants:
        for t in tk:
            st = ref[v]["steps"][t]
            nm = "%s_%s" % (v, t)
            arms[nm] = m1(cent_fn(st["C"], leaf_ids), e)
            moved[nm] = (float(np.mean(st["z"] != z0)), int(st["empty"]))
    info = dict(k=k, fit_n=len(e["fit"]), conv={v: (ref[v]["t_conv"], ref[v]["converged"], ref[v]["moves"][:12]) for v in variants},
                allowed=Counter(int(x) for x in mask.sum(axis=1)), root_parent=sum(1 for p in par if p in roots), moved=moved,
                vdiag={nm: (V[nm].get("seed"), V[nm].get("iters"), V[nm].get("converged"), V[nm].get("mean_ll"),
                            hashlib.sha256(np.ascontiguousarray(np.asarray(V[nm]["mu"], dtype=np.float64)).tobytes()).hexdigest()[:16])
                       for nm in sorted(V)})
    return arms, info


def tree_stats(name, leg, arms, groups, n):
    """The registered per-tree quantities from the per-question arms (pure given arms; C-PLANT calls it on planted arms)."""
    def pm(a, b):
        return GF.paired_m1(arms[a]["per1"], arms[b]["per1"], groups)
    td = "WP_%d" % REG["t_decide"]
    dt, dr, ir = pm("T", "V0"), pm(td, "V0"), pm(td, "T")
    i0, ip = pm("WP_0", "T"), pm(td, "WP_0")
    dgl = pm("GL_%d" % REG["t_decide"], "V0") if ("GL_%d" % REG["t_decide"]) in arms else None
    vm1 = [arms["V%d" % s]["m1"] for s in REG["seeds"]]
    spread_v = float(FM.spread(vm1))
    mde = REG["mde_k"] * math.sqrt(dr["disc"] / n)
    bar = max(mde, spread_v)
    gap = bool(dt["hi"] < 0)
    word = GF.gf1(dr["d"], dr["hi"], ir["d"], ir["lo"], bar)
    return dict(name=name, leg=leg, n=n, dt=dt, dr=dr, ir=ir, i0=i0, ip=ip, dgl=dgl, spread_v=spread_v, mde=mde, bar=bar, gap=gap,
                word=word, refuted=bool(GF.gf1_refuted(dr["hi"], ir["lo"])), arms=arms)


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# admission (guards, hygiene, nomic gate) and identity
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def admit(W, nomic_leg, L):
    """Guards and hygiene per tree; the nomic gate. Sets e['status'] and e['fit']; -> (nomic leg status line or None)."""
    if nomic_leg not in NOMIC_LEGS:
        refuse("--nomic-leg %r is not one of %s" % (nomic_leg, NOMIC_LEGS))
    nomic_off = None
    if nomic_leg == "not-run":
        nomic_off = "NOT RUN (--nomic-leg not-run: the READY review ruled the embedder gate not met)"
    for e in W["entries"]:
        if e["arm"] == "N" and nomic_off is not None:
            e["status"] = nomic_off
            continue
        try:
            fit = e["guard"](L)
        except SystemExit as ex:
            if e["arm"] != "N":
                raise named(e["name"], ex) from None
            msg = str(ex)
            if e["leg"] == "N":
                nomic_off = "NOT RUN (the [EMB-GUARD] / hygiene of %s refused: %s)" % (e["name"], msg[:200])
            e["status"] = "NOT RUN (guard refused: %s)" % msg[:200]
            say(L, "%s %s: guard REFUSED -> %s" % (TAG, e["name"], e["status"]))
            continue
        hygiene_core(e, fit)
        e["fit"] = sorted(fit)
        e["status"] = "ADMITTED"
        if len(e["tree"]["leaf_ids"]) != e["leaves"]:
            refuse("[GFC-LEAVES] %s has %d leaves, registered %d" % (e["name"], len(e["tree"]["leaf_ids"]), e["leaves"]))
        if len(e["heldout"]) != e["n"]:
            refuse("[GFC-N] %s held-out %d, registered %d" % (e["name"], len(e["heldout"]), e["n"]))
    if nomic_off is not None:
        for e in W["entries"]:
            if e["arm"] == "N" and e["leg"] == "N":
                e["status"] = nomic_off
    return nomic_off


def hygiene_core(e, fit):
    """This script's own check beside the guard's: no held-out text in the fit set; the fit set inside the label set."""
    ho = set(t for t, _ in e["heldout"])
    tr = set(t for t, _ in e["train"])
    over = len(set(fit) & ho)
    outside = len(set(fit) - tr)
    if over or outside:
        refuse("[GFC-HYGIENE] %s: %d fit texts are held-out texts, %d fit texts are outside the label set (must be 0 / 0)" % (
            e["name"], over, outside))


def identity_top1(e, arms):
    got = "%.4f" % (arms["T"]["hits"] / float(len(e["heldout"])))
    if got != e["top1"]:
        refuse("[GFC-IDENTITY] %s: T top-1 %s through this path, the record %s" % (e["name"], got, e["top1"]))
    return got


def identity_gapfix(G, L):
    """I-2: GAP-FIX's af_clean_s42 numbers through THIS path (V0 read, never fitted). Refuses on any difference."""
    if len(G["fit"]) != G["expect"]["fit_n"]:
        refuse("[GFC-IDENTITY-GF] %s: fit set %d texts, GAP-FIX's %d" % (G["name"], len(G["fit"]), G["expect"]["fit_n"]))
    arms, _info = tree_arms(G, vparts={"V0": G["v0"]}, identity_only=True)
    groups, _G = FM.twin_groups([t for t, _ in G["heldout"]])
    td = "WP_%d" % REG["t_decide"]

    def pm(a, b):
        return GF.paired_m1(arms[a]["per1"], arms[b]["per1"], groups)
    got_h = {"T": arms["T"]["hits"], "V0": arms["V0"]["hits"], "WP_0": arms["WP_0"]["hits"], "WP_5": arms[td]["hits"]}
    got_c = {"D_T": ci4(pm("T", "V0")), "D_R": ci4(pm(td, "V0")), "I_R": ci4(pm(td, "T")), "I_0": ci4(pm("WP_0", "T"))}
    ip = ci4(pm(td, "WP_0"))
    ex = G["expect"]
    bad = [k for k in ex["hits"] if got_h[k] != ex["hits"][k]] + [k for k in ex["ci"] if got_c[k] != ex["ci"][k]]
    if len(G["heldout"]) != ex.get("n", len(G["heldout"])):
        bad.append("n")
    if bad:
        refuse("[GFC-IDENTITY-GF] %s through this path: %s; GAP-FIX's outcome: %s" % (
            G["name"], {k: got_h.get(k, got_c.get(k)) for k in bad}, {k: ex["hits"].get(k, ex["ci"].get(k)) for k in bad}))
    say(L, "IDENTITY I-2 (GAP-FIX through this path) %s: fit %d; hits T %d / V0 %d / WP_0 %d / WP_5 %d of %d; D_T %s; D_R %s; I_R %s; "
           "I_0 %s -> REPRODUCED; I_P %s beside the POSTRUN's %s (%s)" % (
               G["name"], len(G["fit"]), got_h["T"], got_h["V0"], got_h["WP_0"], got_h["WP_5"], len(G["heldout"]), got_c["D_T"],
               got_c["D_R"], got_c["I_R"], got_c["I_0"], ip, ex["ip_postrun"], "equal" if ip == ex["ip_postrun"] else "DIFFERS"))
    return got_h, got_c, ip


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# render
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def sizes_line(info):
    return "allowed leaves per leaf (WP) %s; leaves whose parent is the root %d" % (
        ", ".join("%d: %d" % kv for kv in sorted(info["allowed"].items())), info["root_parent"])


def render_tree(e, R, info, groups_n, mbar):
    L = []
    L.append("[%s] leg %s | pool %s (%s) | held-out %d in %d stem_key twin groups (Kish %.4f) | k %d | fit set %d | label set %d | "
             "near-copies %s | identity I-1 T top-1 %s REPRODUCED" % (
                 e["name"], LEGS[e["leg"]], e["pool"], e["split_word"], R["n"], groups_n, mbar, info["k"], info["fit_n"], len(e["train"]),
                 "-" if e.get("near") is None else e["near"], e["top1"]))
    L.append("  structure: %s" % sizes_line(info))
    L.append("  passes: WP converged %s at t %d (moves %s); GL converged %s at t %d" % (
        info["conv"]["WP"][1], info["conv"]["WP"][0], info["conv"]["WP"][2], info["conv"]["GL"][1], info["conv"]["GL"][0]))
    L.append("  V fits (V0..V4: seed, iters, converged, mean ll, mu sha256-16; a seed >= 5 is the ruling P-1 replacement): %s" % "; ".join(
        "%s seed %s %s %s %.4f %s" % (nm, d[0], d[1], d[2], d[3], d[4]) for nm, d in sorted(info["vdiag"].items())))
    A = R["arms"]
    L.append("  arm       M1      hits    M1 - M1(V0)   M1 - M1(T)   fit moved  empty")
    for nm in ["T"] + ["V%d" % s for s in REG["seeds"]] + ["%s_%s" % (v, t) for v in ("WP", "GL")
                                                           for t in (0,) + tuple(REG["t_steps"]) + ("conv",)]:
        a = A[nm]
        mv = info["moved"].get(nm)
        L.append("  %-8s  %.4f  %5d/%d  %s       %s      %s" % (
            nm, a["m1"], a["hits"], R["n"], f4((a["hits"] - A["V0"]["hits"]) / float(R["n"])), f4((a["hits"] - A["T"]["hits"]) / float(R["n"])),
            "-" if mv is None else "%.4f     %d" % mv))
    L.append("  D_T = M1(T) - M1(V0) = %s -> %s" % (ci4(R["dt"]), "GAP-SHOWN (UB < 0)" if R["gap"] else "NO-GAP (UB >= 0; not counted)"))
    L.append("  D_R = M1(T-WP 5) - M1(V0) = %s" % ci4(R["dr"]))
    L.append("  I_R = M1(T-WP 5) - M1(T) = %s; of which I_0 (re-centring, WP_0 - T) = %s and I_P (the passes, WP_5 - WP_0) = %s" % (
        ci4(R["ir"]), ci4(R["i0"]), ci4(R["ip"])))
    if R["dgl"] is not None:
        L.append("  D(GL 5) = M1(T-GL 5) - M1(V0) = %s (descriptive)" % ci4(R["dgl"]))
    L.append("  bar = max(MDE80 %.4f (2.80 x sqrt(discordance %.4f / %d)), spread_V %.4f) = %.4f" % (
        R["mde"], R["dr"]["disc"], R["n"], R["spread_v"], R["bar"]))
    L.extend(gf1_condition_lines(R))
    L.append(tree_word_line(R))
    if R["refuted"]:
        L.append("    FAILS (rule 8): CLOSED is REFUTED on this tree (%s)" % "; ".join(x for x in (
            "UB(D_R) %s < 0" % f4(R["dr"]["hi"]) if R["dr"]["hi"] < 0 else "", "LB(I_R) %s <= 0" % f4(R["ir"]["lo"]) if R["ir"]["lo"] <= 0 else "") if x))
    else:
        L.append("    FAILS (rule 8): CLOSED is not refuted on this tree (UB(D_R) %s >= 0 and LB(I_R) %s > 0)" % (f4(R["dr"]["hi"]), f4(R["ir"]["lo"])))
    near = abs(abs(R["dr"]["d"]) - R["bar"])
    L.append("    verdict line on this tree: |D_R| %.4f lies %.4f from its bar %.4f -> OPEN vs PARTIAL %s; CLOSED vs not SCOREABLE by (f)" % (
        abs(R["dr"]["d"]), near, R["bar"], "DESCRIPTIVE-ONLY (within 0.0176)" if near <= REG["mde_dr"] else "beyond 0.0176 of the bar"))
    if e["leg"] == "N1":
        L.append("    N_e1sd1: DESCRIPTIVE ONLY (a construction stall under the qwen3-tuned bar, E1-SPLIT-DRAWS N1); never counted in GF1-N")
    return L


def support_lines(stats_all):
    r = REG
    L = ["SUPPORT (registered beside measured, per tree):",
         "  registered: (a) denominators 3,598 / 3,522 / 3,500 (nomic 3,445 / 3,522 / 3,500); (b) DEFF 1.0 (GAP-FIX PR-1, transported); "
         "(c) n_eff about 3,500; (d) SE(D_R) sqrt(0.1388 / 3,500) = 0.00630, SE(I_R) sqrt(0.0656 / 3,500) = 0.00433; (e) MDE80 D_R "
         "0.0176, I_R 0.0121"]
    for R, mbar, G in stats_all:
        n = R["n"]
        se_dr, se_ir = math.sqrt(R["dr"]["disc"] / n), math.sqrt(R["ir"]["disc"] / n)
        L.append("  %-8s n %d; twin groups %d; Kish m-bar %.4f (DEFF upper bound at rho = 1); n_eff %.0f; discordance D_R %.4f (registered "
                 "%.4f) -> SE %.5f (registered %.5f), MDE80 %.4f (registered %.4f); discordance I_R %.4f (registered %.4f) -> SE %.5f "
                 "(registered %.5f), MDE80 %.4f (registered %.4f)" % (
                     R["name"], n, G, mbar, n / mbar, R["dr"]["disc"], r["disc_dr"], se_dr, r["se_dr"], 2.8 * se_dr, r["mde_dr"],
                     R["ir"]["disc"], r["disc_ir"], se_ir, r["se_ir"], 2.8 * se_ir, r["mde_ir"]))
    L.append("  " + VERDICT_F)
    L.append("  " + STRUCT_G)
    return L


def leg_rows(W, stats, leg):
    """The leg's trees in order: the measured stats, or a VOID-TREE row (ruling P-1: not GAP-SHOWN, no number; drops out)."""
    out = []
    for e in W["entries"]:
        if e["leg"] != leg:
            continue
        if e["name"] in stats:
            out.append(stats[e["name"]])
        elif str(e.get("status", "")).startswith("VOID-TREE"):
            out.append(dict(name=e["name"], void=True, gap=False, word="VOID-TREE", status=e["status"]))
        else:
            refuse("[GFC-LEG] tree %s of leg %s has neither statistics nor a VOID-TREE status (%s)" % (e["name"], leg, e.get("status")))
    return out


def per_tree_text(R):
    if R.get("void"):
        return "%s VOID-TREE (ruling P-1; not counted)" % R["name"]
    return "%s %s%s" % (R["name"], R["word"], "" if R["gap"] else " (NO-GAP, not counted)")


def void_note(rows):
    v = [R["name"] for R in rows if R.get("void")]
    return "" if not v else "; VOID-TREE (ruling P-1, dropped out): %s" % ", ".join(v)


def render_all(W, stats, nomic_off):
    L = []
    cc = leg_rows(W, stats, "CC")
    rows_cc = [(R["name"], R["gap"], R["word"]) for R in cc]
    word_cc, counted = aggregate(rows_cc)
    L.append("")
    L.append("== GF1-CC (DECIDING; qwen3 Q_e1sd1-3; content-closed re-draws) ==")
    L.append("  per tree: %s" % "; ".join(per_tree_text(R) for R in cc))
    L.append("  GAP-SHOWN qwen3 trees: %d of 3; words counted: %s%s" % (len(counted), ", ".join(counted) if counted else "none", void_note(cc)))
    L.append("  GF1-CC: %s" % word_cc)
    ref = closed_refuted(rows_cc)
    L.append("  FAILS (rule 8): GF1-CC CLOSED is %s (%d GAP-SHOWN trees not CLOSED; 2 refute)" % (
        "REFUTED" if ref else "not refuted", sum(1 for _n, g, w in rows_cc if g and w != "CLOSED")))
    fires, m, c = gfc_fires(word_cc, [R["ip"] for R in cc if R["gap"] and R["word"] == "CLOSED"])
    L.append("  LB(I_P) > 0 on %d of %d GAP-SHOWN CLOSED qwen3 trees (B-3: F-GFC needs all of them)" % (m, c))
    L.append("  " + (FGFC_FIRES if fires else "FALSIFIER F-GFC NOT FIRED (GF1-CC %s; LB(I_P) > 0 on %d of %d CLOSED trees)" % (word_cc, m, c)))
    L.append("")
    L.append("== GF1-N (SCORED SECONDARY; nomic_raw N-raw, N_e1sd2, N_e1sd3; never joined with GF1-CC, S4) ==")
    if nomic_off is not None:
        word_n = "NOT RUN"
        L.append("  GF1-N: NOT RUN -- %s" % nomic_off)
    else:
        nn = leg_rows(W, stats, "N")
        rows_n = [(R["name"], R["gap"], R["word"]) for R in nn]
        word_n, counted_n = aggregate(rows_n)
        L.append("  per tree: %s" % "; ".join(per_tree_text(R) for R in nn))
        L.append("  GAP-SHOWN nomic trees: %d of 3; words counted: %s%s" % (len(counted_n), ", ".join(counted_n) if counted_n else "none", void_note(nn)))
        L.append("  GF1-N: %s" % word_n)
        L.append("  FAILS (rule 8): GF1-N CLOSED is %s" % ("REFUTED" if closed_refuted(rows_n) else "not refuted"))
    d1 = [e for e in W["entries"] if e["leg"] == "N1"]
    for e in d1:
        if e["name"] in stats:
            R = stats[e["name"]]
            L.append("  %s DESCRIPTIVE (never counted): the GF1 rule would read %s (%s); D_T %s, D_R %s" % (
                e["name"], R["word"], "GAP-SHOWN" if R["gap"] else "NO-GAP", ci4(R["dt"]), ci4(R["dr"])))
        else:
            L.append("  %s DESCRIPTIVE: %s" % (e["name"], e.get("status")))
    L.append("")
    L.append("PREDICTIONS (blind for every number on these trees; bands HELD iff the point lies in the closed interval; words by Brier):")
    pl, pst = predictions(cc, word_cc, word_n)
    L.extend(pl)
    L.append("")
    L.append("NOT APPLICABLE (stated): no judge verdict enters (no wrong(established), no tie conventions A / B); zero calls (no call cache, "
             "pilot or truncation guard); M2 NOT RUN (registered); LLOYD-WP-A not run (not registered here)")
    L.append(WILL_NOT_SHOW)
    return L, dict(word_cc=word_cc, word_n=word_n, fires=fires, m=m, c=c, refuted=ref, pred=pst)


def arms_csv(W, stats):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["tree", "leg", "arm", "M1", "hits", "n"])
    for e in W["entries"]:
        R = stats.get(e["name"])
        if R is None:
            continue
        for nm, a in R["arms"].items():
            w.writerow([e["name"], e["leg"], nm, repr(a["m1"]), a["hits"], R["n"]])
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# modes (shared by the real loader and the fixtures)
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def out_paths(out_dir):
    return os.path.join(out_dir, OUTCOME), os.path.join(out_dir, ARMS_CSV)


def run_core(loader, out_dir, nomic_leg, L=None):
    """--run: outputs refused before any work if present; load; admit; identity I-2; per tree (identity I-1, statistics); words;
    write-once. -> result dict."""
    L = [] if L is None else L
    op, cp = out_paths(out_dir)
    for p in (op, cp):
        if os.path.exists(p):
            refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    t0 = time.process_time()
    W = loader(L)
    say(L, "[MODE] --run (nomic leg: %s)" % nomic_leg)
    nomic_off = admit(W, nomic_leg, L)
    _LABELS[0] = True
    try:
        if W.get("gapfix") is not None:
            G = W["gapfix"]
            G["fit"] = sorted(G["guard"](L))
            hygiene_core(G, G["fit"])
            identity_gapfix(G, L)
        else:
            refuse("[GFC-IDENTITY-GF] the world carries no GAP-FIX identity tree")
        stats, infos = {}, {}
        for e in W["entries"]:
            if e["status"] != "ADMITTED":
                continue
            try:
                V, void = v_fit_entry(e, L)
                if void is not None:
                    e["status"] = void
                    say(L, "%s %s: %s" % (TAG, e["name"], void))
                    continue
                arms, info = tree_arms(e, vparts=V)
                identity_top1(e, arms)
                groups, G_ = FM.twin_groups([t for t, _ in e["heldout"]])
                R = tree_stats(e["name"], e["leg"], arms, groups, len(e["heldout"]))
            except SystemExit as ex:
                raise named(e["name"], ex) from None
            stats[e["name"]] = R
            infos[e["name"]] = (info, G_, FM.kish_mbar(groups))
    finally:
        _LABELS[0] = False
    say(L, "=== GAP-FIX-CC outcome (%s; zero calls) ===" % REG_TEXT)
    say(L, "script %s" % fmt_pins(pins_of(os.path.abspath(__file__))))
    for e in W["entries"]:
        if e["name"] in stats:
            info, G_, mbar = infos[e["name"]]
            for ln in render_tree(e, stats[e["name"]], info, G_, mbar):
                say(L, ln)
        else:
            say(L, "[%s] leg %s: %s" % (e["name"], LEGS[e["leg"]], e["status"]))
    Lr, res = render_all(W, stats, nomic_off)
    for ln in Lr:
        say(L, ln)
    for ln in support_lines([(stats[n], infos[n][2], infos[n][1]) for n in [e["name"] for e in W["entries"]] if n in stats]):
        say(L, ln)
    say(L, "%s CPU %.1f s; zero calls" % (TAG, time.process_time() - t0))
    txt = "\n".join(L) + "\n"
    sh = write_once(op, txt)
    sh2 = write_once(cp, arms_csv(W, stats))
    print("%s wrote %s (sha256 %s) and %s (sha256 %s), write-once; never committed: back up to E:/TaxoArena_backup_<date>_gap_fix_cc "
          "with SHA256SUMS.txt" % (TAG, op, sh, cp, sh2))
    res.update(stats=stats, text=txt, W=W)
    return res


def dry_core(loader, out_dir, nomic_leg, L=None):
    """--dry-run: load, admit, counts and structure, plan, synthetic cost; NO measure (M1 refuses here), nothing written."""
    L = [] if L is None else L
    W = loader(L)
    say(L, "[MODE] --dry-run (nomic leg: %s): pins, pools, splits, builds, guards, hygiene, counts, structure, cost; NO M1, NO hit, NO "
           "statistic; nothing written" % nomic_leg)
    op, cp = out_paths(out_dir)
    say(L, "OUTPUTS (write-once, --run only): %s %s; %s %s" % (op, "PRESENT (--run would REFUSE)" if os.path.exists(op) else "absent",
                                                               cp, "PRESENT (--run would REFUSE)" if os.path.exists(cp) else "absent"))
    nomic_off = admit(W, nomic_leg, L)
    for e in W["entries"]:
        if e["status"] != "ADMITTED":
            say(L, "TREE %s (%s): %s" % (e["name"], e["leg"], e["status"]))
            continue
        try:
            mask, par, roots = GF.leaf_parent_masks(e["tree"]["byid"], list(e["tree"]["leaf_ids"]))
        except SystemExit as ex:
            raise named(e["name"], ex) from None
        groups, G_ = FM.twin_groups([t for t, _ in e["heldout"]])
        say(L, "TREE %s (%s): %d leaves (registered %d); pool %s (%s); held-out %d (registered %d) in %d twin groups (Kish %.4f); fit set "
               "%d; label set %d; %s" % (e["name"], LEGS[e["leg"]], len(e["tree"]["leaf_ids"]), e["leaves"], e["pool"], e["split_word"],
                                            len(e["heldout"]), e["n"], G_, FM.kish_mbar(groups), len(e["fit"]), len(e["train"]),
                                            sizes_line(dict(allowed=Counter(int(x) for x in mask.sum(axis=1)),
                                                            root_parent=sum(1 for p in par if p in roots)))))
    tv = time.process_time()
    vsum = Counter()
    for e in W["entries"]:                   # P-2: the V fits on the real fit sets, label-free (no M1), every slot printed
        if e["status"] != "ADMITTED":
            continue
        try:
            V, void = v_fit_entry(e, L)
        except SystemExit as ex:
            raise named(e["name"], ex) from None
        if void is not None:
            vsum["VOID-TREE"] += 1
            say(L, "%s %s: %s (--run prints it and drops the tree)" % (TAG, e["name"], void))
        else:
            vsum["replaced"] += sum(1 for j, s in enumerate(REG["seeds"]) if V["V%d" % j]["seed"] != s)
            vsum["fits"] += len(V)
    say(L, "V FITS (P-2, label-free): %d slots fitted, %d by a ruling P-1 replacement; VOID-TREE %d; CPU %.1f s" % (
        vsum["fits"], vsum["replaced"], vsum["VOID-TREE"], time.process_time() - tv))
    if nomic_off is not None:
        say(L, "NOMIC LEG: %s" % nomic_off)
    G = W.get("gapfix")
    if G is not None:
        G["fit"] = sorted(G["guard"](L))
        hygiene_core(G, G["fit"])
        say(L, "IDENTITY I-2 tree %s: fit set %d (GAP-FIX's %d); V0 read from FLAT-MIX-MMLU's pinned state; checked in --run" % (
            G["name"], len(G["fit"]), G["expect"]["fit_n"]))
    say(L, "PLAN: per admitted tree V0-V4 fitted (vmf_em, seeds 0-4; a B6-VOID seed replaced in its slot by the lowest unused of 5-9, "
           "ruling P-1) on its fit set; T; LLOYD-WP / LLOYD-GL at T 0, %s and convergence "
           "(cap %d); M1 per arm; twin-group intervals (B %d, seed %d) for D_T, D_R, I_R, I_0, I_P, D(GL 5)" % (
               ", ".join(str(t) for t in REG["t_steps"]), REG["t_cap"], FM.BOOT_B, FM.BOOT_SEED))
    rng = np.random.default_rng(1)
    Xs = FM.unit_rows(rng.standard_normal((2000, 64)))
    t0 = time.process_time()
    FM.vmf_em(Xs, 20, 0, max_iter=20)
    per = time.process_time() - t0
    say(L, "COST (SYNTHETIC timing, n 2000 x 64, k 20, 20 EM iterations): %.2f CPU-s -> about %.0f CPU-s per real V fit (n 8,200 x 256, "
           "k 80, 200 iterations, scaled), x 5 seeds x %d trees; plus refinement, M1 and %d twin bootstraps per tree (registered: CPU "
           "about 1-2 h; expected 10-20 CPU-min)" % (per, per * (8200 / 2000.) * (256 / 64.) * (80 / 20.) * 10, sum(
               1 for e in W["entries"] if e["status"] == "ADMITTED"), 6))
    say(L, "%s dry-run complete: zero measures, nothing written" % TAG)
    return W


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# the real world (e1_split_draws' loader; never run by the selftest)
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def _sdr():
    global SDR
    if SDR is None:
        verify_pin("e1_split_draws.py")
        import e1_split_draws as _S        # noqa: E402  (its own import pins; flat_mix_mmlu's read-only connect guard)
        SDR = _S
    return SDR


def _p2dca_hygiene(label, fit, train, heldout, L):
    ho = set(t for t, _ in heldout)
    hk = set(SDR.SD.SS.stem_key(t) for t in ho)
    exact = len(fit & ho)
    outside = len(fit - set(t for t, _ in train))
    stem = sum(1 for t in fit if SDR.SD.SS.stem_key(t) in hk)
    say(L, "HYGIENE %s: fit texts %d; outside the label set %d; equal to a held-out text %d (both must be 0); sharing a held-out "
           "stem_key %d (printed; FLAT-MIX-MMLU's rule)" % (label, len(fit), outside, exact, stem))
    if exact or outside:
        refuse("%s: held-out content reaches the fit set (or the fit is outside the label set)" % label)


def load_real(L):
    S = _sdr()
    SW = S.load_real(L)                       # the pool lines FIRST (p2dca, then the three e1sd pools), pins, splits, builds, vectors
    say(L, "[SCRIPT] tools/analysis/gap_fix_cc.py %s" % fmt_pins(pins_of(os.path.abspath(__file__))))
    for nm in IMPORT_PINS:
        say(L, verify_pin(nm))
    say(L, "[REGISTRATION] %s" % REG_TEXT)
    say(L, "[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    if SW["absent"]:
        refuse("builds ABSENT: %s" % SW["absent"])
    other = {"N": "Q", "Q": "N"}
    entries = []
    for spec in REAL_TREES:
        arm, k = spec["arm"], spec["split"]
        if k == 0:
            I = SW["identity"]
            tree, graph, train, heldout = I["trees"]["N-raw"], I["graphs"]["N-raw"], I["train"], I["heldout"]
            pool, word, near = S.P2DCA, "p2dca judgeable; content-closed under stem_key for this split (FLAT-MIX-MMLU's hygiene)", None
        else:
            sp = SW["splits"][k]
            tree, graph, train, heldout = SW["trees"][(arm, k)], SW["graphs"][(arm, k)], sp["train"], sp["heldout"]
            pool, word, near = sp["pool"], "content-closed (CK-CLOSE-v1 e1sd%d)" % k, sp.get("near")

        def guard(Lg, _n=spec["name"], _a=arm, _t=tree, _g=graph, _tr=train, _ho=heldout, _k=k):
            fit = S.check_tree(_n, _a, _t, _g, SW["id2text"], SW["blobs"][_a], SW["blobs"][other[_a]], Lg)
            if _k == 0:
                _p2dca_hygiene(_n, fit, _tr, _ho, Lg)
            else:
                S.hygiene(_n, fit, _tr, _ho, Lg)
            return fit
        entries.append(dict(spec, tree=tree, train=train, heldout=heldout, space=SW["spaces"][arm], pool=pool, split_word=word,
                            near=near, guard=guard))
    I = SW["identity"]
    parts, plines = GF.v_parts(GAPFIX_ID["name"])       # FLAT-MIX-MMLU's pinned V state (sha256 per part; REFUSES on change)
    for ln in plines:
        say(L, "  " + ln)

    def gguard(Lg):
        fit = S.check_tree("E1 af_clean_s42", "Q", I["trees"]["af"], I["graphs"]["af"], SW["id2text"], SW["blobs"]["Q"], SW["blobs"]["N"], Lg)
        _p2dca_hygiene("af_clean_s42", fit, I["train"], I["heldout"], Lg)
        return fit
    gapfix = dict(name=GAPFIX_ID["name"], tree=I["trees"]["af"], train=I["train"], heldout=I["heldout"], space=SW["spaces"]["Q"],
                  v0=parts["V0"], expect=GAPFIX_ID, guard=gguard)
    return dict(entries=entries, gapfix=gapfix)


# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# main
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
def main(argv=None):
    for stream in (sys.stdout, sys.stderr):    # GAP-FIX D-4: a cp1252 console crashed the first --dry-run on an em dash
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="GAP-FIX-CC (zero calls; CPU readout)")
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    gr.add_argument("--banner", action="store_true", help="print the registration line (C-MAIN's encoding check)")
    ap.add_argument("--nomic-leg", choices=NOMIC_LEGS, default=None)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--data-root", default=None, help="the checkout whose DBs, results and run dirs are read")
    a = ap.parse_args(argv)
    if a.data_root:
        os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(a.data_root)
        os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(a.data_root)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.banner:
        print("%s %s" % (TAG, REG_TEXT))
        return 0
    if a.selftest:
        return selftest(only=a.only, quiet=a.quiet)
    if a.mutants:
        return run_mutants(only=a.only)
    if a.nomic_leg is None:
        refuse("--nomic-leg <%s> is REQUIRED with --dry-run / --run (the READY review rules the embedder gate; no default)" % "|".join(NOMIC_LEGS))
    if a.data_root and os.path.normcase(os.path.abspath(a.data_root)) != os.path.normcase(os.path.abspath(FM.DATA_ROOT)):
        refuse("--data-root %s was not applied before the imports (DATA_ROOT %s)" % (a.data_root, FM.DATA_ROOT))
    out_dir = os.path.join(FM.DATA_ROOT, *OUT_REL.split("/"))
    if a.dry_run:
        dry_core(load_real, out_dir, a.nomic_leg)
        return 0
    run_core(load_real, out_dir, a.nomic_leg)
    return 0


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
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn()
    except SystemExit as e:
        return needle in str(e), str(e)
    return False, "no refusal"


def _quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def _line(text, prefix):
    for ln in text.splitlines():
        if ln.strip().startswith(prefix):
            return ln.strip()
    raise AssertionError("no line starting with %r" % prefix)


def _lines(text, prefix):
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith(prefix)]


# ── the fixture: two parents, each an arc of three clusters (0, 60, 120 degrees) in its own plane ──────────────────────────
FX_D = 12
FX_PLANES = {"A": (0, 1, 10), "B": (2, 3, 11)}       # (u, v, parent offset) basis indices
FX_KINDS = {
    # kind: (sigma degrees, leaf angles in A, leaf angles in B, isotropic noise)
    "TRUE": (5.0, (0, 60, 120), (0, 60, 120), 0.03),
    "PASSES": (15.0, (-10, 30, 100), (-10, 30, 100), 0.03),
    "RECENTRE": (5.0, (0, 45, 75), (0, 45, 75), 0.01),
    "OPEN": (4.0, (30, 120), (-5, 5, 60, 120), 0.01),
}


def _fx_dir(parent, deg):
    u, v, w = FX_PLANES[parent]
    x = np.zeros(FX_D)
    th = math.radians(deg)
    x[u], x[v], x[w] = math.cos(th), math.sin(th), 0.6
    return x / np.linalg.norm(x)


def _fx_point(rng, parent, deg, sig, iso=0.03):
    u, v, w = FX_PLANES[parent]
    th = math.radians(deg + sig * rng.standard_normal())
    x = iso * rng.standard_normal(FX_D)
    x[u] += math.cos(th)
    x[v] += math.sin(th)
    x[w] += 0.6
    return x / np.linalg.norm(x)


def _fx_tree(kind, name):
    sig, la, lb, _iso = FX_KINDS[kind]
    nodes = [dict(id="R", childIds=["A", "B"], isLeaf=False, depth=0)]
    leaf_ids, mus = [], []
    for par, angs in (("A", la), ("B", lb)):
        kids = []
        for i, a in enumerate(angs):
            lid = "%s_%s%d" % (name, par, i)
            kids.append(lid)
            nodes.append(dict(id=lid, childIds=[], isLeaf=True, depth=2, vmfMu=_fx_dir(par, a).tolist()))
            leaf_ids.append(lid)
            mus.append(_fx_dir(par, a))
        nodes.append(dict(id=par, childIds=kids, isLeaf=False, depth=1))
    return dict(nodes=nodes, byid={n["id"]: n for n in nodes}, leaf_ids=leaf_ids, leaf_mu=np.array(mus))


def _fx_split(kind, name, seed, n_fit=60, n_other=30, n_ho=34, n_extra=40, space=None):
    """One tree's own split: fit (the tree's members) inside the label set; label set = fit + other TRAIN + an extra region (a
    category seen only in the label set); held-out = the six clusters, cluster B2's held-out items 60% labelled B1 (so a majority
    taken from the held-out side differs), plus 3 stem_key twins."""
    rng = np.random.default_rng(seed)
    sig, iso = FX_KINDS[kind][0], FX_KINDS[kind][3]
    fit, other, ho = [], [], []
    for par in ("A", "B"):
        for ci, deg in enumerate((0, 60, 120)):
            cat = "%s%d" % (par, ci)
            for i in range(n_fit):
                t = "%s fit %s%d n%03d" % (name, par, ci, i)
                space[t] = _fx_point(rng, par, deg, sig, iso)
                fit.append((t, cat))
            for i in range(n_other):
                t = "%s other %s%d n%03d" % (name, par, ci, i)
                space[t] = _fx_point(rng, par, deg, sig, iso)
                other.append((t, cat))
            for i in range(n_ho + (ci + (3 if par == "B" else 0))):    # unequal cluster sizes: each tree its own n
                t = "%s held %s%d n%03d" % (name, par, ci, i)
                space[t] = _fx_point(rng, par, deg, sig, iso)
                lab = "B1" if (par == "B" and ci == 2 and rng.random() < 0.6) else cat
                ho.append((t, lab))
    extra = []
    for i in range(n_extra):
        t = "%s extra n%03d" % (name, i)
        x = 0.05 * rng.standard_normal(FX_D)
        x[6] += 1.0
        x[7] += 1.0
        space[t] = x / np.linalg.norm(x)
        extra.append((t, "X"))
    for j in (0, 50, 100):                       # twins: the upper-cased text shares the stem_key
        t, c = ho[j]
        tw = t.upper()
        space[tw] = space[t]
        ho.append((tw, c))
    train = fit + other + extra
    return [t for t, _ in fit], train, ho


def _fx_world(kinds, seed=11, top1=None, gapfix_kind="PASSES", gapfix_expect=None, guard_refuse=(), gapfix_break=None, leaves_bad=None):
    """A fixture world: entries named like the real ones (3 CC, 3 N, 1 N1), each with its own split and vectors."""
    space = {}
    names = ("Q_e1sd1", "Q_e1sd2", "Q_e1sd3", "N-raw", "N_e1sd2", "N_e1sd3", "N_e1sd1")
    legs = ("CC", "CC", "CC", "N", "N", "N", "N1")
    entries = []
    calls = []
    for i, (nm, leg) in enumerate(zip(names, legs)):
        kind = kinds[i]
        tree = _fx_tree(kind, nm)
        fit, train, ho = _fx_split(kind, nm, seed + 17 * i, n_ho=30 + 2 * i, space=space)

        def guard(Lg, _fit=fit, _nm=nm):
            calls.append(_nm)
            if _nm in guard_refuse:
                raise SystemExit("[EMB-GUARD] fixture refusal for %s" % _nm)
            return set(_fit)
        e = dict(name=nm, leg=leg, arm="Q" if leg == "CC" else "N", split=i, leaves=len(tree["leaf_ids"]) if leaves_bad != nm else 99,
                 n=len(ho), top1=None, tree=tree, train=train, heldout=ho, space=space, pool="pFX%d" % i, split_word="fixture",
                 near=i, guard=guard, kind=kind)
        e["top1"] = (top1 or {}).get(nm) or _o_top1(e, fit)
        entries.append(e)
    gtree = _fx_tree(gapfix_kind, "GF")
    gfit, gtrain, gho = _fx_split(gapfix_kind, "GF", seed + 999, space=space)
    v0 = _fx_truth_v0()
    G = dict(name="GF_identity", tree=gtree, train=gtrain, heldout=gho, space=space, v0=v0, guard=lambda Lg, _f=gfit: set(_f))
    G["expect"] = gapfix_expect or _o_gapfix_expect(G, gfit)
    if gapfix_break is not None:
        G["expect"] = gapfix_break(dict(G["expect"], hits=dict(G["expect"]["hits"]), ci=dict(G["expect"]["ci"])))
    W = dict(entries=entries, gapfix=G, calls=calls)
    return (lambda L: (say(L, "pool pFX (fixture world; no DB)"), W)[1]), W


def _fx_truth_v0():
    mus = [_fx_dir(p, a) for p in ("A", "B") for a in (0, 60, 120)]
    return dict(rule="map", mu=np.array(mus), kappa=np.full(6, 60.0), pi=np.full(6, 1 / 6.0), iters=0, converged=True, mean_ll=0.0)


# ── independent oracles (plain loops; written without tree_arms / m1 / tree_stats / aggregate) ─────────────────────────────
def _o_cells_nearest(Q, C):
    return GF.o_nearest(Q, C)


def _o_map(Q, mu, kappa, pi):
    d = len(mu[0])
    out = []
    for q in Q:
        best, bs = None, None
        for j in range(len(mu)):
            if pi[j] <= 0:
                continue
            s = math.log(pi[j]) + float(FM.log_cd(d, np.array([kappa[j]]))[0]) + kappa[j] * float(np.dot(mu[j], q))
            if bs is None or s > bs:
                best, bs = j, s
        out.append(best)
    return out


def _o_hits(cells_fn, e):
    Qt = [e["space"][t] for t, _ in e["train"]]
    Qh = [e["space"][t] for t, _ in e["heldout"]]
    return GF.o_score(cells_fn(Qt), cells_fn(Qh), e["train"], e["heldout"])


def _o_top1(e, fit):
    h = _o_hits(lambda Q: _o_cells_nearest(Q, e["tree"]["leaf_mu"]), e)
    return "%.4f" % (sum(h) / float(len(e["heldout"])))


def _o_arms(e, fit, V=None, seeds=(0, 1, 2, 3, 4)):
    """Oracle per-question hits of T, V0..V4 (fitted by FM.vmf_em on the oracle's own fit matrix; slot j at seeds[j], the test's
    literal expectation of the P-1 rule), WP_0, WP_5, GL_5."""
    X = np.array([e["space"][t] for t in sorted(fit)])
    mu0 = np.asarray(e["tree"]["leaf_mu"])
    z0 = _o_cells_nearest(X, mu0)
    ps = GF.o_parent_sets(e["tree"]["nodes"], list(e["tree"]["leaf_ids"]))
    out = {"T": _o_hits(lambda Q: _o_cells_nearest(Q, mu0), e)}
    for nm, (var, T) in {"WP_0": ("WP", 0), "WP_5": ("WP", 5), "GL_5": ("GL", 5)}.items():
        _z, C = GF.o_lloyd(X, z0, mu0, ps, var, T)
        out[nm] = _o_hits(lambda Q, _C=C: _o_cells_nearest(Q, _C), e)
    if V is None:
        V = {}
        for j, s in enumerate(seeds):
            r = FM.vmf_em(X, len(mu0), s)
            V["V%d" % j] = dict(mu=r["mu"], kappa=r["kappa"], pi=r["pi"])
    for nm, b in V.items():
        out[nm] = _o_hits(lambda Q, _b=b: _o_map(Q, _b["mu"], _b["kappa"], _b["pi"]), e)
    return out


def _o_gapfix_expect(G, fit):
    a = _o_arms(G, fit, V={"V0": G["v0"]})
    groups, _ = FM.twin_groups([t for t, _ in G["heldout"]])

    def ci(x, y):
        d = np.asarray(a[x]) - np.asarray(a[y])
        lo, hi = FM.twin_boot_ci(d, groups)
        return "%s [%s, %s]" % (f4(float(d.mean())), f4(lo), f4(hi))
    return dict(fit_n=len(fit), n=len(G["heldout"]),
                hits=dict(T=int(sum(a["T"])), V0=int(sum(a["V0"])), WP_0=int(sum(a["WP_0"])), WP_5=int(sum(a["WP_5"]))),
                ci=dict(D_T=ci("T", "V0"), D_R=ci("WP_5", "V0"), I_R=ci("WP_5", "T"), I_0=ci("WP_0", "T")), ip_postrun=ci("WP_5", "WP_0"))


def _o_word(a, groups, n):
    """Oracle GF1 word from oracle hits (own arithmetic; FM.twin_boot_ci for the intervals)."""
    def iv(x, y):
        d = np.asarray(a[x]) - np.asarray(a[y])
        lo, hi = FM.twin_boot_ci(d, groups)
        return float(d.mean()), lo, hi, float(np.mean(d != 0))
    dt, dr, ir = iv("T", "V0"), iv("WP_5", "V0"), iv("WP_5", "T")
    i0, ip = iv("WP_0", "T"), iv("WP_5", "WP_0")
    vm = [sum(a["V%d" % s]) / float(n) for s in range(5)]
    bar = max(2.8 * math.sqrt(dr[3] / n), max(vm) - min(vm))
    if dr[2] >= 0 and ir[0] > 0 and ir[1] > 0:
        w = "CLOSED"
    elif dr[2] < 0 and abs(dr[0]) > bar:
        w = "OPEN"
    else:
        w = "PARTIAL"
    return dict(word=w, gap=dt[2] < 0, dt=dt, dr=dr, ir=ir, i0=i0, ip=ip, bar=bar)


# ── C-PURE ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def st_pure(chk):
    A = aggregate
    chk.ok(A([("a", True, "CLOSED"), ("b", True, "CLOSED"), ("c", True, "PARTIAL")])[0] == "CLOSED", "AGG C,C,P -> CLOSED")
    chk.ok(A([("a", True, "PARTIAL"), ("b", True, "OPEN"), ("c", True, "PARTIAL")])[0] == "PARTIAL", "AGG P,O,P -> PARTIAL (not first-two only)")
    chk.ok(A([("a", True, "CLOSED"), ("b", True, "OPEN"), ("c", True, "OPEN")])[0] == "OPEN", "AGG C,O,O -> OPEN (the last two)")
    chk.ok(A([("a", True, "CLOSED"), ("b", True, "PARTIAL"), ("c", True, "OPEN")])[0] == "MIXED", "AGG C,P,O -> MIXED")
    chk.ok(A([("a", False, "CLOSED"), ("b", True, "CLOSED"), ("c", True, "PARTIAL")])[0] == "MIXED", "AGG NO-GAP tree not counted -> MIXED")
    chk.ok(A([("a", False, "CLOSED"), ("b", True, "OPEN"), ("c", True, "OPEN")])[0] == "OPEN", "AGG 2 GAP-SHOWN agreeing -> OPEN")
    chk.ok(A([("a", True, "OPEN"), ("b", False, "OPEN"), ("c", False, "OPEN")])[0] == "NOT EVALUABLE", "AGG 1 GAP-SHOWN -> NOT EVALUABLE")
    chk.ok(A([("a", False, "OPEN"), ("b", False, "OPEN"), ("c", False, "OPEN")])[0] == "NOT EVALUABLE", "AGG 0 GAP-SHOWN -> NOT EVALUABLE")
    chk.ok(A([])[0] == "NOT EVALUABLE", "AGG empty -> NOT EVALUABLE")
    chk.ok(A([("a", np.bool_(True), "CLOSED"), ("b", np.bool_(True), "CLOSED"), ("c", np.bool_(False), "OPEN")])[0] == "CLOSED",
           "AGG numpy.bool_ flags read by value")
    chk.ok(closed_refuted([("a", True, "PARTIAL"), ("b", True, "OPEN"), ("c", True, "CLOSED")]) is True, "FAILS 2 GAP-SHOWN not CLOSED -> REFUTED")
    chk.ok(closed_refuted([("a", True, "PARTIAL"), ("b", False, "OPEN"), ("c", True, "CLOSED")]) is False, "FAILS NO-GAP not counted -> not refuted")
    chk.ok(closed_refuted([("a", True, "CLOSED"), ("b", True, "CLOSED"), ("c", True, "OPEN")]) is False, "FAILS 1 not CLOSED -> not refuted")
    ipp, ip0 = dict(lo=0.001), dict(lo=0.0)
    chk.ok(gfc_fires("CLOSED", [ipp, ipp]) == (True, 2, 2), "F-GFC CLOSED, LB > 0 on 2 of 2 -> FIRES")
    chk.ok(gfc_fires("CLOSED", [ipp, ip0]) == (False, 1, 2), "F-GFC CLOSED, LB exactly 0 on one -> NOT FIRED (strict > 0)")
    chk.ok(gfc_fires("CLOSED", [ip0, ipp, ipp]) == (False, 2, 3), "F-GFC 3 CLOSED, 2 with LB > 0 -> NOT FIRED under B-3 (count printed)")
    chk.ok(gfc_fires("PARTIAL", [ipp, ipp]) == (False, 2, 2), "F-GFC on a non-CLOSED GF1-CC -> NOT FIRED")
    chk.ok(gfc_fires("CLOSED", []) == (False, 0, 0), "F-GFC with no CLOSED tree -> NOT FIRED")
    # predictions by value
    def R_(nm, dt, dr, i0, ip, gap):
        return dict(name=nm, dt=dict(d=dt), dr=dict(d=dr), i0=dict(d=i0), ip=dict(d=ip), gap=gap)
    cc = [R_("q1", -0.055, 0.002, 0.010, 0.005, True), R_("q2", -0.005, -0.040, 0.004, 0.004, True), R_("q3", -0.0549, -0.041, 0.001, 0.009, True)]
    L, p = predictions(cc, "PARTIAL", "CLOSED")
    chk.ok(p["p1"] is True and "3 of 3 -> occurred; Brier 0.2025" in L[0], "P1 3 of 3 -> occurred, Brier (0.55-1)^2 = 0.2025: %s" % L[0][-40:])
    chk.ok(p["p2"] == [True, True, True], "P2 band edges inclusive (-0.055 and -0.005 HELD)")
    chk.ok(p["p3"] == [True, True, False] and "-> 2 of 3 HELD" in L[2], "P3 +0.002 / -0.040 HELD, -0.041 FAILED -> 2 of 3")
    chk.ok("Brier (5-class) %.4f" % ((0.45 - 1) ** 2 + 0.2 ** 2 + 0.15 ** 2 + 0.1 ** 2 + 0.1 ** 2) in L[3], "P4 PARTIAL Brier 5-class by value")
    chk.ok(p["k5"] == 1 and p["p5"] is False and "Brier %.4f" % (0.75 ** 2) in L[4], "P5 I_0 > I_P strict: 1 of 3 (tie not counted) -> did not occur")
    chk.ok(p["p6_class"] == "CLOSED" and "Brier (4-class) %.4f" % (0.4 ** 2 + 0.8 ** 2 + 0.15 ** 2 + 0.25 ** 2) in L[5], "P6 CLOSED Brier")
    L2, p2 = predictions([R_("q1", 0.0, 0.0, 0.02, 0.01, False)] + cc[1:], "NOT EVALUABLE", "NOT RUN")
    chk.ok(p2["p1"] is False and "2 of 3 -> did not occur; Brier 0.3025" in L2[0], "P1 2 of 3 -> did not occur, Brier 0.3025")
    chk.ok(p2["k5"] == 1 and p2["p5"] is False, "P5 the first tree's I_0 > I_P alone -> 1 of 3")
    chk.ok(p2["p6_class"] == "OTHER" and "Brier (4-class) %.4f" % (0.4 ** 2 + 0.2 ** 2 + 0.15 ** 2 + 0.75 ** 2) in L2[5], "P6 NOT RUN -> OTHER class")
    chk.ok("Brier (5-class) %.4f" % (0.45 ** 2 + 0.2 ** 2 + 0.85 ** 2 + 0.1 ** 2 + 0.1 ** 2) in L2[3], "P4 NOT EVALUABLE Brier")
    L3, p3 = predictions([R_("q1", 0.0, 0.0, 0.03, 0.01, True), R_("q2", 0.0, 0.0, 0.02, 0.01, True), cc[2]], "MIXED", "MIXED")
    chk.ok(p3["k5"] == 2 and p3["p5"] is True and "Brier %.4f" % (0.25 ** 2) in L3[4], "P5 2 of 3 -> occurred (>= 2, not all 3)")
    chk.ok(p3["p6_class"] == "OTHER", "P6 MIXED -> OTHER")


# ── C-PLANT: tree_stats + render on planted per-question arms (exact edges) ────────────────────────────────────────────────
def _plant(n, t, v, wp0, wp5, vs=(0, 0, 0, 0), gl=None):
    """Per-question hit vectors (0/1 arrays of length n). vs: hits offsets of V1..V4 relative to V0 (spread_V)."""
    arms = {"T": dict(per1=np.asarray(t, float)), "V0": dict(per1=np.asarray(v, float)), "WP_0": dict(per1=np.asarray(wp0, float)),
            "WP_5": dict(per1=np.asarray(wp5, float)), "GL_5": dict(per1=np.asarray(gl if gl is not None else wp5, float)),
            "WP_10": dict(per1=np.asarray(t, float))}           # WP_10 = T: a T 5 -> 10 swap changes every word
    for s, off in zip((1, 2, 3, 4), vs):
        x = np.asarray(v, float).copy()
        if off > 0:
            idx = np.flatnonzero(x == 0)[:off]
            x[idx] = 1
        elif off < 0:
            idx = np.flatnonzero(x == 1)[:-off]
            x[idx] = 0
        arms["V%d" % s] = dict(per1=x)
    for a in arms.values():
        a["hits"] = int(a["per1"].sum())
        a["m1"] = a["hits"] / float(n)
    return arms


def st_plant(chk):
    n = 400
    groups = np.arange(n)
    base = np.zeros(n)
    base[:300] = 1
    # (1) CLOSED at the exact edge UB(D_R) = 0: WP_5 == V0 exactly; T loses 40; WP_0 recovers 20 of them
    v = base.copy()
    t = base.copy(); t[:40] = 0
    wp0 = base.copy(); wp0[:20] = 0
    R = tree_stats("q", "CC", _plant(n, t, v, wp0, v), groups, n)
    chk.ok(R["dr"]["hi"] == 0.0 and R["word"] == "CLOSED" and R["gap"] is True, "PLANT UB(D_R) exactly 0 -> CLOSED (>= 0), GAP-SHOWN")
    chk.ok(R["ip"]["lo"] > 0 and R["refuted"] is False, "PLANT passes add 20 -> LB(I_P) > 0; CLOSED not refuted")
    txt = "\n".join(tree_word_line(R).splitlines())
    chk.ok("re-centring" not in txt, "PLANT CLOSED with LB(I_P) > 0: no re-centring sentence")
    # (2) CLOSED by re-centring: WP_0 == WP_5 == V0 -> I_P = [0, 0]
    R2 = tree_stats("q", "CC", _plant(n, t, v, v, v), groups, n)
    chk.ok(R2["word"] == "CLOSED" and R2["ip"]["lo"] == 0.0 == R2["ip"]["hi"], "PLANT WP_0 == WP_5 -> I_P [0, 0]")
    chk.ok("CLOSED by re-centring, not by the passes" in tree_word_line(R2), "PLANT the W-2 sentence printed when I_P contains 0")
    # (3) LB(I_R) exactly 0 -> not CLOSED: WP_5 == T (I_R all zero) with D_R = D_T < 0
    R3 = tree_stats("q", "CC", _plant(n, t, v, t, t), groups, n)
    chk.ok(R3["ir"]["lo"] == 0.0 and R3["word"] != "CLOSED" and R3["refuted"] is True, "PLANT LB(I_R) exactly 0 -> not CLOSED, refuted")
    # (4) NO-GAP: T == V0 -> UB(D_T) = 0 -> not counted
    R4 = tree_stats("q", "CC", _plant(n, v, v, v, v), groups, n)
    chk.ok(R4["dt"]["hi"] == 0.0 and R4["gap"] is False and "NO-GAP" in tree_word_line(R4), "PLANT UB(D_T) exactly 0 -> NO-GAP")
    # (5) the OPEN bar: D_R = -12/400 = -0.03 (all one direction, UB < 0); MDE80 = 2.8 sqrt(0.03 / 400) = 0.02425
    t5 = base.copy(); t5[:12] = 0
    R5 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, vs=(0, 0, 0, 0)), groups, n)
    chk.ok(abs(R5["mde"] - 2.8 * math.sqrt(0.03 / 400)) < 1e-12 and R5["spread_v"] == 0.0 and R5["word"] == "OPEN",
           "PLANT |D_R| 0.0300 > MDE80 0.0242, spread 0 -> OPEN (bar = MDE80)")
    R6 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, vs=(14, 0, 0, 0)), groups, n)
    chk.ok(abs(R6["spread_v"] - 0.035) < 1e-12 and R6["word"] == "PARTIAL" and abs(R6["bar"] - 0.035) < 1e-12,
           "PLANT D-1: MDE80 0.0242 < |D_R| 0.0300 <= spread_V 0.0350 -> PARTIAL (bar = max)")
    R7 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, vs=(0, 12, 0, 0)), groups, n)
    chk.ok(abs(R7["spread_v"] - 0.03) < 1e-12 and R7["word"] == "PARTIAL", "PLANT |D_R| exactly spread_V 0.0300 -> PARTIAL (> strict)")
    t8 = base.copy(); t8[:6] = 0             # D_R -0.015; MDE80 2.8 sqrt(0.015 / 400) = 0.01715 > |D_R| > spread 0.0100
    R8 = tree_stats("q", "CC", _plant(n, t8, v, t8, t8, vs=(0, 0, 4, 0)), groups, n)
    chk.ok(R8["mde"] > 0.015 > R8["spread_v"] and R8["word"] == "PARTIAL", "PLANT spread 0.0100 < |D_R| 0.0150 <= MDE80 0.0171 -> PARTIAL (not min)")
    R9 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, vs=(0, 0, 0, -8)), groups, n)
    chk.ok(abs(R9["spread_v"] - 0.02) < 1e-12 and R9["word"] == "OPEN", "PLANT spread from a V below V0 (max - min) 0.0200 -> OPEN")
    R11 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, vs=(14, 14, 14, 14)), groups, n)
    chk.ok(abs(R11["spread_v"] - 0.035) < 1e-12 and R11["word"] == "PARTIAL", "PLANT V0 the minimum of V0..V4: spread_V includes V0 (0.0350) -> PARTIAL")
    t12 = base.copy(); t12[:2] = 0; t12[300] = 1                          # D_T point -1/400 < 0, interval reaching 0
    R12 = tree_stats("q", "CC", _plant(n, t12, v, t12, t12), groups, n)
    chk.ok(R12["dt"]["d"] < 0 <= R12["dt"]["hi"] and R12["gap"] is False, "PLANT D_T point < 0 with UB %s >= 0 -> NO-GAP (the UB decides)" % f4(R12["dt"]["hi"]))
    # (6) the rendered condition lines carry holds / fails (D-3)
    cl = gf1_condition_lines(R6)
    chk.ok("UB(D_R) +0.0000" not in cl[0] and "[fails]" in cl[0] and cl[1].endswith("> bar 0.0350 [fails]") and "< 0 [holds]" in cl[1],
           "PLANT D-3 'holds' / 'fails' beside each condition: %s | %s" % (cl[0][-30:], cl[1][-30:]))
    # (7) GL is descriptive only: a GL arm that differs changes no word
    R10 = tree_stats("q", "CC", _plant(n, t5, v, t5, t5, gl=v), groups, n)
    chk.ok(R10["word"] == R5["word"] and abs(R10["dgl"]["d"]) == 0.0, "PLANT GL arm descriptive (word unchanged, D(GL) 0)")
    # (8) twin groups decide the interval: a duplicated discordance clustered in 2 groups vs i.i.d.
    g2 = np.arange(n)
    g2[:40] = np.repeat(np.arange(2), 20)
    tt = base.copy(); tt[:40] = 0
    Rg = tree_stats("q", "CC", _plant(n, tt, v, tt, v), g2, n)
    Ri = tree_stats("q", "CC", _plant(n, tt, v, tt, v), groups, n)
    chk.ok(Rg["ir"]["hi"] - Rg["ir"]["lo"] > 3 * (Ri["ir"]["hi"] - Ri["ir"]["lo"]), "PLANT twin-group interval wider than the i.i.d. one")


# ── C-E2E ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
E2E_WORLDS = {
    # name: (kinds of Q1, Q2, Q3, N-raw, N2, N3, N1; GF1-CC; F-GFC; GF1-N; the world seed). Each tree's word is known by construction
    # (KIND_WORD); the seed was chosen (2026-10-08, the builder) so that every tree's five V fits recover the six clusters where its word
    # needs it (k-means++ seeding can place two seeds in one cluster at sigma 15 degrees); the oracle re-derives every number.
    "W1": (("PASSES", "PASSES", "OPEN", "OPEN", "PASSES", "TRUE", "PASSES"), "CLOSED", True, "MIXED", 11),
    "W2": (("OPEN", "TRUE", "RECENTRE", "PASSES", "PASSES", "OPEN", "TRUE"), "MIXED", False, "CLOSED", 15),
    "W3": (("TRUE", "TRUE", "OPEN", "OPEN", "OPEN", "PASSES", "OPEN"), "NOT EVALUABLE", False, "OPEN", 11),
    "W4": (("RECENTRE", "PASSES", "TRUE", "OPEN", "OPEN", "OPEN", "TRUE"), "CLOSED", False, "OPEN", 11),
}
KIND_WORD = {"PASSES": ("CLOSED", True), "RECENTRE": ("CLOSED", True), "OPEN": ("OPEN", True), "TRUE": (None, False)}


def _e2e(td, wname, nomic_leg="e1-guard", **kw):
    kinds, seed = E2E_WORLDS[wname][0], E2E_WORLDS[wname][4]
    loader, W = _fx_world(kinds, seed=seed, **kw)
    out = os.path.join(tempfile.mkdtemp(dir=td), wname + "_" + nomic_leg)
    res, txt = _quiet(run_core, loader, out, nomic_leg)
    return res, txt, W, out


def st_e2e(chk):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        for wname, (kinds, w_cc, fires, w_n, _seed) in E2E_WORLDS.items():
            res, txt, W, out = _e2e(td, wname)
            chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: %s" % w_cc, "E2E %s GF1-CC %s (printed: %s)" % (wname, w_cc, _line(txt, "GF1-CC:")))
            chk.ok(_line(txt, "GF1-N:") == "GF1-N: %s" % w_n, "E2E %s GF1-N %s (printed: %s)" % (wname, w_n, _line(txt, "GF1-N:")))
            fl = _line(txt, "FALSIFIER F-GFC")
            chk.ok(fl.startswith("FALSIFIER F-GFC FIRES") == fires, "E2E %s F-GFC %s" % (wname, "FIRES" if fires else "NOT FIRED"))
            for e in W["entries"]:
                R = res["stats"][e["name"]]
                oa = _o_arms(e, e["fit"])
                ow = _o_word(oa, FM.twin_groups([t for t, _ in e["heldout"]])[0], len(e["heldout"]))
                kw_, gap_ = KIND_WORD[e["kind"]]
                chk.ok(bool(R["gap"]) == bool(ow["gap"]) == gap_, "E2E %s %s (%s) GAP-SHOWN %s by construction and oracle" % (
                    wname, e["name"], e["kind"], gap_))
                if kw_ is not None:
                    chk.ok(R["word"] == ow["word"] == kw_, "E2E %s %s (%s) GF1 %s by construction and oracle (got %s / %s)" % (
                        wname, e["name"], e["kind"], kw_, R["word"], ow["word"]))
                else:
                    chk.ok(R["word"] == ow["word"], "E2E %s %s (TRUE) word equals the oracle's (%s)" % (wname, e["name"], R["word"]))
                for key, o in (("dt", ow["dt"]), ("dr", ow["dr"]), ("ir", ow["ir"]), ("i0", ow["i0"]), ("ip", ow["ip"])):
                    chk.ok(f4(R[key]["d"]) == f4(o[0]) and f4(R[key]["lo"]) == f4(o[1]) and f4(R[key]["hi"]) == f4(o[2]),
                           "E2E %s %s %s %s = oracle %s [%s, %s]" % (wname, e["name"], key, ci4(R[key]), f4(o[0]), f4(o[1]), f4(o[2])))
                chk.ok(abs(R["bar"] - ow["bar"]) < 1e-12, "E2E %s %s bar %.4f = oracle (max(MDE80, spread_V))" % (wname, e["name"], R["bar"]))
                for arm in ("T", "V0", "V3", "WP_0", "WP_5", "GL_5"):
                    chk.ok(R["arms"][arm]["hits"] == int(sum(oa[arm])), "E2E %s %s hits %s %d = oracle" % (wname, e["name"], arm, R["arms"][arm]["hits"]))
                blk = txt[txt.index("[%s] leg" % e["name"]):]
                chk.ok(_line(blk, "D_T = ").endswith(ci4(R["dt"]) + (" -> GAP-SHOWN (UB < 0)" if R["gap"] else " -> NO-GAP (UB >= 0; not counted)")),
                       "E2E %s %s D_T line printed by value" % (wname, e["name"]))
                chk.ok(_line(blk, "GF1 (this tree):").startswith("GF1 (this tree): %s" % R["word"]), "E2E %s %s word line" % (wname, e["name"]))
                chk.ok(("held-out %d in" % len(e["heldout"])) in _line(blk, "[%s] leg" % e["name"]), "E2E %s %s its own held-out n" % (wname, e["name"]))
                fz = _line(blk, "FAILS (rule 8): CLOSED is")
                chk.ok(fz.startswith("FAILS (rule 8): CLOSED is REFUTED" if R["refuted"] else "FAILS (rule 8): CLOSED is not refuted")
                       and bool(R["refuted"]) == bool(ow["dr"][2] < 0 or ow["ir"][1] <= 0), "E2E %s %s per-tree FAILS line by value" % (wname, e["name"]))
            if wname == "W1":
                chk.ok("LB(I_P) > 0 on 2 of 2 GAP-SHOWN CLOSED qwen3 trees" in txt, "E2E W1 F-GFC count 2 of 2")
                chk.ok("N_e1sd1 DESCRIPTIVE (never counted): the GF1 rule would read CLOSED" in txt, "E2E W1 N_e1sd1 descriptive CLOSED, not counted")
                chk.ok(_line(txt, "FAILS (rule 8): GF1-CC CLOSED is").startswith("FAILS (rule 8): GF1-CC CLOSED is not refuted (1 GAP-SHOWN"),
                       "E2E W1 GF1-CC FAILS line: 1 not CLOSED")
                chk.ok("GAP-SHOWN qwen3 trees: 3 of 3; words counted: CLOSED, CLOSED, OPEN" in txt, "E2E W1 counted words in order")
                chk.ok(_line(txt, "P1 GAP-SHOWN").endswith("3 of 3 -> occurred; Brier 0.2025"), "E2E W1 P1 occurred")
                chk.ok("Brier (5-class) %.4f" % (0.45 ** 2 + 0.8 ** 2 + 0.15 ** 2 + 0.1 ** 2 + 0.1 ** 2) in _line(txt, "P4 GF1-CC"), "E2E W1 P4 Brier")
                chk.ok("observed MIXED (class OTHER)" in _line(txt, "P6 GF1-N"), "E2E W1 P6 OTHER")
                op, cp = out_paths(out)
                with open(op, encoding="utf-8") as f:
                    chk.ok(f.read() == res["text"], "E2E W1 the outcome file is the printed text")
                with open(cp, encoding="utf-8") as f:
                    rows = list(csv.reader(f))
                chk.ok(len(rows) == 1 + 7 * 18 and rows[1][:3] == ["Q_e1sd1", "CC", "T"], "E2E W1 arms CSV: 7 trees x 18 arms")
                ok_, msg = _refused(lambda: run_core(_fx_world(kinds)[0], out, "e1-guard"), "WRITE-ONCE")
                chk.ok(ok_, "E2E W1 a second --run REFUSES (write-once): %s" % msg[:80])
                chk.ok(W["calls"][:7] == ["Q_e1sd1", "Q_e1sd2", "Q_e1sd3", "N-raw", "N_e1sd2", "N_e1sd3", "N_e1sd1"], "E2E W1 every tree guarded")
                chk.ok("IDENTITY I-2 (GAP-FIX through this path) GF_identity" in txt and "-> REPRODUCED" in txt, "E2E W1 identity I-2 line")
            if wname == "W2":
                chk.ok("Q_e1sd2 PARTIAL (NO-GAP, not counted)" in txt or "Q_e1sd2 CLOSED (NO-GAP, not counted)" in txt, "E2E W2 NO-GAP tree flagged")
                chk.ok("CLOSED by re-centring, not by the passes" in txt[txt.index("[Q_e1sd3] leg"):txt.index("[N-raw] leg")],
                       "E2E W2 RECENTRE tree prints the W-2 sentence")
                chk.ok(_line(txt, "P1 GAP-SHOWN").endswith("2 of 3 -> did not occur; Brier 0.3025"), "E2E W2 P1 2 of 3")
            if wname == "W4":
                chk.ok("LB(I_P) > 0 on 1 of 2 GAP-SHOWN CLOSED qwen3 trees" in txt, "E2E W4 F-GFC needs all CLOSED trees: 1 of 2 -> NOT FIRED")


def st_nomic(chk):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        res, txt, W, out = _e2e(td, "W1", nomic_leg="not-run")
        chk.ok(_line(txt, "GF1-N:").startswith("GF1-N: NOT RUN -- NOT RUN (--nomic-leg not-run"), "NOMIC not-run -> GF1-N NOT RUN line")
        chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: CLOSED", "NOMIC not-run leaves GF1-CC unchanged")
        chk.ok("observed NOT RUN (class OTHER)" in _line(txt, "P6 GF1-N"), "NOMIC not-run P6 scored as OTHER")
        chk.ok(W["calls"][:3] == ["Q_e1sd1", "Q_e1sd2", "Q_e1sd3"] and "N-raw" not in W["calls"], "NOMIC not-run: no nomic tree guarded or read")
        chk.ok(not any(e["name"] in res["stats"] for e in W["entries"] if e["arm"] == "N"), "NOMIC not-run: no nomic statistic")
        res2, txt2, W2, _o = _e2e(td, "W1", guard_refuse=("N_e1sd2",))
        chk.ok(_line(txt2, "GF1-N:").startswith("GF1-N: NOT RUN -- NOT RUN (the [EMB-GUARD] / hygiene of N_e1sd2 refused"),
               "NOMIC a GF1-N tree's guard refusal -> the whole leg NOT RUN")
        chk.ok("N-raw" not in res2["stats"] and "N_e1sd3" not in res2["stats"], "NOMIC refusal: no nomic GF1-N tree measured")
        res3, txt3, W3, _o = _e2e(td, "W1", guard_refuse=("N_e1sd1",))
        chk.ok(_line(txt3, "GF1-N:") == "GF1-N: MIXED" and "N_e1sd1 DESCRIPTIVE: NOT RUN (guard refused" in txt3,
               "NOMIC the descriptive N_e1sd1 refused alone -> GF1-N still scored")
        ok_, msg = _refused(lambda: _e2e(td, "W2", guard_refuse=("Q_e1sd2",)), "REFUSED on tree Q_e1sd2: [EMB-GUARD] fixture refusal for Q_e1sd2")
        chk.ok(ok_, "NOMIC a qwen3 guard refusal REFUSES the run AT the guard, naming the tree: %s" % msg[:100])


def st_dry(chk):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        loader, W = _fx_world(E2E_WORLDS["W1"][0])
        _W, txt = _quiet(dry_core, loader, td, "e1-guard")
        chk.ok(not os.listdir(td), "DRY writes nothing")
        chk.ok(_LABELS[0] is False and "GF1-CC:" not in txt and "GF1-N:" not in txt and "GF1 (this tree)" not in txt and "D_T = " not in txt and "REPRODUCED" not in txt,
               "DRY prints no measure")
        chk.ok(txt.splitlines()[0].startswith("pool "), "DRY the pool line is printed first")
        chk.ok(len(_lines(txt, "TREE ")) == 7 and "held-out %d (registered %d)" % (W["entries"][4]["n"], W["entries"][4]["n"]) in _lines(txt, "TREE N_e1sd2")[0],
               "DRY one TREE line per tree with its own held-out")
        chk.ok("IDENTITY I-2 tree GF_identity: fit set 360" in txt and "COST (SYNTHETIC" in txt and "PLAN:" in txt, "DRY identity / plan / cost lines")
        _W2, txt2 = _quiet(dry_core, _fx_world(E2E_WORLDS["W1"][0])[0], td, "not-run")
        chk.ok("NOMIC LEG: NOT RUN (--nomic-leg not-run" in txt2 and len(_lines(txt2, "TREE N-raw (N): NOT RUN")) == 1, "DRY not-run nomic lines")
        ok_, msg = _refused(lambda: m1(lambda Q: ["x"] * len(Q), W["entries"][0]), "[GFC-LABELS]")
        chk.ok(ok_, "DRY M1 refuses outside --run")


def st_refuse(chk):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        kinds = E2E_WORLDS["W1"][0]
        ok_, msg = _refused(lambda: run_core(_fx_world(kinds, top1={"Q_e1sd2": "0.1234"})[0], os.path.join(td, "a"), "e1-guard"), "[GFC-IDENTITY] Q_e1sd2")
        chk.ok(ok_, "REFUSE I-1 a wrong recorded T top-1 on the SECOND tree: %s" % msg[:90])
        ok_, msg = _refused(lambda: run_core(_fx_world(kinds, top1={"N_e1sd1": "0.1234"})[0], os.path.join(td, "a2"), "e1-guard"), "[GFC-IDENTITY] N_e1sd1")
        chk.ok(ok_, "REFUSE I-1 on the last (descriptive) tree too")
        for key, val in (("WP_5", 1), ("V0", -1)):
            ok_, msg = _refused(lambda: run_core(_fx_world(kinds, gapfix_break=lambda ex, _k=key, _v=val: dict(ex, hits=dict(ex["hits"], **{_k: ex["hits"][_k] + _v})))[0],
                                                 os.path.join(td, "b" + key), "e1-guard"), "[GFC-IDENTITY-GF]")
            chk.ok(ok_, "REFUSE I-2 GAP-FIX hits %s off by %+d" % (key, val))
        ok_, msg = _refused(lambda: run_core(_fx_world(kinds, gapfix_break=lambda ex: dict(ex, ci=dict(ex["ci"], I_0="+9.9999 [+0.0000, +0.0000]")))[0],
                                             os.path.join(td, "c"), "e1-guard"), "[GFC-IDENTITY-GF]")
        chk.ok(ok_, "REFUSE I-2 GAP-FIX I_0 interval")
        ok_, msg = _refused(lambda: run_core(_fx_world(kinds, gapfix_break=lambda ex: dict(ex, fit_n=ex["fit_n"] + 1))[0], os.path.join(td, "d"), "e1-guard"),
                            "[GFC-IDENTITY-GF]")
        chk.ok(ok_, "REFUSE I-2 fit-set size")
        ok_, msg = _refused(lambda: run_core(_fx_world(kinds, leaves_bad="Q_e1sd3")[0], os.path.join(td, "e"), "e1-guard"), "[GFC-LEAVES] Q_e1sd3")
        chk.ok(ok_, "REFUSE leaf count")
        loader, W = _fx_world(kinds)
        W["entries"][5]["n"] += 1
        ok_, msg = _refused(lambda: run_core(loader, os.path.join(td, "f"), "e1-guard"), "[GFC-N] N_e1sd3")
        chk.ok(ok_, "REFUSE held-out n")
        loader, W = _fx_world(kinds)
        e = W["entries"][1]
        leak = e["heldout"][3][0]
        g0 = e["guard"]
        e["guard"] = lambda Lg, _g=g0, _x=leak: _g(Lg) | {_x}
        ok_, msg = _refused(lambda: run_core(loader, os.path.join(td, "g"), "e1-guard"), "[GFC-HYGIENE] Q_e1sd2")
        chk.ok(ok_, "REFUSE a held-out text in the fit set")
        loader, W = _fx_world(kinds)
        e = W["entries"][0]
        g0 = e["guard"]
        e["guard"] = lambda Lg, _g=g0: _g(Lg) | {"a text outside the label set"}
        e["space"]["a text outside the label set"] = e["space"][e["train"][0][0]]
        ok_, msg = _refused(lambda: run_core(loader, os.path.join(td, "h"), "e1-guard"), "[GFC-HYGIENE] Q_e1sd1")
        chk.ok(ok_, "REFUSE a fit text outside the label set")
        os.makedirs(os.path.join(td, "i"))
        with open(os.path.join(td, "i", ARMS_CSV), "w") as f:
            f.write("x")
        called = []
        ok_, msg = _refused(lambda: run_core(lambda L: called.append(1), os.path.join(td, "i"), "e1-guard"), "WRITE-ONCE")
        chk.ok(ok_ and not called, "REFUSE the CSV present: before any load")
        pw = os.path.join(td, "wo", "x.txt")
        write_once(pw, "a")
        try:
            write_once(pw, "b")
            again = "overwritten"
        except FileExistsError:
            again = "refused"
        with open(pw, encoding="utf-8") as f:
            chk.ok(again == "refused" and f.read() == "a", "REFUSE write_once opens mode x: a second write raises, the first text stays")
        ok_, msg = _refused(lambda: admit(dict(entries=[]), "maybe", []), "--nomic-leg 'maybe'")
        chk.ok(ok_, "REFUSE an unknown nomic leg value in admit()")


# ── ruling P-1 (seed replacement), P-2 (dry-run V fits), P-3 (the tree named), C-2 (R2 / R5) ───────────────────────────────
_FP = {}                 # fingerprint of a fit matrix's first row -> tree name (the patched fitter's key)
B6_MSG = "V seed %d: mean resultant length outside (0, 1) (a one-member or degenerate cell); %s"


@contextlib.contextmanager
def _patched_vmf(void=(), nonb6=(), real=True, log=None):
    """FM.vmf_em replaced: (tree, seed) in void raises FLAT-MIX-MMLU's own B6 refusal text (FM.refuse, FM.B6); in nonb6 a refusal
    without B6; otherwise the real fitter (real=True) or a cheap stand-in. log records every (tree, seed) tried, in order."""
    orig = FM.vmf_em

    def fake(X, k, seed, *a, **kw):
        nm = _FP.get(np.asarray(X[0], dtype=np.float64).tobytes(), "?")
        if log is not None:
            log.append((nm, int(seed)))
            if len(log) > 60:
                raise AssertionError("SELFTEST FAILED: the P-1 rule loops (more than 60 fits tried: %s)" % log[-8:])
        if (nm, seed) in nonb6:
            FM.refuse("V seed %d: a synthetic non-B6 failure" % seed)
        if (nm, seed) in void:
            FM.refuse(B6_MSG % (seed, FM.B6))
        if real:
            return orig(X, k, seed, *a, **kw)
        return dict(mu=np.eye(k, X.shape[1]), kappa=np.ones(k), pi=np.full(k, 1.0 / k), iters=100 + seed, converged=True, mean_ll=float(seed))
    FM.vmf_em = fake
    try:
        yield
    finally:
        FM.vmf_em = orig


def _fp_world(W):
    for e in W["entries"]:
        _FP[np.asarray(e["space"]["%s fit A0 n000" % e["name"]], dtype=np.float64).tobytes()] = e["name"]


def _rule(void, nonb6=()):
    X = FM.unit_rows(np.random.default_rng(5).standard_normal((40, 6)))
    _FP[X[0].tobytes()] = "t"
    log = []
    with _patched_vmf(void=set(("t", s) for s in void), nonb6=set(("t", s) for s in nonb6), real=False, log=log):
        V, lines, why = fit_v_rule(X, 4, "t")
    return V, lines, why, [s for _n, s in log]


def st_vseed(chk):
    def seeds(V):
        return [V["V%d" % j]["seed"] for j in range(5)]
    V, lines, why, log = _rule(())
    chk.ok(why is None and seeds(V) == [0, 1, 2, 3, 4] and log == [0, 1, 2, 3, 4], "P-1 no VOID: slots V0..V4 = seeds 0..4, nothing else tried")
    chk.ok(lines[0] == "VFIT t V0: seed 0 B6 OK (converged True, iters 100, mean ll 0.0000)", "P-2 per-slot line by value: %s" % lines[0])
    V, lines, why, log = _rule((0,))
    chk.ok(seeds(V) == [5, 1, 2, 3, 4] and log == [0, 5, 1, 2, 3, 4], "P-1 seed 0 VOID -> seed 5 in slot V0 (log %s)" % log)
    chk.ok(lines[0] == "VFIT t V0: seed 0 B6-VOID -> seed 5 OK REPLACED (ruling P-1) (converged True, iters 105, mean ll 5.0000)",
           "P-1 the ruled line '<tree> V<j>: seed s B6-VOID -> seed t OK': %s" % lines[0])
    V, lines, why, log = _rule((0, 5))
    chk.ok(seeds(V) == [6, 1, 2, 3, 4] and log == [0, 5, 6, 1, 2, 3, 4] and lines[0].startswith("VFIT t V0: seed 0 B6-VOID -> seed 5 B6-VOID -> seed 6 OK"),
           "P-1 seeds 0 and 5 VOID -> seed 6 (the next unused)")
    V, lines, why, log = _rule((0, 5, 2))
    chk.ok(seeds(V) == [6, 1, 7, 3, 4] and log == [0, 5, 6, 1, 2, 7, 3, 4], "P-1 a tried VOID seed counts as used: V0 -> 6, V2 -> 7 (log %s)" % log)
    V, lines, why, log = _rule((3,))
    chk.ok(seeds(V) == [0, 1, 2, 5, 4] and log == [0, 1, 2, 3, 5, 4], "P-1 a later slot (V3) is replaced in ITS slot by seed 5")
    V, lines, why, log = _rule((1, 3))
    chk.ok(seeds(V) == [0, 5, 2, 6, 4], "P-1 two slots VOID: V1 -> 5, V3 -> 6 (lowest unused, in slot order)")
    V, lines, why, log = _rule((4, 5, 6, 7, 8))
    chk.ok(V is not None and seeds(V) == [0, 1, 2, 3, 9], "P-1 boundary: seed 9 is the last replacement and is used")
    V, lines, why, log = _rule((0, 5, 6, 7, 8, 9))
    chk.ok(V is None and log == [0, 5, 6, 7, 8, 9] and lines == ["VFIT t V0: seed 0 B6-VOID -> seed 5 B6-VOID -> seed 6 B6-VOID -> seed 7 B6-VOID "
                                                                  "-> seed 8 B6-VOID -> seed 9 B6-VOID -> VOID-TREE"],
           "P-1 seeds 5-9 all VOID -> VOID-TREE; no seed 10, no further slot fitted: %s" % lines)
    chk.ok(why.startswith("VOID-TREE (ruling P-1: slot V0 seed 0 B6-VOID") and "seeds 5-9 exhausted" in why, "P-1 VOID-TREE reason")
    V, lines, why, log = _rule((1, 5, 6, 7, 8, 3))
    chk.ok(V is None and log == [0, 1, 5, 6, 7, 8, 9, 2, 3] and lines[-1].endswith("V3: seed 3 B6-VOID -> VOID-TREE"),
           "P-1 the pool is shared across slots: V1 takes 9, V3 then finds 5-9 used -> VOID-TREE (log %s)" % log)
    ok_, msg = _refused(lambda: _rule((), nonb6=(2,)), "[GFC-VFIT] tree t V2 seed 2 (not a B6 VOID)")
    chk.ok(ok_, "P-1 a non-B6 fitter refusal is NOT a VOID: the run refuses, naming tree, slot and seed: %s" % msg[:100])
    # the REAL fitter: cells of identical points are B6 for every seed -> VOID-TREE; a regular set fits seeds 0-4
    Xd = np.repeat(FM.unit_rows(np.random.default_rng(4).standard_normal((3, 8))), 10, axis=0)
    V, lines, why = fit_v_rule(Xd, 3, "deg")
    chk.ok(V is None and lines[-1] == "VFIT deg V0: seed 0 B6-VOID -> seed 5 B6-VOID -> seed 6 B6-VOID -> seed 7 B6-VOID -> seed 8 B6-VOID "
           "-> seed 9 B6-VOID -> VOID-TREE", "P-1 the real fitter's B6 refusal is classified VOID (real message)")
    Xr = FM.unit_rows(np.random.default_rng(6).standard_normal((60, 8)))
    V, lines, why = fit_v_rule(Xr, 3, "reg")
    chk.ok(why is None and [V["V%d" % j]["seed"] for j in range(5)] == [0, 1, 2, 3, 4] and all(" B6 OK " in ln for ln in lines),
           "P-1 the real fitter on a regular set: seeds 0-4, all B6 OK")


def _stat(name, gap, word, iplo=0.01, d=-0.02):
    iv = dict(d=d, lo=d - 0.01, hi=d + 0.01, disc=0.1)
    return dict(name=name, gap=gap, word=word, ip=dict(d=iplo + 0.005, lo=iplo, hi=iplo + 0.01), dt=dict(iv), dr=dict(iv), i0=dict(d=0.0))


def _render(cc, nn, void=()):
    names = ("Q_e1sd1", "Q_e1sd2", "Q_e1sd3", "N-raw", "N_e1sd2", "N_e1sd3")
    W = dict(entries=[dict(name=n, leg="CC" if i < 3 else "N", status="ADMITTED") for i, n in enumerate(names)])
    stats = {}
    for i, (n, row) in enumerate(zip(names, list(cc) + list(nn))):
        if n in void:
            W["entries"][i]["status"] = "VOID-TREE (ruling P-1: fixture)"
            continue
        stats[n] = _stat(n, *row)
    L, res = render_all(W, stats, None)
    return "\n".join(L), res


def st_render(chk):
    # C-2 / R2: a NO-GAP tree reading CLOSED with LB(I_P) <= 0 beside GF1-CC CLOSED is NOT among F-GFC's trees
    txt, res = _render([(True, "CLOSED", 0.01), (True, "CLOSED", 0.02), (False, "CLOSED", -0.01)], [(True, "OPEN"), (True, "OPEN"), (True, "OPEN")])
    chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: CLOSED" and _line(txt, "LB(I_P) > 0 on").startswith("LB(I_P) > 0 on 2 of 2 GAP-SHOWN CLOSED qwen3 trees"),
           "R2 the NO-GAP CLOSED tree is not counted: 'LB(I_P) > 0 on 2 of 2' (%s)" % _line(txt, "LB(I_P) > 0 on")[:40])
    chk.ok(res["m"] == 2 and res["c"] == 2 and res["fires"] is True and _line(txt, "FALSIFIER F-GFC").startswith("FALSIFIER F-GFC FIRES"),
           "R2 F-GFC FIRES (m 2 >= 2, and 2 of 2 under the tool's line)")
    # C-2 / R5: the GF1-N FAILS line reads the N rows, not the CC rows (both directions)
    txt, res = _render([(True, "CLOSED"), (True, "CLOSED"), (True, "OPEN")], [(True, "PARTIAL"), (True, "OPEN"), (True, "CLOSED")])
    chk.ok(_line(txt, "FAILS (rule 8): GF1-CC CLOSED is").startswith("FAILS (rule 8): GF1-CC CLOSED is not refuted")
           and _line(txt, "FAILS (rule 8): GF1-N CLOSED is") == "FAILS (rule 8): GF1-N CLOSED is REFUTED", "R5 CC not refuted, N REFUTED (by value)")
    txt, res = _render([(True, "PARTIAL"), (True, "OPEN"), (True, "CLOSED")], [(True, "CLOSED"), (True, "CLOSED"), (True, "OPEN")])
    chk.ok(_line(txt, "FAILS (rule 8): GF1-CC CLOSED is").startswith("FAILS (rule 8): GF1-CC CLOSED is REFUTED")
           and _line(txt, "FAILS (rule 8): GF1-N CLOSED is") == "FAILS (rule 8): GF1-N CLOSED is not refuted", "R5 CC REFUTED, N not refuted (by value)")
    chk.ok(_line(txt, "GF1-N:") == "GF1-N: CLOSED" and _line(txt, "GF1-CC:") == "GF1-CC: MIXED", "R5 the two words from their own rows")
    # P-1 VOID-TREE drops out of GF1-CC under the registered words
    txt, res = _render([(True, "CLOSED"), (True, "CLOSED"), (True, "OPEN")], [(True, "OPEN")] * 3, void=("Q_e1sd2",))
    chk.ok(_line(txt, "per tree:").startswith("per tree: Q_e1sd1 CLOSED; Q_e1sd2 VOID-TREE (ruling P-1; not counted); Q_e1sd3 OPEN"), "VOID per-tree text")
    chk.ok(_line(txt, "GAP-SHOWN qwen3 trees:") == "GAP-SHOWN qwen3 trees: 2 of 3; words counted: CLOSED, OPEN; VOID-TREE (ruling P-1, dropped out): Q_e1sd2",
           "VOID the counted line: 2 of 3, the VOID tree named")
    chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: MIXED" and res["fires"] is False, "VOID GF1-CC on the other two: CLOSED + OPEN -> MIXED")
    chk.ok(_line(txt, "P1 GAP-SHOWN").endswith("2 of 3 -> did not occur; Brier 0.3025"), "VOID P1: a VOID-TREE is not GAP-SHOWN")
    chk.ok(_line(txt, "P2 D_T").endswith("Q_e1sd2 VOID-TREE NOT SCORED; Q_e1sd3 -0.0200 HELD -> 2 of 2 HELD (1 VOID-TREE not scored: Q_e1sd2)"),
           "VOID P2 tally over the scored trees, the VOID named: %s" % _line(txt, "P2 D_T")[-90:])
    chk.ok("Q_e1sd2 VOID-TREE;" in _line(txt, "P5 I_0") and _line(txt, "P5 I_0").startswith("P5 I_0 > I_P at the point on >= 2 of 3 qwen3 trees, probability 0.75: 0 of 3"),
           "VOID P5 line names the VOID tree")
    txt, res = _render([(True, "CLOSED"), (True, "CLOSED"), (True, "CLOSED")], [(True, "OPEN")] * 3, void=("Q_e1sd1", "Q_e1sd3"))
    chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: NOT EVALUABLE", "VOID two VOID-TREEs -> fewer than 2 GAP-SHOWN -> NOT EVALUABLE")
    txt, res = _render([(True, "CLOSED"), (True, "CLOSED"), (True, "OPEN")], [(True, "CLOSED"), (True, "OPEN"), (True, "CLOSED")], void=("N_e1sd3",))
    chk.ok(_line(txt, "GF1-N:") == "GF1-N: MIXED" and "VOID-TREE (ruling P-1, dropped out): N_e1sd3" in _line(txt, "GAP-SHOWN nomic trees:"),
           "VOID an N tree drops out of GF1-N (CLOSED + OPEN -> MIXED)")


def _o_agg(words_gap):
    c = [w for w, g in words_gap if g]
    if len(c) < 2:
        return "NOT EVALUABLE"
    for w in ("CLOSED", "PARTIAL", "OPEN"):
        if c.count(w) >= 2:
            return w
    return "MIXED"


def st_e2e_void(chk):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        kinds, seed = E2E_WORLDS["W1"][0], E2E_WORLDS["W1"][4]
        # (a) Q_e1sd2 V0 seed 0 VOID -> seed 5 through run_core; every number against the oracle fitted at seed 5
        loader, W = _fx_world(kinds, seed=seed)
        _fp_world(W)
        log = []
        with _patched_vmf(void={("Q_e1sd2", 0)}, log=log):
            res, txt = _quiet(run_core, loader, os.path.join(td, "a"), "e1-guard")
        chk.ok(_line(txt, "VFIT Q_e1sd2 V0:").startswith("VFIT Q_e1sd2 V0: seed 0 B6-VOID -> seed 5 OK REPLACED (ruling P-1)"), "E2E-VOID the replacement printed in --run")
        chk.ok([s for n, s in log if n == "Q_e1sd2"] == [0, 5, 1, 2, 3, 4] and [s for n, s in log if n == "Q_e1sd1"] == [0, 1, 2, 3, 4],
               "E2E-VOID seeds tried per tree (Q_e1sd2 0,5,1..4; the others 0..4)")
        e = [x for x in W["entries"] if x["name"] == "Q_e1sd2"][0]
        R = res["stats"]["Q_e1sd2"]
        oa = _o_arms(e, e["fit"], seeds=(5, 1, 2, 3, 4))
        ow = _o_word(oa, FM.twin_groups([t for t, _ in e["heldout"]])[0], len(e["heldout"]))
        chk.ok(R["arms"]["V0"]["hits"] == int(sum(oa["V0"])) and R["arms"]["V1"]["hits"] == int(sum(oa["V1"])), "E2E-VOID V0 hits = the oracle's seed-5 fit")
        chk.ok(R["word"] == ow["word"] and f4(R["dr"]["d"]) == f4(ow["dr"][0]) and abs(R["bar"] - ow["bar"]) < 1e-12, "E2E-VOID word / D_R / bar = oracle")
        chk.ok("V0 seed 5 " in _line(txt[txt.index("[Q_e1sd2] leg"):], "V fits (V0..V4"), "E2E-VOID the outcome's V fits line carries V0 seed 5")
        ws = [(res["stats"][n]["word"], res["stats"][n]["gap"]) for n in ("Q_e1sd1", "Q_e1sd2", "Q_e1sd3")]
        chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: %s" % _o_agg(ws), "E2E-VOID GF1-CC = the oracle aggregate (%s)" % _o_agg(ws))
        # (b) Q_e1sd2 seeds 0 and 5-9 VOID -> VOID-TREE; GF1-CC on Q_e1sd1 (CLOSED) and Q_e1sd3 (OPEN) -> MIXED; the run completes
        loader, W = _fx_world(kinds, seed=seed)
        _fp_world(W)
        out = os.path.join(td, "b")
        with _patched_vmf(void=set(("Q_e1sd2", s) for s in (0, 5, 6, 7, 8, 9))):
            res, txt = _quiet(run_core, loader, out, "e1-guard")
        chk.ok("Q_e1sd2" not in res["stats"] and _line(txt, "[Q_e1sd2] leg").startswith("[Q_e1sd2] leg DECIDING (GF1-CC; qwen3): VOID-TREE (ruling P-1: slot V0"),
               "E2E-VOID VOID-TREE printed in the outcome, no statistic")
        chk.ok(_line(txt, "GF1-CC:") == "GF1-CC: MIXED" and _line(txt, "GAP-SHOWN qwen3 trees:").startswith("GAP-SHOWN qwen3 trees: 2 of 3; words counted: CLOSED, OPEN; VOID-TREE"),
               "E2E-VOID GF1-CC on the other two -> MIXED")
        chk.ok(_line(txt, "FALSIFIER F-GFC").startswith("FALSIFIER F-GFC NOT FIRED") and _line(txt, "P1 GAP-SHOWN").endswith("2 of 3 -> did not occur; Brier 0.3025"),
               "E2E-VOID F-GFC NOT FIRED; P1 2 of 3")
        with open(out_paths(out)[1], encoding="utf-8") as f:
            chk.ok(len(list(csv.reader(f))) == 1 + 6 * 18, "E2E-VOID arms CSV: 6 measured trees")
        # (c) an N tree VOID-TREE drops out of GF1-N; (d) the descriptive N_e1sd1 VOID-TREE is printed as such
        kinds2, seed2 = E2E_WORLDS["W2"][0], E2E_WORLDS["W2"][4]
        loader, W = _fx_world(kinds2, seed=seed2)
        _fp_world(W)
        with _patched_vmf(void=set((n, s) for n in ("N_e1sd2", "N_e1sd1") for s in (3, 5, 6, 7, 8, 9))):
            res, txt = _quiet(run_core, loader, os.path.join(td, "c"), "e1-guard")
        wn = [(res["stats"][n]["word"], res["stats"][n]["gap"]) for n in ("N-raw", "N_e1sd3")]
        chk.ok(_line(txt, "GF1-N:") == "GF1-N: %s" % _o_agg(wn) and "VOID-TREE (ruling P-1, dropped out): N_e1sd2" in _line(txt, "GAP-SHOWN nomic trees:"),
               "E2E-VOID N_e1sd2 VOID-TREE: GF1-N on the other two (%s)" % _line(txt, "GF1-N:"))
        chk.ok(_line(txt, "N_e1sd1 DESCRIPTIVE:").startswith("N_e1sd1 DESCRIPTIVE: VOID-TREE (ruling P-1: slot V3"), "E2E-VOID N_e1sd1 VOID-TREE descriptive line")
        # (e) P-2: the dry-run fits V label-free and prints every slot; a VOID-TREE is reported, nothing measured or written
        dd = os.path.join(td, "dry")
        os.makedirs(dd)
        loader, W = _fx_world(kinds, seed=seed)
        _fp_world(W)
        with _patched_vmf(void={("Q_e1sd3", 2), ("N-raw", 0), ("N-raw", 5)} | set(("N_e1sd3", s) for s in (4, 5, 6, 7, 8, 9))):
            _W, txt = _quiet(dry_core, loader, dd, "e1-guard")
        chk.ok(len(_lines(txt, "VFIT ")) == 35 and _line(txt, "VFIT Q_e1sd3 V2:").startswith("VFIT Q_e1sd3 V2: seed 2 B6-VOID -> seed 5 OK REPLACED")
               and _line(txt, "VFIT N-raw V0:").startswith("VFIT N-raw V0: seed 0 B6-VOID -> seed 5 B6-VOID -> seed 6 OK"),
               "P-2 dry-run: one VFIT line per slot, replacements printed")
        chk.ok(_line(txt, "VFIT N_e1sd3 V4:").endswith("-> seed 9 B6-VOID -> VOID-TREE") and "[GAP-FIX-CC] N_e1sd3: VOID-TREE (ruling P-1" in txt,
               "P-2 dry-run reports a VOID-TREE before --run")
        chk.ok(_line(txt, "V FITS (P-2, label-free):").startswith("V FITS (P-2, label-free): 30 slots fitted, 2 by a ruling P-1 replacement; VOID-TREE 1"),
               "P-2 dry-run summary by value: %s" % _line(txt, "V FITS (P-2")[:90])
        chk.ok(not os.listdir(dd) and _LABELS[0] is False and "GF1-CC:" not in txt and "D_T = " not in txt, "P-2 dry-run: no measure, nothing written")
        loader, W = _fx_world(kinds, seed=seed)
        _W, txt = _quiet(dry_core, loader, dd, "e1-guard")
        chk.ok(len(_lines(txt, "VFIT ")) == 35 and all(" B6 OK " in ln for ln in _lines(txt, "VFIT "))
               and _line(txt, "V FITS (P-2").startswith("V FITS (P-2, label-free): 35 slots fitted, 0 by a ruling P-1 replacement; VOID-TREE 0"),
               "P-2 dry-run with the real fitter: 35 slots B6 OK")
        # P-3: the tree is named in every refusal (fitter, structure, guard; --run and --dry-run)
        loader, W = _fx_world(kinds, seed=seed)
        _fp_world(W)
        with _patched_vmf(nonb6={("Q_e1sd3", 2)}):
            ok_, msg = _refused(lambda: run_core(loader, os.path.join(td, "p3a"), "e1-guard"), "REFUSED on tree Q_e1sd3:")
        chk.ok(ok_ and "[GFC-VFIT] tree Q_e1sd3 V2 seed 2 (not a B6 VOID)" in msg, "P-3 --run: a non-B6 fitter refusal names the tree: %s" % msg[:120])
        loader, W = _fx_world(kinds, seed=seed)
        _fp_world(W)
        with _patched_vmf(nonb6={("N_e1sd2", 0)}):
            ok_, msg = _refused(lambda: dry_core(loader, os.path.join(td, "p3b"), "e1-guard"), "REFUSED on tree N_e1sd2:")
        chk.ok(ok_, "P-3 --dry-run: the same refusal names the tree: %s" % msg[:100])
        for mode in ("run", "dry"):
            loader, W = _fx_world(kinds, seed=seed)
            e = W["entries"][2]
            e["tree"]["byid"]["B"]["childIds"].append(e["tree"]["leaf_ids"][0])
            fn = run_core if mode == "run" else dry_core
            ok_, msg = _refused(lambda: fn(loader, os.path.join(td, "p3c" + mode), "e1-guard"), "REFUSED on tree Q_e1sd3: ")
            chk.ok(ok_ and "has 2 parents" in msg, "P-3 --%s: a structure refusal (gap_fix, no tree name of its own) names the tree" % mode)
            loader, W = _fx_world(kinds, seed=seed)
            W["entries"][1]["guard"] = lambda Lg: (_ for _ in ()).throw(SystemExit("[EMB-GUARD] a refusal without a name"))
            ok_, msg = _refused(lambda: fn(loader, os.path.join(td, "p3d" + mode), "e1-guard"), "REFUSED on tree Q_e1sd2: [EMB-GUARD] a refusal without a name")
            chk.ok(ok_, "P-3 --%s: a qwen3 guard refusal names the tree" % mode)


def st_main(chk):
    rc, out = _child(["--run", "--data-root", os.path.join(tempfile.gettempdir(), "nowhere")])
    chk.ok(rc != 0 and "--nomic-leg" in out and "REQUIRED" in out, "MAIN --run without --nomic-leg REFUSES (rc %d)" % rc)
    rc, out = _child(["--dry-run", "--nomic-leg", "maybe"])
    chk.ok(rc == 2 and "invalid choice" in out, "MAIN an unknown --nomic-leg value is fatal (argparse rc 2)")
    rc, out = _child(["--banner"], env_extra={"PYTHONIOENCODING": "cp1252"})
    chk.ok(rc == 0 and "— GAP-FIX-CC" in out, "MAIN D-4: --banner prints the em dash under a cp1252 stdout (rc %d)" % rc)


CASES = (("C-PURE", st_pure), ("C-PLANT", st_plant), ("C-E2E", st_e2e), ("C-NOMIC", st_nomic), ("C-DRY", st_dry), ("C-REFUSE", st_refuse),
         ("C-VSEED", st_vseed), ("C-RENDER", st_render), ("C-E2E-VOID", st_e2e_void), ("C-MAIN", st_main))


def _child(args, env_extra=None, src=None, timeout=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    cmd = [sys.executable, src or os.path.abspath(__file__)] + args
    try:
        p = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""
    return p.returncode, p.stdout.decode("utf-8", "replace")


def selftest(only=None, quiet=False):
    chk = Checks(quiet)
    chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "THREADS the three thread variables are 1")
    for name, fn in CASES:
        if only and name not in only:
            continue
        t0 = time.perf_counter()
        fn(chk)
        if not quiet:
            print("  -- %s done (%.1f s)" % (name, time.perf_counter() - t0))
    print("%s SELFTEST: %d checks passed" % (TAG, chk.n))
    return 0


# ── mutants: (id, selftest cases, old, new); each must make the named cases fail ───────────────────────────────────────────
NL = "\n"
MUTANTS = (
    ("M01 aggregate: the first two counted trees only", ("C-PURE",), "    counted = [w for _n, g, w in rows if bool(g)]", "    counted = [w for _n, g, w in rows if bool(g)][:2]"),
    ("M02 aggregate: NO-GAP trees counted", ("C-PURE", "C-E2E"), "    counted = [w for _n, g, w in rows if bool(g)]", "    counted = [w for _n, g, w in rows]"),
    ("M03 aggregate: NOT EVALUABLE threshold < 2 -> < 1", ("C-PURE", "C-E2E"), "    if len(counted) < 2:", "    if len(counted) < 1:"),
    ("M04 aggregate: >= 2 -> >= 1 (first word wins)", ("C-PURE", "C-E2E"), "        if sum(1 for x in counted if x == w) >= 2:", "        if sum(1 for x in counted if x == w) >= 1:"),
    ("M05 bar = min(MDE80, spread_V) (D-1)", ("C-PLANT",), "    bar = max(mde, spread_v)", "    bar = min(mde, spread_v)"),
    ("M06 bar = MDE80 only (spread_V dropped)", ("C-PLANT",), "    bar = max(mde, spread_v)", "    bar = mde"),
    ("M07 MDE80 from the registered 0.0176, not measured", ("C-PLANT",), '    mde = REG["mde_k"] * math.sqrt(dr["disc"] / n)', '    mde = REG["mde_dr"]'),
    ("M08 spread_V over V1..V4 only", ("C-PLANT",), '    vm1 = [arms["V%d" % s]["m1"] for s in REG["seeds"]]', '    vm1 = [arms["V%d" % s]["m1"] for s in REG["seeds"][1:]]'),
    ("M09 GAP-SHOWN UB < 0 -> <= 0", ("C-PLANT",), '    gap = bool(dt["hi"] < 0)', '    gap = bool(dt["hi"] <= 0)'),
    ("M10 GAP-SHOWN on the point, not the UB", ("C-PLANT", "C-E2E"), '    gap = bool(dt["hi"] < 0)', '    gap = bool(dt["d"] < 0)'),
    ("M11 D_R against T", ("C-PLANT", "C-E2E"), '    dt, dr, ir = pm("T", "V0"), pm(td, "V0"), pm(td, "T")', '    dt, dr, ir = pm("T", "V0"), pm(td, "T"), pm(td, "T")'),
    ("M12 I_R against V0", ("C-PLANT", "C-E2E"), '    dt, dr, ir = pm("T", "V0"), pm(td, "V0"), pm(td, "T")', '    dt, dr, ir = pm("T", "V0"), pm(td, "V0"), pm(td, "V0")'),
    ("M13 I_P = WP_5 - T", ("C-PLANT", "C-E2E"), '    i0, ip = pm("WP_0", "T"), pm(td, "WP_0")', '    i0, ip = pm("WP_0", "T"), pm(td, "T")'),
    ("M14 deciding T 5 -> 10", ("C-E2E", "C-PLANT"), '    td = "WP_%d" % REG["t_decide"]' + NL + '    dt, dr, ir', '    td = "WP_10"' + NL + '    dt, dr, ir'),
    ("M15 deciding WP -> GL", ("C-E2E", "C-PLANT"), '    td = "WP_%d" % REG["t_decide"]' + NL + '    dt, dr, ir', '    td = "GL_%d" % REG["t_decide"]' + NL + '    dt, dr, ir'),
    ("M16 F-GFC on any CLOSED tree (>= 1)", ("C-PURE", "C-E2E"), "    return bool(word == \"CLOSED\" and c > 0 and m == c), m, c", "    return bool(word == \"CLOSED\" and m >= 1), m, c"),
    ("M17 F-GFC LB(I_P) >= 0", ("C-PURE",), '    m = sum(1 for ip in closed_stats if bool(ip["lo"] > 0))', '    m = sum(1 for ip in closed_stats if bool(ip["lo"] >= 0))'),
    ("M18 F-GFC fires without CLOSED", ("C-PURE", "C-E2E"), "    return bool(word == \"CLOSED\" and c > 0 and m == c), m, c", "    return bool(c > 0 and m == c), m, c"),
    ("M19 FAILS counts NO-GAP trees", ("C-PURE",), '    return bool(sum(1 for _n, g, w in rows if bool(g) and w != "CLOSED") >= 2)', '    return bool(sum(1 for _n, g, w in rows if w != "CLOSED") >= 2)'),
    ("M20 GF1-N counts N_e1sd1", ("C-E2E",), '        nn = leg_rows(W, stats, "N")', '        nn = leg_rows(W, stats, "N") + leg_rows(W, stats, "N1")'),
    ("M21 GF1-CC on all admitted trees (joined, S4)", ("C-E2E",), '    cc = leg_rows(W, stats, "CC")', '    cc = [stats[e["name"]] for e in W["entries"] if e["name"] in stats][:3][::-1]'),
    ("M22 re-centring sentence omitted", ("C-PLANT", "C-E2E"), '    if w == "CLOSED" and bool(R["ip"]["lo"] <= 0 <= R["ip"]["hi"]):', '    if False:'),
    ("M23 P1 >= 2 instead of 3 of 3", ("C-PURE", "C-E2E"), "    e1 = bool(gs == 3)", "    e1 = bool(gs >= 2)"),
    ("M24 P2 band exclusive", ("C-PURE",), "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])"),
    ("M25 P5 >= 3 (all) instead of >= 2", ("C-PURE",), "    e5 = bool(k5 >= 2)", "    e5 = bool(k5 >= 3)"),
    ("M26 P5 I_0 >= I_P", ("C-PURE",), '    k5 = sum(1 for R in live if bool(R["i0"]["d"] > R["ip"]["d"]))', '    k5 = sum(1 for R in live if bool(R["i0"]["d"] >= R["ip"]["d"]))'),
    ("M27 P6 NOT RUN not lumped into OTHER", ("C-PURE", "C-NOMIC"), '    cls = word_n if word_n in WORDS else "OTHER"', "    cls = word_n"),
    ("M28 P4 Brier on a fixed outcome", ("C-PURE", "C-E2E"), '        word_cc, brier_multi(PRED["P4"], word_cc)))', '        word_cc, brier_multi(PRED["P4"], "PARTIAL")))'),
    ("M29 V fitted on the label set (wrong side)", ("C-E2E",), '    Xv = mat(e["space"], e["fit"])', '    Xv = mat(e["space"], [t for t, _ in e["train"]])'),
    ("M30 refinement on the label set (wrong side)", ("C-E2E",), "    X = mat(e[\"space\"], e[\"fit\"])" + NL + "    mask, par, roots", "    X = mat(e[\"space\"], [t for t, _ in e[\"train\"]])" + NL + "    mask, par, roots"),
    ("M31 M1 majority from the held-out side", ("C-E2E",), '    sc, hits, _kh = FM.m1_block(fn, e["Qt"], e["Qh"], e["train"], e["heldout"])', '    sc, hits, _kh = FM.m1_block(fn, e["Qh"], e["Qh"], e["heldout"], e["heldout"])'),
    ("M32 identity I-1 removed", ("C-REFUSE",), "    if got != e[\"top1\"]:", "    if False:"),
    ("M33 identity I-2 removed", ("C-REFUSE",), "    if bad:" + NL + "        refuse(\"[GFC-IDENTITY-GF]", "    if False:" + NL + "        refuse(\"[GFC-IDENTITY-GF]"),
    ("M34 identity I-2 skipped in run_core", ("C-REFUSE", "C-E2E"), "            identity_gapfix(G, L)", "            pass"),
    ("M35 hygiene_core removed", ("C-REFUSE",), "    if over or outside:", "    if False:"),
    ("M36 leaf-count check removed", ("C-REFUSE",), '        if len(e["tree"]["leaf_ids"]) != e["leaves"]:', "        if False:"),
    ("M37 held-out n check removed", ("C-REFUSE",), '        if len(e["heldout"]) != e["n"]:', "        if False:"),
    ("M38 write-once x -> w", ("C-E2E", "C-REFUSE"), '    with open(path, "x", encoding="utf-8", newline="\\n") as f:', '    with open(path, "w", encoding="utf-8", newline="\\n") as f:'),
    ("M39 outputs pre-check removed", ("C-REFUSE",), "        if os.path.exists(p):" + NL + "            refuse(\"%s exists: outcome", "        if False:" + NL + "            refuse(\"%s exists: outcome"),
    ("M40 nomic gate: a GF1-N refusal leaves the leg on", ("C-NOMIC",), "            if e[\"leg\"] == \"N\":" + NL + "                nomic_off =", "            if False:" + NL + "                nomic_off ="),
    ("M41 nomic gate: a qwen3 refusal swallowed", ("C-NOMIC", "C-E2E-VOID"), "            if e[\"arm\"] != \"N\":" + NL + "                raise", "            if False:" + NL + "                raise"),
    ("M42 nomic not-run ignored", ("C-NOMIC",), "        if e[\"arm\"] == \"N\" and nomic_off is not None:" + NL + "            e[\"status\"] = nomic_off" + NL + "            continue",
     "        if False:" + NL + "            e[\"status\"] = nomic_off" + NL + "            continue"),
    ("M43 dry-run computes M1 (labels flag set)", ("C-DRY",), "    nomic_off = admit(W, nomic_leg, L)" + NL + "    for e in W[\"entries\"]:" + NL + "        if e[\"status\"] != \"ADMITTED\":" + NL + "            say(L, \"TREE",
     "    nomic_off = admit(W, nomic_leg, L)" + NL + "    _LABELS[0] = True" + NL + "    for e in W[\"entries\"]:" + NL + "        if e[\"status\"] != \"ADMITTED\":" + NL + "            say(L, \"TREE"),
    ("M44 D-3 holds/fails omitted", ("C-PLANT",), '        return "holds" if bool(c) else "fails"', '        return ""'),
    ("M45 D-4 stdout reconfigure removed", ("C-MAIN",), '            stream.reconfigure(encoding="utf-8")', "            pass"),
    ("M46 --nomic-leg default e1-guard", ("C-MAIN",), "    if a.nomic_leg is None:" + NL + "        refuse(", "    if False:" + NL + "        refuse("),
    ("M48 N_e1sd1 descriptive line omitted", ("C-E2E",), '            L.append("  %s DESCRIPTIVE (never counted): the GF1 rule would read %s (%s); D_T %s, D_R %s" % (',
     '            (lambda *a: None)("  %s DESCRIPTIVE (never counted): the GF1 rule would read %s (%s); D_T %s, D_R %s" % ('),
    ("M49 GF1-N NOT RUN line omitted", ("C-NOMIC",), '        L.append("  GF1-N: NOT RUN -- %s" % nomic_off)', '        pass'),
    ("M50 per-tree FAILS always 'not refuted'", ("C-E2E",), '    if R["refuted"]:' + NL + '        L.append("    FAILS (rule 8): CLOSED is REFUTED', '    if False:' + NL + '        L.append("    FAILS (rule 8): CLOSED is REFUTED'),
    ("M47 i.i.d. interval in the deciding path", ("C-E2E",), "    groups, G_ = FM.twin_groups([t for t, _ in e[\"heldout\"]])" + NL + "                R = tree_stats(e[\"name\"], e[\"leg\"], arms, groups, len(e[\"heldout\"]))",
     "    groups, G_ = FM.twin_groups([t for t, _ in e[\"heldout\"]])" + NL + "                R = tree_stats(e[\"name\"], e[\"leg\"], arms, np.arange(len(e[\"heldout\"])), len(e[\"heldout\"]))"),
    # ruling P-1 / P-2 / P-3 / C-2 (2026-10-08 delta)
    ("V01 P-1 replacement = slot seed + 5", ("C-VSEED",), "                s = free[0]", "                s = s0 + 5"),
    ("V02 P-1 replacement = the HIGHEST unused seed", ("C-VSEED",), "                s = free[0]", "                s = free[-1]"),
    ("V03 P-1 replacement = the second unused seed", ("C-VSEED",), "                s = free[0]", "                s = free[1] if len(free) > 1 else free[0]"),
    ("V04 P-1 a tried VOID seed not counted as used", ("C-VSEED",), "                used.add(s)", "                pass"),
    ("V05 P-1 pool 5-8 (seed 9 never used)", ("C-VSEED",), "v_pool=(5, 6, 7, 8, 9)", "v_pool=(5, 6, 7, 8)"),
    ("V06 P-1 pool 5-10 (VOID-TREE one seed late)", ("C-VSEED",), "v_pool=(5, 6, 7, 8, 9)", "v_pool=(5, 6, 7, 8, 9, 10)"),
    ("V07 P-1 any fitter refusal treated as VOID", ("C-VSEED", "C-E2E-VOID"), "                if not is_b6_void(ex):", "                if False:"),
    ("V08 P-1 replacement in slot V0 only", ("C-VSEED",), "                if not is_b6_void(ex):", "                if not is_b6_void(ex) or j > 0:"),
    ("V09 P-1 pool restarts per slot (used = seeds 0-4 each slot)", ("C-VSEED",), "        chain, s = [], s0", "        chain, s, used = [], s0, set(REG[\"seeds\"])"),
    ("V10 VOID-TREE counted as GAP-SHOWN", ("C-RENDER", "C-E2E-VOID"), '            out.append(dict(name=e["name"], void=True, gap=False,', '            out.append(dict(name=e["name"], void=True, gap=True,'),
    ("V11 VOID-TREE refuses the run (option (a)/(c) behaviour)", ("C-E2E-VOID",), "                    e[\"status\"] = void", "                    refuse(void)"),
    ("V12 P2 tally counts a VOID-TREE as FAILED", ("C-RENDER",), '                out.append("%s VOID-TREE NOT SCORED" % R["name"])', '                out.append("%s VOID-TREE NOT SCORED" % R["name"])' + NL + "                hs.append(False)"),
    ("V13 P-2 dry-run fits no V", ("C-E2E-VOID",), "        try:" + NL + "            V, void = v_fit_entry(e, L)", "        try:" + NL + "            V, void = {}, None"),
    ("V14 P-3 --run refusal not named", ("C-E2E-VOID",), "            except SystemExit as ex:" + NL + "                raise named(e[\"name\"], ex) from None" + NL + "            stats[",
     "            except SystemExit as ex:" + NL + "                raise" + NL + "            stats["),
    ("V15 P-3 qwen3 guard refusal not named", ("C-E2E-VOID",), "            if e[\"arm\"] != \"N\":" + NL + "                raise named(e[\"name\"], ex) from None",
     "            if e[\"arm\"] != \"N\":" + NL + "                raise"),
    ("V16 P-3 dry-run structure refusal not named", ("C-E2E-VOID",), "list(e[\"tree\"][\"leaf_ids\"]))" + NL + "        except SystemExit as ex:" + NL + "            raise named(e[\"name\"], ex) from None",
     "list(e[\"tree\"][\"leaf_ids\"]))" + NL + "        except SystemExit as ex:" + NL + "            raise"),
    ("V17 P-1 the replacement line not printed", ("C-VSEED", "C-E2E-VOID"), '            " REPLACED (ruling P-1)" if chain else "",', '            "",'),
    ("R2 F-GFC tree list drops the GAP-SHOWN filter (READY C-2)", ("C-RENDER",), 'gfc_fires(word_cc, [R["ip"] for R in cc if R["gap"] and R["word"] == "CLOSED"])', 'gfc_fires(word_cc, [R["ip"] for R in cc if R["word"] == "CLOSED"])'),
    ("R5 GF1-N FAILS line on the CC rows (READY C-2)", ("C-RENDER",), '("REFUTED" if closed_refuted(rows_n) else "not refuted")', '("REFUTED" if closed_refuted(rows_cc) else "not refuted")'),
)


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("# ══ SELFTEST (fixtures and independent oracles")
    rows = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        for mid, cases, old, new in MUTANTS:
            if only and mid.split()[0] not in only:
                continue
            head = src[:cut]
            if head.count(old) != 1:
                rows.append((mid, "BAD-MUTANT (old text found %d times above the selftest line)" % head.count(old)))
                print("  %-62s %s" % (mid, rows[-1][1]), flush=True)
                continue
            mut = head.replace(old, new) + src[cut:]
            p = os.path.join(td, "gap_fix_cc_%s.py" % mid.split()[0])
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(mut)
            rc, out = _child(["--selftest", "--only"] + list(cases) + ["--quiet"], env_extra={"GAPFIXCC_TOOLS_DIR": HERE}, src=p, timeout=900)
            rows.append((mid, "KILLED (timeout: the rule loops)" if rc == "TIMEOUT" else "KILLED" if rc != 0 else "SURVIVED"))
            print("  %-62s %s" % (mid, rows[-1][1]), flush=True)
    killed = sum(1 for _m, r in rows if r.startswith("KILLED"))
    print("%s MUTANTS: %d of %d killed" % (TAG, killed, len(rows)))
    return 0 if killed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
