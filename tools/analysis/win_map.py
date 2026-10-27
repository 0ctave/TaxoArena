"""win_map.py: WIN-MAP (HF post 2) -- ORACLE-WATERFALL (how much of the per-question oracle of the 18-model union roster is luck,
and how much of the luck-adjusted headroom does the frozen TRAIN AF-U router realise?) and REGION-STABILITY (are the map's
regions stable across UMAP and k-means seeds; which regions may carry a winner caption?). ZERO calls: no judge, no LLM, no
embedding call, no construction, no Gradle, no new policy fit beyond UNION-AF-ROUTE's frozen policy and its two-stage refit.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — WIN-MAP: on the content-closed v2 union split,
  how much of the per-question oracle of the 18-model roster is luck, ..." (L25066-L25079, _as_of 375cbcc9): WF1 (DECIDING),
  WF2 (SCORED), RS1 (DECIDING), RS2 (CAPTION RULE), Support (a)-(g), P1-P6, F-WM; the shared rules R1-R6 of the registrar's
  record "## Registrar's record 2026-10-08 ... five HF blog-series analyses ..." (L25043-L25049).
  DATA ALREADY LOOKED AT (R3, disclosed): MC-ROUTER oracle 0.907 / best 0.553 (paeec, id-disjoint only); UNION-AF-ROUTE best
  0.6049, AF 0.6201, declared 0.6316, G_AF +1.52pp [+0.14, +2.91]; CELL-FLIPS 7 / 101. Nothing else of this file was computed.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or from anywhere with --data-root <main checkout>; never beside a
construction: --dry-run and --run are POOL READERS (rule 7: E:/TaxoArena_tmp/busy.ps1 exit 1 before each)):
  0. python tools/analysis/win_map.py --selftest      # synthetic sealed views / DBs under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/win_map.py --mutants       # the mutant table (MUTANTS at the end), re-run
  1. python tools/analysis/win_map.py --dry-run       # POOL line first; pins; the frozen policy; R1 (471 / 427 recomputed);
                                                      #   chance coverage; TRAIN / EVAL structure (key sealed); map rows and
                                                      #   vector coverage; the R1 refusal it would raise; nothing written
  2. python tools/analysis/win_map.py --run           # the TRAIN key read, then ONE EVAL key read (B1 marker); outcome
       WRITE-ONCE experiment_results/archv2/win_map/win_map_outcome.txt (+ win_map.READ_STARTED); the release dataset
       WRITE-ONCE to E:/TaxoArena_tmp/blog/map/ (win_map_items.parquet + README.md); sha256 of each printed. Outputs are never
       committed: the operator copies them to E:/TaxoArena_backup_<date>_win_map with SHA256SUMS.txt.
  RUNTIME (planning): the two-stage bootstrap B 2,000 (UNION-AF-ROUTE's; about 10-20 min single-threaded), 5 UMAP fits on
  about 21,000 x 512 rows (about 2-4 min each, numba single thread), 25 + 50 k-means fits in 2-D and 5 in 512-d (minutes),
  the region bootstrap B 10,000 per stable region (seconds): about 30-60 min in all; RAM about 3 GB.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line (union_cells_io.pool_line: the B0-2 pool check); write-once paths absent (outcome, marker, both export files);
  (2) pins: blob of the LF rendering of this file, union_cells_io.py, union_af_route.py (bf3f17db), v2_declared_cells.py,
  cell_flips.py (998d39a7, asserted at import); umap-learn version == UMAP_VERSION (refused otherwise); (3) the frozen TRAIN
  policy of UNION-AF-ROUTE (sha256-bytes 8d68018c..., union_cells_io.load_policy) and the AF-U cells through the inputs manifest
  (union_cells_io.load_cells); (4) R1: the 471 / 427 exact-text twins recomputed (W-R1); (5) the item texts, options and chance
  c_i (W-C); (6) TRAIN: gen view (pinned), pool row, roster == the policy's, the TRAIN key read (variant UNUSABLE_CELL,
  MATH-FIX overlay; v2_declared_cells.read_key); (7) EVAL: union_cells_io.eval_set (5,907 / 5,404 refused otherwise; B1 marker,
  the ONE key read); (8) R1 on the scored sets: twin items / collapsed duplicates among the scored EVAL items REFUSE (W-R1b);
  (9) v2_declared_cells.build_ud with the AF-U cells and run_boot (B 2,000, default_rng(42), train_unit "item": UNION-AF-ROUTE's
  two-stage bootstrap, unchanged) with a hook that recomputes O_q, O_adj per replicate (B per replicate is the refitted best
  single); (10) identities: the point refit equals the frozen policy (best single, every AF-U pick), R_AF == 0.6201 and
  B == 0.6049 within 1e-4, G_AF prints +1.52pp [+0.14pp, +2.91pp] (W-ID); (11) the waterfall, WF1, WF2; (12) the map: every
  union item of the split (TRAIN, GATE, EVAL) with a text and a 512-d qwen3 RAW unit row, minus R1's twin items; UMAP seeds 0-4
  x k-means seeds 0-4 (k 20); RS1, RS2 (region bootstrap, BH); descriptives; (13) F-WM, predictions, Support; (14) the outcome
  write-once (mode "x"), then the release dataset write-once.
  [AMENDED 2026-10-09 (D-2026-10-08-5; D-2026-10-09-2; delta below): (1) is followed by the MATH scorer header (deviation (1)),
  the D-2026-10-09-2 deviation line and the D-5 disclosure; (2) adds the H table (sha256-lf pinned, REFUSED otherwise); (3) the
  frozen policy supplies the ROSTER only; (6) and (7) read the OFFICIAL key (overlay off; the Scorer seam); after (9)'s set-up
  the ONE official refit is made and its sha256 printed; (10) W-ID is checked against that refit; after (11) the H line
  (descriptive); (14) also writes the refit write-once.]

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  W-R1  R1's exact-text rule: RES = every question_id of experiment_configs/reserved_pool_frozen_paeec.json; GEN = every other
        question_id of corpus_questions (21,606 - 6,482 = 15,124); a RES id is a twin iff a GEN id carries the IDENTICAL text
        string (Python ==, no normalisation; blank texts skipped). REFUSED unless 471 ids / 427 distinct texts. A twin's v2 item
        = "i:" + stem_key(text) (the split's item key: data_v2.common.KeyCache.stem); its GEN partner maps to the SAME item, so
        R1 drops whole items. W-R1b: the drop is applied to the scored EVAL set and REFUSES if it removes any item (the
        registration expects about 0 and asserts R_AF / B on the 5,907; a non-zero count is a registration question for the
        registrar, not a choice made here); the same for exact-text duplicates collapsed among scored EVAL items. The TRAIN side
        of the waterfall is UNION-AF-ROUTE's frozen D unchanged (the policy and its two-stage refit are imported, not refit on a
        different set); twin items among scored TRAIN items are COUNTED (descriptive). The map drops every twin item on every
        side (counted per side); duplicates are collapsed to the lowest question_id (items are stem-key groups, so an exact-text
        duplicate across items is impossible by construction; the count is computed and printed).
  W-C   chance c_i of a v2 item = from its representative question (the smallest question_id of the item; rp12_pairing P4):
        1 / len(options_json) iff the corpus source is MMLU_PRO_LB / MMLU_PRO / GPQA / BBH / MUSR and options_json parses to a
        list of >= 2 options; 0 otherwise (MATH and IFEVAL by format; a BBH / MuSR / MC item without a stored list = the
        registered "free-form BBH" / "no stored option count" class). The 0s are counted per source and reason.
  W-K   k_mc = max(0, (acc_mc - cbar_c) / (1 - cbar_c)) over the TRAIN positions of declared cell c = the view's
        (stratum_source, stratum_domain) (D.g_tdom), weighted by the replicate's TRAIN multiplicities; an EVAL item takes its
        cell's k. q_mi = k / (k + (1 - k) c_i); when c_i = 0 the denominator is k and q_mi = 1 for every k (a correct free-form
        answer is not a guess; also at k = 0). An EVAL cell with no TRAIN mass REFUSES (stratified draws keep every cell).
  W-B   intervals = the g13_comparator percentile rule (union_cells_io.pct) over the B two-stage replicates of
        v2_declared_cells.run_boot; a replicate with O_adj <= B makes rho undefined and is set to +inf (it counts against
        REALISATION-GAP); one with O_q <= B makes lambda undefined and is set to -inf (against LUCK-MATERIAL); both counts printed.
        WF1 at the POINT with O_adj <= B reads NOT EVALUABLE (registered); WF2 at the point with O_q <= B reads NOT-SHOWN
        (lambda undefined; stated).
  W-ID  besides the registered R_AF / B assertions, the G_AF two-stage interval of record (+1.52pp [+0.14pp, +2.91pp]) is
        asserted: Support (b) transports UNION-AF-ROUTE's realised interval ("same items, same policy, same bootstrap").
        [SUPERSEDED 2026-10-09 by D-2026-10-09-2: the MATH-FIX targets R_AF 0.6201, B 0.6049, G_AF +1.52pp [+0.14, +2.91] and the
        frozen-file picks are no longer targets; W-ID = run_boot's point policy IS the official refit, R_AF and B equal a plain
        recomputation from the refit's document within 1e-9, the G_AF point is R_AF - B, policy fits == B + 2 (w_id()).]
  W-RS  partitions on all map rows; RS1 pairs = (u1, k1) x (u2, k2) with u1 < u2 (10 UMAP pairs x 25 k-means pairings = 250);
        ARI = sklearn adjusted_rand_score. RS2: for region r of the PUBLISHED partition (u0, k0) and each of the other 24
        partitions, the matched region = the best-match Jaccard region (ties to the lower label); STABLE iff the median of the
        24 Jaccards >= 0.75. EVAL argmax of a region = the model with the most correct EVAL scored items in it (ties to the
        first in sorted-roster order, numpy argmax; None if it holds no EVAL item); the 25 = r itself + its 24 matched regions;
        a consensus winner needs >= 20 of 25. BH family = the STABLE regions (m = their count); each tested with challenger =
        the consensus winner if any, else r's own EVAL argmax, D = mean over r's EVAL items of A[challenger] - A[g] (g = the
        frozen best single); p by cell_flips.cell_boot / p_of (components of r's EVAL items, B 10,000, one-sided, p floor
        1 / (B + 1)), one stream default_rng(20261008), stable regions in label order, only those with challenger != g and
        >= 1 EVAL item draw (the others p = 1, no draw); cell_flips.bh at q 0.05. Caption iff STABLE AND consensus (>= 20)
        AND BH-rejected AND RS1 = STABLE-MAP.
  W-E   entropy of an item = binary entropy (bits) of the share of the 18 models correct; region entropy = its mean over the
        region's EVAL scored items. Export "winner" = the region's EVAL argmax on the published map (descriptive) with
        caption_licensed beside; correctness is exported for key-read items only (TRAIN and EVAL scored; GATE and unscored
        items null); NO question text of any source is exported (R4 / R5).
        [AMENDED 2026-10-08 after READY review 12f42190 B2: "winner" is the licensed consensus winner and NULL unless
        caption_licensed (RS2 under a STABLE-MAP); the EVAL argmax ships as eval_argmax_descriptive, stated "NOT a caption"
        in the README. W-C guard added: run() REFUSES when MMLU items are scored on EVAL and none gets c_i > 0 (B1a).]
  W-S   O_sim: 200 rosters, item i model m correct with probability k + (1 - k) c_i (point k), one stream
        default_rng(20261008); oracle per roster = share of items solved by >= 1 simulated model; mean and 2.5 / 97.5 pct.
  W-R2  R2 (one extractor per harness) = v2_declared_cells.read_key with the MATH-FIX overlay under UNUSABLE_CELL, exactly as
        UNION-AF-ROUTE / CELL-FLIPS read the key (keyed correctness for the MC sources, MATH-FIX for MATH, the stored IFEval
        prompt-level strict label); nothing here varies it.
        [SUPERSEDED 2026-10-09 for MATH by D-2026-10-08-5 (R2's MATH clause bracketed by the registrar): the official scorer,
        eval_results.is_correct WITHOUT the MATH-FIX overlay, on TRAIN and EVAL; H is printed beside and decides nothing.]
  Not applicable (stated): no judge verdict enters (keyed correctness), so no wrong(established) count and no tie
  convention A / B; no call cache, --pilot, truncation guard or --analyze (zero calls; the outcome is written by --run alone).
  NOT COMPUTED here (registered as descriptive and gated): the second-embedder (nomic) map, until EMBEDDER-PLUMBING's gate.

SELFTEST (--selftest; fixtures under E:/TaxoArena_tmp via scratch_dir, removed afterwards): sealed synthetic gen / eval views
(v2_declared_cells._mk_view), a texts DB, an embeddings DB (16-d, 4 separated blobs), a side export, a paeec pool file, the
frozen policy / manifest / cells files; the pool check stubbed. Cases (the mutant table is at the end of this file and in the
commit message):
  e2e        run() end to end (AF-U cells differ from the declared cells; unsolved EVAL items): R1 3 ids / 2 texts (an exact
             twin kept apart from a norm-only twin), c_i per source, every waterfall number (O_q, O_adj, O_chance, O_cell AF /
             declared, R_AF, B, rho, lambda) and the WF1 / WF2 intervals and words against an INDEPENDENT plain-loop oracle
             replaying the recorded replicate weights (WF1 NOT-SHOWN, WF2 NOT-SHOWN, F-WM FIRED here); RS1 median against an
             independent contingency-table ARI over the returned partitions (STABLE-MAP on the blobs); RS2: the m3 region
             captioned (p at the floor, consensus 25 of 25), the g region not; the release parquet read back (no text column or
             text substring, GPQA rows present, correctness null on GATE); the outcome == the printed text; a 2nd --run REFUSED
  unstable   run() on unstructured points with m0 right on every TRAIN item: WF1 REALISATION-GAP with rho = 0 [0, 0] exactly
             (hand-known), F-WM NOT FIRED; UNSTABLE-MAP (median against the independent ARI), per-region STABLE flags against an
             independent Jaccard, "no region is captioned"; g = the frozen pick (m0) while the EVAL-best is m3
  luck       run() with r0's TRAIN won by m0: WF2 LUCK-MATERIAL against the oracle interval
  regions    regions() on hand-made partitions: a Jaccard median EXACTLY 0.75 (STABLE), an empty region, a region with no EVAL
             row, an unstable region with a strong winner (never tested), the component bootstrap p about 0.36 (0.12 by items),
             BH over the stable regions only (2 captions), RS1 at its exact boundary (>= decides), UNSTABLE-MAP withdraws captions
  rs2        regions() with the bootstrap stubbed by D (known p): a STABLE, BH-rejected region WITHOUT the 20-of-25 consensus
             (15 / 25) stays uncaptioned; a 5-region p family where BH at q 0.05 and q 0.10 differ (independent plain-loop BH)
  branches   wf_lines / rs_lines / pred lines on synthetic st: every WF1 / WF2 / RS1 / RS2 / F-WM word at its boundary
             (0.25 / 0.10 / 0.80 / 0.75 / 20 of 25), NOT EVALUABLE, undefined replicates, prediction bands closed, Brier
  pure       know_rates / adj_terms / rs pairs / best-match Jaccard / consensus against hand values
  refusals   twin count, a scored EVAL twin item, R_AF, B, G_AF, a frozen pick differing from the refit, an EVAL cell with no
             TRAIN mass, a scored EVAL item without a vector, the UMAP version, write-once outcome / marker / export, the pool
             check (POOL line still first); no outcome written by any of them
  dry_run    POOL line first; R1 counts; the key never read (tripwire sealed); nothing written
  branch_cover  every print branch of the registry was hit by the cases above
MUTANTS (--mutants; M01-M64 + the C00 control; each a temporary in-memory edit of this file, the named cases re-run): 2026-10-08
at this commit 64 of 64 KILLED, control survived. First full pass 62 / 64: M17 (replicate O_q unweighted: every fixture item
was solved, O_q = 1) and M44 (RS1 bar > 0.80: no fixture sat at the boundary) survived; killed by unsolved EVAL items in the
fixture and by an RS1 boundary case in "regions". Classes: the deciding bound / boundary / min<->max (M01-M05, M12, M13, M42,
M44-M47), the registered ratio forms and undefined replicates (M06-M09), refit vs frozen and wrong split side / population (M10,
M11, M14-M16, M52, M53), the luck model (M18-M21, M24, M25), first-site-only / empty or no-EVAL regions / family (M48-M51, M55,
M56), R1 (M26-M30), every refusal and gate (M23, M28, M29, M31-M36), write-once and modes (M37-M41), skip paths that drop a
required line and the predictions (M57-M62), the release (M63, M64). No fork or subprocess exists in this script (no uncapped
fork class). The cleanup (rmtree) runs only on mkdtemp dirs under E:/TaxoArena_tmp and no mutant edits it.
[ADDED 2026-10-08 after READY review 12f42190 (B1 / B2): the reviewer's survivors R2 (caption without consensus), R3 (BH q
0.10), R4 (MMLU_PRO dropped from MC_SOURCES; the fixture now carries the real corpus source MMLU_PRO and the oracle's MC list is
written out, not MC_SOURCES), R8 (F-WM on the upper bound), plus B2a / B2b (winner exported for every region / under
UNSTABLE-MAP), M65 (W-C MMLU refusal off), M66 (MMLU count by the stratum label only): selftest 10 / 10; 72 of 72 KILLED,
control survived.]
NOT DONE HERE: the real --dry-run / --run (no pool read in this build; rule 7, the brief); the Kotlin suite (no Kotlin / Gradle
file touched).

DELTA 2026-10-09 (builder; zero calls): D-2026-10-08-5 (the official MATH scorer of record, H a sensitivity line;
docs/agents/author_decisions/2026-10-08.md) and D-2026-10-09-2 ("(a) Refit under official (Recommended)";
docs/agents/author_decisions/2026-10-09.md, defab40c; prog L25394-L25401), on the READY blob 74f2e234 (scorer-delta review
9af2c14a D1 ruled by the author).
  W-SC  Every key read is the OFFICIAL scorer. union_cells_io.py (blob 92a04543, pinned by adaptive_profile / cell_difficulty) and
        v2_declared_cells.py are NOT edited: run() binds v2_declared_cells.read_key to Scorer.read_key, which expects exactly
        (1) this script's TRAIN read (response_lite, overlay False, train_block) then (2) union_cells_io.eval_set's pinned EVAL
        read (response, overlay True passed, FORCED OFF), calls the pinned read_key with overlay False, refuses any other read,
        any MATH-FIX overlay row, and an H key whose usable cells differ from the official key's [W-SCORER]. The eval_set line
        prints "overlay rows 0 (changed 0)" and run() prints "MATH-FIX overlay rows read 0 / 0".
  W-RF  The ONE refit (D-2026-10-09-2): P_off = V.fit(D, V.train_full(D)) on the scored TRAIN items under the official key (the
        G3 TRAIN-support guard runs inside fit); its document (policy_doc: roster, best_single, tree_cell, true_source_domain,
        scorer, tie rule, TRAIN count) is canonical JSON (sort_keys, indent 1, LF), sha256 printed, written write-once (mode "x")
        to experiment_results/archv2/win_map/win_map_official_policy.json (in the prelude's write-once check). run_boot then makes
        its own identical point fit (P0) and the B registered replicate refits (the two-stage interval, unchanged). The frozen
        8d68018c file is still sha-checked and read, for the ROSTER only; its picks are printed beside the refit (descriptive).
        RS2's g = the refit's best single.
  W-H   The H line (D-2026-10-08-5 deviations (2), (4)): load_h() REFUSES unless the table's bytes' sha256 is the pin
        6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1 with 23,832 rows [W-H-PIN]; h_key() joins MATH rows
        by (legacy_qid, model) in the official read's window and scope [W-H-JOIN: missing row, model, id space]. The H points
        (O_q, O_adj, R_AF, B, rho, lambda; no interval) use the OFFICIAL refit's picks (no refit under H) and k_mc from TRAIN
        under H; they are printed after F-WM, under "SENSITIVITY H ... DESCRIPTIVE, decides nothing", and enter no word.
  HEADER  the outcome's 3rd line is the registrar's scorer header verbatim ("MATH scorer: official (eval_results.is_correct, no
        overlay); sensitivity: H (table sha256-lf 6b010fa6...); MATH-FIX beside: no"), the 4th the D-2026-10-09-2 deviation, the
        5th the D-5 disclosure (official 2,335 / MATH-FIX 7,516 / H 7,126 of 23,832; UNION-AF-ROUTE's EVAL 7,272 overlay rows,
        1,572 changed). Support (b)-(g) print as PRE-DEVIATION planning values with the registrar's re-derivation binding over
        them; (g) reads "bounded by the policy fitted on TRAIN only (the ONE official refit)".
  FIXTURE  is_correct carries the fixture's truth; is_correct_mathfix DIFFERS on MATH m1 (TRAIN 18 rows, EVAL 14), so an overlay
        leak moves values; 1,000 GATE padding rows of an out-of-scope item keep the gen view's legacy_qid keys disjoint from the
        eval view's; the fixture H table is built from both views' MATH rows (official 1 -> imported; m2 on q % 3 == 0 and m4 on
        q % 2 == 0 credited, route boxed); variants h_missing / h_idspace; badpick = a frozen file whose best single (m4) and one
        AF-U pick differ from the refit (NOT refused now).
  CASES  scorer (the seam on stubs: order, flags, forced-off flag, overlay-row refusal; the pinned constants), deviation (badpick:
        no refusal, the frozen line by value, g / R_AF / B the refit's), e2e + _check_official (header lines by literal and
        position, overlay 0 / 0, MATH m1 = the official value on every MATH position, the refit == an independent plain-loop
        TRAIN fit, the written file's sha256 == the printed one, fits B + 2, R_AF / B / G_AF == an independent V.build_ud +
        V.run_boot build, the H matrix and the six H points == an independent oracle reading the views and the H csv directly,
        the H line after F-WM and before the map), refusals (+ W-ID x5 by stubs, overlay-row, H pin / absent / rows / join /
        id space, the policy file write-once), dry_run (header, deviation, H TABLE, per-source structure).
  EQUIVALENT (not in the table; proof): "H line: k_mc from the official key (D.A), not H" (DH.A = D.A in h_points). H differs
        from the official key only on MATH cells; a MATH item sits in a MATH declared cell and has c_i = 0, where q = 1 for every
        k (W-K), so k of a MATH cell never enters O_adj; every other cell's k is computed from identical columns. Found as a
        survivor (S22) of the first pass and removed with this proof.
  MUTANTS 2026-10-09: see the MUTANTS table (S01-S28 new, S22 removed as equivalent; R1 / R5 / R6 / R7 / N1 / N3 of the prior reviewers carried in;
        M31-M34 retargeted to the official W-ID, M14 / M38 / M53 retargeted). Result recorded in the commit message.
  SUPPORT RE-DERIVATION NOTE (for the reviewer and the registrar; the builder's planning arithmetic from records only, no pool
        read, no key; the registrar's insertion decides): see the commit message of this delta.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ[_v] = "1"

import io
import csv
import copy
import json
import math
import hashlib
import argparse
import contextlib
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _pre_data_root(argv):
    """--data-root must reach TAXOARENA_DATA_ROOT BEFORE the readers import (as cell_flips.py)."""
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


if __name__ == "__main__" and _pre_data_root(sys.argv[1:]):
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_pre_data_root(sys.argv[1:]))
import union_cells_io as U      # noqa: E402  (pins union_af_route bf3f17db, which pins v2_declared_cells and its readers)

CF_PIN = "998d39a7b718faa6647c4d5795dcf03044544955"
if U.blob_lf(os.path.join(HERE, "cell_flips.py")) != CF_PIN:
    raise SystemExit("[WIN-MAP] REFUSED: cell_flips.py is blob:%s, not the READY blob:%s"
                     % (U.blob_lf(os.path.join(HERE, "cell_flips.py")), CF_PIN))
import cell_flips as CF         # noqa: E402
V = U.V
RP = U.RP
EP = RP.EP
from data_v2 import ro as dv2ro          # noqa: E402
from data_v2 import common as dv2c       # noqa: E402

TAG = "[WIN-MAP]"
TEST_ID = "WIN-MAP"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — WIN-MAP: on the content-closed v2'
           ' union split, how much of the per-question oracle ..." L25066-L25079 (_as_of 375cbcc9); shared rules R1-R6 L25043-L25049')
UMAP_VERSION = "0.5.12"
MC_SOURCES = ("MMLU_PRO_LB", "MMLU_PRO", "GPQA", "BBH", "MUSR")
MMLU_NAMES = ("MMLU_PRO", "MMLU_PRO_LB")      # the corpus source (MMLU_PRO) and the stratum label (MMLU_PRO_LB)

CONST = dict(
    pool="pv2_1575de61bb20e977", cv="mc6-2026-09-11",
    paeec_rel="experiment_configs/reserved_pool_frozen_paeec.json", twins=(471, 427),
    texts_db="multicorpus_cache_v1.db", emb_db="embeddings_cache.db", dim=512,
    side_rel=EP.DEFAULT_SIDE.replace(os.sep, "/"),
    gen_rel=V.GEN_REL.replace(os.sep, "/"), gen_sha=V.GEN_SHA,
    B=V.REG["B"], seed=V.REG["seed"], placebo_seed=V.REG["placebo_seed"], train_unit=V.PRECONDITIONS["train_unit"],
    rule="UNUSABLE_CELL",
    tol=1e-9,                                     # W-ID (D-2026-10-09-2): identities against the official refit, not MATH-FIX targets
    h_table="experiment_results/math_scorer_h/math_h_table.csv",
    h_sha="6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1", h_rows=23832,
    umap=dict(metric="cosine", n_neighbors=30, min_dist=0.1), seeds=(0, 1, 2, 3, 4), k=20, n_init=10, k_desc=(10, 40),
    ari_bar=0.80, jac_bar=0.75, consensus=20, q=0.05, region_B=10000, region_seed=20261008, sim_reps=200, sim_seed=20261008,
    out_dir="experiment_results/archv2/win_map", outcome="win_map_outcome.txt", marker="win_map.READ_STARTED",
    policy_out="win_map_official_policy.json",
    export_dir="E:/TaxoArena_tmp/blog/map", export_file="win_map_items.parquet", readme="README.md",
)
_C = [CONST]
SUPPORT = dict(wf1=dict(se=0.0363, mde=0.102, deff=1.595, n_eff=3388), wf2=dict(se=0.0143, mde=0.040, deff=1.10, n_eff=4913),
               rs1=dict(sd=0.05, se=0.0280, mde=0.078, deff=2.0, n_eff=5))
PRED = dict(O_q=(0.86, 0.93), O_adj=(0.72, 0.86), O_chance=(0.60, 0.85), O_cell=(0.64, 0.71), rho=(0.00, 0.16), p_gap=0.90,
            lam=(0.20, 0.50), p_luck=0.85, ari=(0.55, 0.88), p_stable=0.35, n_stable=(4, 14), n_caption=(0, 5))
HIT = Counter()
BRANCHES = ("WF1.GAP", "WF1.NOT_SHOWN", "WF1.NOT_EVALUABLE", "WF2.LUCK", "WF2.NOT_SHOWN", "WF2.UNDEFINED", "RS1.STABLE",
            "RS1.UNSTABLE", "RS2.CAPTIONS", "RS2.WITHDRAWN", "RS2.NO_STABLE", "FWM.FIRED", "FWM.NOT_FIRED", "FWM.NOT_EVALUABLE",
            "UNDEF.REPS", "PRED.HELD", "PRED.FAILED", "DRY.DONE", "RUN.DONE", "H.LINE")


def C():
    return _C[0]


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def in_band(x, band):
    return band[0] <= x <= band[1]


def hw(x, band):
    held = bool(in_band(x, band))
    hit("PRED.HELD" if held else "PRED.FAILED")
    return "HELD" if held else "FAILED"


def f4(x):
    return "%.4f" % x if x == x and abs(x) != float("inf") else ("%s" % x)


def pp(x):
    return "%+.2fpp" % (100.0 * x)


# ── R1 and the item table ───────────────────────────────────────────────────────────────────────────────────────────────

def blank(t):
    return EP._kotlin_blank(t)


def twins_exact(qtext, res_ids):
    """W-R1: RES ids whose IDENTICAL text is carried by a GEN id (GEN = every other question). -> (sorted ids, n texts)."""
    res = set(res_ids)
    gen_texts = set(t for q, t in qtext.items() if q not in res and not blank(t))
    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and qtext[q] in gen_texts)
    return ids, len(set(qtext[q] for q in ids))


def item_table(rows):
    """{item: dict(qid, source, domain, text, options, n_q)}: the smallest question_id of each stem-key item (rp12_pairing P4)
    and the number of question_ids grouped in the item."""
    keys = dv2c.KeyCache()
    best, nq = {}, Counter()
    for qid, src, dom, text, opts in rows:
        if blank(text):
            continue
        it = "i:" + keys.stem(text)
        nq[it] += 1
        cur = best.get(it)
        if cur is None or qid < cur["qid"]:
            best[it] = dict(qid=qid, source=src, domain=dom, text=text, options=opts)
    for it in best:
        best[it]["n_q"] = nq[it]
    return best


def item_of(text):
    return "i:" + dv2c.KeyCache().stem(text)


def chance_of(source, options):
    """W-C -> (c_i, reason)."""
    if source not in MC_SOURCES:
        return 0.0, "generative source"
    try:
        lst = json.loads(options) if options else None
    except (TypeError, ValueError):
        lst = None
    if not isinstance(lst, list) or len(lst) < 2:
        return 0.0, "no stored option list"
    return 1.0 / len(lst), "MC"


def collapse_exact(table, items):
    """Exact-text duplicates across the given items -> {dropped item: kept item} (kept = lowest question_id)."""
    by = defaultdict(list)
    for it in items:
        if it in table:
            by[table[it]["text"]].append(it)
    out = {}
    for _t, its in by.items():
        if len(its) > 1:
            keep = min(its, key=lambda i: table[i]["qid"])
            for i in its:
                if i != keep:
                    out[i] = keep
    return out


# ── the waterfall (pure) ────────────────────────────────────────────────────────────────────────────────────────────────

def know_rates(A, w, cell, n_cells, c):
    """W-K: k[cell, model] from the positions with weight w (TRAIN multiplicities); NaN where a cell has no mass."""
    w = np.asarray(w, dtype=np.float64)
    m = A.shape[1]
    mass = np.bincount(cell, weights=w, minlength=n_cells)
    acc = np.stack([np.bincount(cell, weights=w * A[:, j], minlength=n_cells) for j in range(m)], axis=1)
    cs = np.bincount(cell, weights=w * c, minlength=n_cells)
    with np.errstate(invalid="ignore", divide="ignore"):
        acc = acc / mass[:, None]
        cbar = cs / mass
        k = np.maximum(0.0, (acc - cbar[:, None]) / (1.0 - cbar[:, None]))
    k[mass <= 0] = np.nan
    return k


def adj_terms(A, k, c):
    """Per item: 1{solved} x (1 - prod over solvers (1 - q_mi)); q = k / (k + (1 - k) c), q = 1 when c = 0 (W-K)."""
    c = np.asarray(c, dtype=np.float64)[:, None]
    den = k + (1.0 - k) * c
    with np.errstate(invalid="ignore", divide="ignore"):
        q = np.where(c == 0, 1.0, np.where(den > 0, k / np.where(den > 0, den, 1.0), 0.0))
    prod = np.prod(1.0 - A * q, axis=1)
    solved = A.max(axis=1)
    return solved * (1.0 - prod)


def o_cell(A, cells):
    """In-sample per-cell ceiling: each cell's EVAL-best model (chosen on EVAL)."""
    tot = 0.0
    for g in sorted(set(cells)):
        idx = [i for i, x in enumerate(cells) if x == g]
        tot += float(A[idx].sum(axis=0).max())
    return tot / A.shape[0]


def o_sim(kE, c, reps, seed):
    rng = np.random.default_rng(seed)
    P = kE + (1.0 - kE) * np.asarray(c, dtype=np.float64)[:, None]
    out = np.empty(reps)
    for r in range(reps):
        out[r] = float((rng.random(P.shape) < P).any(axis=1).mean())
    return out


def ratio(num, den, undefined):
    return num / den if den > 0 else undefined


def rep_ratios(r_rep, b_rep, oq, oa):
    """W-B: per replicate rho = (R - B) / (O_adj - B) (+inf when O_adj <= B) and lambda = (O_q - O_adj) / (O_q - B) (-inf when
    O_q <= B)."""
    rho_b = np.array([ratio(r - b, a - b, float("inf")) for r, b, a in zip(r_rep, b_rep, oa)])
    lam_b = np.array([ratio(q - a, q - b, float("-inf")) for q, a, b in zip(oq, oa, b_rep)])
    return rho_b, lam_b


def pct_iv(x):
    s = sorted(float(v) for v in x)
    return U.pct(s, 0.025), U.pct(s, 0.975)


def k_for_eval(D, w, c_all):
    k = know_rates(D.A, w, D.g_tdom, len(D.dom_keys), c_all)
    cells_e = D.g_tdom[D.E]
    bad = sorted(set(int(x) for x in cells_e if not np.all(np.isfinite(k[int(x)]))))
    if bad:
        refuse("W-K: declared cell(s) %s of EVAL items carry no TRAIN mass: k_mc undefined" % [D.dom_keys[b] for b in bad])
    return k[cells_e]


def waterfall(D, bt, rec, c_all, af_cells_e, dom_cells_e):
    """-> st (points, replicate arrays, intervals, words)."""
    c = C()
    AE = D.A[D.E].astype(np.float64)
    cE = c_all[D.E]
    w0 = np.zeros(D.n)
    w0[D.T] = 1
    kE = k_for_eval(D, w0, c_all)
    st = dict(N=len(D.E), G=D.eval_units["n_units"], m=len(D.models), models=list(D.models))
    st["O_q"] = float(AE.max(axis=1).mean())
    st["O_adj"] = float(adj_terms(AE, kE, cE).mean())
    st["O_chance"] = float((1.0 - (1.0 - cE) ** len(D.models)).mean())
    sims = o_sim(kE, cE, c["sim_reps"], c["sim_seed"])
    st["O_sim"] = (float(sims.mean()),) + pct_iv(sims)
    st["O_cell_af"] = o_cell(AE, af_cells_e)
    st["O_cell_dom"] = o_cell(AE, dom_cells_e)
    st["R_AF"] = float(bt["point"][0, V.TREE])
    st["B"] = float(bt["point"][0, V.BS])
    st["R_dom"] = float(bt["point"][0, V.TDOM])
    st["c0"] = int((cE == 0).sum())
    r_rep = bt["two"][:, 0, V.TREE]
    b_rep = bt["two"][:, 0, V.BS]
    oq = np.array(rec["O_q"])
    oa = np.array(rec["O_adj"])
    if len(oq) != len(r_rep):
        refuse("the hook recorded %d replicates, run_boot made %d" % (len(oq), len(r_rep)))
    rho_b, lam_b = rep_ratios(r_rep, b_rep, oq, oa)
    st["undef_rho"] = int(np.isinf(rho_b).sum())
    st["undef_lam"] = int(np.isinf(lam_b).sum())
    st["iv"] = dict(O_q=pct_iv(oq), O_adj=pct_iv(oa), R_AF=pct_iv(r_rep), B=pct_iv(b_rep), rho=pct_iv(rho_b), lam=pct_iv(lam_b))
    st["sd_rho"] = float(np.std(rho_b[np.isfinite(rho_b)], ddof=1)) if np.isfinite(rho_b).sum() > 1 else float("nan")
    st["sd_lam"] = float(np.std(lam_b[np.isfinite(lam_b)], ddof=1)) if np.isfinite(lam_b).sum() > 1 else float("nan")
    st["den_adj"] = st["O_adj"] - st["B"]
    st["den_q"] = st["O_q"] - st["B"]
    st["rho"] = ratio(st["R_AF"] - st["B"], st["den_adj"], float("nan"))
    st["lam"] = ratio(st["O_q"] - st["O_adj"], st["den_q"], float("nan"))
    st["rho_raw"] = ratio(st["R_AF"] - st["B"], st["den_q"], float("nan"))
    st["B_reps"] = len(r_rep)
    # per source (descriptive points)
    src = np.array([D.src[k] for k in D.E])
    per = []
    for s in sorted(set(src.tolist())):
        mk = src == s
        per.append((s, int(mk.sum()), float(AE[mk].max(axis=1).mean()), float(adj_terms(AE[mk], kE[mk], cE[mk]).mean()),
                    o_cell(AE[mk], [x for x, b in zip(af_cells_e, mk) if b]),
                    float(bt["point"][[n for n, _ in D.subsets].index("SRC:" + s), V.TREE]),
                    float(bt["point"][[n for n, _ in D.subsets].index("SRC:" + s), V.BS])))
    st["per_source"] = per
    return st


def wf_words(st):
    if not st["den_adj"] > 0:
        w1 = "NOT EVALUABLE"
    else:
        w1 = "REALISATION-GAP" if st["iv"]["rho"][1] < 0.25 else "NOT-SHOWN"
    if not st["den_q"] > 0:
        w2 = "NOT-SHOWN (undefined)"
    else:
        w2 = "LUCK-MATERIAL" if st["iv"]["lam"][0] > 0.10 else "NOT-SHOWN"
    return w1, w2


def wf_lines(st):
    L = ["", "== ORACLE-WATERFALL on EVAL (relative to these %d models; %d items / %d components; two-stage bootstrap B %d,"
             " 95%% percentile) ==" % (st["m"], st["N"], st["G"], st["B_reps"])]
    iv = st["iv"]
    L.append("  O_q (per-question oracle: share solved by >= 1 model)        %.4f [%.4f, %.4f]" % ((st["O_q"],) + iv["O_q"]))
    L.append("  O_adj (luck-adjusted; independence across models assumed)   %.4f [%.4f, %.4f]" % ((st["O_adj"],) + iv["O_adj"]))
    L.append("  O_chance (%d chance-level guessers; descriptive)              %.4f (items with c_i = 0: %d)" % (
        st["m"], st["O_chance"], st["c0"]))
    L.append("  O_sim (200 simulated know / guess rosters; descriptive)       %.4f [%.4f, %.4f]" % st["O_sim"])
    L.append("  O_cell AF-U (per-cell EVAL-best, in-sample ceiling)            %.4f" % st["O_cell_af"])
    L.append("  O_cell declared (descriptive)                                  %.4f" % st["O_cell_dom"])
    L.append("  R_AF (the official TRAIN refit of the AF-U policy)             %.4f [%.4f, %.4f]" % ((st["R_AF"],) + iv["R_AF"]))
    L.append("  R_declared (official TRAIN refit, declared cells; descriptive) %.4f" % st["R_dom"])
    L.append("  B (TRAIN-chosen best single model)                            %.4f [%.4f, %.4f]" % ((st["B"],) + iv["B"]))
    if st["undef_rho"] or st["undef_lam"]:
        hit("UNDEF.REPS")
        L.append("  UNDEFINED REPLICATES (W-B): rho %d (O_adj <= B; set +inf), lambda %d (O_q <= B; set -inf) of %d" % (
            st["undef_rho"], st["undef_lam"], st["B_reps"]))
    else:
        L.append("  undefined replicates (W-B): none of %d" % st["B_reps"])
    w1, w2 = wf_words(st)
    L.append("")
    L.append("== WF1 (DECIDING; the 95% INTERVAL decides): rho = (R_AF - B) / (O_adj - B); REALISATION-GAP iff upper < 0.25 ==")
    if w1 == "NOT EVALUABLE":
        hit("WF1.NOT_EVALUABLE")
        L.append("WF1: NOT EVALUABLE: O_adj %.4f <= B %.4f (the ratio is undefined; registered)" % (st["O_adj"], st["B"]))
    elif w1 == "REALISATION-GAP":
        hit("WF1.GAP")
        L.append("WF1: REALISATION-GAP: rho %s [%s, %s]; upper %s < 0.25: the router realises under a quarter of the"
                 " luck-adjusted headroom" % (f4(st["rho"]), f4(iv["rho"][0]), f4(iv["rho"][1]), f4(iv["rho"][1])))
    else:
        hit("WF1.NOT_SHOWN")
        L.append("WF1: NOT-SHOWN: rho %s [%s, %s]; upper %s >= 0.25; WF1 FAILS (rule 8). For the post: \"routers realise a"
                 " material share\" replaces \"your router can't get there\"" % (f4(st["rho"]), f4(iv["rho"][0]), f4(iv["rho"][1]),
                                                                                f4(iv["rho"][1])))
    L.append("== WF2 (SCORED; the 95% INTERVAL decides): lambda = (O_q - O_adj) / (O_q - B); LUCK-MATERIAL iff lower > 0.10 ==")
    if w2 == "NOT-SHOWN (undefined)":
        hit("WF2.UNDEFINED")
        L.append("WF2: NOT-SHOWN: O_q %.4f <= B %.4f, lambda undefined (W-B); WF2 FAILS (rule 8); the luck step is dropped"
                 " from the waterfall's caption" % (st["O_q"], st["B"]))
    elif w2 == "LUCK-MATERIAL":
        hit("WF2.LUCK")
        L.append("WF2: LUCK-MATERIAL: lambda %s [%s, %s]; lower %s > 0.10: a material share of the oracle headroom is luck" % (
            f4(st["lam"]), f4(iv["lam"][0]), f4(iv["lam"][1]), f4(iv["lam"][0])))
    else:
        hit("WF2.NOT_SHOWN")
        L.append("WF2: NOT-SHOWN: lambda %s [%s, %s]; lower %s <= 0.10; WF2 FAILS (rule 8); the luck step is dropped from the"
                 " waterfall's caption" % (f4(st["lam"]), f4(iv["lam"][0]), f4(iv["lam"][1]), f4(iv["lam"][0])))
    L.append("  rho_raw = (R_AF - B) / (O_q - B) (descriptive): %s" % f4(st["rho_raw"]))
    L.append("  PER SOURCE (descriptive points): source n O_q O_adj O_cell(AF) R_AF B")
    for s, n, oq, oa, oc, r, b in st["per_source"]:
        L.append("    %-12s %5d  %.4f  %.4f  %.4f  %.4f  %.4f" % (s, n, oq, oa, oc, r, b))
    if w1 == "NOT EVALUABLE":
        hit("FWM.NOT_EVALUABLE")
        L.append("F-WM: NOT EVALUABLE (O_adj <= B)")
    elif st["rho"] >= 0.25:
        hit("FWM.FIRED")
        L.append("F-WM: FIRED: rho's point %s >= 0.25: the router realises at least a quarter of the luck-adjusted headroom;"
                 " the post's thesis \"most oracle headroom is unreachable by a router\" is overturned for this roster and"
                 " split; the post reports realisation, not a gap" % f4(st["rho"]))
    else:
        hit("FWM.NOT_FIRED")
        L.append("F-WM: NOT FIRED (rho's point %s < 0.25)" % f4(st["rho"]))
    return L, dict(WF1=w1, WF2=w2)


# ── the map (REGION-STABILITY) ──────────────────────────────────────────────────────────────────────────────────────────

def umap_version():
    import umap
    return umap.__version__


def project(X, seed):
    import umap
    p = C()["umap"]
    return umap.UMAP(n_components=2, metric=p["metric"], n_neighbors=p["n_neighbors"], min_dist=p["min_dist"],
                     random_state=seed).fit_transform(X)


def kmeans(Y, k, seed):
    from sklearn.cluster import KMeans
    return KMeans(n_clusters=k, init="k-means++", n_init=C()["n_init"], random_state=seed).fit_predict(Y).astype(np.int64)


def ari(a, b):
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(a, b))


def rs1_pairs(seeds):
    """W-RS: partition pairs that differ in UMAP seed: (u1, k1) x (u2, k2), u1 < u2."""
    return [((u1, k1), (u2, k2)) for u1 in seeds for u2 in seeds if u1 < u2 for k1 in seeds for k2 in seeds]


def best_match(P0, Q, r, kq):
    """-> (Jaccard, matched label) of region r of P0 in partition Q (ties to the lower label)."""
    inr = P0 == r
    n_r = int(inr.sum())
    inter = np.bincount(Q[inr], minlength=kq)
    size_q = np.bincount(Q, minlength=kq)
    jac = inter / (n_r + size_q - inter).clip(min=1)
    j = int(np.argmax(jac))
    return float(jac[j]), j


def region_argmax(A_rows, mask):
    """EVAL argmax model index among the rows in mask (None if no EVAL row)."""
    if not mask.any():
        return None
    return int(np.argmax(A_rows[mask].sum(axis=0)))


def consensus(argmaxes, need):
    cnt = Counter(a for a in argmaxes if a is not None)
    if not cnt:
        return None, 0
    top = max(cnt.items(), key=lambda kv: (kv[1], -kv[0]))
    return (top[0] if top[1] >= need else None), top[1]


def map_partitions(X, seeds, k):
    Ys = {u: project(X, u) for u in seeds}
    parts = {(u, s): kmeans(Ys[u], k, s) for u in seeds for s in seeds}
    return Ys, parts


def regions(parts, seeds, k, eval_mask, A_map, gi, comp_map, models):
    """RS1 / RS2 -> st."""
    c = C()
    st = dict(k=k, n_rows=len(eval_mask), n_eval=int(eval_mask.sum()))
    pairs = rs1_pairs(seeds)
    aris = [ari(parts[a], parts[b]) for a, b in pairs]
    st["pairs"], st["aris"] = len(pairs), aris
    st["ari_med"] = float(np.median(aris))
    st["ari_sd"] = float(np.std(aris, ddof=1)) if len(aris) > 1 else float("nan")
    st["stable_map"] = bool(st["ari_med"] >= c["ari_bar"])
    pub = (seeds[0], seeds[0])
    P0 = parts[pub]
    others = [p for p in sorted(parts) if p != pub]
    rows = []
    for r in range(k):
        jacs, args = [], []
        mine = region_argmax(A_map, (P0 == r) & eval_mask)
        args.append(mine)
        for p in others:
            j, q = best_match(P0, parts[p], r, k)
            jacs.append(j)
            args.append(region_argmax(A_map, (parts[p] == q) & eval_mask))
        win, cnt = consensus(args, c["consensus"])
        idx = np.flatnonzero((P0 == r) & eval_mask)
        sh = A_map[idx].mean(axis=1) if len(idx) else np.zeros(0)
        ent = float(np.mean([bin_entropy(x) for x in sh])) if len(idx) else float("nan")
        rows.append(dict(r=r, n=int((P0 == r).sum()), n_eval=len(idx), jac_med=float(np.median(jacs)) if jacs else float("nan"),
                         stable=bool(np.median(jacs) >= c["jac_bar"]) if jacs else False, own=mine, win=win, cnt=cnt, idx=idx,
                         ent=ent, ch=None, D=None, p=None, rej=False, caption=False))
    rng = np.random.default_rng(c["region_seed"])
    fam = [r for r in rows if r["stable"]]
    for r in fam:
        ch = r["win"] if r["win"] is not None else r["own"]
        r["ch"] = ch
        if ch is None or ch == gi or r["n_eval"] == 0:
            r["p"] = 1.0
            r["D"] = 0.0 if ch is None or r["n_eval"] == 0 else float((A_map[r["idx"], ch] - A_map[r["idx"], gi]).mean())
            continue
        d = (A_map[r["idx"], ch] - A_map[r["idx"], gi]).astype(np.float64)
        reps, D_ = CF.cell_boot(d, [comp_map[i] for i in r["idx"]], c["region_B"], rng)
        r["D"], r["p"] = D_, CF.p_of(reps, c["region_B"])
    rej = CF.bh([r["p"] for r in fam], c["q"])
    for r, x in zip(fam, rej):
        r["rej"] = bool(x)
        r["caption"] = bool(x) and r["win"] is not None
    st["rows"] = rows
    st["n_stable"] = len(fam)
    st["n_caption_rs2"] = sum(1 for r in rows if r["caption"])
    st["n_caption"] = st["n_caption_rs2"] if st["stable_map"] else 0
    st["models"] = models
    st["g"] = models[gi]
    return st


def bin_entropy(p):
    if p <= 0 or p >= 1:
        return 0.0
    return float(-(p * math.log2(p) + (1 - p) * math.log2(1 - p)))


def rs_lines(st):
    c = C()
    L = ["", "== REGION-STABILITY (map rows %d, EVAL scored rows %d; UMAP %s seeds %s x k-means k %d seeds %s; published = (%d, %d))"
             " ==" % (st["n_rows"], st["n_eval"], json.dumps(c["umap"], sort_keys=True), list(c["seeds"]), st["k"], list(c["seeds"]),
                      c["seeds"][0], c["seeds"][0])]
    L.append("== RS1 (DECIDING; the POINT decides): median ARI over the %d UMAP-differing partition pairs >= %.2f ==" % (
        st["pairs"], c["ari_bar"]))
    if st["stable_map"]:
        hit("RS1.STABLE")
        L.append("RS1: STABLE-MAP: median ARI %.4f >= %.2f (seed SD of the pair ARIs %.4f)" % (st["ari_med"], c["ari_bar"], st["ari_sd"]))
    else:
        hit("RS1.UNSTABLE")
        L.append("RS1: UNSTABLE-MAP: median ARI %.4f < %.2f; RS1 FAILS (rule 8); the map ships with no region captions and the"
                 " post says the regions are not seed-stable (seed SD of the pair ARIs %.4f)" % (st["ari_med"], c["ari_bar"], st["ari_sd"]))
    L.append("== RS2 (CAPTION RULE; counts; the POINT decides): STABLE iff median best-match Jaccard >= %.2f over the other 24;"
             " caption iff STABLE, the same EVAL argmax in >= %d of 25 and winner - g BH-surviving at q %.2f over the stable"
             " regions (B %d, one-sided component bootstrap) ==" % (c["jac_bar"], c["consensus"], c["q"], c["region_B"]))
    L.append("  region  n_rows  n_EVAL  Jaccard_med  STABLE  consensus(count/25)  challenger  D_vs_g    p        BH    caption  entropy")
    for r in st["rows"]:
        L.append("  %6d  %6d  %6d  %11.4f  %-6s  %-20s %-10s  %-8s  %-7s  %-4s  %-7s  %s" % (
            r["r"], r["n"], r["n_eval"], r["jac_med"], "yes" if r["stable"] else "no",
            "%s (%d)" % (st["models"][r["win"]] if r["win"] is not None else "none", r["cnt"]),
            st["models"][r["ch"]] if r["ch"] is not None else "-", ("%+.4f" % r["D"]) if r["D"] is not None else "-",
            ("%.5f" % r["p"]) if r["p"] is not None else "-", "REJ" if r["rej"] else "-",
            "YES" if (r["caption"] and st["stable_map"]) else "no", f4(r["ent"])))
    if st["n_stable"] == 0:
        hit("RS2.NO_STABLE")
        L.append("RS2: 0 of %d regions STABLE; 0 licensed winner captions (BH over an empty family)" % st["k"])
    elif st["stable_map"]:
        hit("RS2.CAPTIONS")
        L.append("RS2: %d of %d regions STABLE; licensed winner captions %d%s" % (
            st["n_stable"], st["k"], st["n_caption"], (": " + "; ".join("region %d: %s wins here" % (r["r"], st["models"][r["win"]])
                                                                      for r in st["rows"] if r["caption"])) if st["n_caption"] else ""))
    if not st["stable_map"] and st["n_stable"] > 0:
        hit("RS2.WITHDRAWN")
        L.append("RS2: %d of %d regions STABLE; RS2 would license %d caption(s), but under UNSTABLE-MAP no region is captioned"
                 " (licensed captions 0)" % (st["n_stable"], st["k"], st["n_caption_rs2"]))
    elif not st["stable_map"]:
        L.append("RS2: under UNSTABLE-MAP no region is captioned (licensed captions 0)")
    return L, dict(RS1="STABLE-MAP" if st["stable_map"] else "UNSTABLE-MAP")


def desc_map_lines(dst):
    L = ["", "== MAP DESCRIPTIVES (decide nothing) =="]
    L.append("  ARI across k-means seeds at fixed UMAP seed (k %d; 50 pairs): median %.4f" % (C()["k"], dst["ari_kfix"]))
    for k, v in dst["k_desc"]:
        L.append("  RS1-type median ARI at k = %d (250 UMAP-differing pairs): %.4f" % (k, v))
    L.append("  k-means k %d on the %d-d rows directly (no UMAP), seeds %s: median pairwise ARI %.4f; median ARI vs the published"
             " 2-D partition %.4f" % (C()["k"], dst["dim"], list(C()["seeds"]), dst["ari_hd"], dst["ari_hd_pub"]))
    L.append("  second-embedder (nomic) map: NOT COMPUTED (registered only after the EMBEDDER-PLUMBING gate; descriptive)")
    return L


def map_descriptives(X, Ys, parts, seeds):
    c = C()
    st = {}
    st["ari_kfix"] = float(np.median([ari(parts[(u, a)], parts[(u, b)]) for u in seeds for a in seeds for b in seeds if a < b]))
    st["k_desc"] = []
    for kk in c["k_desc"]:
        pk = {(u, s): kmeans(Ys[u], kk, s) for u in seeds for s in seeds}
        st["k_desc"].append((kk, float(np.median([ari(pk[a], pk[b]) for a, b in rs1_pairs(seeds)]))))
    hd = {s: kmeans(X, c["k"], s) for s in seeds}
    st["ari_hd"] = float(np.median([ari(hd[a], hd[b]) for a in seeds for b in seeds if a < b]))
    st["ari_hd_pub"] = float(np.median([ari(hd[s], parts[(seeds[0], seeds[0])]) for s in seeds]))
    st["dim"] = X.shape[1]
    return st


# ── predictions and Support ─────────────────────────────────────────────────────────────────────────────────────────────

def pred_lines(wst, w1, w2, rst):
    L = ["", "== PREDICTIONS (registrar's priors; bands closed; probabilities by Brier) =="]
    L.append("  P1 O_q 0.90 [0.86, 0.93]: %s -> %s" % (f4(wst["O_q"]), hw(wst["O_q"], PRED["O_q"])))
    L.append("  P1 O_adj 0.80 [0.72, 0.86]: %s -> %s" % (f4(wst["O_adj"]), hw(wst["O_adj"], PRED["O_adj"])))
    L.append("  P1 O_chance 0.75 [0.60, 0.85]: %s -> %s" % (f4(wst["O_chance"]), hw(wst["O_chance"], PRED["O_chance"])))
    L.append("  P2 O_cell (AF-U, in-sample) 0.67 [0.64, 0.71]: %s -> %s" % (f4(wst["O_cell_af"]), hw(wst["O_cell_af"], PRED["O_cell"])))
    o = 1.0 if w1 == "REALISATION-GAP" else 0.0
    L.append("  P3 WF1 REALISATION-GAP 0.90: outcome %s -> Brier %.4f" % (w1, (PRED["p_gap"] - o) ** 2))
    rho = wst["rho"]
    L.append("  P3 rho 0.08 [0.00, 0.16]: %s -> %s" % (f4(rho), hw(rho, PRED["rho"]) if rho == rho else "NOT SCOREABLE (undefined)"))
    o = 1.0 if w2 == "LUCK-MATERIAL" else 0.0
    L.append("  P4 WF2 LUCK-MATERIAL 0.85: outcome %s -> Brier %.4f" % (w2, (PRED["p_luck"] - o) ** 2))
    lam = wst["lam"]
    L.append("  P4 lambda 0.35 [0.20, 0.50]: %s -> %s" % (f4(lam), hw(lam, PRED["lam"]) if lam == lam else "NOT SCOREABLE (undefined)"))
    o = 1.0 if rst["stable_map"] else 0.0
    L.append("  P5 RS1 STABLE-MAP 0.35 / UNSTABLE-MAP 0.65: outcome %s -> Brier %.4f" % (
        "STABLE-MAP" if rst["stable_map"] else "UNSTABLE-MAP", (PRED["p_stable"] - o) ** 2))
    L.append("  P5 median ARI 0.70 [0.55, 0.88]: %.4f -> %s" % (rst["ari_med"], hw(rst["ari_med"], PRED["ari"])))
    L.append("  P6 stable regions 8 [4, 14] of 20: %d -> %s" % (rst["n_stable"], hw(rst["n_stable"], PRED["n_stable"])))
    L.append("  P6 licensed winner captions 2 [0, 5]: %d -> %s" % (rst["n_caption"], hw(rst["n_caption"], PRED["n_caption"])))
    return L


def support_lines(wst, rst, gaf):
    s = SUPPORT
    L = ["", "== SUPPORT (registered planning numbers; MEASURED beside) [D-2026-10-09-2: (b)-(g) below are the PRE-DEVIATION"
             " (MATH-FIX, frozen-policy) planning values; their re-derivation under the official refit is the registrar's insertion"
             " and binds over these] =="]
    L.append("  (a) WF1 / WF2: %d EVAL items / %d components (registered 5,907 / 5,404); RS1: %d UMAP-differing pairs from %d UMAP"
             " seeds (registered 250 from 5)" % (wst["N"], wst["G"], rst["pairs"], len(C()["seeds"])))
    L.append("  (b)-(e) WF1: G_AF %s two-stage [%s, %s], DEFF (two-stage / i.i.d.) %.3f measured (registered 1.595), n_eff %.0f"
             " (registered 3,388); SE(rho) = bootstrap SD %s (registered 0.0363), MDE80 %s (registered 0.102)" % (
                 pp(gaf["point"]), pp(gaf["lo"]), pp(gaf["hi"]), gaf["deff"], gaf["n_eff"], f4(wst["sd_rho"]),
                 f4(2.8 * wst["sd_rho"])))
    L.append("  (b)-(e) WF2: SE(lambda) = bootstrap SD %s (registered 0.0143), MDE80 %s (registered 0.040); planning DEFF 1.10"
             " (not separately measured: lambda carries the two-stage replicates)" % (f4(wst["sd_lam"]), f4(2.8 * wst["sd_lam"])))
    se = 1.2533 * rst["ari_sd"] / math.sqrt(s["rs1"]["n_eff"]) if rst["ari_sd"] == rst["ari_sd"] else float("nan")
    L.append("  (b)-(e) RS1: realised SD of the pair ARIs %s (DECLARED 0.05); SE(median) = 1.2533 x SD / sqrt(5) = %s (registered"
             " 0.0280); MDE80 %s (registered 0.078); DEFF 2.0 DECLARED (pairs share seeds)" % (
                 f4(rst["ari_sd"]), f4(se), f4(2.8 * se)))
    L.append("  (f) VERDICT LINE (registered): WF1 SCOREABLE (predicted rho 0.08, 0.17 below 0.25, beyond MDE 0.102); WF2"
             " SCOREABLE (O_adj model-based, independence disclosed, not powered); RS1 SCOREABLE on a DECLARED seed spread."
             " (g) STRUCTURAL: every word reachable; rho bounded by the policy fitted on TRAIN only (the ONE official refit,"
             " D-2026-10-09-2; the G3 TRAIN-support guard executed on every fit); O_adj <= B -> WF1 NOT EVALUABLE.")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (keyed correctness; no judge verdict enters).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): that O_adj is the true knowable ceiling; any router beyond AF-U's"
             " policy (here the ONE official TRAIN refit, D-2026-10-09-2); new cell flips; judged orders; anything beyond these 18 models and draw 5a3e756; that a stable UMAP"
             " region is a semantic category.")
    return L


# ── the MATH scorer and the official refit (D-2026-10-08-5; D-2026-10-09-2) ─────────────────────────────────────────────

MATH_SRC = "MATH"                        # response.source of a MATH row (= corpus_questions.source; data_v2 ingest)
H_HEAD = ["question_id", "model", "H", "route"]
DEVIATION_TXT = (
    "DECLARED PRE-RUN DEVIATION D-2026-10-09-2 (the author's, \"(a) Refit under official (Recommended)\";"
    " docs/agents/author_decisions/2026-10-09.md, defab40c; prog \"## Author's decision 2026-10-09 ...\" L25394-L25401): the"
    " registered \"never refit\" clause on AF-U's frozen TRAIN policy (sha256 8d68018c...) is broken by exactly ONE refit of the"
    " policy on TRAIN under the official MATH scorer; the policy, the W-ID identities (R_AF, B, G_AF, refit == policy) and the"
    " oracle terms (O_q, O_adj, O_chance) use the official scorer; the MATH-FIX values R_AF 0.6201, B 0.6049 and the frozen"
    " 8d68018c are NOT targets; H is a sensitivity line that decides nothing; Support (b)-(g) are the registrar's re-derivation")
D5_DISCLOSURE = (
    "DISCLOSURE (D-2026-10-08-5; pilot figures of the audit's summary.json, not of record): the official scorer credits 2,335 of"
    " 23,832 MATH rows, MATH-FIX 7,516, H 7,126; its strict false negatives on the 5,181 disagreements are about 4,731 (MC 95%"
    " 4,495-4,843); MATH ranks differ (Qwen2.5-32B 16th official, 1st MATH-FIX). UNION-AF-ROUTE's EVAL read (of record) carried"
    " 7,272 MATH-FIX overlay rows, 1,572 changed")


def scorer_line(c):
    """The registrar's declared pre-run deviation (1) of D-2026-10-08-5, verbatim form (prog L25322)."""
    return ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside: no"
            % c["h_sha"])


def load_h(root, say):
    """D-2026-10-08-5 deviation (2): the per-row H table of record, REFUSED unless its bytes' sha256 equals the pin (the file is
    LF, so this is the sha256-lf), it carries the pinned row count, the header question_id,model,H,route, H in {0, 1} and no
    repeated key. -> {(question_id, model): (H, route)}. Not a pool file; read before any key."""
    c = C()
    p = U.P(root, c["h_table"])
    if not os.path.isfile(p):
        refuse("[W-H-PIN] the H table %s is absent: no H line without the pinned table (D-2026-10-08-5, deviation (2))" % p)
    raw = open(p, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != c["h_sha"]:
        refuse("[W-H-PIN] the H table %s is sha256 %s, not the pinned %s" % (p, sha, c["h_sha"]))
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8"))))
    if not rows or rows[0] != H_HEAD:
        refuse("[W-H-PIN] the H table's header is %r, not %r" % (rows[0] if rows else None, H_HEAD))
    tab = {}
    for r in rows[1:]:
        if len(r) != 4 or r[2] not in ("0", "1") or (int(r[0]), r[1]) in tab:
            refuse("[W-H-PIN] the H table row %r is malformed or repeated" % (r,))
        tab[(int(r[0]), r[1])] = (int(r[2]), r[3])
    if len(tab) != int(c["h_rows"]):
        refuse("[W-H-PIN] the H table carries %d rows, not the pinned %d" % (len(tab), c["h_rows"]))
    say("%s H TABLE (the sensitivity line's input; decides nothing): %s sha256-lf %s (= the pin); %d rows, %d models; H credits %d,"
        " route 'imported' %d" % (TAG, c["h_table"], sha, len(tab), len(set(m for _q, m in tab)), sum(h for h, _r in tab.values()),
                                  sum(1 for _h, r in tab.values() if r == "imported")))
    return tab


def h_key(tw, table, cv, models, items, rule, htab):
    """The H key over the SAME scope and unsealed window as the official read: a MATH row's value is H(question_id = legacy_qid,
    model), every other row's the official is_correct; a cell with more than one row is unusable (UNUSABLE_CELL, as read_key).
    REFUSED: a model outside the H table; a MATH row without an H row; an id-space mismatch (H route 'imported' iff official 1)."""
    ms = set(models)
    hm = set(m for _q, m in htab)
    if ms - hm:
        refuse("[W-H-JOIN] model(s) %s have no row in the H table" % sorted(ms - hm))
    mlist, ilist = sorted(ms), sorted(items)
    vals = defaultdict(list)
    n_math = n_diff = 0
    for s0 in range(0, len(ilist), 500):
        ch = ilist[s0:s0 + 500]
        for m, iid, q, src, ok in tw.execute("SELECT model, item_id, legacy_qid, source, is_correct FROM %s WHERE corpus_version=? AND"
                                             " model IN (%s) AND item_id IN (%s)" % (table, ",".join("?" * len(mlist)),
                                                                                    ",".join("?" * len(ch))), [cv] + mlist + ch):
            if m not in ms or iid not in items:
                continue
            v = int(ok)
            if src == MATH_SRC:
                hv = htab.get((int(q), m))
                if hv is None:
                    refuse("[W-H-JOIN] MATH row (question_id %s, model %s) has no H row" % (q, m))
                if (hv[1] == "imported") != (v == 1):
                    refuse("[W-H-JOIN] id space: (question_id %s, model %s) official %d but H route %r" % (q, m, v, hv[1]))
                n_math += 1
                n_diff += int(hv[0] != v)
                v = hv[0]
            vals[(iid, m)].append(v)
    K = defaultdict(dict)
    for (iid, m), vs in vals.items():
        if len(vs) == 1 or (rule == "AGREE_OR_UNUSABLE" and len(set(vs)) == 1):
            K[iid][m] = vs[0]
    return K, dict(math_rows=n_math, h_changed=n_diff)


class Scorer:
    """D-2026-10-08-5 / D-2026-10-09-2: every key read of --run is the OFFICIAL scorer (is_correct, no MATH-FIX overlay). Inside
    run() the name v2_declared_cells.read_key is bound to Scorer.read_key (restored on exit; the pinned modules are not edited).
    Two reads are expected, in this order: (1) THIS script's TRAIN read (train_block; response_lite; it passes overlay False),
    (2) union_cells_io.eval_set's pinned EVAL read (response; it passes overlay True, which is forced OFF here). Anything else
    REFUSES [W-SCORER]. Each read builds the H key (sensitivity) in the same window and scope; an overlay row read REFUSES."""
    OVERLAY = False                      # passed to the pinned read_key; a selftest sets it True to prove the overlay-row refusal

    def __init__(self, htab):
        self.htab, self.calls, self.orig = htab, [], None

    def __enter__(self):
        self.orig = V.read_key
        V.read_key = self.read_key
        return self

    def __exit__(self, *exc):
        V.read_key = self.orig
        return False

    def read_key(self, tw, table, cv, models, items, overlay, rule):
        want = [("response_lite", False), ("response", True)]
        n = len(self.calls)
        if n >= len(want) or (table, overlay) != want[n]:
            refuse("[W-SCORER] key read %d is (%s, overlay %r), not %s: the TRAIN read is this script's own (overlay False), the"
                   " EVAL read union_cells_io's pinned call (overlay True passed, forced off)" % (
                       n + 1, table, overlay, want[n] if n < len(want) else "none"))
        K, st = self.orig(tw, table, cv, models, items, self.OVERLAY, rule)
        if st["overlay_rows"]:
            refuse("[W-SCORER] %d MATH-FIX overlay row(s) were read on %s (official scorer: no overlay)" % (st["overlay_rows"], table))
        KH, hs = h_key(tw, table, cv, models, items, rule, self.htab)
        if set((i, m) for i, d in K.items() for m in d) != set((i, m) for i, d in KH.items() for m in d):
            refuse("[W-SCORER] the H key's usable cells differ from the official key's (%s)" % table)
        self.calls.append(dict(table=table, K=K, KH=KH, hs=hs, overlay_rows=st["overlay_rows"]))
        return K, st


def policy_doc(D, P):
    """The ONE official refit as a document (canonical JSON; its sha256 is printed and the file written write-once)."""
    return dict(test=TEST_ID, kind="the ONE TRAIN refit of the AF-U policy under the official MATH scorer (D-2026-10-09-2)",
                scorer="eval_results.is_correct, no MATH-FIX overlay (D-2026-10-08-5)", roster=list(D.models),
                tie_break="the first model in sorted-name order (numpy argmax over the sorted roster)", absent_group="best single",
                variant_rule=C()["rule"], train_items_scored=int(D.n_train), best_single=D.models[P.gb],
                tree_cell={D.tree_keys[i]: (D.models[q] if q >= 0 else None) for i, q in enumerate(P.pol["tree"])},
                true_source_domain={"%s/%s" % D.dom_keys[i]: (D.models[q] if q >= 0 else None) for i, q in enumerate(P.pol["tdom"])})


def policy_bytes(doc):
    return (json.dumps(doc, sort_keys=True, indent=1) + "\n").encode("utf-8")


def same_policy(P, Q):
    return P.gb == Q.gb and sorted(P.pol) == sorted(Q.pol) and all(np.array_equal(P.pol[k], Q.pol[k]) for k in P.pol)


def plain_acc(D, doc, arm):
    """W-ID: an EVAL accuracy recomputed from the policy DOCUMENT by a plain loop (no V.correctness_E): arm "tree" = each EVAL
    item's AF-U cell pick (None -> best single), arm "best" = the best single."""
    mi = {m: j for j, m in enumerate(D.models)}
    tot = 0
    for p in D.E:
        m = doc["best_single"]
        if arm == "tree":
            m = doc["tree_cell"].get(D.tree_keys[int(D.g_tree[p])]) or doc["best_single"]
        tot += int(D.A[p, mi[m]])
    return tot / float(len(D.E))


def w_id(D, P_off, doc, bt, gaf, fits, say):
    """W-ID (D-2026-10-09-2): the identities are checked against the official refit. REFUSED: (1) run_boot's point policy is not
    the refit; (2) R_AF or B of run_boot differs from the plain recomputation from the policy document by more than tol; (3) the
    G_AF point is not R_AF - B; (4) the full-TRAIN point policy was fitted other than twice (the refit + run_boot's own
    identical point fit) or the replicate refits are not B."""
    c = C()
    R_af, B_ = float(bt["point"][0, V.TREE]), float(bt["point"][0, V.BS])
    r_plain, b_plain = plain_acc(D, doc, "tree"), plain_acc(D, doc, "best")
    say("%s W-ID (against the official refit): R_AF %.6f (plain recomputation %.6f), B %.6f (plain %.6f), tolerance %g; G_AF %s"
        " [%s, %s] two-stage, percentile [%s, %s]; policy fits %d (expected 2 point fits + %d replicate refits)" % (
            TAG, R_af, r_plain, B_, b_plain, c["tol"], pp(gaf["point"]), pp(gaf["lo"]), pp(gaf["hi"]), pp(gaf["pct"][0]),
            pp(gaf["pct"][1]), fits, bt["B"]))
    if not same_policy(bt["P0"], P_off):
        refuse("W-ID: run_boot's point policy differs from the official refit (best single %s vs %s)" % (
            D.models[bt["P0"].gb], D.models[P_off.gb]))
    if abs(R_af - r_plain) > c["tol"]:
        refuse("W-ID: R_AF %.6f differs from the official refit's plain recomputation %.6f by more than %g" % (R_af, r_plain, c["tol"]))
    if abs(B_ - b_plain) > c["tol"]:
        refuse("W-ID: B %.6f differs from the official refit's plain recomputation %.6f by more than %g" % (B_, b_plain, c["tol"]))
    if abs(gaf["point"] - (R_af - B_)) > c["tol"]:
        refuse("W-ID: the G_AF point %.6f is not R_AF - B = %.6f" % (gaf["point"], R_af - B_))
    if fits != bt["B"] + 2:
        refuse("W-ID: %d policy fits, not the ONE refit + run_boot's point fit + B %d replicate refits" % (fits, bt["B"]))


def frozen_lines(doc, pol):
    """DESCRIPTIVE (decides nothing): the frozen MATH-FIX policy 8d68018c beside the official refit."""
    cells = sorted(set(doc["tree_cell"]) | set(pol["tree_cell"]))
    dt = sum(1 for k in cells if doc["tree_cell"].get(k) != pol["tree_cell"].get(k))
    dk = sorted(set(doc["true_source_domain"]) | set(pol["true_source_domain"]))
    dd = sum(1 for k in dk if doc["true_source_domain"].get(k) != pol["true_source_domain"].get(k))
    return ["%s FROZEN MATH-FIX POLICY BESIDE THE OFFICIAL REFIT (descriptive; decides nothing): best single %s (frozen) vs %s"
            " (official refit); AF-U picks differ on %d of %d cells; declared-cell picks differ on %d of %d" % (
                TAG, pol["best_single"], doc["best_single"], dt, len(cells), dd, len(dk))]


def h_matrix(D, KH_tr, KH_ev):
    return np.array([[(KH_ev if D.is_eval[k] else KH_tr)[i][m] for m in D.models] for k, i in enumerate(D.items)],
                    dtype=np.int64).reshape(D.n, len(D.models))


def h_points(D, A_H, P_off, c_all):
    """The H sensitivity points (DESCRIPTIVE): the MATH cells re-scored by H, every other cell official; the policy is the
    OFFICIAL refit (not refit under H); k_mc from TRAIN under H."""
    DH = copy.copy(D)
    DH.A = A_H
    AE = A_H[D.E].astype(np.float64)
    w0 = np.zeros(D.n)
    w0[D.T] = 1
    kE = k_for_eval(DH, w0, c_all)
    CE = V.correctness_E(DH, P_off)
    h = dict(O_q=float(AE.max(axis=1).mean()), O_adj=float(adj_terms(AE, kE, c_all[D.E]).mean()),
             R_AF=float(CE[V.TREE].mean()), B=float(CE[V.BS].mean()))
    h["rho"] = ratio(h["R_AF"] - h["B"], h["O_adj"] - h["B"], float("nan"))
    h["lam"] = ratio(h["O_q"] - h["O_adj"], h["O_q"] - h["B"], float("nan"))
    h["dT"] = int((D.A[D.T] != A_H[D.T]).sum())
    h["dE"] = int((D.A[D.E] != A_H[D.E]).sum())
    return h


def h_lines(h, calls):
    c = C()
    hit("H.LINE")
    return ["", "SENSITIVITY H (D-2026-10-08-5 deviation (4); DESCRIPTIVE, decides nothing: no criterion word, falsifier or"
            " prediction is read off these lines): the MATH cells re-scored by H (table sha256-lf %s), every other cell official;"
            " the policy is the OFFICIAL refit (not refit under H); MATH rows read TRAIN %d / EVAL %d, H differs on %d / %d; scored"
            " (model, item) cells changed TRAIN %d, EVAL %d" % (c["h_sha"], calls[0]["hs"]["math_rows"], calls[1]["hs"]["math_rows"],
                                                                 calls[0]["hs"]["h_changed"], calls[1]["hs"]["h_changed"], h["dT"], h["dE"]),
            "  H points: O_q %s, O_adj %s, R_AF %s, B %s, rho %s, lambda %s (no interval)" % (
                f4(h["O_q"]), f4(h["O_adj"]), f4(h["R_AF"]), f4(h["B"]), f4(h["rho"]), f4(h["lam"]))]


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def paths(root):
    c = C()
    od = U.P(root, c["out_dir"])
    return dict(outcome=os.path.join(od, c["outcome"]), marker=os.path.join(od, c["marker"]), policy=os.path.join(od, c["policy_out"]),
                parquet=os.path.join(c["export_dir"], c["export_file"]), readme=os.path.join(c["export_dir"], c["readme"]))


def read_questions(root):
    """corpus_questions (mode=ro, immutable=1 through data_v2.ro.open_ro): (qid, source, domain, text, options_json)."""
    conn = dv2ro.open_ro(U.P(root, C()["texts_db"]))
    try:
        return [tuple(r) for r in conn.execute("SELECT question_id, source, domain, text, options_json FROM corpus_questions")]
    finally:
        conn.close()


def read_res(root):
    p = U.P(root, C()["paeec_rel"])
    d = json.load(open(p, encoding="utf-8"))
    return sorted(set(int(q) for v in d.values() for q in v)), U.sha256_bytes(p)


def read_vectors(root, texts):
    return RP.vectors(U.P(root, C()["emb_db"]), texts, C()["dim"])


_IO = dict(questions=read_questions, res=read_res, vectors=read_vectors, umap_version=umap_version)


def r1_block(root, say):
    rows = _IO["questions"](root)
    qtext = {q: t for q, _s, _d, t, _o in rows}
    res, rsha = _IO["res"](root)
    ids, ntx = twins_exact(qtext, res)
    say("%s R1: paeec RES %d ids (%s sha256-bytes %s), GEN %d; exact-text twins %d ids / %d texts (registered %d / %d; W-R1)" % ((
        TAG, len(res), C()["paeec_rel"], rsha, len(qtext) - len([q for q in res if q in qtext]), len(ids), ntx) + tuple(C()["twins"])))
    if (len(ids), ntx) != tuple(C()["twins"]):
        refuse("R1: the exact-text rule gives %d ids / %d texts, not the registered %d / %d" % ((len(ids), ntx) + tuple(C()["twins"])))
    table = item_table(rows)
    twin_items = sorted(set(item_of(qtext[q]) for q in ids))
    return table, twin_items


def chance_block(table, say):
    ch, why = {}, Counter()
    for it, d in table.items():
        c_, r_ = chance_of(d["source"], d["options"])
        ch[it] = c_
        why[(d["source"], r_)] += 1
    say("%s W-C chance by source and reason: %s" % (TAG, "; ".join("%s %s %d" % (s, r, n) for (s, r), n in sorted(why.items()))))
    return ch


def train_block(root, say, models, key):
    c = C()
    path = U.P(root, c["gen_rel"])
    tw, gsha = V.open_tw("gen", "policy_fit", path, c["gen_sha"], "gen_view", say)
    try:
        nc, ni, _ = V.pool_row(tw, c["pool"], c["cv"])
        if (nc, ni) != (U.C()["pool_comp"], U.C()["pool_items"]):
            refuse("the gen view's pool row is %d / %d, not %d / %d" % (nc, ni, U.C()["pool_comp"], U.C()["pool_items"]))
        regm = V.registry(tw, c["cv"])
        if sorted(m for m, s in regm.items() if s == "ACTIVE") != list(models):
            refuse("the gen view's ACTIVE roster differs from the frozen policy's")
        if V.side_counts(tw).get("EVAL", 0):
            refuse("the generation view carries EVAL rows")
        train_meta = V.side_items(tw, c["cv"], "TRAIN")
        comp_strata = V.component_strata(tw)
        cc = V.cell_counts(tw, "response_lite", c["cv"], models, train_meta)
        pre = V.structurally_complete(cc, models, c["rule"])
        K = kst = None
        if key:
            tw.unseal("%s: the TRAIN key read (the ONE official refit and k_mc; official scorer, no overlay)" % TAG)
            K, kst = V.read_key(tw, "response_lite", c["cv"], models, train_meta, False, c["rule"])
    finally:
        tw.close()
    if not V.after_sha(path, gsha, "gen_view", say):
        refuse("the gen view's sha256 changed during the read")
    say("%s TRAIN: %d items of %s; structurally key-complete %d%s" % (TAG, len(train_meta), c["cv"], len(pre),
                                                                     "" if not key else "; key-complete %d" % len(V.complete_items(K, models))))
    return train_meta, comp_strata, K, pre


def side_rows(root):
    items, meta = EP.read_side(U.P(root, C()["side_rel"]))
    return {i: (cp, s) for i, (cp, s, cs) in items.items() if C()["cv"] in cs}, meta


def prelude(root, say, dry):
    U.pool_line(say, TAG)
    pa = paths(root)
    if not dry:
        U.write_once_check([pa["outcome"], pa["marker"], pa["policy"], pa["parquet"], pa["readme"]], TAG)
    say("%s %s (zero calls; %s) | registration %s" % (TAG, TEST_ID, "DRY-RUN" if dry else "RUN", REG_TXT))
    say(scorer_line(C()))
    say("%s %s" % (TAG, DEVIATION_TXT))
    say("%s %s" % (TAG, D5_DISCLOSURE))
    U.script_pins(say, TAG, [os.path.abspath(__file__), os.path.join(HERE, "union_cells_io.py"), os.path.join(HERE, "union_af_route.py"),
                             os.path.join(HERE, "v2_declared_cells.py"), os.path.join(HERE, "cell_flips.py")])
    uv = _IO["umap_version"]()
    import sklearn
    say("%s umap-learn %s (pinned %s); scikit-learn %s; numpy %s; threads %s" % (
        TAG, uv, UMAP_VERSION, sklearn.__version__, np.__version__, ",".join("%s=%s" % (v, os.environ.get(v)) for v in (
            "OMP_NUM_THREADS", "NUMBA_NUM_THREADS"))))
    if uv != UMAP_VERSION:
        refuse("umap-learn is %s, not the pinned %s" % (uv, UMAP_VERSION))
    htab = load_h(root, say)
    say("%s DATA ALREADY LOOKED AT (R3, disclosed): MC-ROUTER oracle 0.907 / best 0.553 (paeec, id-disjoint only); UNION-AF-ROUTE"
        " best 0.6049, AF 0.6201, declared 0.6316, G_AF +1.52pp [+0.14, +2.91]; CELL-FLIPS 7 / 101. Every claim is relative to"
        " these 18 models (R6)." % TAG)
    say("%s data root %s; outputs %s, %s, %s; release %s, %s (all write-once; never committed)" % (
        TAG, root, pa["outcome"], pa["marker"], pa["policy"], pa["parquet"], pa["readme"]))
    pol = U.load_policy(root, say, TAG)
    say("%s the frozen policy above supplies the ROSTER only; its picks are NOT the policy of this run (D-2026-10-09-2)" % TAG)
    _man, af, _k0 = U.load_cells(root, say, TAG)
    return pol, af, pa, htab


def map_rows(root, say, side, table, twin_items, need_eval):
    """Every union item of the split with a text and a vector, minus R1's twin items (counted per side)."""
    tws = set(twin_items)
    drop = Counter(side[i][1] for i in twin_items if i in side)
    items = sorted(i for i in side if i not in tws)
    notext = Counter(side[i][1] for i in items if i not in table)
    items = [i for i in items if i in table]
    coll = collapse_exact(table, items)
    items = [i for i in items if i not in coll]
    vec = _IO["vectors"](root, [table[i]["text"] for i in items])
    novec = [i for i in items if table[i]["text"] not in vec]
    nvs = set(novec)
    miss_eval = sorted(set(need_eval) - set(i for i in items if table[i]["text"] in vec))
    say("%s MAP ROWS: union items of the split %d; R1 twin items dropped %s; without a text %s; exact duplicates collapsed %d;"
        " without a %d-d vector %d; rows %d (%s)" % (
            TAG, len(side), dict(sorted(drop.items())), dict(sorted(notext.items())), len(coll), C()["dim"], len(novec),
            len(items) - len(novec), dict(sorted(Counter(side[i][1] for i in items if i not in nvs).items()))))
    if miss_eval:
        refuse("%d scored EVAL item(s) have no map row (no text / vector; first %s)" % (len(miss_eval), miss_eval[:3]))
    items = [i for i in items if table[i]["text"] in vec]
    X = np.array([vec[table[i]["text"]] for i in items], dtype=np.float64)
    return items, X


def dry_run(root, out=print):
    pol, af, pa, _htab = prelude(root, out, True)
    table, twin_items = r1_block(root, out)
    chance_block(table, out)
    side, smeta = side_rows(root)
    out("%s side export %s sha256 (LF) %s: %d union items" % (TAG, smeta["path"], smeta["sha256_lf"], len(side)))
    train_meta, _cs, _K, pre_tr = train_block(root, out, pol["roster"], False)
    E = U.eval_set(root, out, TAG, roster=pol["roster"], key=False)
    tw_e = sorted(set(twin_items) & set(E["items"]))
    tr_strata = set((train_meta[i][1], train_meta[i][2]) for i in pre_tr if i in train_meta)
    ev_strata = Counter((E["meta"][i][1], E["meta"][i][2]) for i in E["items"])
    orphan = sorted(k for k in ev_strata if k not in tr_strata)
    out("%s EVAL structurally complete items per source (structure only, no key): %s" % (
        TAG, dict(sorted(Counter(E["meta"][i][1] for i in E["items"]).items()))))
    out("%s W-K structure: declared EVAL strata %d; without a structurally complete TRAIN item %d%s" % (
        TAG, len(ev_strata), len(orphan), (" (--run REFUSES: %s)" % orphan[:5]) if orphan else ""))
    out("%s R1 on the structurally complete EVAL set: twin items %d (W-R1b: --run REFUSES if > 0); on structurally complete"
        " TRAIN items %d (counted)" % (TAG, len(tw_e), len(set(twin_items) & set(pre_tr))))
    items, X = map_rows(root, out, side, table, twin_items, E["items"])
    out("%s PLANNED: two-stage B %d default_rng(%d) (UNION-AF-ROUTE's); UMAP %s seeds %s; k-means k %d n_init %d; region B %d"
        " default_rng(%d); O_sim %d default_rng(%d); map matrix %d x %d" % (
            TAG, C()["B"], C()["seed"], json.dumps(C()["umap"], sort_keys=True), list(C()["seeds"]), C()["k"], C()["n_init"],
            C()["region_B"], C()["region_seed"], C()["sim_reps"], C()["sim_seed"], X.shape[0], X.shape[1]))
    out("%s DRY-RUN complete: no key column was selected (tripwires sealed); no statistic; nothing written" % TAG)
    hit("DRY.DONE")


def run(root, out=print):
    c = C()
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    pol, af, pa, htab = prelude(root, say, False)
    models = list(pol["roster"])
    table, twin_items = r1_block(root, say)
    ch = chance_block(table, say)
    side, smeta = side_rows(root)
    say("%s side export %s sha256 (LF) %s: %d union items" % (TAG, smeta["path"], smeta["sha256_lf"], len(side)))
    with Scorer(htab) as sc:
        train_meta, comp_strata, K_tr, _pre = train_block(root, say, models, True)
        E = U.eval_set(root, say, TAG, roster=models, key=True, marker=pa["marker"])
    if [x["table"] for x in sc.calls] != ["response_lite", "response"] or sc.calls[0]["K"] is not K_tr or sc.calls[1]["K"] is not E["K"]:
        refuse("[W-SCORER] the key reads %s are not the TRAIN and EVAL reads of record" % [x["table"] for x in sc.calls])
    say("%s MATH SCORER (D-2026-10-08-5): TRAIN and EVAL keys read through the pinned read_key with overlay OFF (official"
        " is_correct, of record); MATH-FIX overlay rows read %d / %d" % (TAG, sc.calls[0]["overlay_rows"], sc.calls[1]["overlay_rows"]))
    tw_e = sorted(set(twin_items) & set(E["items"]))
    tw_t = sorted(set(twin_items) & set(V.complete_items(K_tr, models)))
    coll_e = collapse_exact(table, E["items"])
    say("%s R1 on the scored sets: twin items among the %d scored EVAL items %d; exact duplicates collapsed among them %d;"
        " twin items among scored TRAIN items %d (counted; W-R1)" % (TAG, len(E["items"]), len(tw_e), len(coll_e), len(tw_t)))
    if tw_e or coll_e:
        refuse("W-R1b: R1 would remove %d twin / %d duplicate item(s) from the scored EVAL set (first %s); the registration"
               " asserts R_AF / B on the 5,907: a registrar's question, not decided here" % (len(tw_e), len(coll_e), (tw_e + list(coll_e))[:3]))
    mm_ev = [i for i in E["items"] if E["meta"][i][1] in MMLU_NAMES]
    mm_mc = sum(1 for i in mm_ev if ch.get(i, 0.0) > 0)
    say("%s W-C on the scored EVAL set: MMLU items %d, of them MC (c_i > 0) %d" % (TAG, len(mm_ev), mm_mc))
    if mm_ev and mm_mc == 0:
        refuse("W-C: %d MMLU item(s) are scored on EVAL but none gets c_i > 0 (corpus source names %s vs MC_SOURCES %s): the"
               " luck model would treat MMLU-Pro as generative" % (len(mm_ev), MMLU_NAMES, MC_SOURCES))
    norow = [i for i in E["items"] if af.get(i) in (None, V.NO_ROUTING_ROW)]
    if norow:
        refuse("%d scored EVAL item(s) carry no AF-U cell (first %s)" % (len(norow), norow[:3]))
    D = V.build_ud(models, train_meta, E["meta"], K_tr, E["K"], comp_strata, c["train_unit"], None, c["placebo_seed"], tree=af)
    if (D.n_eval, D.eval_units["n_units"]) != (U.C()["n_eval"], U.C()["comp_eval"]):
        refuse("D holds %d EVAL items / %d components" % (D.n_eval, D.eval_units["n_units"]))
    miss = [D.items[k] for k in range(D.n) if D.items[k] not in table]
    c_all = np.array([ch[i] if i in ch else 0.0 for i in D.items], dtype=np.float64)
    say("%s scored: TRAIN %d, EVAL %d (%d components); positions without a text (c_i = 0, counted) %d" % (
        TAG, D.n_train, D.n_eval, D.eval_units["n_units"], len(miss)))
    k_for_eval(D, (~D.is_eval).astype(np.float64), c_all)          # W-K refusal before the bootstrap
    # D-2026-10-09-2: the ONE refit of the policy on TRAIN under the official scorer (V.fit's G3 guard: TRAIN support only)
    P_off = V.fit(D, V.train_full(D))
    doc = policy_doc(D, P_off)
    pbytes = policy_bytes(doc)
    psha = hashlib.sha256(pbytes).hexdigest()
    say("%s OFFICIAL REFIT (D-2026-10-09-2; the ONE refit on TRAIN %d items, official scorer): sha256 %s (canonical JSON, LF;"
        " written write-once to %s); best single %s; AF-U cells %d (picks %d, absent -> best single %d)" % (
            TAG, D.n_train, psha, pa["policy"], doc["best_single"], len(doc["tree_cell"]),
            sum(1 for v in doc["tree_cell"].values() if v is not None), sum(1 for v in doc["tree_cell"].values() if v is None)))
    for ln in frozen_lines(doc, pol):
        say(ln)
    rec = dict(O_q=[], O_adj=[])

    def hook(D_, wt, v):
        kE = k_for_eval(D_, wt, c_all)
        AE = D_.A[D_.E].astype(np.float64)
        rec["O_q"].append(float((v * AE.max(axis=1)).sum() / v.sum()))
        rec["O_adj"].append(float((v * adj_terms(AE, kE, c_all[D_.E])).sum() / v.sum()))
    bt = V.run_boot(D, c["B"], c["seed"], hook=hook)
    gaf = V.contrast(bt, D, "ALL", V.TREE, V.BS)
    w_id(D, P_off, doc, bt, gaf, D.fit_asserts, say)
    af_e = [D.tree_keys[g] for g in D.g_tree[D.E]]
    dom_e = [D.dom[k] for k in D.E]
    wst = waterfall(D, bt, rec, c_all, af_e, dom_e)
    wL, wW = wf_lines(wst)
    for ln in wL:
        say(ln)
    A_H = h_matrix(D, sc.calls[0]["KH"], sc.calls[1]["KH"])
    hst = h_points(D, A_H, P_off, c_all)
    for ln in h_lines(hst, sc.calls):
        say(ln)
    # the map
    items, X = map_rows(root, say, side, table, twin_items, E["items"])
    pos = {it: j for j, it in enumerate(items)}
    eval_set = set(E["items"])
    eval_mask = np.array([it in eval_set for it in items], dtype=bool)
    A_map = np.zeros((len(items), len(models)), dtype=np.int64)
    for j, it in enumerate(items):
        if it in eval_set:
            A_map[j] = [E["K"][it][m] for m in models]
    comp_map = {j: E["meta"][it][0] for j, it in enumerate(items) if it in eval_set}
    seeds = tuple(c["seeds"])
    Ys, parts = map_partitions(X, seeds, c["k"])
    rst = regions(parts, seeds, c["k"], eval_mask, A_map, models.index(doc["best_single"]), comp_map, models)
    rL, rW = rs_lines(rst)
    for ln in rL:
        say(ln)
    dst = map_descriptives(X, Ys, parts, seeds)
    for ln in desc_map_lines(dst):
        say(ln)
    for ln in pred_lines(wst, wW["WF1"], wW["WF2"], rst):
        say(ln)
    for ln in support_lines(wst, rst, gaf):
        say(ln)
    text = "\n".join(lines) + "\n"
    with open(pa["policy"], "xb") as fh:                      # write-once (mode "x"): the official refit of record
        fh.write(pbytes)
    write_outcome(pa["outcome"], text)
    out("%s OFFICIAL REFIT written write-once: %s sha256 %s" % (TAG, pa["policy"], U.sha256_bytes(pa["policy"])))
    out("%s OUTCOME written write-once: %s sha256 %s" % (TAG, pa["outcome"], U.sha256_bytes(pa["outcome"])))
    exp = export(pa, items, Ys[seeds[0]], parts[(seeds[0], seeds[0])], rst, table, side, models, E, K_tr, D)
    for p_ in (pa["parquet"], pa["readme"]):
        out("%s RELEASE written write-once: %s sha256 %s" % (TAG, p_, U.sha256_bytes(p_)))
    hit("RUN.DONE")
    return dict(wst=wst, rst=rst, dst=dst, words=dict(wW, **rW), text=text, D=D, bt=bt, rec=rec, parts=parts, items=items,
                eval_mask=eval_mask, A_map=A_map, export=exp, c_all=c_all, doc=doc, psha=psha, hst=hst, A_H=A_H, gaf=gaf,
                calls=sc.calls)


def write_outcome(path, text):
    """The outcome of record: mode "x" (v2_reader_guards.write_once); an existing path is REFUSED and left unchanged."""
    return U.G.write_once(path, text)


README = """# WIN-MAP release: the union correctness map (TaxoArena, HF blog post 2)

One row per question of the content-closed v2 union split (draw 5a3e756, pool pv2_1575de61bb20e977), relative to these 18
models; the 471 exact-text train/eval twins of CONTENT-DISJOINT-SPLIT-AUDIT are dropped. NO question text is released for any
benchmark (GPQA items in particular carry ids only); NO raw model output is released.

| column | type | meaning |
|---|---|---|
| item_id | string | the v2 split's item key ("i:" + sha256 stem key of the text; no text, but anyone holding a question's text can confirm its membership) |
| question_id | int64 | the item's representative (smallest) question_id in multicorpus_cache_v1.db |
| benchmark | string | the corpus source: MMLU_PRO, GPQA, BBH, MUSR, MATH or IFEVAL |
| domain | string | the benchmark's declared subject / task |
| side | string | TRAIN, GATE or EVAL of the split |
| x, y | float64 | 2-D coordinates: UMAP (umap-learn {umap}, cosine, n_neighbors {nn}, min_dist {md}, random_state {seed}) of the 512-d qwen3-embedding row |
| region | int64 | the published k-means region (k {k}, seed {seed}) |
| correct__<model> | Int8 (nullable) | 1 / 0 keyed correctness of each of the 18 models (null where the key was not read: GATE and unscored items); MATH: the benchmark's official scorer (eval_results.is_correct, no MATH-FIX overlay) |
| n_correct | Int16 (nullable) | number of the 18 models correct |
| entropy | float64 (nullable) | binary entropy (bits) of the share of models correct |
| winner | string (nullable) | the region's licensed winner caption (the 20-of-25 consensus EVAL argmax, BH-surviving vs the best single model); NULL unless caption_licensed |
| caption_licensed | bool | the region's winner caption is licensed by RS2 under a STABLE-MAP (WIN-MAP registration) |
| eval_argmax_descriptive | string (nullable) | the region's EVAL argmax model in the published partition (descriptive; ties to the first in roster order). NOT a caption: only caption_licensed regions may be captioned |

Models: {models}
"""


def export(pa, items, Y, P0, rst, table, side, models, E, K_tr, D):
    import pandas as pd
    import pyarrow as pa_
    import pyarrow.parquet as pq
    c = C()
    trk = set(V.complete_items(K_tr, models))
    cap = {r["r"]: bool(r["caption"] and rst["stable_map"]) for r in rst["rows"]}
    # B2 (READY review 12f42190): a winner is exported ONLY where RS2 licenses the caption under a STABLE-MAP (the consensus
    # winner that was tested); the EVAL argmax of every region ships as eval_argmax_descriptive, which is not a caption
    win = {r["r"]: (models[r["win"]] if cap[r["r"]] and r["win"] is not None else None) for r in rst["rows"]}
    desc = {r["r"]: (models[r["own"]] if r["own"] is not None else None) for r in rst["rows"]}
    evs = set(E["items"])
    cols = dict(item_id=[], question_id=[], benchmark=[], domain=[], side=[], x=[], y=[], region=[], n_correct=[], entropy=[],
                winner=[], caption_licensed=[], eval_argmax_descriptive=[])
    corr = {m: [] for m in models}
    for j, it in enumerate(items):
        t = table[it]
        cols["item_id"].append(it)
        cols["question_id"].append(int(t["qid"]))
        cols["benchmark"].append(t["source"])
        cols["domain"].append(t["domain"])
        cols["side"].append(side[it][1])
        cols["x"].append(float(Y[j, 0]))
        cols["y"].append(float(Y[j, 1]))
        cols["region"].append(int(P0[j]))
        kd = E["K"][it] if it in evs else (K_tr[it] if it in trk else None)
        for m in models:
            corr[m].append(None if kd is None else int(kd[m]))
        if kd is None:
            cols["n_correct"].append(None)
            cols["entropy"].append(None)
        else:
            n = sum(int(kd[m]) for m in models)
            cols["n_correct"].append(n)
            cols["entropy"].append(bin_entropy(n / len(models)))
        cols["winner"].append(win[int(P0[j])])
        cols["caption_licensed"].append(cap[int(P0[j])])
        cols["eval_argmax_descriptive"].append(desc[int(P0[j])])
    df = pd.DataFrame(cols)
    for m in models:
        df["correct__" + m] = pd.array(corr[m], dtype="Int8")
    df["n_correct"] = pd.array(cols["n_correct"], dtype="Int16")
    df["entropy"] = pd.array(cols["entropy"], dtype="Float64")
    os.makedirs(os.path.dirname(pa["parquet"]), exist_ok=True)
    with open(pa["parquet"], "xb") as fh:
        pq.write_table(pa_.Table.from_pandas(df, preserve_index=False), fh)
    txt = README.format(umap=UMAP_VERSION, nn=c["umap"]["n_neighbors"], md=c["umap"]["min_dist"], seed=c["seeds"][0], k=c["k"],
                        models=", ".join(models))
    U.G.write_once(pa["readme"], txt)
    return df


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
TMP_BASE = "E:/TaxoArena_tmp"
NL = chr(10)
FX_MODELS = ["m0", "m1", "m2", "m3", "m4"]
FX_CV = "fxcv"


def _fx_corr(region, k, side, variant="main"):
    """Correctness by region: r0 m3 always right (others wrong but m0 half on TRAIN); r1 m0 best; r2 mixed; r3 m1 a bit better.
    variant "unstable": m0 is right on every TRAIN item, so every frozen pick (and every replicate's refit) is g = m0 and
    R_AF == B in every replicate: rho = 0 exactly (the WF1 REALISATION-GAP path with a hand-known answer)."""
    if variant == "luck" and region == 0 and side == "TRAIN":     # r0's TRAIN won by m0: low know rates, a large luck share
        return dict(m0=1, m1=0, m2=int(k % 5 == 0), m3=0, m4=0)
    if variant == "unstable" and side == "EVAL" and region == 1:   # the EVAL-best model (m3) differs from g (m0)
        return dict(m0=0, m1=int(k % 2 == 0), m2=int(k % 3 == 0), m3=0, m4=1)
    if variant == "unstable" and side == "TRAIN":
        d = _fx_corr(region, k, side)
        d["m0"] = 1
        return d
    if region == 0:
        return dict(m0=int(side == "TRAIN" and k % 2 == 0), m1=0, m2=int(k % 5 == 0), m3=1, m4=0)
    if region == 1:
        return dict(m0=1, m1=int(k % 2 == 0), m2=int(k % 3 == 0), m3=0, m4=int(k % 4 == 0))
    if region == 2 and side == "EVAL" and k % 4 == 0:              # unsolved EVAL items: O_q < 1 (the replicate weights matter)
        return dict(m0=0, m1=0, m2=0, m3=0, m4=0)
    if region == 2:
        return dict(m0=int(k % 2 == 0), m1=int(k % 2 == 1), m2=int(k % 3 == 0), m3=int(k % 3 == 1), m4=int(k % 3 == 2))
    return dict(m0=int(k % 3 != 0), m1=int(k % 4 != 0), m2=0, m3=int(k % 2 == 0), m4=0)


FX_SRC = {0: ("MMLU_PRO", "MMLU_PRO", "law"), 1: ("GPQA", "GPQA", "Physics"), 2: ("MATH", "MATH", "Algebra"), 3: ("BBH", "BBH", "navigate")}


def _fx_opts(region, k):
    if region == 0:
        return json.dumps(["o%d" % j for j in range(10)])
    if region == 1:
        return json.dumps(["a", "b", "c", "d"])
    if region == 2:
        return None
    return None if k == 0 else json.dumps(["Yes", "No"])        # one BBH item without a stored list (free-form class)


def _fixture(tmp, variant="main"):
    """A complete layout. Items: 4 regions x 36 (TRAIN 18, GATE 4, EVAL 14); twins (exact and norm-only); a response-only item.
    Returns (root, X) with the expectations."""
    from data_v2 import split as S
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    rng = np.random.default_rng(7)
    centres = np.eye(16)[:4] * 6.0
    qrows, items, responses, vecs = [], [], [], {}
    qid = [100]
    eval_n_comp = Counter()
    spec_rows = []

    def add_q(text, src_c, dom, opts):
        qid[0] += 1
        qrows.append((qid[0], src_c, dom, text, opts))
        return qid[0]
    for r in range(4):
        vs, src_c, dom = FX_SRC[r]
        for k in range(36):
            side = "TRAIN" if k < 18 else ("GATE" if k < 22 else "EVAL")
            text = "Fixture question r%d k%02d about %s" % (r, k, dom)
            add_q(text, src_c, dom, _fx_opts(r, k))
            it = "i:" + dv2c.KeyCache().stem(text)
            comp = "c:" + it[2:] if not (side == "EVAL" and k % 5 == 1 and k + 1 < 36) else "c:pair%d_%d" % (r, k)
            if side == "EVAL" and k % 5 == 2:
                comp = "c:pair%d_%d" % (r, k - 1)
            items.append(dict(id=it, comp=comp, side=side, src=vs, dom=dom, cvs=[FX_CV]))
            if variant == "unstable":
                v = rng.standard_normal(16)
            else:
                v = centres[r] + rng.standard_normal(16) * 0.3
            vecs[text] = v
            corr = _fx_corr(r, k, side, variant)
            if side != "GATE":
                for m in FX_MODELS:
                    ov = vs == "MATH" and m == "m1"
                    # D-2026-10-08-5: is_correct (official) carries the fixture's truth; is_correct_mathfix DIFFERS on MATH m1
                    responses.append(dict(cv=FX_CV, model=m, item=it, side=side, src=vs, c=corr[m],
                                          mf=(1 - corr[m]) if ov else None))
            spec_rows.append((it, comp, side, vs, dom, r, k, corr, text))
    # twins: T1 = RES 9001, 9002 + GEN 9003 (EVAL item, 3 responses -> unscored); T2 = RES 9011 + GEN 9012 (TRAIN item);
    # NORM-ONLY: RES 9021 "Norm twin" vs GEN 9022 "  norm TWIN " (same stem, not exact: not counted)
    twin_spec = [((9001, 9002, 9003), "Exact twin one about law", "EVAL", 0), ((9011, 9012), "Exact twin two about law", "TRAIN", 0),
                 ((9021, 9022), None, "TRAIN", 0)]
    res = [9001, 9002, 9011, 9021]
    for qs, text, side, r in twin_spec:
        vs, src_c, dom = FX_SRC[r]
        texts = [text] * len(qs) if text else ["Norm twin item", "  norm TWIN item "]
        for q, t in zip(qs, texts):
            qrows.append((q, src_c, dom, t, _fx_opts(0, 3)))
        it = "i:" + dv2c.KeyCache().stem(texts[0])
        scored_twin = variant == "twin_scored" and qs[0] == 9001
        items.append(dict(id=it, comp="c:" + it[2:], side=side, src=vs, dom=dom, cvs=[FX_CV]))
        vecs[texts[0]] = centres[r] + rng.standard_normal(16) * 0.3
        for q in (qs[:1] if scored_twin else qs):
            for m in FX_MODELS:
                responses.append(dict(cv=FX_CV, model=m, item=it, side=side, src=vs, c=1, mf=None))
    # a response-only TRAIN item (no corpus text)
    items.append(dict(id="i:responseonly", comp="c:responseonly", side="TRAIN", src="BBH", dom="navigate", cvs=[FX_CV]))
    for m in FX_MODELS:
        responses.append(dict(cv=FX_CV, model=m, item="i:responseonly", side="TRAIN", src="BBH", c=0, mf=None))
    if variant == "novec":
        vecs.pop(spec_rows[-1][8])          # a scored EVAL item without a vector
    ev = [it for it in items if it["side"] == "EVAL"]
    n_comp_all = len(set(i["comp"] for i in ev))
    # legacy_qid = the view's row counter (v2_declared_cells._mk_view): 1000 GATE-side padding rows of an item outside every
    # scope shift the gen view's counter so its MATH (legacy_qid, model) keys never collide with the eval view's (the H join)
    pad = [dict(cv=FX_CV, model="m0", item="i:pad", side="GATE", src="BBH", c=0, mf=None) for _ in range(1000)]
    responses = pad + responses
    spec = dict(items=items, responses=responses,
                registry=[(FX_CV, m, "ACTIVE") for m in FX_MODELS] + [(FX_CV, V.EXCLUDED, "QUARANTINED")],
                pools=[("pv_fx", FX_CV, n_comp_all, json.dumps({FX_CV: len(ev)}))])
    vdir = os.path.join(root, "data_v2")
    os.makedirs(vdir)
    esha = V._mk_view(os.path.join(vdir, "eval_view_fx.db"), "eval", ("EVAL",), spec)
    gsha = V._mk_view(os.path.join(vdir, "gen_view_fx.db"), "gen", ("TRAIN", "GATE"), spec)
    # texts DB, embeddings DB (big-endian float32, as rp12_pairing.vectors reads them)
    import struct
    tdb = os.path.join(root, "mc.db")
    cn = dv2ro.create_new(tdb)
    cn.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT, domain TEXT, text TEXT, options_json TEXT)")
    cn.executemany("INSERT INTO corpus_questions VALUES (?,?,?,?,?)", qrows)
    cn.commit()
    cn.close()
    edb = os.path.join(root, "emb.db")
    cn = dv2ro.create_new(edb)
    cn.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    cn.executemany("INSERT INTO embeddings VALUES (?,?)", [(t, struct.pack(">16f", *v)) for t, v in vecs.items()])
    cn.commit()
    cn.close()
    # side export
    srows = sorted((it["id"], it["comp"], it["side"], it["src"], it["dom"], FX_CV) for it in items)
    sp = os.path.join(root, "side.tsv")
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (S.SIDE_EXPORT_FORMAT, S._side_rows_sha(srows), len(srows), "0" * 64))
        fh.write("\t".join(S.SIDE_COLS) + "\n")
        for r_ in srows:
            fh.write("\t".join(r_) + "\n")
    pj = os.path.join(root, "paeec.json")
    json.dump({"X/y": res}, open(pj, "w", encoding="utf-8"))
    # AF-U cells: region cells; the frozen policy fitted by plain loops on TRAIN (argmax ties to the first sorted model)
    af = {}
    for it, comp, side, vs, dom, r, k, corr, text in spec_rows:
        af[it] = "%s:n%08d" % (vs, r + 1 if not (r == 3 and k % 2) else 5)       # BBH split in two AF cells (AF != declared)
    for it in items:
        af.setdefault(it["id"], "%s:n%08d" % (it["src"], 1))
    tr = [s for s in spec_rows if s[2] == "TRAIN"] + [("i:responseonly", "c:responseonly", "TRAIN", "BBH", "navigate", 3, -1,
                                                        {m: 0 for m in FX_MODELS}, None)]
    tot = {m: sum(s[7][m] for s in tr) for m in FX_MODELS}
    g = max(FX_MODELS, key=lambda m: (tot[m], -FX_MODELS.index(m)))
    pick, dpick = {}, {}
    for cell in sorted(set(af[s[0]] for s in tr)):
        cs = [s for s in tr if af[s[0]] == cell]
        pick[cell] = max(FX_MODELS, key=lambda m: (sum(s[7][m] for s in cs), -FX_MODELS.index(m)))
    for dk in sorted(set("%s/%s" % (s[3], s[4]) for s in tr)):
        cs = [s for s in tr if "%s/%s" % (s[3], s[4]) == dk]
        dpick[dk] = max(FX_MODELS, key=lambda m: (sum(s[7][m] for s in cs), -FX_MODELS.index(m)))
    if variant == "badpick":
        pick[sorted(pick)[0]] = "m4" if pick[sorted(pick)[0]] != "m4" else "m2"
    g_frozen = g if variant != "badpick" else ("m4" if g != "m4" else "m2")      # badpick: the frozen file's best single differs too
    pol = dict(best_single=g_frozen, roster=FX_MODELS, tree_cell=pick, xtree_cell={"K0": {}}, true_source_domain=dpick, test="SELFTEST")
    pp_ = U.P(root, U.CONST["policy_rel"])
    os.makedirs(os.path.dirname(pp_))
    with open(pp_, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
    inp = U.P(root, U.UA.RES + "/inputs")
    os.makedirs(inp)
    shas = {}
    for rel, cells in ((U.CONST["af_rel"], af), (U.CONST["k0_rel"], {i: "K0:x:000" for i in af})):
        with open(U.P(root, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(U.UA.cells_text(cells, "fixture"))
        shas[rel] = U.UA.sha256_lf(U.P(root, rel))
    mp = U.P(root, U.UA.RES + "/inputs/inputs_manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(dict(afu_files={}, inputs=shas), indent=1, sort_keys=True) + "\n")
    scored_ev = [s for s in spec_rows if s[2] == "EVAL"]
    n_scored = len(scored_ev) + (1 if variant == "twin_scored" else 0)
    comps_scored = len(set(s[1] for s in scored_ev)) + (1 if variant == "twin_scored" else 0)
    uconst = dict(U.CONST, pool="pv_fx", cv=FX_CV, n_eval=n_scored, comp_eval=comps_scored, pool_items=len(ev), pool_comp=n_comp_all,
                  roster=len(FX_MODELS), eval_rel="data_v2/eval_view_fx.db", eval_sha=esha, policy_sha=U.sha256_bytes(pp_),
                  manifest_sha=U.UA.sha256_lf(mp))
    wconst = dict(CONST, pool="pv_fx", cv=FX_CV, paeec_rel="paeec.json", twins=(3, 2), texts_db="mc.db", emb_db="emb.db", dim=16,
                  side_rel="side.tsv", gen_rel="data_v2/gen_view_fx.db", gen_sha=gsha, B=200, umap=dict(CONST["umap"], n_neighbors=10),
                  k=4, k_desc=(2, 6), region_B=2000, sim_reps=50, export_dir=os.path.join(tmp, "export"))
    hrel, hsha, hn, hmap = _fx_h_table(root, [os.path.join(vdir, "gen_view_fx.db"), os.path.join(vdir, "eval_view_fx.db")], variant)
    wconst.update(h_table=hrel, h_sha=hsha, h_rows=hn)
    X = dict(root=root, uconst=uconst, wconst=wconst, rows=spec_rows, g=g, pick=pick, dpick=dpick, af=af, qrows=qrows, res=res, hmap=hmap,
             views=dict(gen=os.path.join(vdir, "gen_view_fx.db"), eval=os.path.join(vdir, "eval_view_fx.db")))
    return root, X


def _fx_h_rule(q, m, off):
    """The fixture's H: official 1 -> (1, imported); else m2 credited on q % 3 != 1 and m4 on q % 2 == 0 (route boxed). Chosen so
    that a refit under H picks m2 in the MATH cell (official: m0) AND m2's EVAL MATH H-accuracy differs from m0's (S21 discriminates)."""
    if off == 1:
        return 1, "imported"
    if (m == "m2" and q % 3 != 1) or (m == "m4" and q % 2 == 0):
        return 1, "boxed"
    return 0, "none"


def _fx_h_table(root, views, variant):
    """The fixture's H table from the MATH rows of both sealed views (read ro): -> (rel, sha256, rows, {(qid, model): H})."""
    import sqlite3
    hfx = {}
    for vp in views:
        cn = dv2ro.open_ro(vp)
        try:
            for tab in ("response_lite", "response"):
                try:
                    rows = cn.execute("SELECT legacy_qid, model, is_correct FROM %s WHERE source='MATH'" % tab).fetchall()
                except sqlite3.OperationalError:
                    continue
                for q, m, off in rows:
                    assert (int(q), m) not in hfx, ("fixture H key collision", q, m)
                    hfx[(int(q), m)] = _fx_h_rule(int(q), m, int(off))
        finally:
            cn.close()
    if variant == "h_missing":
        hfx.pop(sorted(hfx)[0])
    if variant == "h_idspace":
        k0 = sorted(k for k, v in hfx.items() if v[1] == "imported")[0]
        hfx[k0] = (1, "boxed")
    rel = "hfx/math_h_table.csv"
    txt = "question_id,model,H,route\n" + "".join("%d,%s,%d,%s\n" % (q, m, h, r) for (q, m), (h, r) in sorted(hfx.items()))
    hp = U.P(root, rel)
    os.makedirs(os.path.dirname(hp), exist_ok=True)
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    return rel, hashlib.sha256(txt.encode("utf-8")).hexdigest(), len(hfx), {k: v[0] for k, v in hfx.items()}


def _fx_h_oracle(res, X):
    """INDEPENDENT H matrix over D's positions: the views read directly (sqlite3 ro), MATH cells -> the fixture's H rule, every
    other cell the official is_correct; then the points by plain loops (the official refit's picks X["pick"], g)."""
    D = res["D"]
    vals = {}
    for side, vp, tab in (("TRAIN", X["views"]["gen"], "response_lite"), ("EVAL", X["views"]["eval"], "response")):
        cn = dv2ro.open_ro(vp)
        try:
            for q, m, it, src, off in cn.execute("SELECT legacy_qid, model, item_id, source, is_correct FROM %s" % tab):
                v = _fx_h_rule(int(q), m, int(off))[0] if src == "MATH" else int(off)
                vals.setdefault((it, m), []).append(v)
        finally:
            cn.close()
    A = np.array([[vals[(it, m)][0] for m in FX_MODELS] for it in D.items], dtype=np.int64)
    assert all(len(vals[(it, m)]) == 1 for it in D.items for m in FX_MODELS)
    O = _oracle_waterfall(res, X, A=A)
    rho = (O["R_AF"] - O["B"]) / (O["O_adj"] - O["B"]) if O["O_adj"] > O["B"] else float("nan")
    lam = (O["O_q"] - O["O_adj"]) / (O["O_q"] - O["B"]) if O["O_q"] > O["B"] else float("nan")
    return A, dict(O_q=O["O_q"], O_adj=O["O_adj"], R_AF=O["R_AF"], B=O["B"], rho=rho, lam=lam)


def _fx_identities(root, X):
    """The fixture's R_AF / B / G_AF strings, computed by an independent build of D and V.run_boot (no win_map code path)."""
    rows = X["rows"]
    tr = [s for s in rows if s[2] == "TRAIN"]
    ev = [s for s in rows if s[2] == "EVAL"]
    K_tr = {s[0]: dict(s[7]) for s in tr}
    K_tr["i:responseonly"] = {m: 0 for m in FX_MODELS}
    K_ev = {s[0]: dict(s[7]) for s in ev}
    tmeta = {s[0]: (s[1], s[3], s[4]) for s in tr}
    tmeta["i:responseonly"] = ("c:responseonly", "BBH", "navigate")
    emeta = {s[0]: (s[1], s[3], s[4]) for s in ev}
    D = V.build_ud(FX_MODELS, tmeta, emeta, K_tr, K_ev, {}, "item", None, 42, tree=X["af"])
    bt = V.run_boot(D, X["wconst"]["B"], X["wconst"]["seed"])
    g = V.contrast(bt, D, "ALL", V.TREE, V.BS)
    return float(bt["point"][0, V.TREE]), float(bt["point"][0, V.BS]), (pp(g["point"]), pp(g["lo"]), pp(g["hi"]))


@contextlib.contextmanager
def _patched(X, pool=(0, "SELFTEST stub: pool check not run"), **over):
    old = (U._C[0], U._POOL[0], U.UA._ROOT[0], _C[0])
    U._C[0] = X["uconst"]
    U._POOL[0] = lambda _p: pool
    _C[0] = dict(X["wconst"], **over)
    try:
        yield
    finally:
        U._C[0], U._POOL[0], U.UA._ROOT[0], _C[0] = old


def _capture(fn, *a, **k):
    buf = []
    res = fn(*a, out=buf.append, **k)
    return res, NL.join(buf)


def _need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def _prepare(tmp, variant="main"):
    root, X = _fixture(tmp, variant)
    X["ident"] = _fx_identities(root, X)          # independent of win_map's path: the official R_AF, B, G_AF strings
    return root, X


def _ari_loop(a, b):
    """INDEPENDENT ARI (Hubert-Arabie) from the contingency table, plain loops."""
    n = len(a)
    cont = Counter(zip(a.tolist(), b.tolist()))
    ca, cb = Counter(a.tolist()), Counter(b.tolist())
    c2 = lambda x: x * (x - 1) / 2.0
    s = sum(c2(v) for v in cont.values())
    sa, sb = sum(c2(v) for v in ca.values()), sum(c2(v) for v in cb.values())
    e = sa * sb / c2(n)
    mx = (sa + sb) / 2.0
    return (s - e) / (mx - e) if mx != e else 1.0


def _oracle_waterfall(res, X, A=None):
    """INDEPENDENT plain loops on the fixture spec: O_q, O_adj, O_chance, O_cell, R_AF, B at the point; per replicate from the
    recorded weights (wt over D positions, v over EVAL positions). A (optional): a correctness matrix over D's positions that
    replaces the spec's (the H sensitivity); R_AF / B then read it with the official picks."""
    D = res["D"]
    AA = D.A if A is None else A
    rows = {s[0]: s for s in X["rows"]}
    opt = {}
    for q, src, dom, text, o in X["qrows"]:
        it = "i:" + dv2c.KeyCache().stem(text) if text.strip() else None
        if it and (it not in opt or q < opt[it][0]):
            opt[it] = (q, src, o)

    def cval(it):
        if it not in opt:
            return 0.0
        _q, src, o = opt[it]
        if src not in ("MMLU_PRO_LB", "MMLU_PRO", "GPQA", "BBH", "MUSR") or o is None:     # the registered list, not MC_SOURCES
            return 0.0
        L = json.loads(o)
        return 1.0 / len(L) if len(L) >= 2 else 0.0

    def ks(wt):
        acc, mass, cs = defaultdict(float), defaultdict(float), defaultdict(float)
        for p, it in enumerate(D.items):
            if D.is_eval[p] or wt[p] == 0:
                continue
            cell = D.dom[p]
            mass[cell] += wt[p]
            cs[cell] += wt[p] * cval(it)
            for j, m in enumerate(FX_MODELS):
                acc[(cell, m)] += wt[p] * AA[p, j]
        out = {}
        for (cell, m), a in acc.items():
            cb = cs[cell] / mass[cell]
            out[(cell, m)] = max(0.0, (a / mass[cell] - cb) / (1 - cb))
        return out

    def oq_oa(wt, v):
        kk = ks(wt)
        sq = sa = sv = 0.0
        for e, p in enumerate(D.E):
            it = D.items[p]
            ci = cval(it)
            solved = [j for j in range(len(FX_MODELS)) if AA[p, j] == 1]
            prod = 1.0
            for j in solved:
                k_ = kk[(D.dom[p], FX_MODELS[j])]
                q = 1.0 if ci == 0 else k_ / (k_ + (1 - k_) * ci)
                prod *= (1 - q)
            sq += v[e] * (1 if solved else 0)
            sa += v[e] * ((1 - prod) if solved else 0)
            sv += v[e]
        return sq / sv, sa / sv
    w0 = [0 if D.is_eval[p] else 1 for p in range(D.n)]
    oq, oa = oq_oa(w0, [1.0] * len(D.E))
    ev = [rows[D.items[p]] for p in D.E]
    och = sum(1 - (1 - cval(s[0])) ** len(FX_MODELS) for s in ev) / len(ev)
    by = defaultdict(list)
    for s in ev:
        by[X["af"][s[0]]].append(s)
    ocell = sum(max(sum(s[7][m] for s in ss) for m in FX_MODELS) for ss in by.values()) / len(ev)
    byd = defaultdict(list)
    for s in ev:
        byd[(s[3], s[4])].append(s)
    ocd = sum(max(sum(s[7][m] for s in ss) for m in FX_MODELS) for ss in byd.values()) / len(ev)
    r_af = sum(s[7][X["pick"].get(X["af"][s[0]], X["g"])] for s in ev) / len(ev)
    b = sum(s[7][X["g"]] for s in ev) / len(ev)
    if A is not None:
        pos = {it: p for p, it in enumerate(D.items)}
        r_af = sum(A[pos[s[0]], FX_MODELS.index(X["pick"].get(X["af"][s[0]], X["g"]))] for s in ev) / float(len(ev))
        b = sum(A[pos[s[0]], FX_MODELS.index(X["g"])] for s in ev) / float(len(ev))
    return dict(O_q=oq, O_adj=oa, O_chance=och, O_cell_af=ocell, O_cell_dom=ocd, R_AF=r_af, B=b, ks=ks, oq_oa=oq_oa)


def _num(text, label):
    for ln in text.split(NL):
        if ln.strip().startswith(label):
            return float(ln.split()[-3 if "[" in ln else -1].strip("[,]"))
    raise AssertionError("no line %r" % label)


def _check_wf(res, X, text, recw):
    """The waterfall numbers, intervals and words against the independent oracle; returns (rho, lo_r, hi_r, lo_l)."""
    c = C()
    O = _oracle_waterfall(res, X)
    w = res["wst"]
    for k_ in ("O_q", "O_adj", "O_chance", "O_cell_af", "O_cell_dom", "R_AF", "B"):
        assert abs(w[k_] - O[k_]) < 1e-12, "%s: %r vs the oracle %r" % (k_, w[k_], O[k_])
    for k_, lab in (("O_q", "O_q (per-question"), ("O_adj", "O_adj (luck"), ("R_AF", "R_AF (the official"), ("B", "B (TRAIN-chosen")):
        assert abs(_num(text, lab) - round(w[k_], 4)) < 1e-9, "%s printed %r" % (k_, _num(text, lab))
    assert len(recw) == c["B"]
    rr, ll = [], []
    two = res["bt"]["two"]
    for b_, (wt, v) in enumerate(recw):
        oq, oa = O["oq_oa"](wt, v)
        r_, bb = two[b_, 0, V.TREE], two[b_, 0, V.BS]
        rr.append((r_ - bb) / (oa - bb) if oa > bb else float("inf"))
        ll.append((oq - oa) / (oq - bb) if oq > bb else float("-inf"))
    rr.sort()
    ll.sort()
    lo_r, hi_r = rr[int(0.025 * c["B"])], rr[int(0.975 * c["B"]) - 1]
    lo_l, hi_l = ll[int(0.025 * c["B"])], ll[int(0.975 * c["B"]) - 1]
    assert abs(w["iv"]["rho"][1] - hi_r) < 1e-12 and abs(w["iv"]["rho"][0] - lo_r) < 1e-12, (w["iv"]["rho"], lo_r, hi_r)
    assert abs(w["iv"]["lam"][0] - lo_l) < 1e-12 and abs(w["iv"]["lam"][1] - hi_l) < 1e-12, (w["iv"]["lam"], lo_l, hi_l)
    rho = (O["R_AF"] - O["B"]) / (O["O_adj"] - O["B"])
    lam = (O["O_q"] - O["O_adj"]) / (O["O_q"] - O["B"])
    assert abs(w["rho"] - rho) < 1e-12 and abs(w["lam"] - lam) < 1e-12
    want1 = "REALISATION-GAP" if hi_r < 0.25 else "NOT-SHOWN"
    want2 = "LUCK-MATERIAL" if lo_l > 0.10 else "NOT-SHOWN"
    assert res["words"]["WF1"] == want1 and res["words"]["WF2"] == want2, (res["words"], want1, want2)
    _need(text, "WF1: %s: rho %.4f [%.4f, %.4f]" % (want1, rho, lo_r, hi_r), "WF2: %s: lambda %.4f [%.4f, %.4f]" % (want2, lam, lo_l, hi_l))
    _need(text, "F-WM: %s" % ("FIRED" if rho >= 0.25 else "NOT FIRED"))
    return rho, lo_r, hi_r, lo_l


@contextlib.contextmanager
def _recording(recw):
    orig = V.run_boot

    def rb(D, B, seed, hook=None):
        def h(D_, wt, v):
            recw.append((wt.copy(), v.copy()))
            hook(D_, wt, v)
        return orig(D, B, seed, hook=h)
    V.run_boot = rb
    try:
        yield
    finally:
        V.run_boot = orig


def st_e2e(tmp):
    root, X = _prepare(tmp)
    recw = []
    with _recording(recw), _patched(X):
        if True:
            res, printed = _capture(run, root)
            c = C()
            pa = paths(root)
            text = open(pa["outcome"], encoding="utf-8").read()
            assert text == res["text"], "the outcome differs from the printed text"
            assert printed.split(NL)[0].startswith("%s POOL pv_fx" % TAG), "the POOL line is not first"
            _need(text, "exact-text twins 3 ids / 2 texts (registered 3 / 2", "twin items among the 56 scored EVAL items 0",
                  "twin items among scored TRAIN items 0", "R1 twin items dropped {'EVAL': 1, 'TRAIN': 1}")
            _need(text, "W-C chance by source and reason: BBH MC 35; BBH no stored option list 1; GPQA MC 36; MATH generative source 36;"
                        " MMLU_PRO MC 39", "W-C on the scored EVAL set: MMLU items 14, of them MC (c_i > 0) 14")
            rho, lo_r, hi_r, lo_l = _check_wf(res, X, text, recw)
            assert res["words"]["WF1"] == "NOT-SHOWN" and rho >= 0.25 and res["words"]["WF2"] == "NOT-SHOWN", (rho, res["words"])
            _check_official(res, X, text, printed)
            _need(text, "rows 145 ({'EVAL': 56, 'GATE': 16, 'TRAIN': 73})")
            assert res["rst"]["g"] == X["g"] == "m0"
            # RS1 by an independent ARI over the returned partitions
            P = res["parts"]
            aris = [_ari_loop(P[(u1, k1)], P[(u2, k2)]) for u1 in range(5) for u2 in range(5) if u1 < u2 for k1 in range(5) for k2 in range(5)]
            assert len(aris) == 250
            med = float(np.median(aris))
            assert abs(res["rst"]["ari_med"] - med) < 1e-9, (res["rst"]["ari_med"], med)
            assert res["words"]["RS1"] == "STABLE-MAP" and med >= 0.80, med
            _need(text, "RS1: STABLE-MAP: median ARI %.4f" % med)
            # RS2: the m3 region captioned at the p floor; m0 (g) region not
            rows = res["rst"]["rows"]
            caps = [r for r in rows if r["caption"]]
            assert len(caps) == 1 and FX_MODELS[caps[0]["win"]] == "m3", [(r["r"], r["win"], r["p"]) for r in rows]
            assert abs(caps[0]["p"] - 1.0 / (c["region_B"] + 1)) < 1e-15 and abs(caps[0]["D"] - 1.0) < 1e-12 and caps[0]["cnt"] == 25
            assert caps[0]["n_eval"] == 14
            assert all(r["stable"] for r in rows), [r["jac_med"] for r in rows]
            gr = [r for r in rows if r["own"] == FX_MODELS.index(X["g"])]
            assert gr and all(not r["caption"] and r["p"] == 1.0 for r in gr)
            _need(text, "RS2: 4 of 4 regions STABLE; licensed winner captions 1: region %d: m3 wins here" % caps[0]["r"])
            _need(text, "  P6 licensed winner captions 2 [0, 5]: 1 -> HELD", "  P5 RS1 STABLE-MAP 0.35 / UNSTABLE-MAP 0.65: outcome"
                        " STABLE-MAP -> Brier 0.4225")
            # the release
            import pandas as pd
            df = pd.read_parquet(pa["parquet"])
            assert not any("text" in col.lower() for col in df.columns), list(df.columns)
            for col in df.columns:
                if df[col].dtype == object:
                    assert not df[col].astype(str).str.contains("about|Exact twin|Norm twin", case=False).any(), col
            assert len(df) == len(res["items"]) and int((df["benchmark"] == "GPQA").sum()) == 36
            gate = df[df["side"] == "GATE"]
            assert len(gate) == 16 and gate["correct__m0"].isna().all() and gate["n_correct"].isna().all()
            ev = df[df["side"] == "EVAL"]
            assert ev["correct__m3"].notna().all() and int(ev["n_correct"].sum()) == int(res["A_map"].sum())
            assert int(df["caption_licensed"].sum()) == int((df["region"] == caps[0]["r"]).sum())
            # B2: a winner only where the caption is licensed (the consensus winner m3), null elsewhere; the argmax is descriptive
            lic = df[df["caption_licensed"]]
            assert len(lic) and (lic["winner"] == "m3").all(), lic["winner"].unique()
            assert df[~df["caption_licensed"]]["winner"].isna().all(), df[~df["caption_licensed"]]["winner"].unique()
            want_desc = {r["r"]: FX_MODELS[r["own"]] for r in rows}
            assert all(df["eval_argmax_descriptive"] == df["region"].map(want_desc)), "eval_argmax_descriptive differs"
            assert df["eval_argmax_descriptive"].nunique() >= 2
            readme = open(pa["readme"], encoding="utf-8").read()
            _need(readme, "NO question text is released", "| caption_licensed | bool |", "NULL unless caption_licensed",
                  "NOT a caption: only caption_licensed regions may be captioned", "the corpus source: MMLU_PRO, GPQA")
            try:
                _capture(run, root)
                raise AssertionError("a second --run was not refused")
            except SystemExit as e:
                assert "write-once" in str(e), e
            assert open(pa["outcome"], encoding="utf-8").read() == text


SCORER_TEXT = ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside:"
               " no")


def _check_official(res, X, text, printed):
    """D-2026-10-08-5 / D-2026-10-09-2 on the --run outcome, BY VALUE: the scorer header (a literal, not scorer_line) as the 2nd
    line after the POOL and test lines; the deviation line; the overlay never read although the fixture's overlay DIFFERS on MATH
    m1 (the key = the official is_correct: the oracle in _check_wf reads the spec's official values); the ONE refit equals an
    independent plain-loop TRAIN fit and its sha256 is the written file's; the identities equal an independent build; the H
    line equals an independent H oracle."""
    L = text.split(NL)
    assert L[1].startswith("%s %s (zero calls; RUN)" % (TAG, TEST_ID)) and L[2] == SCORER_TEXT % X["wconst"]["h_sha"], L[:3]
    assert L[3].startswith("%s DECLARED PRE-RUN DEVIATION D-2026-10-09-2 (the author's" % TAG), L[3]
    _need(text, "the registered \"never refit\" clause on AF-U's frozen TRAIN policy (sha256 8d68018c...) is broken by exactly ONE"
                " refit", "R_AF 0.6201, B 0.6049 and the frozen 8d68018c are NOT targets; H is a sensitivity line that decides nothing",
          "the official scorer credits 2,335 of 23,832 MATH rows, MATH-FIX 7,516, H 7,126")
    _need(text, "MATH-FIX overlay rows read 0 / 0", "overlay rows 0 (changed 0)")
    assert [x["overlay_rows"] for x in res["calls"]] == [0, 0]
    # the overlay is live in the fixture: a MATH-FIX read would move these cells
    D = res["D"]
    m1 = FX_MODELS.index("m1")
    rows = {s_[0]: s_ for s_ in X["rows"]}
    nm = [p_ for p_ in range(D.n) if D.src[p_] == "MATH"]
    assert len(nm) > 20 and all(D.A[p_, m1] == rows[D.items[p_]][7]["m1"] for p_ in nm), "MATH m1 is not the official value"
    # the ONE refit: independent plain-loop picks (X["pick"], X["g"], X["dpick"] from the spec's official values)
    doc = res["doc"]
    assert doc["best_single"] == X["g"] and {k: v for k, v in doc["tree_cell"].items() if v is not None} == X["pick"], doc
    assert {k: v for k, v in doc["true_source_domain"].items() if v is not None} == X["dpick"]
    pol_p = paths_of(X["root"], X)["policy"]
    psha = U.sha256_bytes(pol_p)
    assert psha == res["psha"] and json.load(open(pol_p, encoding="utf-8")) == json.loads(json.dumps(doc)), psha
    _need(text, "OFFICIAL REFIT (D-2026-10-09-2; the ONE refit on TRAIN %d items, official scorer): sha256 %s" % (D.n_train, psha))
    _need(printed, "OFFICIAL REFIT written write-once: %s sha256 %s" % (pol_p, psha))
    assert D.fit_asserts == X["wconst"]["B"] + 2, D.fit_asserts
    # the identities by value against the independent build (_fx_identities: V.build_ud + V.run_boot on the spec, no win_map path)
    r_af, b, gaf = X["ident"]
    assert abs(res["wst"]["R_AF"] - r_af) < 1e-12 and abs(res["wst"]["B"] - b) < 1e-12, (res["wst"]["R_AF"], r_af, res["wst"]["B"], b)
    assert (pp(res["gaf"]["point"]), pp(res["gaf"]["lo"]), pp(res["gaf"]["hi"])) == gaf, (res["gaf"], gaf)
    _need(text, "W-ID (against the official refit): R_AF %.6f (plain recomputation %.6f), B %.6f (plain %.6f)" % (r_af, r_af, b, b),
          "G_AF %s [%s, %s] two-stage" % gaf, "policy fits %d (expected 2 point fits + %d replicate refits)" % (
              X["wconst"]["B"] + 2, X["wconst"]["B"]))
    _need(text, "AF-U picks differ on 0 of %d cells" % len(doc["tree_cell"]))
    # the H sensitivity line by value (independent oracle) and its place: descriptive, after the WF words
    A_o, H = _fx_h_oracle(res, X)
    assert np.array_equal(res["A_H"], A_o), "the H matrix differs from the independent oracle"
    assert int((A_o != D.A).sum()) > 0 and int((A_o[D.E] != D.A[D.E]).sum()) > 0, "the fixture's H changes no EVAL cell"
    for k_ in ("O_q", "O_adj", "R_AF", "B", "rho", "lam"):
        assert abs(res["hst"][k_] - H[k_]) < 1e-12, (k_, res["hst"][k_], H[k_])
    _need(text, "  H points: O_q %s, O_adj %s, R_AF %s, B %s, rho %s, lambda %s (no interval)" % (
        f4(H["O_q"]), f4(H["O_adj"]), f4(H["R_AF"]), f4(H["B"]), f4(H["rho"]), f4(H["lam"])))
    _need(text, "SENSITIVITY H (D-2026-10-08-5 deviation (4); DESCRIPTIVE, decides nothing", "table sha256-lf %s" % X["wconst"]["h_sha"],
          "scored (model, item) cells changed TRAIN %d, EVAL %d" % (int((A_o[D.T] != D.A[D.T]).sum()), int((A_o[D.E] != D.A[D.E]).sum())))
    assert text.index("SENSITIVITY H") > text.index("F-WM: ") and text.index("SENSITIVITY H") < text.index("== REGION-STABILITY")
    # the fixture discriminates "H points on the OFFICIAL refit" from "H points on a refit under H" (else S21 would be untestable)
    DH = copy.copy(D)
    DH.A = A_o
    r_href = float(V.correctness_E(DH, V.fit(DH, V.train_full(DH)))[V.TREE].mean())
    D.fit_asserts -= 1
    assert abs(r_href - H["R_AF"]) > 1e-6, ("the fixture does not discriminate the H refit", r_href, H["R_AF"])


def st_deviation(tmp):
    """The frozen MATH-FIX policy is no longer the run's policy (D-2026-10-09-2): a frozen file whose pick DIFFERS from the TRAIN
    refit is NOT refused (it was, as W-ID, under the READY blob 74f2e234); its difference is printed (descriptive) and every
    number is the official refit's (g, R_AF, B equal the independent build)."""
    root, X = _prepare(tmp, "badpick")
    with _patched(X):
        res, printed = _capture(run, root)
    r_af, b, gaf = X["ident"]
    assert res["doc"]["best_single"] == X["g"] and abs(res["wst"]["R_AF"] - r_af) < 1e-12 and abs(res["wst"]["B"] - b) < 1e-12
    assert X["g"] == "m0"
    _need(printed, "FROZEN MATH-FIX POLICY BESIDE THE OFFICIAL REFIT (descriptive; decides nothing): best single m4 (frozen) vs m0"
                   " (official refit); AF-U picks differ on 1 of %d cells" % len(res["doc"]["tree_cell"]))
    assert res["rst"]["g"] == X["g"]


def st_scorer():
    """Scorer.read_key on hand stubs: the expected read order and overlay flags; the pinned read_key always called with the
    OFFICIAL flag; an overlay row read refuses; a third read refuses. h_key on a hand table (pure)."""
    seen = []

    def orig(tw, table, cv, models, items, overlay, rule):
        seen.append(overlay)
        return {"i:a": {"m0": 1}}, dict(overlay_rows=0)
    sc = Scorer({})
    sc.orig = orig
    old_hk = globals()["h_key"]
    globals()["h_key"] = lambda *a: ({"i:a": {"m0": 0}}, dict(math_rows=1, h_changed=1))
    try:
        for args, needle in (((None, "response", "cv", ["m0"], {"i:a"}, True, "UNUSABLE_CELL"), "key read 1 is (response, overlay True)"),
                             ((None, "response_lite", "cv", ["m0"], {"i:a"}, True, "UNUSABLE_CELL"), "key read 1 is (response_lite, overlay True)")):
            try:
                sc.read_key(*args)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), e
        sc.read_key(None, "response_lite", "cv", ["m0"], {"i:a"}, False, "UNUSABLE_CELL")
        sc.read_key(None, "response", "cv", ["m0"], {"i:a"}, True, "UNUSABLE_CELL")
        assert seen == [False, False], seen                   # the EVAL caller's True is forced off
        try:
            sc.read_key(None, "response", "cv", ["m0"], {"i:a"}, True, "UNUSABLE_CELL")
            raise AssertionError("a third read was not refused")
        except SystemExit as e:
            assert "key read 3" in str(e), e
        sc2 = Scorer({})
        sc2.orig = lambda *a: ({"i:a": {"m0": 1}}, dict(overlay_rows=2))
        try:
            sc2.read_key(None, "response_lite", "cv", ["m0"], {"i:a"}, False, "UNUSABLE_CELL")
            raise AssertionError("an overlay row read was not refused")
        except SystemExit as e:
            assert "[W-SCORER] 2 MATH-FIX overlay row(s) were read on response_lite" in str(e), e
    finally:
        globals()["h_key"] = old_hk
    assert scorer_line(dict(h_sha="ab")) == SCORER_TEXT % "ab"
    assert CONST["h_sha"] == "6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1" and CONST["h_rows"] == 23832
    assert CONST["h_table"] == "experiment_results/math_scorer_h/math_h_table.csv"


def st_unstable(tmp):
    root, X = _prepare(tmp, "unstable")
    recw = []
    with _recording(recw), _patched(X):
        res, printed = _capture(run, root)
        rho, lo_r, hi_r, lo_l = _check_wf(res, X, res["text"], recw)
    assert rho == 0.0 and lo_r == 0.0 and hi_r == 0.0 and res["words"]["WF1"] == "REALISATION-GAP", (rho, lo_r, hi_r)
    _need(printed, "WF1: REALISATION-GAP: rho 0.0000 [0.0000, 0.0000]; upper 0.0000 < 0.25", "F-WM: NOT FIRED (rho's point 0.0000 < 0.25)")
    assert res["words"]["RS1"] == "UNSTABLE-MAP", res["rst"]["ari_med"]
    assert res["rst"]["g"] == X["g"] == "m0"                              # g is the official TRAIN refit's pick; the EVAL-best is m3 here
    P = res["parts"]
    med = float(np.median([_ari_loop(P[a], P[b]) for a, b in rs1_pairs((0, 1, 2, 3, 4))]))
    assert abs(res["rst"]["ari_med"] - med) < 1e-12, (res["rst"]["ari_med"], med)
    others = [k for k in sorted(P) if k != (0, 0)]
    for r in res["rst"]["rows"]:
        js = [_jac_loop(P[(0, 0)], P[k], r["r"])[0] for k in others]
        assert r["stable"] == bool(np.median(js) >= 0.75), (r["r"], r["jac_med"], np.median(js))
    assert res["rst"]["n_caption"] == 0
    _need(printed, "RS1: UNSTABLE-MAP: median ARI %.4f < 0.80; RS1 FAILS (rule 8)" % res["rst"]["ari_med"])
    assert ("no region is captioned" in printed), "the UNSTABLE-MAP caption withdrawal line is missing"
    _need(printed, "  P6 licensed winner captions 2 [0, 5]: 0 -> HELD")
    import pandas as pd                                                  # B2: under UNSTABLE-MAP no exported winner
    df = pd.read_parquet(paths_of(root, X)["parquet"])
    assert len(df) == len(res["items"]) and df["winner"].isna().all() and not df["caption_licensed"].any(), df["winner"].unique()
    assert df["eval_argmax_descriptive"].notna().all()


def st_luck(tmp):
    root, X = _prepare(tmp, "luck")
    recw = []
    with _recording(recw), _patched(X):
        res, printed = _capture(run, root)
        rho, lo_r, hi_r, lo_l = _check_wf(res, X, res["text"], recw)
    assert res["words"]["WF2"] == "LUCK-MATERIAL" and lo_l > 0.10, (res["words"], lo_l)
    _need(printed, "lower %.4f > 0.10: a material share of the oracle headroom is luck" % lo_l)


def _syn_w(rho_iv=(0.05, 0.2), lam_iv=(0.2, 0.4), rho=0.1, lam=0.3, den_adj=0.2, den_q=0.3, undef=(0, 0)):
    return dict(N=100, G=90, m=18, B_reps=2000, O_q=0.9, O_adj=0.8, O_chance=0.7, c0=10, O_sim=(0.85, 0.84, 0.86), O_cell_af=0.67,
                O_cell_dom=0.66, R_AF=0.62, R_dom=0.63, B=0.6, iv=dict(O_q=(0.89, 0.91), O_adj=(0.79, 0.81), R_AF=(0.61, 0.63),
                                                                       B=(0.59, 0.61), rho=rho_iv, lam=lam_iv),
                undef_rho=undef[0], undef_lam=undef[1], den_adj=den_adj, den_q=den_q, rho=rho, lam=lam, rho_raw=0.07,
                per_source=[("BBH", 10, 0.9, 0.8, 0.7, 0.6, 0.5)], sd_rho=0.03, sd_lam=0.01)


def _syn_r(med=0.85, n_stable=3, stable_rows=None):
    rows = stable_rows or []
    return dict(k=20, n_rows=100, n_eval=50, pairs=250, aris=[med], ari_med=med, ari_sd=0.04, stable_map=bool(med >= 0.80),
                rows=rows, n_stable=n_stable, n_caption_rs2=sum(1 for r in rows if r["caption"]),
                n_caption=sum(1 for r in rows if r["caption"]) if med >= 0.80 else 0, models=FX_MODELS, g="m0")


def st_branches():
    L, W = wf_lines(_syn_w(rho_iv=(0.1, 0.2499)))
    assert W["WF1"] == "REALISATION-GAP"
    _need(NL.join(L), "WF1: REALISATION-GAP: rho 0.1000 [0.1000, 0.2499]; upper 0.2499 < 0.25")
    L, W = wf_lines(_syn_w(rho_iv=(0.1, 0.25)))
    assert W["WF1"] == "NOT-SHOWN"
    _need(NL.join(L), "WF1: NOT-SHOWN: rho 0.1000 [0.1000, 0.2500]; upper 0.2500 >= 0.25; WF1 FAILS (rule 8)",
          "routers realise a material share")
    L, W = wf_lines(_syn_w(den_adj=0.0, rho=float("nan")))
    assert W["WF1"] == "NOT EVALUABLE"
    _need(NL.join(L), "WF1: NOT EVALUABLE: O_adj 0.8000 <= B 0.6000", "F-WM: NOT EVALUABLE (O_adj <= B)")
    L, W = wf_lines(_syn_w(lam_iv=(0.1001, 0.3)))
    assert W["WF2"] == "LUCK-MATERIAL"
    _need(NL.join(L), "WF2: LUCK-MATERIAL: lambda 0.3000 [0.1001, 0.3000]; lower 0.1001 > 0.10")
    L, W = wf_lines(_syn_w(lam_iv=(0.10, 0.3)))
    assert W["WF2"] == "NOT-SHOWN"
    _need(NL.join(L), "WF2: NOT-SHOWN: lambda 0.3000 [0.1000, 0.3000]; lower 0.1000 <= 0.10; WF2 FAILS (rule 8)")
    L, W = wf_lines(_syn_w(den_q=0.0, lam=float("nan")))
    assert W["WF2"] == "NOT-SHOWN (undefined)"
    _need(NL.join(L), "WF2: NOT-SHOWN: O_q 0.9000 <= B 0.6000, lambda undefined (W-B); WF2 FAILS (rule 8)")
    L, _W = wf_lines(_syn_w(rho=0.25, rho_iv=(0.2, 0.3)))
    _need(NL.join(L), "F-WM: FIRED: rho's point 0.2500 >= 0.25")
    L, _W = wf_lines(_syn_w(rho=0.2499))
    _need(NL.join(L), "F-WM: NOT FIRED (rho's point 0.2499 < 0.25)")
    L, W = wf_lines(_syn_w(rho=0.2, rho_iv=(0.1, 0.3)))                 # point < 0.25 <= upper: the POINT decides F-WM (R8)
    t = NL.join(L)
    assert W["WF1"] == "NOT-SHOWN" and "F-WM: FIRED" not in t, W
    _need(t, "WF1: NOT-SHOWN: rho 0.2000 [0.1000, 0.3000]", "F-WM: NOT FIRED (rho's point 0.2000 < 0.25)")
    L, _W = wf_lines(_syn_w(undef=(3, 1)))
    _need(NL.join(L), "UNDEFINED REPLICATES (W-B): rho 3 (O_adj <= B; set +inf), lambda 1 (O_q <= B; set -inf) of 2000")
    # RS1 / RS2
    cap_row = dict(r=0, n=10, n_eval=5, jac_med=0.8, stable=True, own=3, win=3, cnt=22, ch=3, D=1.0, p=0.0001, rej=True,
                   caption=True, ent=0.5)
    L, W = rs_lines(_syn_r(med=0.80, n_stable=1, stable_rows=[cap_row]))
    assert W["RS1"] == "STABLE-MAP"
    _need(NL.join(L), "RS1: STABLE-MAP: median ARI 0.8000 >= 0.80", "RS2: 1 of 20 regions STABLE; licensed winner captions 1: region 0: m3 wins here")
    L, W = rs_lines(_syn_r(med=0.7999, n_stable=1, stable_rows=[cap_row]))
    assert W["RS1"] == "UNSTABLE-MAP"
    _need(NL.join(L), "RS1: UNSTABLE-MAP: median ARI 0.7999 < 0.80; RS1 FAILS (rule 8)",
          "RS2: 1 of 20 regions STABLE; RS2 would license 1 caption(s), but under UNSTABLE-MAP no region is captioned (licensed captions 0)")
    L, _W = rs_lines(_syn_r(med=0.9, n_stable=0))
    _need(NL.join(L), "RS2: 0 of 20 regions STABLE; 0 licensed winner captions")
    L, _W = rs_lines(_syn_r(med=0.5, n_stable=0))
    _need(NL.join(L), "RS2: under UNSTABLE-MAP no region is captioned (licensed captions 0)")
    # predictions: closed bands, Brier
    wst = _syn_w(rho=np.float64(0.16), lam=np.float64(0.20))
    wst.update(O_q=np.float64(0.86), O_adj=0.86, O_chance=0.5999, O_cell_af=np.float64(0.71))
    L = pred_lines(wst, "REALISATION-GAP", "NOT-SHOWN", _syn_r(med=0.55, n_stable=14))
    t = NL.join(L)
    _need(t, "P1 O_q 0.90 [0.86, 0.93]: 0.8600 -> HELD", "P1 O_adj 0.80 [0.72, 0.86]: 0.8600 -> HELD",
          "P1 O_chance 0.75 [0.60, 0.85]: 0.5999 -> FAILED", "P2 O_cell (AF-U, in-sample) 0.67 [0.64, 0.71]: 0.7100 -> HELD",
          "P3 WF1 REALISATION-GAP 0.90: outcome REALISATION-GAP -> Brier 0.0100", "P3 rho 0.08 [0.00, 0.16]: 0.1600 -> HELD",
          "P4 WF2 LUCK-MATERIAL 0.85: outcome NOT-SHOWN -> Brier 0.7225", "P4 lambda 0.35 [0.20, 0.50]: 0.2000 -> HELD",
          "P5 RS1 STABLE-MAP 0.35 / UNSTABLE-MAP 0.65: outcome UNSTABLE-MAP -> Brier 0.1225", "P5 median ARI 0.70 [0.55, 0.88]: 0.5500 -> HELD",
          "P6 stable regions 8 [4, 14] of 20: 14 -> HELD")
    L = pred_lines(_syn_w(rho=float("nan"), lam=float("nan")), "NOT EVALUABLE", "NOT-SHOWN (undefined)", _syn_r(med=0.89, n_stable=3))
    t = NL.join(L)
    _need(t, "P3 rho 0.08 [0.00, 0.16]: nan -> NOT SCOREABLE (undefined)", "P5 median ARI 0.70 [0.55, 0.88]: 0.8900 -> FAILED",
          "P6 stable regions 8 [4, 14] of 20: 3 -> FAILED", "P3 WF1 REALISATION-GAP 0.90: outcome NOT EVALUABLE -> Brier 0.8100")


def st_pure():
    A = np.array([[1, 0], [1, 1], [0, 0], [1, 0], [0, 1]], dtype=np.float64)
    cell = np.array([0, 0, 0, 1, 1])
    w = np.array([1, 1, 2, 1, 0], dtype=np.float64)
    c = np.array([0.5, 0.5, 0.5, 0.0, 0.0])
    k = know_rates(A, w, cell, 3, c)
    # cell 0: mass 4; acc m0 = 2/4 = 0.5, m1 = 1/4; cbar 0.5 -> k m0 0, m1 max(0, -0.5) = 0; cell 1: mass 1 (w 0 on the last), acc
    # m0 1, m1 0, cbar 0 -> k 1, 0; cell 2: no mass -> NaN
    assert np.allclose(k[0], [0, 0]) and np.allclose(k[1], [1, 0]) and np.isnan(k[2]).all(), k
    w2 = np.array([1, 1, 0, 1, 1], dtype=np.float64)
    k2 = know_rates(A, w2, cell, 2, np.array([0.25, 0.25, 0.25, 0.0, 0.0]))
    assert np.allclose(k2[0], [(1 - 0.25) / 0.75, (0.5 - 0.25) / 0.75]) and np.allclose(k2[1], [0.5, 0.5]), k2
    kE = np.array([[0.5, 0.0], [0.5, 0.2], [0.0, 0.0]])
    t = adj_terms(np.array([[1, 0], [1, 1], [0, 1]], dtype=np.float64), kE, np.array([0.25, 0.25, 0.0]))
    q11, q12 = 0.5 / (0.5 + 0.5 * 0.25), 0.2 / (0.2 + 0.8 * 0.25)
    assert np.allclose(t, [q11, 1 - (1 - q11) * (1 - q12), 1.0]), t      # c = 0 -> q = 1 even at k = 0
    assert rs1_pairs((0, 1, 2)) == [((u1, k1), (u2, k2)) for u1 in (0, 1, 2) for u2 in (0, 1, 2) if u1 < u2 for k1 in (0, 1, 2) for k2 in (0, 1, 2)]
    assert len(rs1_pairs((0, 1, 2, 3, 4))) == 250
    P0 = np.array([0, 0, 0, 1, 1, 2])
    Q = np.array([1, 1, 0, 0, 0, 2])
    j, q = best_match(P0, Q, 0, 3)
    assert (round(j, 6), q) == (round(2 / 3, 6), 1), (j, q)        # |{0,1}| / |{0,1,2}|
    j, q = best_match(P0, Q, 1, 3)
    assert (round(j, 6), q) == (round(2 / 3, 6), 0), (j, q)
    assert consensus([1] * 20 + [2] * 5, 20) == (1, 20) and consensus([1] * 19 + [2] * 6, 20) == (None, 19)
    assert consensus([None] * 25, 20) == (None, 0)
    assert region_argmax(np.array([[0, 1], [1, 0]]), np.array([False, False])) is None
    assert region_argmax(np.array([[1, 1], [1, 1]]), np.array([True, True])) == 0       # tie -> the first sorted model
    assert twins_exact({1: "a", 2: "a", 3: " a", 4: "b", 5: "b", 6: "  "}, [1, 3, 4, 6]) == ([1, 4], 2)
    assert chance_of("GPQA", '["a","b","c","d"]') == (0.25, "MC") and chance_of("MATH", '["a","b"]')[0] == 0.0
    assert chance_of("BBH", None) == (0.0, "no stored option list") and chance_of("MUSR", '["x"]')[0] == 0.0
    assert abs(bin_entropy(0.5) - 1.0) < 1e-12 and bin_entropy(0.0) == 0.0 and bin_entropy(1.0) == 0.0
    assert pct_iv(list(range(2000))) == (50.0, 1949.0)
    rb, lb = rep_ratios([0.62, 0.62, 0.62], [0.60, 0.60, 0.60], [0.90, 0.60, 0.95], [0.80, 0.80, 0.60])
    assert np.allclose(rb[:2], [0.1, 0.1]) and rb[2] == float("inf"), rb       # O_adj 0.60 <= B 0.60 -> +inf
    assert abs(lb[0] - 1.0 / 3) < 1e-12 and lb[1] == float("-inf") and abs(lb[2] - 0.35 / 0.35) < 1e-12, lb


def _jac_loop(P0, Q, r):
    """INDEPENDENT best-match Jaccard (plain sets; ties to the lower label)."""
    R = set(np.flatnonzero(P0 == r).tolist())
    best = (-1.0, None)
    for q in sorted(set(Q.tolist())):
        S = set(np.flatnonzero(Q == q).tolist())
        j = len(R & S) / len(R | S) if R | S else 0.0
        if j > best[0]:
            best = (j, q)
    return best


def st_regions_hand():
    """regions() on hand-made partitions (100 rows, blocks A-E of 20; P0 = A0 B1 C2 D3 E4, label 5 empty):
    A m1 always right (caption, p floor); B m2 +0.1 over g on 20 items whose two winning rows share one component (p about
    (18/19)^19 = 0.358, NOT about (18/20)^20 = 0.12 by items); C intact in 12 of the 24 other partitions and split in 12
    (median Jaccard EXACTLY 0.75: STABLE at the boundary; m1 caption); D intact, no EVAL row (argmax None, p 1); E split in
    every other partition (Jaccard 0.5, unstable) though m1 always right there (an unstable region is never tested); label 5
    empty in P0 (n 0). Family = {A, B, C, D} (m 4): BH rejects A and C: RS2 2 captions."""
    seeds = (0, 1, 2, 3, 4)
    N, models = 100, ["m0", "m1", "m2"]
    P0 = np.repeat(np.arange(5), 20)
    others = [p for p in sorted((u, k) for u in seeds for k in seeds) if p != (0, 0)]
    parts = {(0, 0): P0.copy()}
    for j, key in enumerate(others):
        Q = np.empty(N, dtype=np.int64)
        Q[0:20], Q[20:40], Q[60:80] = 2, 0, 3
        Q[40:60] = 1
        if j >= 12:
            Q[50:60] = 5
        Q[80:90], Q[90:100] = 4, 5
        parts[key] = Q
    A = np.zeros((N, 3), dtype=np.int64)
    A[0:20, 1] = 1
    A[20:32, 2] = 1
    A[22:32, 0] = 1
    A[40:60, 1] = 1
    A[80:100, 1] = 1
    evm = np.ones(N, dtype=bool)
    evm[60:80] = False
    comp = {i: ("b0" if i in (20, 21) else "c%d" % i) for i in range(N) if evm[i]}
    old = _C[0]
    try:
        _C[0] = dict(CONST, region_B=4000)
        st = regions(parts, seeds, 6, evm, A, 0, comp, models)
        _C[0] = dict(CONST, region_B=4000, ari_bar=1.01)
        st_u = regions(parts, seeds, 6, evm, A, 0, comp, models)
        med_exact = float(np.median([_ari_loop(parts[a], parts[b]) for a, b in rs1_pairs(seeds)]))
        _C[0] = dict(CONST, region_B=200, ari_bar=med_exact)
        st_b = regions(parts, seeds, 6, evm, A, 0, comp, models)
        _C[0] = dict(CONST, region_B=200, ari_bar=med_exact + 1e-9)
        st_c = regions(parts, seeds, 6, evm, A, 0, comp, models)
    finally:
        _C[0] = old
    rows = {r["r"]: r for r in st["rows"]}
    for r in range(6):
        js = [_jac_loop(P0, parts[k], r)[0] for k in others]
        assert abs(rows[r]["jac_med"] - float(np.median(js))) < 1e-12, (r, rows[r]["jac_med"], np.median(js))
    assert [rows[r]["stable"] for r in range(6)] == [True, True, True, True, False, False], [rows[r]["jac_med"] for r in range(6)]
    assert rows[2]["jac_med"] == 0.75 and rows[4]["jac_med"] == 0.5 and rows[5]["n"] == 0
    assert (rows[0]["win"], rows[0]["cnt"]) == (1, 25) and (rows[1]["win"], rows[1]["cnt"]) == (2, 25)
    assert (rows[2]["win"], rows[2]["cnt"]) == (1, 25) and (rows[3]["own"], rows[3]["win"], rows[3]["cnt"]) == (None, None, 0)
    assert rows[0]["p"] == 1.0 / 4001 and rows[2]["p"] == 1.0 / 4001 and abs(rows[0]["D"] - 1.0) < 1e-12
    assert abs(rows[1]["D"] - 0.1) < 1e-12 and 0.30 < rows[1]["p"] < 0.42, rows[1]["p"]
    assert rows[3]["p"] == 1.0 and rows[4]["p"] is None and rows[5]["p"] is None
    assert [r for r in range(6) if rows[r]["caption"]] == [0, 2] and st["n_stable"] == 4 and st["n_caption_rs2"] == 2
    aris = [_ari_loop(parts[a], parts[b]) for a, b in rs1_pairs(seeds)]
    assert abs(st["ari_med"] - float(np.median(aris))) < 1e-12 and st["stable_map"] == bool(np.median(aris) >= 0.80)
    assert st["n_caption"] == (2 if st["stable_map"] else 0)
    assert st_b["stable_map"] and not st_c["stable_map"], (med_exact, st_b["ari_med"])      # RS1 at its boundary: >= decides
    assert not st_u["stable_map"] and st_u["n_caption"] == 0 and st_u["n_caption_rs2"] == 2
    L, _w = rs_lines(st_u)
    _need(NL.join(L), "RS2: 4 of 6 regions STABLE; RS2 would license 2 caption(s), but under UNSTABLE-MAP no region is captioned")


def _bh_loop(ps, q):
    """INDEPENDENT BH step-up (plain loop): the largest rank i with p_(i) <= i q / m; reject ranks 1..i."""
    srt = sorted(ps)
    m, cut = len(ps), -1.0
    for i, p in enumerate(srt, 1):
        if p <= i * q / m:
            cut = p
    return [p <= cut for p in ps]


def st_regions_rs2():
    """regions() on a hand-made family for the caption rule's two guards (READY review 12f42190, B1 b/c).
    100 rows, P0 = 5 blocks of 20 (labels 0-4); models m0 (= g, never right), m1, m2; all rows EVAL, one component each.
    Block 0: m1 right on rows 0-11, m2 on rows 8-19 (P0 argmax m1 by the tie rule); in 10 of the 24 other partitions rows
    0-3 move to label 4 (Jaccard 16/20 = 0.80: STABLE), where the argmax is m2: votes m1 15 / m2 10 -> NO consensus; the
    challenger is the own argmax m1, D 0.60, BH-rejected -> caption MUST stay off. Blocks 1-3: m1 right on 19 / 18 / 17 rows;
    block 4: m2 right on all 20 (consensus 25 each). The bootstrap is stubbed by D so p is known: D 0.60 / 1.00 -> 1/2000,
    0.95 -> 0.025, 0.90 -> 0.035, 0.85 -> 0.070. BH (m 5) at q 0.05 rejects {0, 1, 2, 4}; at q 0.10 also 3."""
    seeds = (0, 1, 2, 3, 4)
    N, models = 100, ["m0", "m1", "m2"]
    P0 = np.repeat(np.arange(5), 20)
    others = [p for p in sorted((u, k) for u in seeds for k in seeds) if p != (0, 0)]
    parts = {(0, 0): P0.copy()}
    for j, key in enumerate(others):
        Q = P0.copy()
        if j < 10:
            Q[0:4] = 4
        parts[key] = Q
    A = np.zeros((N, 3), dtype=np.int64)
    A[0:12, 1] = 1
    A[8:20, 2] = 1
    A[20:39, 1] = 1
    A[40:58, 1] = 1
    A[60:77, 1] = 1
    A[80:100, 2] = 1
    evm = np.ones(N, dtype=bool)
    comp = {i: "c%d" % i for i in range(N)}
    B = 2000
    kk = {0.6: 1, 1.0: 1, 0.95: 50, 0.9: 70, 0.85: 140}
    orig = CF.cell_boot

    def stub(d, comp_, B_, rng):
        k = kk[round(float(d.mean()), 6)]
        return np.array([-1.0] * k + [1.0] * (B_ - k)), float(d.mean())
    old = _C[0]
    try:
        CF.cell_boot = stub
        _C[0] = dict(CONST, region_B=B, ari_bar=0.0)
        st = regions(parts, seeds, 5, evm, A, 0, comp, models)
    finally:
        CF.cell_boot = orig
        _C[0] = old
    rows = {r["r"]: r for r in st["rows"]}
    assert all(rows[r]["stable"] for r in range(5)), [rows[r]["jac_med"] for r in range(5)]
    assert (rows[0]["own"], rows[0]["win"], rows[0]["cnt"], rows[0]["ch"]) == (1, None, 15, 1), rows[0]
    assert abs(rows[0]["D"] - 0.6) < 1e-12 and rows[0]["p"] == 1.0 / B
    assert [(rows[r]["win"], rows[r]["cnt"]) for r in (1, 2, 3, 4)] == [(1, 25), (1, 25), (1, 25), (2, 25)]
    ps = [rows[r]["p"] for r in range(5)]
    assert ps == [1.0 / B, 0.025, 0.035, 0.07, 1.0 / B], ps
    want05, want10 = _bh_loop(ps, 0.05), _bh_loop(ps, 0.10)
    assert want05 == [True, True, True, False, True] and want10 == [True] * 5      # the family discriminates q 0.05 / 0.10
    assert [rows[r]["rej"] for r in range(5)] == want05, [rows[r]["rej"] for r in range(5)]
    assert [rows[r]["caption"] for r in range(5)] == [False, True, True, False, True], [rows[r]["caption"] for r in range(5)]
    assert st["n_caption_rs2"] == 3 and st["n_caption"] == 3 and st["stable_map"]
    L, _w = rs_lines(st)
    _need(NL.join(L), "RS2: 5 of 5 regions STABLE; licensed winner captions 3: region 1: m1 wins here; region 2: m1 wins here;"
                      " region 4: m2 wins here")


def st_refusals(tmp_factory):
    def expect(variant, needle, pool=(0, "stub"), pre=None, **over):
        tmp = tmp_factory()
        root, X = _prepare(tmp, variant)
        X["wconst"].update(over)
        if pre:
            pre(root, X)
        buf = []
        try:
            with _patched(X, pool=pool):
                run(root, out=buf.append)
            raise AssertionError("not refused: %s" % needle)
        except SystemExit as e:
            assert needle in str(e), "%s: %s" % (needle, e)
        assert not os.path.exists(paths_of(root, X)["outcome"]), "an outcome was written by a refused run (%s)" % needle
        return buf
    t0 = tmp_factory()
    p0 = os.path.join(t0, "o.txt")
    write_outcome(p0, "first" + NL)
    try:
        write_outcome(p0, "second" + NL)
        raise AssertionError("write_outcome overwrote")
    except SystemExit as e:
        assert "write-once" in str(e), e
    assert open(p0, encoding="utf-8").read() == "first" + NL
    expect("main", "R1: the exact-text rule gives 3 ids / 2 texts, not the registered 471 / 427", twins=(471, 427))
    expect("twin_scored", "W-R1b: R1 would remove 1 twin")
    # W-ID against the official refit (D-2026-10-09-2): each identity broken by a stub around the pinned helpers
    def boot_stub(edit):
        orig = V.run_boot

        def rb(D, B, seed, hook=None):
            bt = orig(D, B, seed, hook=hook)
            edit(D, bt)
            return bt
        return rb

    def gb_other(D, bt):
        bt["P0"].gb = (bt["P0"].gb + 1) % len(D.models)

    def r_moved(D, bt):
        bt["point"][0, V.TREE] += 0.01

    def b_moved(D, bt):
        bt["point"][0, V.BS] += 0.01

    def extra_fit(D, bt):
        V.fit(D, V.train_full(D))
    for edit, needle in ((gb_other, "W-ID: run_boot's point policy differs from the official refit"),
                         (r_moved, "W-ID: R_AF "), (b_moved, "W-ID: B "), (extra_fit, "W-ID: %d policy fits" % (200 + 3))):
        orig_rb = V.run_boot
        V.run_boot = boot_stub(edit)
        try:
            expect("main", needle)
        finally:
            V.run_boot = orig_rb
    orig_ct = V.contrast

    def ct(*a):
        d = orig_ct(*a)
        d["point"] += 0.001
        return d
    V.contrast = ct
    try:
        expect("main", "W-ID: the G_AF point")
    finally:
        V.contrast = orig_ct
    # the official scorer: an overlay row read refuses (the seam's flag flipped: the pinned read_key then reads the overlay)
    Scorer.OVERLAY = True
    try:
        expect("main", "[W-SCORER] 18 MATH-FIX overlay row(s) were read on response_lite")
    finally:
        Scorer.OVERLAY = False
    # the H table: pin, absence, row count, join, id space (no H line, no outcome, without the pinned table)
    expect("main", "[W-H-PIN] the H table", h_sha="0" * 64)
    expect("main", "absent.csv is absent: no H line without the pinned table", h_table="hfx/absent.csv")
    expect("main", "carries", h_rows=1)
    expect("h_missing", "[W-H-JOIN] MATH row")
    expect("h_idspace", "[W-H-JOIN] id space")
    expect("novec", "scored EVAL item(s) have no map row")
    global MC_SOURCES
    old_mc = MC_SOURCES
    MC_SOURCES = ("MMLU_PRO_LB", "GPQA", "BBH", "MUSR")                  # the corpus source name dropped (reviewer R4)
    try:
        expect("main", "W-C: 14 MMLU item(s) are scored on EVAL but none gets c_i > 0")
    finally:
        MC_SOURCES = old_mc
    buf = expect("main", "the B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf and buf[0].startswith("%s POOL pv_fx: B0-2 pool check rc 1" % TAG), buf[:1]
    old = _IO["umap_version"]
    _IO["umap_version"] = lambda: "0.5.0"
    try:
        expect("main", "umap-learn is 0.5.0, not the pinned")
    finally:
        _IO["umap_version"] = old

    def mk_marker(root, X):
        with _patched(X):
            p = paths(root)["marker"]
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").close()
    expect("main", "write-once output(s) exist", pre=mk_marker)

    def mk_export(root, X):
        os.makedirs(X["wconst"]["export_dir"], exist_ok=True)
        open(os.path.join(X["wconst"]["export_dir"], X["wconst"]["readme"]), "w").close()
    expect("main", "write-once output(s) exist", pre=mk_export)

    def mk_policy(root, X):
        pp_ = paths_of(root, X)["policy"]
        os.makedirs(os.path.dirname(pp_), exist_ok=True)
        open(pp_, "w").close()
    expect("main", "write-once output(s) exist", pre=mk_policy)
    # an EVAL declared cell without TRAIN mass: W-K refusal (pure path through k_for_eval on a hand-made D)

    class _D:
        pass
    D = _D()
    D.A = np.array([[1, 0], [0, 1], [1, 1]])
    D.g_tdom = np.array([0, 0, 1])
    D.dom_keys = [("X", "a"), ("X", "b")]
    D.E = np.array([2])
    try:
        k_for_eval(D, np.array([1.0, 1.0, 0.0]), np.zeros(3))
        raise AssertionError("W-K not refused")
    except SystemExit as e:
        assert "carry no TRAIN mass" in str(e) and "('X', 'b')" in str(e), e


def paths_of(root, X):
    old = _C[0]
    _C[0] = X["wconst"]
    try:
        return paths(root)
    finally:
        _C[0] = old


def st_dry(tmp):
    root, X = _prepare(tmp)
    with _patched(X):
        _r, printed = _capture(dry_run, root)
    assert printed.split(NL)[0].startswith("%s POOL pv_fx" % TAG)
    _need(printed, SCORER_TEXT % X["wconst"]["h_sha"], "DECLARED PRE-RUN DEVIATION D-2026-10-09-2",
          "H TABLE (the sensitivity line's input; decides nothing): hfx/math_h_table.csv sha256-lf %s (= the pin)" % X["wconst"]["h_sha"],
          "EVAL structurally complete items per source (structure only, no key): {'BBH': 14, 'GPQA': 14, 'MATH': 14, 'MMLU_PRO': 14}")
    _need(printed, "exact-text twins 3 ids / 2 texts", "R1 on the structurally complete EVAL set: twin items 0",
          "W-K structure: declared EVAL strata 4; without a structurally complete TRAIN item 0",
          "DRY-RUN complete: no key column was selected")
    assert "; key-complete" not in printed, "the dry-run read the TRAIN key"
    pa = paths_of(root, X)
    for p in pa.values():
        assert not os.path.exists(p), "the dry-run wrote %s" % p


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print branches never executed: %s" % miss


CASES = (("scorer", st_scorer, "plain"), ("deviation", st_deviation, "tmp"), ("pure", st_pure, "plain"), ("regions", st_regions_hand, "plain"), ("rs2", st_regions_rs2, "plain"), ("branches", st_branches, "plain"), ("e2e", st_e2e, "tmp"), ("unstable", st_unstable, "tmp"), ("luck", st_luck, "tmp"),
         ("refusals", st_refusals, "factory"), ("dry_run", st_dry, "tmp"), ("branch_cover", st_branch_cover, "plain"))


def selftest(only=None, quiet=False):
    import tempfile
    try:
        import scratch_dir          # noqa: F401  (temp under E:/TaxoArena_tmp, removed at exit)
    except Exception:               # noqa: BLE001
        pass
    os.makedirs(TMP_BASE, exist_ok=True)
    HIT.clear()
    fails, ran, made = [], 0, []

    def factory():
        d = tempfile.mkdtemp(prefix="win_map_", dir=TMP_BASE)
        made.append(d)
        return d
    try:
        for name, fn, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    if kind == "tmp":
                        fn(factory())
                    elif kind == "factory":
                        fn(factory)
                    else:
                        fn()
                if not quiet:
                    print("  ok   %s" % name, flush=True)
            except BaseException as e:          # noqa: B902
                fails.append(name)
                if not quiet:
                    print("  FAIL %s: %s: %s" % (name, type(e).__name__, str(e)[:600]), flush=True)
    finally:
        for d in made:
            if os.path.normcase(os.path.abspath(d)).startswith(os.path.normcase(os.path.abspath(TMP_BASE))):
                U.rmtree_ro(d)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def _exec_selftest(src, tests):
    ns = {"__name__": "win_map_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                  # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("\nMUTANTS = (")
    head, tail = src[:cut], src[cut:]
    killed, surv, n_real, control = 0, [], 0, None
    for name, old, new, tests in MUTANTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        olds, news = (old, new) if isinstance(old, tuple) else ((old,), (new,))
        msrc = head
        for o_, n_ in zip(olds, news):
            if msrc.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times: %r" % (TAG, name, msrc.count(o_), o_[:80]))
            msrc = msrc.replace(o_, n_)
        res = _exec_selftest(msrc + tail, tests)
        if name.startswith("C00"):
            control = res is True
            print("  %-66s control %s" % (name, "SURVIVED (as it must)" if control else "KILLED (harness broken): %s" % res), flush=True)
            continue
        n_real += 1
        k = res is not True
        killed += int(k)
        if not k:
            surv.append(name)
        print("  %-66s %-8s %s" % (name, "KILLED" if k else "SURVIVED", "" if res is True else res[:110]), flush=True)
    print("%s MUTANTS: %d of %d KILLED; control %s; survivors %s" % (TAG, killed, n_real, "survived" if control else "KILLED/not run", surv or "none"))
    return 0 if killed == n_real and control else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=U.ROOT, help="the checkout holding experiment_results/, data_v2/ and the DBs (default: this one)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=set(a.only) if a.only else None)
        return 0
    if a.mutants:
        return run_mutants(a.only)
    if a.dry_run:
        dry_run(os.path.abspath(a.data_root))
        return 0
    run(os.path.abspath(a.data_root))
    return 0


# (name, old, new, selftest cases)
MUTANTS = (
    ("C00 control (no-op edit)", "    return band[0] <= x <= band[1]", "    return band[0] <= x <= band[1]", ["branches"]),
    # WF1 / WF2: what decides, the boundary, the bound used (registered form)
    ("M01 WF1 decided by the point, not the upper bound", '        w1 = "REALISATION-GAP" if st["iv"]["rho"][1] < 0.25 else',
     '        w1 = "REALISATION-GAP" if st["rho"] < 0.25 else', ["branches", "e2e"]),
    ("M02 WF1 bar <= 0.25 (boundary)", 'st["iv"]["rho"][1] < 0.25 else', 'st["iv"]["rho"][1] <= 0.25 else', ["branches"]),
    ("M03 WF2 decided by the upper bound (min<->max)", '"LUCK-MATERIAL" if st["iv"]["lam"][0] > 0.10', '"LUCK-MATERIAL" if st["iv"]["lam"][1] > 0.10',
     ["branches", "e2e"]),
    ("M04 WF2 bar >= 0.10 (boundary)", 'st["iv"]["lam"][0] > 0.10 else', 'st["iv"]["lam"][0] >= 0.10 else', ["branches"]),
    ("M05 NOT EVALUABLE branch removed", '    if not st["den_adj"] > 0:\n        w1 = "NOT EVALUABLE"', '    if False:\n        w1 = "NOT EVALUABLE"',
     ["branches"]),
    ("M06 rho over O_q - B (rho_raw) instead of O_adj - B", '    st["rho"] = ratio(st["R_AF"] - st["B"], st["den_adj"]',
     '    st["rho"] = ratio(st["R_AF"] - st["B"], st["den_q"]', ["e2e"]),
    ("M07 replicate rho over O_q", '    rho_b = np.array([ratio(r - b, a - b, float("inf")) for r, b, a in zip(r_rep, b_rep, oa)])',
     '    rho_b = np.array([ratio(r - b, a - b, float("inf")) for r, b, a in zip(r_rep, b_rep, oq)])', ["pure", "e2e"]),
    ("M08 undefined rho replicates set to 0 (not +inf)", 'ratio(r - b, a - b, float("inf"))', 'ratio(r - b, a - b, 0.0)', ["pure"]),
    ("M09 lambda numerator O_q - B", 'ratio(q - a, q - b, float("-inf"))', 'ratio(q - b, q - b, float("-inf"))', ["pure", "e2e"]),
    ("M10 B per replicate frozen at the point (no refit)", '    b_rep = bt["two"][:, 0, V.BS]', '    b_rep = np.full(len(bt["two"]), bt["point"][0, V.BS])',
     ["e2e"]),
    ("M11 R_AF read from the declared arm", '    st["R_AF"] = float(bt["point"][0, V.TREE])', '    st["R_AF"] = float(bt["point"][0, V.TDOM])', ["e2e"]),
    ("M12 percentile lower 0.05", '    return U.pct(s, 0.025), U.pct(s, 0.975)', '    return U.pct(s, 0.05), U.pct(s, 0.975)', ["pure", "e2e"]),
    ("M13 percentile upper = max", '    return U.pct(s, 0.025), U.pct(s, 0.975)', '    return U.pct(s, 0.025), s[-1]', ["pure", "e2e"]),
    # O_adj / k_mc (wrong split side, luck rule, product over solvers)
    ("M14 k_mc fitted on EVAL (wrong split side)", "    w0[D.T] = 1\n    kE = k_for_eval(D, w0, c_all)\n", "    w0[D.E] = 1\n    kE = k_for_eval(D, w0, c_all)\n", ["e2e"]),
    ("M15 replicate k_mc with EVAL mass added", "        kE = k_for_eval(D_, wt, c_all)", "        kE = k_for_eval(D_, wt + D_.is_eval, c_all)", ["e2e"]),
    ("M16 replicate k_mc at the point weights (not refit)", "        kE = k_for_eval(D_, wt, c_all)",
     "        kE = k_for_eval(D_, (~D_.is_eval).astype(np.float64), c_all)", ["e2e"]),
    ("M17 replicate O_q unweighted", "        rec[\"O_q\"].append(float((v * AE.max(axis=1)).sum() / v.sum()))",
     "        rec[\"O_q\"].append(float(AE.max(axis=1).mean()))", ["e2e"]),
    ("M18 k without max(0, .)", "        k = np.maximum(0.0, (acc - cbar[:, None]) / (1.0 - cbar[:, None]))",
     "        k = (acc - cbar[:, None]) / (1.0 - cbar[:, None])", ["pure"]),
    ("M19 c_i = 0 -> q from the formula (k 0 gives 0)", "    q = np.where(c == 0, 1.0,", "    q = np.where(c < 0, 1.0,", ["pure", "e2e"]),
    ("M20 product over every model, not the solvers", "    prod = np.prod(1.0 - A * q, axis=1)", "    prod = np.prod(1.0 - q, axis=1)", ["pure", "e2e"]),
    ("M21 no luck adjustment (q = 1)", "    prod = np.prod(1.0 - A * q, axis=1)", "    prod = np.prod(1.0 - A * np.ones_like(q), axis=1)", ["pure", "e2e"]),
    ("M22 O_cell min instead of max", "        tot += float(A[idx].sum(axis=0).max())", "        tot += float(A[idx].sum(axis=0).min())", ["e2e"]),
    ("M23 W-K refusal off (empty TRAIN cell)", '    if bad:\n        refuse("W-K', '    if False:\n        refuse("W-K', ["refusals"]),
    # c_i (W-C)
    ("M24 generative sources get 1 / len(options)", '    if source not in MC_SOURCES:\n        return 0.0, "generative source"',
     '    if False:\n        return 0.0, "generative source"', ["pure", "e2e"]),
    ("M25 a one-option list counted MC", "    if not isinstance(lst, list) or len(lst) < 2:", "    if not isinstance(lst, list) or len(lst) < 1:", ["pure"]),
    # R1
    ("M26 twins by stem key, not exact text", "    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and qtext[q] in gen_texts)",
     "    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and dv2c.KeyCache().stem(qtext[q]) in set(dv2c.KeyCache().stem(t) for t in gen_texts))",
     ["pure", "e2e"]),
    ("M27 GEN includes RES", "    gen_texts = set(t for q, t in qtext.items() if q not in res and not blank(t))",
     "    gen_texts = set(t for q, t in qtext.items() if not blank(t))", ["pure", "e2e"]),
    ("M28 twin-count refusal off", '    if (len(ids), ntx) != tuple(C()["twins"]):', "    if False:", ["refusals"]),
    ("M29 W-R1b refusal off (a scored EVAL twin kept)", "    if tw_e or coll_e:", "    if False:", ["refusals"]),
    ("M30 the map keeps the twin items", "    items = sorted(i for i in side if i not in tws)", "    items = sorted(side)", ["e2e"]),
    # identities / gates / write-once / modes
    ("M31 W-ID R_AF identity off (official refit)", '    if abs(R_af - r_plain) > c["tol"]:', "    if False:", ["refusals"]),
    ("M32 W-ID B identity off (official refit)", '    if abs(B_ - b_plain) > c["tol"]:', "    if False:", ["refusals"]),
    ("M33 W-ID G_AF point identity off", '    if abs(gaf["point"] - (R_af - B_)) > c["tol"]:', "    if False:", ["refusals"]),
    ("M34 W-ID refit == run_boot point policy off", '    if not same_policy(bt["P0"], P_off):', "    if False:", ["refusals"]),
    ("M35 scored EVAL item without a map row accepted", "    if miss_eval:", "    if False:", ["refusals"]),
    ("M36 umap version gate off", "    if uv != UMAP_VERSION:", "    if False:", ["refusals"]),
    ("M37 write-once outcome opened 'w'", "    return U.G.write_once(path, text)",
     "    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"]),
    ("M38 prelude write-once check removed", '        U.write_once_check([pa["outcome"], pa["marker"], pa["policy"], pa["parquet"], pa["readme"]], TAG)', "        pass",
     ["e2e", "refusals"]),
    ("M39 the POOL line not printed first", "    U.pool_line(say, TAG)\n    pa = paths(root)", "    pa = paths(root)", ["e2e", "refusals", "dry_run"]),
    ("M40 dry-run reads the EVAL key", '    E = U.eval_set(root, out, TAG, roster=pol["roster"], key=False)',
     '    E = U.eval_set(root, out, TAG, roster=pol["roster"], key=True, marker=paths(root)["marker"])', ["dry_run"]),
    ("M41 dry-run reads the TRAIN key", '    train_meta, _cs, _K, pre_tr = train_block(root, out, pol["roster"], False)',
     '    train_meta, _cs, _K, pre_tr = train_block(root, out, pol["roster"], True)', ["dry_run"]),
    # RS1 / RS2
    ("M42 RS1 median -> min", '    st["ari_med"] = float(np.median(aris))', '    st["ari_med"] = float(np.min(aris))', ["unstable", "regions"]),
    ("M43 RS1 pairs include same-UMAP pairs", "for u1 in seeds for u2 in seeds if u1 < u2 for k1", "for u1 in seeds for u2 in seeds if u1 <= u2 for k1",
     ["pure", "e2e"]),
    ("M44 RS1 bar > 0.80 (boundary)", '    st["stable_map"] = bool(st["ari_med"] >= c["ari_bar"])', '    st["stable_map"] = bool(st["ari_med"] > c["ari_bar"])',
     ["regions", "branches"]),
    ("M45 RS2 Jaccard median -> max", 'stable=bool(np.median(jacs) >= c["jac_bar"])', 'stable=bool(np.max(jacs) >= c["jac_bar"])', ["regions", "unstable"]),
    ("M46 RS2 Jaccard bar > 0.75 (boundary)", 'stable=bool(np.median(jacs) >= c["jac_bar"])', 'stable=bool(np.median(jacs) > c["jac_bar"])', ["regions"]),
    ("M47 consensus needs > 20 (boundary)", "    return (top[0] if top[1] >= need else None), top[1]", "    return (top[0] if top[1] > need else None), top[1]",
     ["pure"]),
    ("M48 the published region's own argmax not counted (24, not 25)", "        args.append(mine)\n", "        pass\n", ["regions", "e2e"]),
    ("M49 BH family = every region (unstable ones tested)", '    fam = [r for r in rows if r["stable"]]', "    fam = rows", ["regions"]),
    ("M50 first stable region only tested", "    for r in fam:\n        ch =", "    for r in fam[:1]:\n        ch =", ["regions", "e2e"]),
    ("M51 region bootstrap over items, not components", '        reps, D_ = CF.cell_boot(d, [comp_map[i] for i in r["idx"]], c["region_B"], rng)',
     '        reps, D_ = CF.cell_boot(d, list(range(len(r["idx"]))), c["region_B"], rng)', ["regions"]),
    ("M52 winners over every row (wrong population: TRAIN/GATE rows)", "    eval_mask = np.array([it in eval_set for it in items], dtype=bool)",
     "    eval_mask = np.ones(len(items), dtype=bool)", ["e2e"]),
    ("M53 g = the EVAL-best model, not the official TRAIN refit's pick", 'rst = regions(parts, seeds, c["k"], eval_mask, A_map, models.index(doc["best_single"]), comp_map, models)',
     'rst = regions(parts, seeds, c["k"], eval_mask, A_map, int(np.argmax(A_map.sum(axis=0))), comp_map, models)', ["unstable"]),
    ("M54 captions kept under UNSTABLE-MAP", '    st["n_caption"] = st["n_caption_rs2"] if st["stable_map"] else 0', '    st["n_caption"] = st["n_caption_rs2"]',
     ["regions", "unstable"]),
    ("M55 the published partition is (1, 0)", "    pub = (seeds[0], seeds[0])", "    pub = (seeds[1], seeds[0])", ["regions"]),
    ("M56 region argmax ignores the EVAL mask (empty region gets m0)", "    if not mask.any():\n        return None", "    if False:\n        return None",
     ["pure", "regions"]),
    # print branches / skip paths / predictions
    ("M57 WF1 NOT-SHOWN null meaning omitted", ' For the post: \\"routers realise a"', ' For the post: [omitted]"', ["branches"]),
    ("M58 UNSTABLE-MAP with no stable region: line omitted", '        L.append("RS2: under UNSTABLE-MAP no region is captioned (licensed captions 0)")',
     "        pass", ["branches"]),
    ("M59 F-WM FIRED sentence omitted", '        L.append("F-WM: FIRED: rho\'s point', '        (lambda *_: None)("F-WM: FIRED: rho\'s point', ["branches"]),
    ("M60 Brier against 1 - p", '(PRED["p_gap"] - o) ** 2', '(1 - PRED["p_gap"] - o) ** 2', ["branches"]),
    ("M61 prediction bands open at the ends", "    return band[0] <= x <= band[1]", "    return band[0] < x < band[1]", ["branches"]),
    ("M62 identity test on a computed band verdict (numpy bool)", "    held = bool(in_band(x, band))", "    held = in_band(x, band) is True", ["branches"]),
    # the release
    ("M63 correctness released for GATE / unscored rows", "        kd = E[\"K\"][it] if it in evs else (K_tr[it] if it in trk else None)",
     "        kd = E[\"K\"].get(it) or K_tr.get(it) or {m: 0 for m in models}", ["e2e"]),
    ("M64 question text leaked into the release ids", '        cols["item_id"].append(it)', '        cols["item_id"].append(it + "|" + t["text"])', ["e2e"]),
    # READY review 12f42190: the reviewer's survivors R2 / R3 / R4 / R8 and B2
    ("R2 caption without the 20-of-25 consensus", '        r["caption"] = bool(x) and r["win"] is not None', '        r["caption"] = bool(x)', ["rs2"]),
    ("R3 BH at q 0.10", '    rej = CF.bh([r["p"] for r in fam], c["q"])', '    rej = CF.bh([r["p"] for r in fam], 0.10)', ["rs2"]),
    ("R4 MMLU_PRO dropped from MC_SOURCES", 'MC_SOURCES = ("MMLU_PRO_LB", "MMLU_PRO", "GPQA", "BBH", "MUSR")\n',
     'MC_SOURCES = ("MMLU_PRO_LB", "GPQA", "BBH", "MUSR")\n', ["e2e"]),
    ("R8 F-WM decided by the upper bound", '    elif st["rho"] >= 0.25:', '    elif st["iv"]["rho"][1] >= 0.25:', ["branches"]),
    ("B2a winner exported for every region (the EVAL argmax)", '    win = {r["r"]: (models[r["win"]] if cap[r["r"]] and r["win"] is not None else None) for r in rst["rows"]}',
     '    win = {r["r"]: (models[r["own"]] if r["own"] is not None else None) for r in rst["rows"]}', ["e2e", "unstable"]),
    ("B2b winner licensed by RS2 alone (UNSTABLE-MAP ignored)", '    cap = {r["r"]: bool(r["caption"] and rst["stable_map"]) for r in rst["rows"]}',
     '    cap = {r["r"]: bool(r["caption"]) for r in rst["rows"]}', ["e2e", "unstable"]),
    ("M65 W-C MMLU refusal off", "    if mm_ev and mm_mc == 0:", "    if False:", ["refusals"]),
    ("M66 W-C MMLU count by the view label only (MMLU_PRO_LB)", '    mm_ev = [i for i in E["items"] if E["meta"][i][1] in MMLU_NAMES]',
     '    mm_ev = [i for i in E["items"] if E["meta"][i][1] == "MMLU_PRO_LB"]', ["e2e", "refusals"]),
    # the prior reviewers' decisive mutants (READY 12f42190 R1-R8; delta READY 7e2673d4 N1 / N3), carried into this table
    ("R1 undefined rho reps -> -inf", 'ratio(r - b, a - b, float("inf"))', 'ratio(r - b, a - b, float("-inf"))', ["pure", "e2e"]),
    ("R5 GPQA text in the domain column", '        cols["domain"].append(t["domain"])',
     '        cols["domain"].append(t["text"] if t["source"] == "GPQA" else t["domain"])', ["e2e"]),
    ("R6 consensus counts None", "    cnt = Counter(a for a in argmaxes if a is not None)", "    cnt = Counter(a if a is not None else 0 for a in argmaxes)",
     ["pure", "regions"]),
    ("R7 WF2 decided by the point lambda", '        w2 = "LUCK-MATERIAL" if st["iv"]["lam"][0] > 0.10 else "NOT-SHOWN"',
     '        w2 = "LUCK-MATERIAL" if st["lam"] > 0.10 else "NOT-SHOWN"', ["branches", "e2e"]),
    ("N1 W-C MC count vacuous (>= 0)", "    mm_mc = sum(1 for i in mm_ev if ch.get(i, 0.0) > 0)", "    mm_mc = sum(1 for i in mm_ev if ch.get(i, 0.0) >= 0)",
     ["refusals"]),
    ("N3 licence ignores the RS2 caption (STABLE-MAP only)", '    cap = {r["r"]: bool(r["caption"] and rst["stable_map"]) for r in rst["rows"]}',
     '    cap = {r["r"]: bool(rst["stable_map"]) for r in rst["rows"]}', ["e2e"]),
    # DELTA 2026-10-09 (D-2026-10-08-5 official scorer; D-2026-10-09-2 the ONE official refit; the H line): S01-S27
    ("S01 OVERLAY ON: the TRAIN key read with the MATH-FIX overlay (L832 back to True)",
     '            K, kst = V.read_key(tw, "response_lite", c["cv"], models, train_meta, False, c["rule"])',
     '            K, kst = V.read_key(tw, "response_lite", c["cv"], models, train_meta, True, c["rule"])', ["e2e"]),
    ("S02 OVERLAY ON: the seam forwards the caller's overlay (the pinned EVAL read reads MATH-FIX)",
     "        K, st = self.orig(tw, table, cv, models, items, self.OVERLAY, rule)",
     "        K, st = self.orig(tw, table, cv, models, items, overlay, rule)", ["e2e"]),
    ("S03 OVERLAY ON, guard off: the seam forwards the overlay AND the overlay-row refusal is removed (values must catch it)",
     ("        K, st = self.orig(tw, table, cv, models, items, self.OVERLAY, rule)", '        if st["overlay_rows"]:\n            refuse("[W-SCORER] %d MATH-FIX'),
     ("        K, st = self.orig(tw, table, cv, models, items, overlay, rule)", '        if False:\n            refuse("[W-SCORER] %d MATH-FIX'), ["e2e"]),
    ("S04 OVERLAY ON everywhere, every seam guard off (TRAIN True + forwarded + order and overlay-row checks removed)",
     ('            K, kst = V.read_key(tw, "response_lite", c["cv"], models, train_meta, False, c["rule"])',
      "        K, st = self.orig(tw, table, cv, models, items, self.OVERLAY, rule)", '        if st["overlay_rows"]:\n            refuse("[W-SCORER] %d MATH-FIX',
      "        if n >= len(want) or (table, overlay) != want[n]:"),
     ('            K, kst = V.read_key(tw, "response_lite", c["cv"], models, train_meta, True, c["rule"])',
      "        K, st = self.orig(tw, table, cv, models, items, overlay, rule)", '        if False:\n            refuse("[W-SCORER] %d MATH-FIX',
      "        if False:"), ["e2e"]),
    ("S05 the overlay-row refusal removed", '        if st["overlay_rows"]:\n            refuse("[W-SCORER] %d MATH-FIX', '        if False:\n            refuse("[W-SCORER] %d MATH-FIX',
     ["scorer", "refusals"]),
    ("S06 the read-order / flag check removed", "        if n >= len(want) or (table, overlay) != want[n]:", "        if False:", ["scorer"]),
    ("S07 the seam not installed (the pinned EVAL read keeps overlay True)", "    with Scorer(htab) as sc:", "    with contextlib.nullcontext(Scorer(htab)) as sc:",
     ["e2e"]),
    ("S08 the seam not installed AND its post-check removed", ("    with Scorer(htab) as sc:", '    if [x["table"] for x in sc.calls] != ["response_lite", "response"]'),
     ("    with contextlib.nullcontext(Scorer(htab)) as sc:", '    if False and [x["table"] for x in sc.calls] != ["response_lite", "response"]'), ["e2e"]),
    ("S09 the refit fitted with EVAL weight (wrong split side)", "    P_off = V.fit(D, V.train_full(D))", "    P_off = V.fit(D, np.ones(D.n, dtype=np.int64))",
     ["e2e"]),
    ("S10 the policy document's best single taken from the frozen MATH-FIX file", "    doc = policy_doc(D, P_off)\n",
     '    doc = dict(policy_doc(D, P_off), best_single=pol["best_single"])\n', ["deviation"]),
    ("S11 g of RS2 = the frozen MATH-FIX best single", 'models.index(doc["best_single"]), comp_map, models)', 'models.index(pol["best_single"]), comp_map, models)',
     ["deviation"]),
    ("S12 the fit-count identity off", '    if fits != bt["B"] + 2:', "    if False:", ["refusals"]),
    ("S13 plain R_AF ignores the AF-U pick (best single)", '            m = doc["tree_cell"].get(D.tree_keys[int(D.g_tree[p])]) or doc["best_single"]',
     '            m = doc["best_single"]', ["e2e"]),
    ("S14 the policy file not in the write-once check and opened 'wb'", ('pa["marker"], pa["policy"], pa["parquet"], pa["readme"]], TAG)', '    with open(pa["policy"], "xb") as fh:'),
     ('pa["marker"], pa["parquet"], pa["readme"]], TAG)', '    with open(pa["policy"], "wb") as fh:'), ["refusals"]),
    ("S15 the printed refit sha is not the written bytes' (sha of the doc without the trailing newline)", "    psha = hashlib.sha256(pbytes).hexdigest()",
     "    psha = hashlib.sha256(pbytes[:-1]).hexdigest()", ["e2e"]),
    ("S16 H pin check off", '    if sha != c["h_sha"]:\n        refuse("[W-H-PIN]', '    if False:\n        refuse("[W-H-PIN]', ["refusals"]),
    ("S17 H absent table not refused", '    if not os.path.isfile(p):\n        refuse("[W-H-PIN]', '    if False:\n        refuse("[W-H-PIN]', ["refusals"]),
    ("S18 H row-count check off", '    if len(tab) != int(c["h_rows"]):', "    if False:", ["refusals"]),
    ("S19 H join: a missing MATH row read as H 0", '                if hv is None:\n                    refuse("[W-H-JOIN] MATH row',
     '                if hv is None:\n                    hv = (0, "none")\n                if False:\n                    refuse("[W-H-JOIN] MATH row', ["refusals"]),
    ("S20 H join: the id-space check off", "                if (hv[1] == \"imported\") != (v == 1):", "                if False:", ["refusals"]),
    ("S21 H line: the policy refit under H (not the official refit)", "    CE = V.correctness_E(DH, P_off)",
     "    CE = V.correctness_E(DH, V.fit(DH, V.train_full(DH)))", ["e2e"]),
    ("S23 H line: TRAIN and EVAL H keys swapped", 'A_H = h_matrix(D, sc.calls[0]["KH"], sc.calls[1]["KH"])', 'A_H = h_matrix(D, sc.calls[1]["KH"], sc.calls[0]["KH"])',
     ["e2e"]),
    ("S24 H decides: the waterfall computed on the H matrix", "    wst = waterfall(D, bt, rec, c_all, af_e, dom_e)",
     "    D.A = h_matrix(D, sc.calls[0]['KH'], sc.calls[1]['KH'])\n    wst = waterfall(D, bt, rec, c_all, af_e, dom_e)", ["e2e"]),
    ("S25 the scorer header line omitted", "    say(scorer_line(C()))\n", "", ["e2e", "dry_run"]),
    ("S26 the deviation line omitted", '    say("%s %s" % (TAG, DEVIATION_TXT))\n', "", ["e2e", "dry_run"]),
    ("S28 H line: k_mc on EVAL (wrong split side)", "    w0[D.T] = 1\n    kE = k_for_eval(DH, w0, c_all)\n", "    w0[D.E] = 1\n    kE = k_for_eval(DH, w0, c_all)\n",
     ["e2e"]),
    ("S27 the D-5 disclosure line omitted", '    say("%s %s" % (TAG, D5_DISCLOSURE))\n', "", ["e2e"]),
)


if __name__ == "__main__":
    sys.exit(main())
