"""coverage_audit.py: COVERAGE-AUDIT -- for each union member, what share of its EVAL items is filed into cells dominated by other
members, under AF-U, K_0 (nearest of all) and declared-centroid cells, and do tree cells mix members more or less than k-means?
ZERO calls: no judge, no LLM, no embedding call (cached vectors read only), no construction, no Gradle. No key column is read.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — COVERAGE-AUDIT: for each union member, what share
  of its EVAL items is filed into cells dominated by other members, under AF-U, K_0 (nearest of all) and declared-centroid cells
  ..." L24156-L24167 (_as_of fac3d50b): CV1 (DECIDING; TOST +/-0.020), Support (a)-(g), P1-P3, F-CV.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or from anywhere with --data-root <main checkout>; never beside a
construction: --dry-run and --run are pool readers; --run also reads multicorpus_cache_v1.db and embeddings_cache.db read-only):
  0. python tools/analysis/coverage_audit.py --selftest    # synthetic sealed fixture views under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/coverage_audit.py --mutants     # the mutant table, re-run
  1. python tools/analysis/coverage_audit.py --dry-run     # POOL line first; pins; the cells and bundle; the EVAL set's
                                                           #   denominators per member (structure only); nothing filed or written
  2. python tools/analysis/coverage_audit.py --run         # outcome WRITE-ONCE: experiment_results/archv2/coverage_audit/
       coverage_audit_outcome.txt + coverage_audit_occupancy.tsv (+ coverage_audit.READ_STARTED); never committed (sha256 + E:)
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line (B0-2 pool check); write-once paths absent; pins (blob of the LF rendering of this file, union_cells_io.py,
  union_af_route.py bf3f17db, v2_declared_cells.py f0f56805); (2) the inputs manifest 53021e26... through
  union_af_route.load_inputs (every AF-U / input file re-hashed: the bundle npz, af_cells.tsv, k_cells_s0.tsv); (3) the K_0 refit
  (union_af_route.us_fit, seed 0, k per source = the manifest's ksrc, on the bundle's 12,334 TRAIN rows: the call UNION-AF-ROUTE
  made) and K0-IDENTITY: filed BY SOURCE it must reproduce k_cells_s0.tsv on every bundle item (refused on any difference);
  (4) the marker; the eval view's EVAL set, structure only (no key column; the tripwire stays sealed), REFUSED unless 5,907 / 5,404;
  (5) vectors: the bundle's for its items; the EVAL items outside the bundle (MC-EXCLUDE'd multi-class items) and the GATE items
  through rp12_pairing's readers (multicorpus_cache_v1.db texts, embeddings_cache.db vectors, read-only), with a 20-item sample
  checked against the bundle (atol 1e-9); (6) filing, dominance, X_m, D_X, the component bootstrap, CV1, F-CV, predictions,
  descriptive lines, Support; (7) the outcome and the occupancy TSV written write-once (mode "x").

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  CV-R1 Member of an EVAL item = the eval view's stratum_source (BBH, GPQA, IFEVAL, MATH, MMLU_PRO, MUSR); of a TRAIN row = the
        source of its bundle class (MMLU_PRO_LB named MMLU_PRO). Multi-class EVAL items keep the view's one stratum_source.
  CV-R2 "TRAIN rows in a cell" = the bundle's 12,334 TRAIN rows (MC-EXCLUDE'd; the K_0 fit set) filed BY THE ARM'S OWN FILING
        RULE (AF-U: af_cells.tsv, the R1 modal flatLeaf leaf over all 123 cells; K_0: nearest of ALL its centroids; declared:
        nearest of the 52 TRAIN class centroids) -- the same rule that files the EVAL items, so like with like.
  CV-R3 DOMINANT member = the member with the most such TRAIN rows; a tie goes to the member first in sorted name order; a cell
        with no TRAIN row is dominated by its construction member (the AF-U leaf's / K_0 centroid's source, the declared class's
        source). Ties and empty cells are counted and printed. The construction-member dominance is printed beside (descriptive).
  CV-R4 f_arm(i) = 1 iff member(i) != dominant(cell_arm(i)); X_m = mean of f over member m's EVAL items; X = mean over all 5,907
        (item-weighted pooled); D_X = X(AF-U) - X(K_0 nearest of all), item-paired (per item f_AF - f_K0).
  CV-R5 Component bootstrap: B = 2,000, numpy default_rng(20261004); each replicate draws the 5,404 components with replacement,
        D* = sum of drawn diffs / number of drawn items; intervals by the g13_comparator percentile rule (95%: sorted[int(.025 B)],
        sorted[int(.975 B) - 1]; 90%: sorted[int(.05 B)], sorted[int(.95 B) - 1]). DEFF (Support (b)) = Var_comp(D*) / Var_iid(D*),
        the i.i.d. replicates drawing items (default_rng(20261005)).
  CV-R6 CV1: EQUIVALENT iff -0.020 < lo90 and hi90 < +0.020 (strict: an end point at +/-0.020 is outside); DIFFERENT iff |D_X| >
        0.020 AND (lo95 > 0 or hi95 < 0), TREE-MORE-MIXED if D_X > 0 else TREE-LESS-MIXED; NEITHER otherwise. The two cannot fire
        together (EQUIVALENT implies |D_X| < 0.020). Rule 8: "EQUIVALENT REFUTED" printed iff |D_X| >= 0.020.
  CV-R7 OOS (descriptive; AF-U only): a cell's centroid = the normalised mean of its TRAIN rows' unit vectors; score = the max cosine
        over the cell centroids; threshold = sorted(GATE scores)[floor(0.05 n)] (OOS-BASELINES' rule, TPR 0.95 on GATE); an EVAL
        item is OOS iff its score < the threshold. GATE = the gen view's GATE items of the union corpus (ids only; vectors from the
        cache; an id without a vector is counted and skipped).
  CV-R8 Predictions: bands closed; CV1's three probabilities scored by the multi-outcome Brier sum_k (p_k - o_k)^2; P2's order claim
        ("highest X_m GPQA, then MATH") HELD iff GPQA is first and MATH second among the members' AF-U X_m (ties by name).
  Not applicable (stated): no judge verdict and no key enter, so no wrong(established), no tie convention A / B; no call cache,
  --pilot or truncation guard (zero calls).

SELFTEST (--selftest; fixtures under tempfile.mkdtemp(dir=E:/TaxoArena_tmp), removed afterwards): sealed synthetic eval / gen views
(v2_declared_cells._mk_view), a bundle with well-separated clusters (k-means recovers them exactly), the AF-U / K_0 cells files and
manifest, a tie cell, an empty-TRAIN cell, a multi-class EVAL item outside the bundle; the vector reader and the pool check stubbed.
  e2e        run() end to end: X_m per member and arm, X pooled, D_X, the dominance ties / empties, the declared X, the OOS threshold and
             rate, all to the printed digits against an independent plain-loop oracle; CV1's word from the printed intervals by the hand
             rule; the predictions' words and Brier; the outcome equals the printed text; the TSV rows; a second --run REFUSED
  branches   cv1() at every boundary (strict 90% ends, |D| = 0.020, 95% touching 0, both signs), F-CV / rule-8 / prediction lines
  refusals   the K0-IDENTITY refusal, the manifest pin, the EVAL denominator, a missing EVAL vector, the pool check (POOL line first),
             the write-once outcome present; no outcome written by any of them
  dry_run    POOL line first, pins, denominators per member, nothing written, no filing statistic
  branch_cover  every print branch hit
MUTANTS: see MUTANTS at the end (--mutants; the table with the result is in the commit message).
[DELTA 2026-10-04 cell-flips-coverage, READY_cell_flips_coverage D-1 / B-1 / B-4 / B-5; insertion only]
  B-4 (the registrar's ruling): the MIRRORED K_0 filing decides CV1, as UNION-AF-ROUTE C-S1: a one-cell member (the inputs
  manifest's "single": IFEVAL) has its TRAIN and EVAL rows filed BY SOURCE to its k = 1 centroid in K_0, exactly as AF-U files it to
  IFEVAL:n00000001; every other row is filed to the nearest of the remaining centroids (the one-cell centroid excluded from every
  other row's search). Arm "K_0" is the mirrored one (deciding); arm "K_0 all" is the registered nearest-of-all K_0, printed beside
  with its D_X, interval and the word its CV1 rule would give, DESCRIPTIVE; D_X without the one-cell member(s) (5,745 items on the
  real set) is printed beside for both K_0 filings, DESCRIPTIVE. X_m / dominance / occupancy carry all four arms.
  B-5: CV-R2 (dominance from TRAIN rows filed by the arm's own rule; for "K_0" the mirrored rule) and CV-R3 (ties to the sorted-first
  member, empty cell to its construction member) are kept as coded. B-1: the seeds default_rng(20261004) (component) and
  default_rng(20261005) (i.i.d.) are pinned by the e2e oracle, which redraws both streams by loops and checks the printed intervals
  and DEFF to the printed digits.
  Selftest: the fixture gains a one-cell IFEVAL member (an IFEVAL item near MATH, a MATH item near IFEVAL) so that mirrored, nearest
  of all and IFEVAL-excluded D_X all differ; the oracle computes each independently. New mutants V32-V37.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import io
import json
import argparse
import contextlib
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _pre_data_root(argv):
    """--data-root must reach TAXOARENA_DATA_ROOT BEFORE the readers import (data_v2.common / rp12_pairing read it at import;
    the B0-2 pool check's child inherits it)."""
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


if __name__ == "__main__" and _pre_data_root(sys.argv[1:]):
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_pre_data_root(sys.argv[1:]))
import union_cells_io as U      # noqa: E402

TAG = "[COVERAGE-AUDIT]"
TEST_ID = "COVERAGE-AUDIT"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — COVERAGE-AUDIT: for each union member,'
           ' what share of its EVAL items is filed into cells dominated by other members ..." L24156-L24167 (_as_of fac3d50b)')
ARMS = ("AF-U", "K_0", "K_0 all", "declared")   # "K_0" = MIRRORED (decides, B-4); "K_0 all" = registered nearest of all
RP_ = dict(B=2000, seed=20261004, seed_iid=20261005, delta=0.020, tpr=0.95, k0_seed=0, sample=20,
           out_dir="experiment_results/archv2/coverage_audit", outcome="coverage_audit_outcome.txt",
           occupancy="coverage_audit_occupancy.tsv", marker="coverage_audit.READ_STARTED")
_RP = [RP_]
SUPPORT = dict(deff=1.102, n_eff=5360, se=0.00432, disc=0.10, reach_eq=0.0093, reach_diff=0.0236)
PRED = dict(P1_d=(-0.015, 0.025), P1_prob=dict(EQUIVALENT=0.50, NEITHER=0.30, DIFFERENT=0.20), P2_x=(0.05, 0.25),
            P2_gpqa=(0.20, 0.75), P2_math=(0.10, 0.45), P3_x=(0.03, 0.18))
HIT = Counter()


def hit(name):
    HIT[name] += 1


def R():
    return _RP[0]


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def in_band(x, band):
    return band[0] <= x <= band[1]


def hw(x, band):
    return "HELD" if in_band(x, band) else "FAILED"


def unit(M):
    M = np.asarray(M, dtype=np.float64)
    n = np.linalg.norm(M, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return M / n


# ── hooks the selftest swaps (nothing else writes them) ─────────────────────────────────────────────────────────────────

def _fetch_vectors(root, ids, dim):
    """{item: unit 256-d vector} through rp12_pairing's P4 readers (multicorpus_cache_v1.db texts, embeddings_cache.db vectors;
    data_v2.ro.open_ro: mode=ro, immutable=1 after the -wal / -journal refusal). Items without a text or a vector are absent."""
    texts = U.RP.item_texts(U.P(root, U.C()["texts_db"]), None)
    have = [i for i in ids if i in texts]
    vec = U.RP.vectors(U.P(root, U.C()["emb_db"]), [texts[i] for i in have], dim)
    return {i: vec[texts[i]] for i in have if texts[i] in vec}


def _gate_items(root, say):
    """The union corpus's GATE item ids from the gen view (sha256-bytes pinned by v2_declared_cells; key never named)."""
    c = U.C()
    tw, gsha = U.V.open_tw("gen", "policy_fit", U.P(root, c["gen_rel"]), c["gen_sha"], "gen_view", say)
    try:
        gate = sorted(U.V.side_items(tw, c["cv"], "GATE"))
    finally:
        tw.close()
    U.V.after_sha(U.P(root, c["gen_rel"]), gsha, "gen_view", say)
    return gate


_TV = [_fetch_vectors]
_GATE = [_gate_items]


# ── the computation ─────────────────────────────────────────────────────────────────────────────────────────────────────

def dominance(train_cells, train_members, all_cells):
    """CV-R3: {cell: dominant member} from the TRAIN rows filed into each cell; ties to the sorted-first member; a cell with no
    TRAIN row -> its construction member. -> (dominant, n_ties, n_empty, train counts)."""
    cnt = defaultdict(Counter)
    for c, m in zip(train_cells, train_members):
        cnt[c][m] += 1
    dom, ties, empty = {}, 0, 0
    for c in sorted(set(all_cells) | set(cnt)):
        if not cnt[c]:
            dom[c] = U.cell_member(c)
            empty += 1
            continue
        top = max(cnt[c].values())
        best = sorted(m for m, n in cnt[c].items() if n == top)
        ties += int(len(best) > 1)
        dom[c] = best[0]
    return dom, ties, empty, cnt


def foreign(eval_cells, eval_members, dom):
    return np.array([int(m != dom[c]) for c, m in zip(eval_cells, eval_members)], dtype=np.int64)


def xm(fv, members):
    out = {}
    for m in sorted(set(members)):
        idx = [k for k, x in enumerate(members) if x == m]
        out[m] = (len(idx), float(np.mean(fv[idx])))
    return out


def comp_boot(diff, comp, B, rng):
    keys = sorted(set(comp))
    pos = {k: j for j, k in enumerate(keys)}
    g = np.array([pos[c] for c in comp], dtype=np.int64)
    sd = np.bincount(g, weights=diff, minlength=len(keys))
    sn = np.bincount(g, minlength=len(keys)).astype(np.float64)
    out = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, len(keys), len(keys))
        out[b] = sd[idx].sum() / sn[idx].sum()
    return out


def iid_boot(diff, B, rng):
    n = len(diff)
    out = np.empty(B)
    for b in range(B):
        out[b] = diff[rng.integers(0, n, n)].mean()
    return out


def cv1(d, lo90, hi90, lo95, hi95, delta):
    """CV-R6 -> (word, direction or None)."""
    if -delta < lo90 and hi90 < delta:
        return "EQUIVALENT", None
    if abs(d) > delta and (lo95 > 0 or hi95 < 0):
        return "DIFFERENT", ("TREE-MORE-MIXED" if d > 0 else "TREE-LESS-MIXED")
    return "NEITHER", None


def nearest(X, Cn):
    return np.argmax(X @ Cn.T, axis=1)


def oos_threshold(gate_scores, tpr):
    sg = np.sort(np.asarray(gate_scores, dtype=np.float64))
    return float(sg[int(np.floor((1 - tpr) * len(sg)))])


def interval_stats(diff, comp):
    c = R()
    bs_c = comp_boot(diff, comp, c["B"], np.random.default_rng(c["seed"]))
    bs_i = iid_boot(diff, c["B"], np.random.default_rng(c["seed_iid"]))
    s = sorted(float(x) for x in bs_c)
    vc, vi = float(np.var(bs_c, ddof=1)), float(np.var(bs_i, ddof=1))
    return dict(d=float(diff.mean()), lo95=U.pct(s, 0.025), hi95=U.pct(s, 0.975), lo90=U.pct(s, 0.05), hi90=U.pct(s, 0.95),
                se=float(np.sqrt(vc)), se_iid=float(np.sqrt(vi)), deff=(vc / vi) if vi > 0 else float("nan"))


def verdict_lines(st):
    c = R()
    D = st["D"]
    word, direc = cv1(D["d"], D["lo90"], D["hi90"], D["lo95"], D["hi95"], c["delta"])
    st["cv1"] = (word, direc)
    L = ["", "== CV1 (DECIDING; the INTERVAL decides; TOST +/-%.3f; OS1 / OL1's form) ==" % c["delta"]]
    L.append("  D_X = X(AF-U) - X(K_0 MIRRORED; B-4) = %+.5f (X(AF-U) %.5f, X(K_0) %.5f; item-paired over %d EVAL items / %d components);"
             " 95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f] (component bootstrap B %d, percentile)" % (
                 D["d"], st["X"]["AF-U"], st["X"]["K_0"], st["N"], st["G"], D["lo95"], D["hi95"], D["lo90"], D["hi90"], c["B"]))
    if word == "EQUIVALENT":
        hit("CV1.EQUIVALENT")
        L.append("CV1: EQUIVALENT: the 90%% interval [%+.5f, %+.5f] lies inside +/-%.3f" % (D["lo90"], D["hi90"], c["delta"]))
    elif word == "DIFFERENT":
        hit("CV1.DIFFERENT." + direc)
        L.append("CV1: DIFFERENT (%s): |D_X| %.5f > %.3f and the 95%% interval [%+.5f, %+.5f] excludes 0" % (
            direc, abs(D["d"]), c["delta"], D["lo95"], D["hi95"]))
    else:
        hit("CV1.NEITHER")
        L.append("CV1: NEITHER: the 90%% interval [%+.5f, %+.5f] is not inside +/-%.3f, and not (|D_X| %.5f > %.3f with the 95%%"
                 " interval excluding 0)" % (D["lo90"], D["hi90"], c["delta"], abs(D["d"]), c["delta"]))
    if abs(D["d"]) >= c["delta"]:
        hit("RULE8.REFUTED")
        L.append("  rule 8: EQUIVALENT REFUTED (|D_X| %.5f >= %.3f)" % (abs(D["d"]), c["delta"]))
    else:
        hit("RULE8.NOT_REFUTED")
        L.append("  rule 8: EQUIVALENT not refuted by the point (|D_X| %.5f < %.3f)" % (abs(D["d"]), c["delta"]))
    if word == "DIFFERENT" and direc == "TREE-MORE-MIXED":
        hit("FCV.FIRED")
        L.append("F-CV: FIRED (CV1 DIFFERENT, TREE-MORE-MIXED): the anchor-free tree files members into foreign cells more than k-means"
                 " does; for coverage audits it is the worse index")
    else:
        hit("FCV.NOT_FIRED")
        L.append("F-CV: NOT FIRED (CV1 %s)" % (word + (" " + direc if direc else "")))
    if word == "DIFFERENT" and direc == "TREE-LESS-MIXED":
        hit("FCV.LESS_MIXED_NOTE")
        L.append("  TREE-LESS-MIXED is recorded as a descriptive advantage only (never 'the tree separates benchmarks better' without"
                 " the declared reference)")
    L.append("  BESIDE (DESCRIPTIVE per B-4; decides nothing):")
    Da = st["D_all"]
    L.append("    D_X registered nearest-of-all K_0 = %+.5f (X(K_0 all) %.5f); 95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f]; its CV1 rule would read %s"
             % (Da["d"], st["X"]["K_0 all"], Da["lo95"], Da["hi95"], Da["lo90"], Da["hi90"],
                " ".join(x for x in cv1(Da["d"], Da["lo90"], Da["hi90"], Da["lo95"], Da["hi95"], c["delta"]) if x)))
    if "D_ex" in st:
        hit("BESIDE.EXCL")
        for lab, Dx in (("mirrored K_0", st["D_ex"]), ("nearest-of-all K_0", st["D_ex_all"])):
            L.append("    D_X without the one-cell member(s) %s (%d items / %d components), %s = %+.5f; 95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f]" % (
                ", ".join(st["single"]), st["n_ex"], st["G_ex"], lab, Dx["d"], Dx["lo95"], Dx["hi95"], Dx["lo90"], Dx["hi90"]))
    else:
        hit("BESIDE.NO_SINGLE")
        L.append("    D_X without one-cell members: no one-cell member (mirrored = nearest of all)")
    L.append("")
    L.append("== X_m PER MEMBER AND ARM (share of the member's EVAL items filed into a cell whose dominant TRAIN member is another) ==")
    L.append("  member        n     AF-U      K_0(mirr) K_0 all   declared")
    for m in sorted(st["Xm"]["AF-U"]):
        L.append("  %-10s %5d   %.5f   %.5f   %.5f   %.5f" % (m, st["Xm"]["AF-U"][m][0], st["Xm"]["AF-U"][m][1], st["Xm"]["K_0"][m][1],
                                                            st["Xm"]["K_0 all"][m][1], st["Xm"]["declared"][m][1]))
    L.append("  pooled     %5d   %.5f   %.5f   %.5f   %.5f" % (st["N"], st["X"]["AF-U"], st["X"]["K_0"], st["X"]["K_0 all"], st["X"]["declared"]))
    for arm in ARMS:
        a = st["dom"][arm]
        L.append("  %-8s cells %d (with EVAL items %d); dominance ties %d (to the sorted-first member); cells with no TRAIN row %d"
                 " (construction member); X under construction-member dominance (beside, descriptive) %.5f; cells with own-member"
                 " EVAL coverage < 0.50: %d" % (arm, a["n_cells"], a["n_eval_cells"], a["ties"], a["empty"], a["x_constr"], a["low_cov"]))
    if st["dom"]["AF-U"]["low_list"]:
        hit("DESC.LOW_COV_LIST")
        L.append("  AF-U cells with own-member coverage < 0.50 (cell: dominant, coverage, EVAL n): " + "; ".join(
            "%s: %s %.3f n %d" % x for x in st["dom"]["AF-U"]["low_list"]))
    else:
        hit("DESC.NO_LOW_COV")
        L.append("  AF-U cells with own-member coverage < 0.50: none")
    o = st["oos"]
    L.append("  OOS (AF-U, descriptive; validated on tree cells by OOS-TREE-CELLS on intents only): GATE %d ids, %d with a vector;"
             " threshold %.5f (GATE TPR %.4f); EVAL OOS rate %.5f; per member: %s" % (
                 o["n_gate"], o["n_gate_vec"], o["thr"], o["tpr_gate"], o["rate"], ", ".join("%s %.4f" % (m, r) for m, r in sorted(o["by_member"].items()))))
    top = [x for x in o["cells"] if x[2] >= 20][:10]
    L.append("  OOS highest (member, AF-U cell) rates, n >= 20 (all rows in the occupancy TSV): " + ("; ".join(
        "%s in %s: %.3f (n %d)" % (m, c_, r, n) for m, c_, n, r in top) or "none"))
    L.append("")
    L.append("== PREDICTIONS (registrar's priors; bands closed) ==")
    L.append("  P1 D_X +0.005 [-0.015, +0.025]: %+.5f -> %s" % (D["d"], hw(D["d"], PRED["P1_d"])))
    bri = sum((p - (1.0 if k == word else 0.0)) ** 2 for k, p in PRED["P1_prob"].items())
    L.append("  P1 CV1 EQUIVALENT 0.50, NEITHER 0.30, DIFFERENT 0.20: outcome %s -> Brier %.4f" % (word, bri))
    xa = st["Xm"]["AF-U"]
    L.append("  P2 X(AF-U) pooled 0.12 [0.05, 0.25]: %.5f -> %s" % (st["X"]["AF-U"], hw(st["X"]["AF-U"], PRED["P2_x"])))
    for m, band, txt in (("GPQA", PRED["P2_gpqa"], "0.45 [0.20, 0.75]"), ("MATH", PRED["P2_math"], "0.25 [0.10, 0.45]")):
        if m in xa:
            hit("P2.MEMBER")
            L.append("  P2 X_m(AF-U) %s %s: %.5f -> %s" % (m, txt, xa[m][1], hw(xa[m][1], band)))
        else:
            hit("P2.ABSENT")
            L.append("  P2 X_m(AF-U) %s %s: NOT SCOREABLE (no %s EVAL item)" % (m, txt, m))
    order = sorted(xa, key=lambda m: (-xa[m][1], m))
    ok = order[:2] == ["GPQA", "MATH"]
    L.append("  P2 order (highest X_m GPQA, then MATH): observed %s -> %s" % (" > ".join("%s %.4f" % (m, xa[m][1]) for m in order[:3]),
                                                                            "HELD" if ok else "FAILED"))
    L.append("  P3 X(declared-centroid) 0.08 [0.03, 0.18] (descriptive): %.5f -> %s" % (st["X"]["declared"], hw(st["X"]["declared"], PRED["P3_x"])))
    L.append("")
    L.append("== SUPPORT (registered planning numbers; MEASURED beside) ==")
    L.append("  (a) EVAL %d items / %d components; Kish mean cluster size %.4f" % (st["N"], st["G"], st["kish"]))
    L.append("  (b) DEFF measured (Var_comp / Var_iid of D*) %.3f (registered 1.102, AK1's D_AU); (c) n_eff %.0f (registered 5,360)" % (
        D["deff"], st["N"] / D["deff"] if D["deff"] > 0 else float("nan")))
    L.append("  (d) SE(D_X) measured %.5f (registered planning 0.00432); discordance (f_AF != f_K0) measured %.4f (planning 0.10)" % (
        D["se"], st["disc"]))
    L.append("  (e) TOST reach at the measured SE |D_true| < 0.020 - 2.487 SE = %.4f (registered 0.0093); DIFFERENT reach >= 0.020 +"
             " 0.842 SE = %.4f (registered 0.0236)" % (c["delta"] - 2.487 * D["se"], c["delta"] + 0.842 * D["se"]))
    L.append("  (f) VERDICT LINE (registered): the prediction (+0.005) is 0.0043 inside the TOST reach: SCOREABLE (EQUIVALENT side)."
             " (g) STRUCTURAL: reachable; IFEVAL (one cell) contributes only through foreign items filed into its cell and its own"
             " items filed out.")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (no judge verdict, no key).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): that foreign filing is an error (members overlap in content); OOS validity"
             " on capability text; real gaps in any benchmark (only the six members); anything beyond one draw.")
    return L


# ── the modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def out_paths(root, out_dir):
    d = out_dir or U.P(root, R()["out_dir"])
    return tuple(os.path.join(d, R()[k]) for k in ("outcome", "occupancy", "marker"))


def load_bundle(root):
    z = np.load(U.P(root, U.C()["bundle_rel"]), allow_pickle=False)
    classes = [str(x) for x in z["classes"]]
    return dict(Xt=unit(z["train_X"]), yt=np.asarray(z["train_y"], dtype=int), titems=[str(x) for x in z["train_item"]],
                Xe=unit(z["eval_X"]), ey=np.asarray(z["eval_y"], dtype=int), eitems=[str(x) for x in z["eval_item"]], classes=classes)


def prelude(root, out_dir, say, dry):
    U.pool_line(say, TAG)
    paths = out_paths(root, out_dir)
    if not dry:
        U.write_once_check(list(paths), TAG)
    say("%s %s (zero calls; %s) | registration %s" % (TAG, TEST_ID, "DRY-RUN" if dry else "RUN", REG_TXT))
    U.script_pins(say, TAG, [os.path.abspath(__file__), os.path.join(HERE, "union_cells_io.py"), os.path.join(HERE, "union_af_route.py"),
                             os.path.join(HERE, "v2_declared_cells.py")])
    say("%s data root %s; outputs %s (write-once; never committed)" % (TAG, root, ", ".join(paths)))
    man, af, k0 = U.load_cells(root, say, TAG)
    b = load_bundle(root)
    ksrc = {k: int(v) for k, v in man["ksrc"].items()}
    sources = [s for s in U.UA.reg()["sources"] if s in ksrc]
    if set(sources) != set(ksrc):
        refuse("the manifest's sources %s are not among the registered %s" % (sorted(ksrc), list(U.UA.reg()["sources"])))
    say("%s bundle: TRAIN %d rows, EVAL %d rows (MC-EXCLUDE'd), %d classes, dim %d; K_0 k per source %s (total %d)" % (
        TAG, len(b["titems"]), len(b["eitems"]), len(b["classes"]), b["Xt"].shape[1], ", ".join("%s %d" % (s, ksrc[s]) for s in sources),
        sum(ksrc.values())))
    return man, af, k0, b, ksrc, sources, paths


def dry_run(root, out_dir=None, out=print):
    _man, _af, _k0, b, _ks, _so, _p = prelude(root, out_dir, out, True)
    E = U.eval_set(root, out, TAG, key=False)
    mem = Counter(E["meta"][i][1] for i in E["items"])
    inb = set(b["eitems"])
    out("%s DENOMINATORS per member (EVAL set): %s; EVAL items outside the bundle (vectors from the cache at --run): %d" % (
        TAG, ", ".join("%s %d" % kv for kv in sorted(mem.items())), sum(1 for i in E["items"] if i not in inb)))
    out("%s PLANNED: K_0 refit seed %d + K0-IDENTITY; B = %d component replicates (default_rng(%d)), i.i.d. (default_rng(%d));"
        " TOST +/-%.3f; OOS threshold at GATE TPR %.2f" % (TAG, R()["k0_seed"], R()["B"], R()["seed"], R()["seed_iid"], R()["delta"], R()["tpr"]))
    out("%s DRY-RUN complete: no filing statistic; no key column; nothing written" % TAG)
    hit("DRY.DONE")


def write_outcome(path, text):
    """Mode "x" (v2_reader_guards.write_once): an existing path is REFUSED and left unchanged."""
    return U.G.write_once(path, text)


def run(root, out_dir=None, out=print):
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    c = R()
    man, af, k0, b, ksrc, sources, (outp, occp, mark) = prelude(root, out_dir, say, False)
    classes, Xt, yt = b["classes"], b["Xt"], b["yt"]
    tsrc_raw = np.array([classes[j].split("/", 1)[0] for j in yt])
    tmem = [U.member(s) for s in tsrc_raw]
    # K_0 refit (the UNION-AF-ROUTE call) and K0-IDENTITY (filed by source == k_cells_s0.tsv on every bundle item)
    Ck, csrc, cloc, _lab, _f = U.UA.us_fit(Xt, tsrc_raw, ksrc, sources, c["k0_seed"])
    kname = np.array(["K%d:%s:%03d" % (c["k0_seed"], s, j) for s, j in zip(csrc, cloc)])
    esrc = np.array([classes[j].split("/", 1)[0] for j in b["ey"]])
    bad = []
    for items_b, Xb, sb in ((b["titems"], Xt, tsrc_raw), (b["eitems"], b["Xe"], esrc)):
        S = np.where(csrc[None, :] == sb[:, None], Xb @ Ck.T, -np.inf)       # by source (UNION-AF-ROUTE R3)
        for it, g_ in zip(items_b, np.argmax(S, axis=1)):
            if kname[g_] != k0.get(it):
                bad.append(it)
    n_id = len(b["titems"]) + len(b["eitems"])
    say("%s K0-IDENTITY: the seed-%d refit, filed by source, reproduces k_cells_s0.tsv on %d of %d bundle items (TRAIN %d + EVAL %d)" % (
        TAG, c["k0_seed"], n_id - len(bad), n_id, len(b["titems"]), len(b["eitems"])))
    if bad:
        refuse("K0-IDENTITY: %d bundle item(s) differ from k_cells_s0.tsv (first %s)" % (len(bad), bad[:3]))
    # EVAL set (structure only) after the marker
    U.G.read_marker(mark, "%s: the EVAL set read started (structure + cached vectors; no key)" % TAG)
    E = U.eval_set(root, say, TAG, key=False)
    items = E["items"]
    emem = [E["meta"][i][1] for i in items]
    comp = [E["meta"][i][0] for i in items]
    pos_b = {it: k for k, it in enumerate(b["eitems"])}
    miss = [i for i in items if i not in pos_b]
    gate = _GATE[0](root, say)
    sample = [b["eitems"][k] for k in range(0, len(b["eitems"]), max(1, len(b["eitems"]) // c["sample"]))][:c["sample"]]
    vec = _TV[0](root, sorted(set(miss) | set(gate) | set(sample)), Xt.shape[1])
    off = [i for i in sample if i not in vec or not np.allclose(vec[i], b["Xe"][pos_b[i]], atol=1e-9)]
    say("%s vectors: %d EVAL items from the bundle, %d EVAL items outside it from the cache; sample check %d of %d bundle items equal"
        " (atol 1e-9)" % (TAG, len(items) - len(miss), len(miss), len(sample) - len(off), len(sample)))
    if off:
        refuse("the cache's vectors differ from the bundle's on %d sample item(s) (first %s)" % (len(off), off[:3]))
    nov = [i for i in miss if i not in vec]
    if nov:
        refuse("%d EVAL item(s) of the set have no cached vector (first %s)" % (len(nov), nov[:3]))
    Xe = np.array([b["Xe"][pos_b[i]] if i in pos_b else vec[i] for i in items])
    # filing per arm (EVAL and TRAIN by the same rule)
    Cd = unit(np.array([Xt[yt == j].mean(axis=0) if (yt == j).any() else np.zeros(Xt.shape[1]) for j in range(len(classes))]))
    have = np.array([(yt == j).any() for j in range(len(classes))])      # a class without TRAIN rows has no centroid
    single = sorted(U.member(s_) for s_ in man.get("single", {}))
    cmem = np.array([U.member(s_) for s_ in csrc])
    one = np.isin(cmem, single)
    say("%s ONE-CELL members (inputs manifest 'single'): %s; K_0 MIRRORED decides CV1 (registrar's B-4, the UNION-AF-ROUTE C-S1"
        " precedent): a one-cell member's TRAIN / EVAL rows filed by source to its k = 1 centroid, every other row to the nearest of"
        " the %d other centroids; the registered nearest-of-all K_0 (\"K_0 all\") is printed beside, DESCRIPTIVE" % (
            TAG, ", ".join(single) or "none (mirrored = nearest of all)", int((~one).sum())))

    def mirrored(X, mem):
        g = np.argmax(np.where(one[None, :], -np.inf, X @ Ck.T), axis=1)
        for k, m in enumerate(mem):
            if m in single:
                idx = np.flatnonzero(cmem == m)
                if len(idx) != 1:
                    refuse("one-cell member %s has %d K_0 centroids (must be exactly 1)" % (m, len(idx)))
                g[k] = idx[0]
        return list(kname[g])
    cells = {"AF-U": ([af.get(i) for i in items], [af.get(i) for i in b["titems"]]),
             "K_0": (mirrored(Xe, emem), mirrored(Xt, tmem)),
             "K_0 all": (list(kname[nearest(Xe, Ck)]), list(kname[nearest(Xt, Ck)])),
             "declared": ([classes[j] for j in np.argmax(np.where(have[None, :], Xe @ Cd.T, -np.inf), axis=1)],
                          [classes[j] for j in np.argmax(np.where(have[None, :], Xt @ Cd.T, -np.inf), axis=1)])}
    for arm in ARMS:
        nb = [i for i, x in zip(items, cells[arm][0]) if x is None or x in (U.UA.NO_ROW, U.UA.UNROUTED)]
        if nb:
            refuse("arm %s: %d EVAL item(s) carry no cell (first %s)" % (arm, len(nb), nb[:3]))
    st = dict(N=len(items), G=len(set(comp)), kish=U.kish(Counter(comp).values()), X={}, Xm={}, dom={}, f={})
    occ = []
    for arm in ARMS:
        ecl, tcl = cells[arm]
        tpairs = [(cc, m) for cc, m in zip(tcl, tmem) if cc is not None]
        dom, ties, empty, cnt = dominance([p[0] for p in tpairs], [p[1] for p in tpairs], ecl)
        fv = foreign(ecl, emem, dom)
        st["f"][arm] = fv
        st["X"][arm] = float(fv.mean())
        st["Xm"][arm] = xm(fv, emem)
        constr = foreign(ecl, emem, {cc: U.cell_member(cc) for cc in dom})
        ev_by = defaultdict(Counter)
        for cc, m in zip(ecl, emem):
            ev_by[cc][m] += 1
        low = []
        for cc in sorted(ev_by):
            n_ = sum(ev_by[cc].values())
            cov = ev_by[cc][dom[cc]] / n_
            if cov < 0.50:
                low.append((cc, dom[cc], cov, n_))
            occ.append((arm, cc, U.cell_member(cc), dom[cc], sum(cnt[cc].values()), n_,
                        ",".join("%s:%d" % kv for kv in sorted(ev_by[cc].items())), "%.4f" % cov))
        st["dom"][arm] = dict(n_cells=len(dom), n_eval_cells=len(ev_by), ties=ties, empty=empty, x_constr=float(constr.mean()),
                              low_cov=len(low), low_list=low)
    diff = (st["f"]["AF-U"] - st["f"]["K_0"]).astype(np.float64)
    st["D"] = interval_stats(diff, comp)
    st["disc"] = float(np.mean(diff != 0))
    st["single"] = single
    st["D_all"] = interval_stats((st["f"]["AF-U"] - st["f"]["K_0 all"]).astype(np.float64), comp)
    keep = np.array([m not in single for m in emem], dtype=bool)
    st["n_ex"], st["G_ex"] = int(keep.sum()), len(set(np.asarray(comp, dtype=object)[keep].tolist()))
    if single and keep.any():
        ck = list(np.asarray(comp, dtype=object)[keep])
        st["D_ex"] = interval_stats(diff[keep], ck)
        st["D_ex_all"] = interval_stats((st["f"]["AF-U"] - st["f"]["K_0 all"]).astype(np.float64)[keep], ck)
    # OOS (AF-U, descriptive)
    tc = [cc for cc in cells["AF-U"][1]]
    cl = sorted(set(x for x in tc if x not in (None, U.UA.NO_ROW, U.UA.UNROUTED)))
    cpos = {x: j for j, x in enumerate(cl)}
    Ca = np.zeros((len(cl), Xt.shape[1]))
    for k, x in enumerate(tc):
        if x in cpos:
            Ca[cpos[x]] += Xt[k]
    Ca = unit(Ca)
    gv = [g for g in gate if g in vec]
    gs = (np.array([vec[g] for g in gv]) @ Ca.T).max(axis=1) if gv else np.array([])
    if len(gs):
        hit("OOS.GATE")
        thr = oos_threshold(gs, c["tpr"])
        tpr_g = float(np.mean(gs >= thr))
    else:
        hit("OOS.NO_GATE")
        thr, tpr_g = float("nan"), float("nan")
    es = (Xe @ Ca.T).max(axis=1)
    isoos = (es < thr).astype(np.float64)
    by_m = {m: float(np.mean(isoos[[k for k, x in enumerate(emem) if x == m]])) for m in sorted(set(emem))}
    mc = defaultdict(list)
    for k, (m, cc) in enumerate(zip(emem, cells["AF-U"][0])):
        mc[(m, cc)].append(isoos[k])
    mcl = sorted(((m, cc, len(v), float(np.mean(v))) for (m, cc), v in mc.items()), key=lambda x: (-x[3], -x[2], x[0], x[1]))
    st["oos"] = dict(n_gate=len(gate), n_gate_vec=len(gv), thr=thr, tpr_gate=tpr_g, rate=float(isoos.mean()), by_member=by_m, cells=mcl)
    for l in verdict_lines(st):
        say(l)
    tsv = ["# %s occupancy (descriptive; never committed): kind=cell rows per arm, kind=member_cell rows (AF-U OOS)" % TEST_ID,
           "kind\tarm\tcell\tconstruction_member\tdominant_train\tn_train\tn_eval\teval_by_member\town_coverage\toos_rate"]
    for r in occ:
        tsv.append("cell\t" + "\t".join(str(x) for x in r) + "\t-")
    for m, cc, n_, r in sorted(mcl, key=lambda x: (x[1], x[0])):
        tsv.append("member_cell\tAF-U\t%s\t%s\t-\t-\t%d\t%s\t-\t%.4f" % (cc, U.cell_member(cc), n_, m, r))
    text = "\n".join(lines) + "\n"
    write_outcome(occp, "\n".join(tsv) + "\n")
    write_outcome(outp, text)
    out("%s OUTCOME written write-once: %s, %s" % (TAG, outp, occp))
    hit("RUN.DONE")
    return st, text


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
TMP_BASE = "E:/TaxoArena_tmp"
NL = chr(10)
FX_DIM = 8
FX_MODELS = ["m0", "m1", "m2"]
# classes: (class name, centre axis)
FX_CLASSES = [("BBH/a", 0), ("BBH/b", 1), ("GPQA/phys", 5), ("MATH/x", 2), ("MMLU_PRO_LB/bio", 4), ("MMLU_PRO_LB/math", 3),
              ("IFEVAL/ifeval", 6)]
FX_KSRC = {"BBH": 2, "GPQA": 1, "MATH": 1, "MMLU_PRO_LB": 1, "IFEVAL": 1}     # K_0 merges the two MMLU classes: K_0 != declared
# EVAL design: (member (view naming), class-axis to sit near, AF-U cell, count, multi-class outside the bundle)
FX_EVAL = [("BBH", 0, "BBH:n00000001", 12, False), ("BBH", 1, "BBH:n00000002", 10, False), ("BBH", 1, "BBH:n00000007", 3, False),
           ("MATH", 2, "MATH:n00000003", 8, False), ("MATH", 3, "MATH:n00000003", 5, False),        # near MMLU math: K_0 files foreign
           ("MATH", 3, "BBH:n00000007", 2, False),                                                  # into the tie cell (BBH wins)
           ("MMLU_PRO", 3, "MMLU_PRO_LB:n00000004", 10, False), ("MMLU_PRO", 4, "MMLU_PRO_LB:n00000005", 9, False),
           ("GPQA", 5, "GPQA:n00000006", 3, False), ("GPQA", 4, "MMLU_PRO_LB:n00000005", 4, False),  # GPQA near MMLU bio: foreign
           ("GPQA", 5, "GPQA:n00000008", 2, False),                                                  # the empty-TRAIN AF cell
           ("MATH", {2: 1.0, 3: 1.1}, "MATH:n00000003", 4, False),   # declared: MMLU math (foreign); K_0: MATH (own)
           ("MMLU_PRO", 5, "GPQA:n00000006", 4, False),               # own-member coverage of GPQA:n6 3 / 7 < 0.50
           ("BBH", 7, "BBH:n00000001", 2, False),                     # far from every cell: OOS
           ("MATH", 2, "BBH:n00000009", 2, False),                    # TRAIN-dominant MATH, constructed by BBH
           ("IFEVAL", 6, "IFEVAL:n00000001", 6, False),               # the one-cell member, filed by source in AF-U
           ("IFEVAL", 2, "IFEVAL:n00000001", 3, False),               # near MATH: nearest-of-all K_0 foreign, mirrored own
           ("MATH", 6, "MATH:n00000003", 2, False),                   # near IFEVAL: nearest-of-all K_0 into IFEVAL's cell
           ("MATH", 2, "MATH:n00000003", 1, True)]                                                   # outside the bundle
# TRAIN design per class: (AF-U cell, count) -- includes MATH rows in the MMLU math cell and the BBH/MATH tie cell
FX_TRAIN = {"BBH/a": [("BBH:n00000001", 20)], "BBH/b": [("BBH:n00000002", 17), ("BBH:n00000007", 3)],
            "GPQA/phys": [("GPQA:n00000006", 12)],
            "MATH/x": [("MATH:n00000003", 15), ("MMLU_PRO_LB:n00000004", 2), ("BBH:n00000007", 3), ("BBH:n00000009", 4)],
            "MMLU_PRO_LB/bio": [("MMLU_PRO_LB:n00000005", 18)], "MMLU_PRO_LB/math": [("MMLU_PRO_LB:n00000004", 18)],
            "IFEVAL/ifeval": [("IFEVAL:n00000001", 10)]}
FX_SINGLE = {"IFEVAL": {"cell": "IFEVAL:n00000001", "source": "IFEVAL", "member": "ifeval"}}


def _fx_vec(rs, axis, scale=0.05):
    v = np.zeros(FX_DIM)
    for a, w in (axis.items() if isinstance(axis, dict) else ((axis, 1.0),)):
        v[a] = w
    v = v + rs.normal(0, scale, FX_DIM)
    return v / np.linalg.norm(v)


def _fixture(tmp, variant="main"):
    V = U.V
    rs = np.random.RandomState(7)
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    nid = [0]

    def new(prefix):
        nid[0] += 1
        return "i:%s%05d" % (prefix, nid[0])
    tr_items, tr_X, tr_y, af, k0 = [], [], [], {}, {}
    cname = [c for c, _a in FX_CLASSES]
    for ci, (cls, ax) in enumerate(FX_CLASSES):
        for cell, n in FX_TRAIN[cls]:
            for _ in range(n):
                it = new("t")
                tr_items.append(it)
                tr_X.append(_fx_vec(rs, ax))
                tr_y.append(ci)
                af[it] = cell
    for _ in range(13):
        it = new("t")
        tr_items.append(it)
        tr_X.append(_fx_vec(rs, 5))
        tr_y.append(cname.index("MATH/x"))
        af[it] = "MATH:n00000003"
    for _ in range(12):               # MATH rows near IFEVAL: nearest of all files them into K0:IFEVAL (MATH 12 > IFEVAL 10); mirrored not
        it = new("t")
        tr_items.append(it)
        tr_X.append(_fx_vec(rs, 6))
        tr_y.append(cname.index("MATH/x"))
        af[it] = "MATH:n00000003"
    tr_X = np.array(tr_X)
    ev, ev_items, ev_X, ev_y, truth, items_view, responses = [], [], [], [], {}, [], []
    axis_class = {ax: ci for ci, (_c, ax) in enumerate(FX_CLASSES)}
    for mem, ax, cell, n, outside in FX_EVAL:
        for j in range(n):
            it = new("e")
            x = _fx_vec(rs, ax)
            comp = "c:%s" % (it if j % 4 != 1 else ev[-1][0]) if ev else "c:%s" % it
            src_lb = {"MMLU_PRO": "MMLU_PRO_LB"}.get(mem, mem)
            cls_i = [ci for ci, (c, _a) in enumerate(FX_CLASSES) if c.startswith(src_lb + "/")]
            yc = axis_class[ax] if (not isinstance(ax, dict) and axis_class.get(ax) in cls_i) else cls_i[0]
            ev.append((it, comp, mem, cname[yc].split("/")[1], x, cell, outside))
            af[it] = cell
            truth[it] = x
            if not outside:
                ev_items.append(it)
                ev_X.append(x)
                ev_y.append(yc)
    # K_0 cells file = by-source filing of the per-source cluster centroids (plain loops; the clusters are exact)
    cents = {}
    for ci, (cls, ax) in enumerate(FX_CLASSES):
        src = cls.split("/")[0]
        cents.setdefault(src, []).append((ax, U.UA.FM.unit_rows(tr_X[np.array(tr_y) == ci].mean(axis=0, keepdims=True))[0]))
    fit_order = {}
    for src in cents:      # the k-means label order is the fit's; map it by refitting exactly as the reader does
        m = np.array([cname[y].split("/")[0] == src for y in tr_y])
        fit, _t = U.GB.ukm_fit(U.UA.FM.unit_rows(tr_X[m]), FX_KSRC[src], 0)
        fit_order[src] = fit["centers"]
    for items_, X_, ys in ((tr_items, tr_X, [cname[y].split("/")[0] for y in tr_y]),
                           (ev_items, np.array(ev_X), [cname[y].split("/")[0] for y in ev_y])):
        for it, x, s in zip(items_, U.UA.FM.unit_rows(np.asarray(X_)), ys):
            k0[it] = "K0:%s:%03d" % (s, int(np.argmax(fit_order[s] @ x)))
    for e in ev:
        if e[6]:
            k0[e[0]] = "K0:MATH:000"
    if variant == "k0_bad":
        k0[tr_items[0]] = "K0:BBH:001" if k0[tr_items[0]] != "K0:BBH:001" else "K0:BBH:000"
    # GATE items (vectors via the stub)
    gate = []
    for j in range(40):
        it = new("g")
        gate.append(it)
        truth[it] = _fx_vec(rs, 7 if j % 20 == 0 else j % 6, scale=0.15)     # 2 of 40 far from every cell (axis 7)
    # views
    for e in ev:
        items_view.append(dict(id=e[0], comp=e[1], side="EVAL", src=e[2], dom=e[3], cvs=["fx"]))
        for m in FX_MODELS:
            responses.append(dict(cv="fx", model=m, item=e[0], side="EVAL", src=e[2], c=1, mf=None))
    for g in gate:
        items_view.append(dict(id=g, comp="c:" + g, side="GATE", src="BBH", dom="a", cvs=["fx"]))
    for it in tr_items[:5]:
        items_view.append(dict(id=it, comp="c:" + it, side="TRAIN", src="BBH", dom="a", cvs=["fx"]))
    n_ev = len(ev)
    comps = sorted(set(e[1] for e in ev))
    spec = dict(items=items_view, responses=responses, registry=[("fx", m, "ACTIVE") for m in FX_MODELS],
                pools=[("pv_fx", "fx", len(comps), json.dumps({"fx": n_ev}))])
    os.makedirs(os.path.join(root, "data_v2"))
    esha = V._mk_view(os.path.join(root, "data_v2", "eval_fx.db"), "eval", ("EVAL",), spec)
    gsha = V._mk_view(os.path.join(root, "data_v2", "gen_fx.db"), "gen", ("TRAIN", "GATE"), spec)
    inp = U.P(root, U.UA.RES + "/inputs")
    os.makedirs(inp)
    np.savez(U.P(root, U.CONST["bundle_rel"]), train_X=tr_X, train_y=np.array(tr_y, dtype=np.int32), train_item=np.array(tr_items),
             eval_X=np.array(ev_X), eval_y=np.array(ev_y, dtype=np.int32), eval_item=np.array(ev_items), classes=np.array(cname))
    shas = {U.CONST["bundle_rel"]: U.sha256_bytes(U.P(root, U.CONST["bundle_rel"]))}
    for rel, cells in ((U.CONST["af_rel"], af), (U.CONST["k0_rel"], k0)):
        with open(U.P(root, rel), "w", encoding="utf-8", newline=NL) as fh:
            fh.write(U.UA.cells_text(cells, "fixture"))
        shas[rel] = U.UA.sha256_lf(U.P(root, rel))
    mp = U.P(root, U.UA.RES + "/inputs/inputs_manifest.json")
    with open(mp, "w", encoding="utf-8", newline=NL) as fh:
        fh.write(json.dumps(dict(afu_files={}, inputs=shas, ksrc=FX_KSRC, single=FX_SINGLE), indent=1, sort_keys=True) + NL)
    const = dict(U.CONST, pool="pv_fx", cv="fx", n_eval=n_ev, comp_eval=len(comps), pool_items=n_ev, pool_comp=len(comps),
                 roster=len(FX_MODELS), eval_rel="data_v2/eval_fx.db", eval_sha=esha, gen_rel="data_v2/gen_fx.db", gen_sha=gsha,
                 manifest_sha=U.UA.sha256_lf(mp))
    return root, dict(const=const, ev=ev, tr_items=tr_items, tr_X=tr_X, tr_y=tr_y, af=af, k0=k0, truth=truth, gate=gate, cname=cname)


@contextlib.contextmanager
def _patched(X, pool=(0, "SELFTEST stub: pool check not run"), drop=(), perturb=()):
    old = (U._C[0], U._POOL[0], U.UA._ROOT[0], _TV[0], U.UA._REG[0])
    U._C[0] = X["const"]
    U._POOL[0] = lambda _pool: pool
    _TV[0] = lambda root, ids, dim: {i: X["truth"][i] + (0.1 if i in perturb else 0.0) for i in ids if i in X["truth"] and i not in drop}
    U.UA._REG[0] = dict(U.UA.REG, sources=("MMLU_PRO_LB", "BBH", "MATH", "IFEVAL", "GPQA"))
    try:
        yield
    finally:
        U._C[0], U._POOL[0], U.UA._ROOT[0], _TV[0], U.UA._REG[0] = old


def _capture(fn, *a, **k):
    buf = []
    res = fn(*a, out=buf.append, **k)
    return res, NL.join(buf)


def _need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def _oracle(X):
    """INDEPENDENT plain-loop X_m / X / D_X / dominance / OOS on the fixture (cluster centroids by loops; no reader function)."""
    def nrm(v):
        s = sum(a * a for a in v) ** 0.5
        return [a / s for a in v]

    def dot(a, b):
        return sum(p * q for p, q in zip(a, b))
    cname = X["cname"]

    def cm(c_):                       # the construction member, parsed by hand (not U.cell_member)
        s_ = c_.split(":")[1] if c_.startswith("K0:") else c_.split("/")[0].split(":")[0]
        return "MMLU_PRO" if s_ == "MMLU_PRO_LB" else s_
    trm = [{"MMLU_PRO_LB": "MMLU_PRO"}.get(cname[y].split("/")[0], cname[y].split("/")[0]) for y in X["tr_y"]]
    trv = [nrm(list(v)) for v in X["tr_X"]]
    # class / cluster centroids (the K_0 clusters are the classes; names from the K_0 file of a TRAIN row of the class)
    cc = {}
    for ci in range(len(cname)):
        rows = [trv[k] for k in range(len(trv)) if X["tr_y"][k] == ci]
        cc[ci] = nrm([sum(r[d] for r in rows) for d in range(FX_DIM)])
    kc = {}
    for k, t in enumerate(X["tr_items"]):
        kc.setdefault(X["k0"][t], []).append(trv[k])
    kcen = {n_: nrm([sum(r[d] for r in rows) for d in range(FX_DIM)]) for n_, rows in kc.items()}

    def near(v):
        return max(cc, key=lambda ci: dot(v, cc[ci]))

    def knear(v):
        return max(sorted(kcen), key=lambda n_: dot(v, kcen[n_]))

    def kmirr(v, m):                  # B-4 / C-S1: a one-cell member by source; every other row among the other centroids
        if m in single:
            return [n_ for n_ in kcen if cm(n_) == m][0]
        return max(sorted(n_ for n_ in kcen if cm(n_) not in single), key=lambda n_: dot(v, kcen[n_]))
    single = {"IFEVAL"}
    ev = X["ev"]
    emem = [e[2] for e in ev]
    arms = {"AF-U": ([e[5] for e in ev], [X["af"][t] for t in X["tr_items"]]),
            "K_0": ([kmirr(nrm(list(e[4])), e[2]) for e in ev], [kmirr(v, m) for v, m in zip(trv, trm)]),
            "K_0 all": ([knear(nrm(list(e[4]))) for e in ev], [knear(v) for v in trv]),
            "declared": ([cname[near(nrm(list(e[4])))] for e in ev], [cname[near(v)] for v in trv])}
    out = {}
    for arm, (ecl, tcl) in arms.items():
        cnt = defaultdict(Counter)
        for c_, m in zip(tcl, trm):
            cnt[c_][m] += 1
        dom = {}
        for c_ in set(ecl) | set(cnt):
            if cnt[c_]:
                top = max(cnt[c_].values())
                dom[c_] = sorted(m for m, n in cnt[c_].items() if n == top)[0]
            else:
                dom[c_] = cm(c_)
        f_ = [int(m != dom[c_]) for c_, m in zip(ecl, emem)]
        xm_ = {m: sum(f_[k] for k in range(len(f_)) if emem[k] == m) / emem.count(m) for m in set(emem)}
        fc = [int(m != cm(c_)) for c_, m in zip(ecl, emem)]
        out[arm] = dict(f=f_, X=sum(f_) / len(f_), Xm=xm_, Xc=sum(fc) / len(fc))
    out["D"] = out["AF-U"]["X"] - out["K_0"]["X"]
    out["D_all"] = out["AF-U"]["X"] - out["K_0 all"]["X"]

    def boot(other, sel):
        """CV-R5 by loops with the PINNED seeds: component default_rng(20261004), one integers(0, G, G) per replicate over the
        sorted components; i.i.d. default_rng(20261005), one integers(0, n, n) per replicate -> (point, ci, DEFF)."""
        idx = [k for k in range(len(ev)) if sel(k)]
        comps = sorted(set(ev[k][1] for k in idx))
        by = {c_: [k for k in idx if ev[k][1] == c_] for c_ in comps}
        dif = {k: out["AF-U"]["f"][k] - out[other]["f"][k] for k in idx}
        rng = np.random.default_rng(20261004)
        reps = []
        for _b in range(2000):
            num = den = 0
            for j in rng.integers(0, len(comps), len(comps)):
                num += sum(dif[k] for k in by[comps[j]])
                den += len(by[comps[j]])
            reps.append(num / den)
        rng2 = np.random.default_rng(20261005)
        dl = [dif[k] for k in idx]
        ri = [sum(dl[j] for j in rng2.integers(0, len(dl), len(dl))) / len(dl) for _b in range(2000)]
        deff = float(np.var(reps, ddof=1) / np.var(ri, ddof=1))
        point = sum(dl) / len(dl)
        reps.sort()
        return point, (reps[50], reps[1949], reps[100], reps[1899]), deff
    _p, out["ci"], out["deff"] = boot("K_0", lambda k: True)
    out["ex"] = boot("K_0", lambda k: emem[k] not in single)
    out["ex_all"] = boot("K_0 all", lambda k: emem[k] not in single)
    out["all"] = boot("K_0 all", lambda k: True)
    out["n_ex"] = sum(1 for m in emem if m not in single)
    # OOS
    cells = sorted(set(X["af"][t] for t in X["tr_items"]))
    cen = {c_: nrm([sum(trv[k][d] for k in range(len(trv)) if X["af"][X["tr_items"][k]] == c_) for d in range(FX_DIM)]) for c_ in cells}
    gs = sorted(max(dot(nrm(list(X["truth"][g])), cen[c_]) for c_ in cells) for g in X["gate"])
    thr = gs[int((1 - 0.95) * len(gs) // 1)]
    es = [max(dot(nrm(list(e[4])), cen[c_]) for c_ in cells) for e in ev]
    out["thr"], out["oos"] = thr, sum(1 for s in es if s < thr) / len(es)
    return out


def st_e2e(tmp):
    root, X = _fixture(tmp)
    od = os.path.join(tmp, "out")
    with _patched(X):
        (st, text), printed = _capture(run, root, od)
        assert printed.split(NL)[0].startswith(TAG + " POOL pv_fx"), "POOL line first"
        assert open(os.path.join(od, R()["outcome"]), encoding="utf-8").read() == text
        O = _oracle(X)
        for m in sorted(O["AF-U"]["Xm"]):
            n = sum(1 for e in X["ev"] if e[2] == m)
            _need(text, "  %-10s %5d   %.5f   %.5f   %.5f   %.5f" % (m, n, O["AF-U"]["Xm"][m], O["K_0"]["Xm"][m], O["K_0 all"]["Xm"][m],
                                                                 O["declared"]["Xm"][m]))
        _need(text, "  pooled     %5d   %.5f   %.5f   %.5f   %.5f" % (len(X["ev"]), O["AF-U"]["X"], O["K_0"]["X"], O["K_0 all"]["X"], O["declared"]["X"]))
        _need(text, "D_X = X(AF-U) - X(K_0 MIRRORED; B-4) = %+.5f" % O["D"])
        assert O["D"] != O["D_all"] and O["K_0"]["Xm"]["IFEVAL"] != O["K_0 all"]["Xm"]["IFEVAL"], "mirrored != nearest of all"
        assert O["ex"][0] != O["D"], "the IFEVAL-excluded D_X must differ"
        _need(text, "    D_X registered nearest-of-all K_0 = %+.5f (X(K_0 all) %.5f); 95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f]" % (
            (O["D_all"], O["K_0 all"]["X"]) + O["all"][1]))
        ne = O["n_ex"]
        for lab, key in (("mirrored K_0", "ex"), ("nearest-of-all K_0", "ex_all")):
            _need(text, "without the one-cell member(s) IFEVAL (%d items / " % ne)
            _need(text, ", %s = %+.5f; 95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f]" % ((lab, O[key][0]) + O[key][1]))
        _need(text, "(b) DEFF measured (Var_comp / Var_iid of D*) %.3f" % O["deff"])
        assert R()["seed"] == 20261004 and R()["seed_iid"] == 20261005, "B-1: the bootstrap seeds of record"
        assert O["D"] != 0 and O["AF-U"]["X"] > 0 and O["K_0"]["X"] > 0, "the fixture must discriminate"
        assert O["K_0"]["X"] != O["declared"]["X"] and O["K_0"]["Xm"]["MATH"] != O["declared"]["Xm"]["MATH"], "K_0 != declared"
        _need(text, "AF-U     cells 10 (with EVAL items 10); dominance ties 1 (to the sorted-first member); cells with no TRAIN row 1"
                    " (construction member); X under construction-member dominance (beside, descriptive) %.5f" % O["AF-U"]["Xc"])
        assert O["AF-U"]["Xc"] != O["AF-U"]["X"], "construction vs TRAIN dominance must differ on the fixture"
        _need(text, "K_0      cells 6 (with EVAL items 6); dominance ties 0 (to the sorted-first member); cells with no TRAIN row 0"
                    " (construction member); X under construction-member dominance (beside, descriptive) %.5f" % O["K_0"]["Xc"])
        _need(text, "AF-U cells with own-member coverage < 0.50 (cell: dominant, coverage, EVAL n): GPQA:n00000006: GPQA 0.429 n 7")
        _need(text, "95%% [%+.5f, %+.5f], 90%% [%+.5f, %+.5f] (component bootstrap B 2000" % O["ci"])
        mk = os.path.join(od, R()["marker"])
        assert os.path.isfile(mk), "the marker is written"
        _need(text, "threshold %.5f" % O["thr"], "EVAL OOS rate %.5f" % O["oos"])
        assert 0 < O["oos"] < 1, "the OOS fixture must discriminate"
        _need(text, "K0-IDENTITY: the seed-0 refit, filed by source, reproduces k_cells_s0.tsv on %d of %d" % (
            len(X["tr_items"]) + sum(1 for e in X["ev"] if not e[6]), len(X["tr_items"]) + sum(1 for e in X["ev"] if not e[6])))
        _need(text, "EVAL items outside it from the cache" if False else "1 EVAL items outside it from the cache")
        # CV1's word from the PRINTED intervals by the hand rule
        ln = [l_ for l_ in text.split(NL) if l_.startswith("  D_X = ")][0]
        nums = [float(x) for x in ln.split("95% [")[1].split("]")[0].split(", ")] + [float(x) for x in ln.split("90% [")[1].split("]")[0].split(", ")]
        lo95, hi95, lo90, hi90 = nums
        d = O["D"]
        want = "EQUIVALENT" if (-0.02 < lo90 and hi90 < 0.02) else ("DIFFERENT" if abs(d) > 0.02 and (lo95 > 0 or hi95 < 0) else "NEITHER")
        _need(text, "CV1: %s" % want)
        bri = sum((p - (1.0 if k == want else 0.0)) ** 2 for k, p in PRED["P1_prob"].items())
        _need(text, "outcome %s -> Brier %.4f" % (want, bri))
        _need(text, "  P2 X(AF-U) pooled 0.12 [0.05, 0.25]: %.5f -> %s" % (O["AF-U"]["X"], "HELD" if 0.05 <= O["AF-U"]["X"] <= 0.25 else "FAILED"))
        _need(text, "  P2 X_m(AF-U) GPQA 0.45 [0.20, 0.75]: %.5f -> %s" % (O["AF-U"]["Xm"]["GPQA"], "HELD" if 0.20 <= O["AF-U"]["Xm"]["GPQA"] <= 0.75 else "FAILED"))
        _need(text, "  P3 X(declared-centroid) 0.08 [0.03, 0.18] (descriptive): %.5f" % O["declared"]["X"])
        tsv = open(os.path.join(od, R()["occupancy"]), encoding="utf-8").read()
        assert "cell\tAF-U\tBBH:n00000007\tBBH\tBBH\t6\t5\tBBH:3,MATH:2\t0.6000\t-" in tsv, "the tie cell's TSV row"
        assert "cell\tAF-U\tGPQA:n00000008\tGPQA\tGPQA\t0\t2\tGPQA:2\t1.0000\t-" in tsv, "the empty cell's TSV row"
        try:
            _capture(run, root, od)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e)
        assert open(os.path.join(od, R()["outcome"]), encoding="utf-8").read() == text


def _syn(d, lo95, hi95, lo90, hi90, xa=None):
    xa = xa or {"GPQA": (10, 0.5), "MATH": (10, 0.3), "BBH": (10, 0.1)}
    oos = dict(n_gate=10, n_gate_vec=10, thr=0.5, tpr_gate=0.95, rate=0.1, by_member={"BBH": 0.1}, cells=[])
    dom = dict(n_cells=3, n_eval_cells=3, ties=0, empty=0, x_constr=0.1, low_cov=0, low_list=[])
    Db = dict(d=0.001, lo95=-0.01, hi95=0.012, lo90=-0.008, hi90=0.01, se=0.0043, se_iid=0.004, deff=1.1)
    return dict(N=5907, G=5404, kish=1.09, X={"AF-U": 0.12, "K_0": 0.11, "K_0 all": 0.13, "declared": 0.08},
                Xm={a: xa for a in ARMS}, dom={a: dom for a in ARMS}, oos=oos, disc=0.1, single=["IFEVAL"], n_ex=5745, G_ex=5250,
                D_all=Db, D_ex=Db, D_ex_all=Db,
                D=dict(d=d, lo95=lo95, hi95=hi95, lo90=lo90, hi90=hi90, se=0.0043, se_iid=0.004, deff=1.1))


def st_branches():
    dl = 0.020
    assert cv1(0.0, -0.0199, 0.0199, -0.03, 0.03, dl) == ("EQUIVALENT", None)
    assert cv1(0.0, -0.0200, 0.0100, -0.03, 0.03, dl) == ("NEITHER", None), "strict lower end"
    assert cv1(0.0, -0.0100, 0.0200, -0.03, 0.03, dl) == ("NEITHER", None), "strict upper end"
    assert cv1(0.0201, 0.01, 0.03, 0.001, 0.04, dl) == ("DIFFERENT", "TREE-MORE-MIXED")
    assert cv1(-0.0201, -0.03, -0.01, -0.04, -0.001, dl) == ("DIFFERENT", "TREE-LESS-MIXED")
    assert cv1(0.0200, 0.01, 0.03, 0.001, 0.04, dl) == ("NEITHER", None), "|D| = 0.020 is not > 0.020"
    assert cv1(0.025, 0.01, 0.04, 0.0, 0.05, dl) == ("NEITHER", None), "95% touching 0 does not exclude it"
    assert cv1(0.025, 0.01, 0.04, -0.001, 0.05, dl) == ("NEITHER", None)
    assert oos_threshold([0.5, 0.1, 0.9, 0.3] * 5, 0.95) == 0.1 and oos_threshold(list(range(40)), 0.95) == 2.0
    L = NL.join(verdict_lines(_syn(0.005, -0.004, 0.014, -0.002, 0.012)))
    _need(L, "CV1: EQUIVALENT: the 90% interval [-0.00200, +0.01200] lies inside +/-0.020", "rule 8: EQUIVALENT not refuted",
          "F-CV: NOT FIRED (CV1 EQUIVALENT)", "outcome EQUIVALENT -> Brier 0.3800", "P1 D_X +0.005 [-0.015, +0.025]: +0.00500 -> HELD",
          "P2 order (highest X_m GPQA, then MATH): observed GPQA 0.5000 > MATH 0.3000 > BBH 0.1000 -> HELD")
    L = NL.join(verdict_lines(_syn(0.030, 0.012, 0.048, 0.015, 0.045)))
    _need(L, "CV1: DIFFERENT (TREE-MORE-MIXED): |D_X| 0.03000 > 0.020", "rule 8: EQUIVALENT REFUTED (|D_X| 0.03000 >= 0.020)",
          "F-CV: FIRED (CV1 DIFFERENT, TREE-MORE-MIXED)", "outcome DIFFERENT -> Brier 0.9800", "+0.03000 -> FAILED")
    L = NL.join(verdict_lines(_syn(-0.030, -0.048, -0.012, -0.045, -0.015)))
    _need(L, "CV1: DIFFERENT (TREE-LESS-MIXED)", "F-CV: NOT FIRED (CV1 DIFFERENT TREE-LESS-MIXED)", "descriptive advantage only")
    L = NL.join(verdict_lines(_syn(0.020, -0.002, 0.042, 0.001, 0.039)))
    _need(L, "CV1: NEITHER", "rule 8: EQUIVALENT REFUTED (|D_X| 0.02000 >= 0.020)", "F-CV: NOT FIRED (CV1 NEITHER)",
          "outcome NEITHER -> Brier 0.7800")
    L = NL.join(verdict_lines(_syn(-0.015, -0.03, 0.0, -0.025, -0.005, xa={"MATH": (5, 0.4), "GPQA": (5, 0.3)})))
    _need(L, "-0.01500 -> HELD", "observed MATH 0.4000 > GPQA 0.3000 -> FAILED")
    L = NL.join(verdict_lines(_syn(0.0, -0.01, 0.01, -0.01, 0.01, xa={"GPQA": (5, 0.5), "MMLU_PRO": (5, 0.3), "MATH": (5, 0.2)})))
    _need(L, "observed GPQA 0.5000 > MMLU_PRO 0.3000 > MATH 0.2000 -> FAILED")
    L = NL.join(verdict_lines(_syn(0.0251, 0.0, 0.05, 0.0, 0.05, xa={"BBH": (5, 0.1)})))
    _need(L, "+0.02510 -> FAILED", "GPQA 0.45 [0.20, 0.75]: NOT SCOREABLE (no GPQA EVAL item)")
    L = NL.join(verdict_lines(_syn(0.0, -0.01, 0.01, -0.01, 0.01, xa={"GPQA": (5, 0.20), "MATH": (5, 0.10)})))
    _need(L, "GPQA 0.45 [0.20, 0.75]: 0.20000 -> HELD", "MATH 0.25 [0.10, 0.45]: 0.10000 -> HELD")
    L = NL.join(verdict_lines(_syn(0.0, -0.01, 0.01, -0.01, 0.01, xa={"GPQA": (5, 0.7501), "MATH": (5, 0.0999)})))
    _need(L, "0.75010 -> FAILED", "0.09990 -> FAILED")
    sy = _syn(0.0, -0.01, 0.01, -0.01, 0.01)
    del sy["D_ex"]
    L = NL.join(verdict_lines(sy))
    _need(L, "D_X without one-cell members: no one-cell member (mirrored = nearest of all)",
          "D_X registered nearest-of-all K_0 = +0.00100 (X(K_0 all) 0.13000); 95% [-0.01000, +0.01200], 90% [-0.00800, +0.01000]; its CV1"
          " rule would read EQUIVALENT", "X(K_0) 0.11000")
    # dominance: tie to the sorted-first member; empty -> construction member
    dom, ties, empty, _c = dominance(["A:1", "A:1", "B:2"], ["MATH", "BBH", "BBH"], ["A:1", "B:2", "GPQA:9"])
    assert dom == {"A:1": "BBH", "B:2": "BBH", "GPQA:9": "GPQA"} and ties == 1 and empty == 1, dom


def st_refusals(tmp):
    os.makedirs(tmp, exist_ok=True)

    def expect(needle, variant="main", const=None, pool=(0, "stub"), drop=(), pre=None, existed=False, perturb=()):
        root, X = _fixture(os.path.join(tmp, "r%d" % len(os.listdir(tmp))), variant)
        od = os.path.join(root, "out")
        if const:
            X["const"] = dict(X["const"], **const)
        if pre:
            pre(od)
        buf = []
        with _patched(X, pool=pool, drop=drop, perturb=perturb):
            try:
                run(root, od, out=buf.append)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e)[:300])
        op = os.path.join(od, R()["outcome"])
        assert (os.path.getsize(op) == 0) if existed else not os.path.exists(op), "no outcome after a refusal"
        assert existed or not os.path.exists(os.path.join(od, R()["occupancy"]))
        return buf, X
    expect("K0-IDENTITY", variant="k0_bad")
    expect("inputs manifest is sha256", const=dict(manifest_sha="0" * 64))
    expect("the EVAL set is", const=dict(n_eval=10 ** 6))
    root_, X_ = _fixture(os.path.join(tmp, "probe"))
    miss = [e[0] for e in X_["ev"] if e[6]]
    expect("have no cached vector", drop=tuple(miss))
    first_b = [e[0] for e in X_["ev"] if not e[6]][0]
    expect("differ from the bundle's", perturb=(first_b,))
    buf, _X = expect("B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf[0].startswith(TAG + " POOL")

    def mk(od):
        os.makedirs(od, exist_ok=True)
        open(os.path.join(od, R()["outcome"]), "w").close()
    expect("write-once output(s) exist", pre=mk, existed=True)
    wp = os.path.join(tmp, "existing.txt")
    with open(wp, "w", encoding="utf-8") as fh:
        fh.write("kept")
    try:
        write_outcome(wp, "new")
        raise AssertionError("overwrote")
    except SystemExit as e:
        assert "write-once" in str(e)
    assert open(wp, encoding="utf-8").read() == "kept"


def st_dry(tmp):
    root, X = _fixture(tmp)
    od = os.path.join(tmp, "out")

    def files():
        return sorted(os.path.join(a, f_) for a, _d, fs in os.walk(tmp) for f_ in fs)
    before = files()
    with _patched(X):
        _r, text = _capture(dry_run, root, od)
    assert files() == before, "the dry-run writes nothing"
    assert text.split(NL)[0].startswith(TAG + " POOL pv_fx")
    mem = Counter(e[2] for e in X["ev"])
    _need(text, "DENOMINATORS per member (EVAL set): %s; EVAL items outside the bundle (vectors from the cache at --run): 1" % (
        ", ".join("%s %d" % kv for kv in sorted(mem.items()))), "PIN tools/analysis/coverage_audit.py blob:", "DRY-RUN complete",
          "%d items / %d components" % (len(X["ev"]), X["const"]["comp_eval"]))
    assert "CV1" not in text and "D_X" not in text and "K0-IDENTITY:" not in text


BRANCHES = ("CV1.EQUIVALENT", "CV1.DIFFERENT.TREE-MORE-MIXED", "CV1.DIFFERENT.TREE-LESS-MIXED", "CV1.NEITHER", "RULE8.REFUTED",
            "RULE8.NOT_REFUTED", "FCV.FIRED", "FCV.NOT_FIRED", "FCV.LESS_MIXED_NOTE", "DESC.LOW_COV_LIST", "DESC.NO_LOW_COV",
            "P2.MEMBER", "P2.ABSENT", "OOS.GATE", "DRY.DONE", "RUN.DONE", "BESIDE.EXCL", "BESIDE.NO_SINGLE")


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print branches never executed: %s" % miss


CASES = (("branches", st_branches, "plain"), ("e2e", st_e2e, "tmp"), ("refusals", st_refusals, "tmp"), ("dry_run", st_dry, "tmp"),
         ("branch_cover", st_branch_cover, "plain"))


def selftest(only=None, quiet=False):
    import tempfile
    os.makedirs(TMP_BASE, exist_ok=True)
    HIT.clear()
    fails, ran, made = [], 0, []
    try:
        for name, fn, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    if kind == "tmp":
                        d = tempfile.mkdtemp(prefix="coverage_audit_", dir=TMP_BASE)
                        made.append(d)
                        fn(d)
                    else:
                        fn()
                if not quiet:
                    print("  ok   %s" % name, flush=True)
            except BaseException as e:          # noqa: B902
                fails.append(name)
                if not quiet:
                    print("  FAIL %s: %s: %s" % (name, type(e).__name__, str(e)[:400]), flush=True)
    finally:
        for d in made:
            U.rmtree_ro(d)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def _exec_selftest(src, tests, usrc=None, uorig=None):
    ns = {"__name__": "coverage_audit_mutant", "__file__": os.path.abspath(__file__)}
    try:
        if usrc is not None:
            exec(compile(usrc, U.__file__, "exec"), U.__dict__)
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                  # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])
    finally:
        if usrc is not None:
            exec(compile(uorig, U.__file__, "exec"), U.__dict__)


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    usrc = open(U.__file__, encoding="utf-8").read()
    cut = src.index(NL + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    killed, surv, n_real, control = 0, [], 0, None
    for name, old, new, tests, target in MUTANTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        base = head if target == "self" else usrc
        if base.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times: %r" % (TAG, name, base.count(old), old[:80]))
        mut = base.replace(old, new)
        res = _exec_selftest(mut + tail, tests) if target == "self" else _exec_selftest(src, tests, usrc=mut, uorig=usrc)
        if name.startswith("C00"):
            control = res is True
            print("  %-64s control %s" % (name, "SURVIVED (as it must)" if control else "KILLED (harness broken): %s" % res), flush=True)
            continue
        n_real += 1
        k = res is not True
        killed += int(k)
        if not k:
            surv.append(name)
        print("  %-64s %-8s %s" % (name, "KILLED" if k else "SURVIVED", "" if res is True else res[:100]), flush=True)
    print("%s MUTANTS: %d of %d KILLED; control %s; survivors %s" % (TAG, killed, n_real, "survived" if control else "KILLED/not run", surv or "none"))
    return 0 if killed == n_real and control else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split(NL)[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    ap.add_argument("--data-root", default=U.ROOT, help="the checkout holding experiment_results/, data_v2/ and the cache DBs")
    ap.add_argument("--out-dir", default=None, help="default <data-root>/experiment_results/archv2/coverage_audit")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        dry_run(os.path.abspath(a.data_root), a.out_dir)
        return 0
    run(os.path.abspath(a.data_root), a.out_dir)
    return 0


# (name, old, new, selftest cases, target "self" | "io")
MUTANTS = (
    ("C00 control (no-op edit)", "    return band[0] <= x <= band[1]", "    return band[0] <= x <= band[1]", ["branches", "e2e"], "self"),
    # dominance / filing (min<->max, boundary / empty, wrong population, wrong arm)
    ("V01 dominance tie to the sorted-last member (min<->max)", "        dom[c] = best[0]", "        dom[c] = best[-1]", ["branches", "e2e"], "self"),
    ("V02 empty cell -> no dominant (always foreign)", "            dom[c] = U.cell_member(c)\n            empty += 1", "            dom[c] = None\n            empty += 1",
     ["branches", "e2e"], "self"),
    ("V03 K_0 all EVAL filed by source (the k_cells file), not nearest of all", '"K_0 all": (list(kname[nearest(Xe, Ck)])', '"K_0 all": ([k0.get(i) for i in items]',
     ["e2e"], "self"),
    ("V04 K_0 all TRAIN rows by fit label, not the filing rule", "list(kname[nearest(Xt, Ck)])),", '[k0.get(i) for i in b["titems"]]),', ["e2e"], "self"),
    ("V05 declared TRAIN rows by label, not nearest centroid", '[classes[j] for j in np.argmax(np.where(have[None, :], Xt @ Cd.T, -np.inf), axis=1)])}',
     "[classes[j] for j in yt])}", ["e2e"], "self"),
    ("V06 X pooled = mean of member X_m (not item-weighted)", '        st["X"][arm] = float(fv.mean())', '        st["X"][arm] = float(np.mean([v[1] for v in xm(fv, emem).values()]))',
     ["e2e"], "self"),
    ("V07 D_X against declared (wrong arm)", '    diff = (st["f"]["AF-U"] - st["f"]["K_0"]).astype(np.float64)', '    diff = (st["f"]["AF-U"] - st["f"]["declared"]).astype(np.float64)',
     ["e2e"], "self"),
    ("V08 construction dominance printed as the TRAIN one", '        constr = foreign(ecl, emem, {cc: U.cell_member(cc) for cc in dom})', "        constr = fv", ["e2e"], "self"),
    # the interval / bootstrap
    ("V09 bootstrap over items, not components", "    keys = sorted(set(comp))\n    pos = {k: j for j, k in enumerate(keys)}\n    g = np.array([pos[c] for c in comp], dtype=np.int64)\n    sd",
     "    comp = list(range(len(comp)))\n    keys = sorted(set(comp))\n    pos = {k: j for j, k in enumerate(keys)}\n    g = np.array([pos[c] for c in comp], dtype=np.int64)\n    sd",
     ["e2e"], "self"),
    ("V10 90% interval printed from the 95% quantiles", "lo90=U.pct(s, 0.05), hi90=U.pct(s, 0.95)", "lo90=U.pct(s, 0.025), hi90=U.pct(s, 0.975)", ["e2e"], "self"),
    # CV1 / F-CV / rule 8 / predictions
    ("V11 EQUIVALENT ends inclusive", "    if -delta < lo90 and hi90 < delta:", "    if -delta <= lo90 and hi90 <= delta:", ["branches"], "self"),
    ("V12 DIFFERENT without the 95% clause", "    if abs(d) > delta and (lo95 > 0 or hi95 < 0):", "    if abs(d) > delta:", ["branches"], "self"),
    ("V13 DIFFERENT at |D| >= 0.020", "    if abs(d) > delta and (lo95 > 0 or hi95 < 0):", "    if abs(d) >= delta and (lo95 > 0 or hi95 < 0):", ["branches"], "self"),
    ("V14 direction reversed", '("TREE-MORE-MIXED" if d > 0 else "TREE-LESS-MIXED")', '("TREE-LESS-MIXED" if d > 0 else "TREE-MORE-MIXED")', ["branches", "e2e"], "self"),
    ("V15 F-CV fires on any DIFFERENT", '    if word == "DIFFERENT" and direc == "TREE-MORE-MIXED":\n        hit("FCV.FIRED")', '    if word == "DIFFERENT":\n        hit("FCV.FIRED")',
     ["branches", "e2e"], "self"),
    ("V16 rule 8 at > 0.020", '    if abs(D["d"]) >= c["delta"]:', '    if abs(D["d"]) > c["delta"]:', ["branches"], "self"),
    ("V17 identity test on the CV1 word (numpy-bool class)", '    if word == "EQUIVALENT":\n        hit("CV1.EQUIVALENT")', '    if word is "".join(["EQUI", "VALENT"]):\n        hit("CV1.EQUIVALENT")',
     ["branches"], "self"),
    ("V18 Brier without the square", '    bri = sum((p - (1.0 if k == word else 0.0)) ** 2 for k, p in PRED["P1_prob"].items())',
     '    bri = sum(abs(p - (1.0 if k == word else 0.0)) for k, p in PRED["P1_prob"].items())', ["branches", "e2e"], "self"),
    ("V19 P2 order needs only GPQA first", '    ok = order[:2] == ["GPQA", "MATH"]', '    ok = order[0] == "GPQA"', ["branches", "e2e"], "self"),
    ("V20 prediction bands open at the ends", "    return band[0] <= x <= band[1]", "    return band[0] < x < band[1]", ["branches"], "self"),
    ("V21 low-coverage list omitted", '        L.append("  AF-U cells with own-member coverage < 0.50 (cell: dominant, coverage, EVAL n): " + "; ".join(',
     '        (lambda *_: None)("  AF-U cells with own-member coverage < 0.50 (cell: dominant, coverage, EVAL n): " + "; ".join(', ["e2e"], "self"),
    ("V22 P2 absent-member line omitted", '            L.append("  P2 X_m(AF-U) %s %s: NOT SCOREABLE', '            (lambda *_: None)("  P2 X_m(AF-U) %s %s: NOT SCOREABLE', ["branches"], "self"),
    # OOS (descriptive, but printed and scored by the reviewer)
    ("V23 OOS threshold at TPR 0.90", "    return float(sg[int(np.floor((1 - tpr) * len(sg)))])", "    return float(sg[int(np.floor(0.10 * len(sg)))])", ["branches", "e2e"], "self"),
    ("V24 OOS threshold from EVAL scores", '        thr = oos_threshold(gs, c["tpr"])', '        thr = oos_threshold((Xe @ Ca.T).max(axis=1), c["tpr"])', ["e2e"], "self"),
    ("V25 OOS direction (score above the threshold)", "    isoos = (es < thr).astype(np.float64)", "    isoos = (es > thr).astype(np.float64)", ["e2e"], "self"),
    # gates / write-once / modes
    ("V26 K0-IDENTITY refusal off", '    if bad:\n        refuse("K0-IDENTITY', '    if False:\n        refuse("K0-IDENTITY', ["refusals"], "self"),
    ("V27 cache-vs-bundle sample check off", "    if off:\n", "    if False:\n", ["refusals"], "self"),
    ("V28 missing EVAL vector refusal off", "    if nov:\n", "    if False:\n", ["refusals"], "self"),
    ("V29 outcome opened 'w'", "    return U.G.write_once(path, text)", "    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"], "self"),
    ("V30 marker not written", '    U.G.read_marker(mark, "%s: the EVAL set read started (structure + cached vectors; no key)" % TAG)', "    pass", ["e2e"], "self"),
    ("V31 prelude write-once check removed", "        U.write_once_check(list(paths), TAG)", "        pass", ["e2e", "refusals"], "self"),
    # D-1 / B-4 / B-1 (the delta)
    ("V32 nearest-of-all K_0 decides (B-4 ignored)", '"K_0": (mirrored(Xe, emem), mirrored(Xt, tmem)),',
     '"K_0": (list(kname[nearest(Xe, Ck)]), list(kname[nearest(Xt, Ck)])),', ["e2e"], "self"),
    ("V33 mirror: one-cell centroid left in the others' search", "        g = np.argmax(np.where(one[None, :], -np.inf, X @ Ck.T), axis=1)",
     "        g = np.argmax(X @ Ck.T, axis=1)", ["e2e"], "self"),
    ("V34 mirror: one-cell rows not filed by source", "                g[k] = idx[0]", "                pass", ["e2e"], "self"),
    ("V35 mirror on EVAL only (TRAIN dominance nearest of all)", '"K_0": (mirrored(Xe, emem), mirrored(Xt, tmem)),',
     '"K_0": (mirrored(Xe, emem), list(kname[nearest(Xt, Ck)])),', ["e2e"], "self"),
    ("V36 IFEVAL-excluded D_X over all items", "        st[\"D_ex\"] = interval_stats(diff[keep], ck)", "        st[\"D_ex\"] = interval_stats(diff, comp)",
     ["e2e"], "self"),
    ("V37 component seed changed (B-1)", "    bs_c = comp_boot(diff, comp, c[\"B\"], np.random.default_rng(c[\"seed\"]))",
     "    bs_c = comp_boot(diff, comp, c[\"B\"], np.random.default_rng(c[\"seed\"] + 1))", ["e2e"], "self"),
    ("V38 i.i.d. seed = the component seed (B-1)", "    bs_i = iid_boot(diff, c[\"B\"], np.random.default_rng(c[\"seed_iid\"]))",
     "    bs_i = iid_boot(diff, c[\"B\"], np.random.default_rng(c[\"seed\"]))", ["e2e"], "self"),
    ("V39 no-one-cell beside line omitted", '        L.append("    D_X without one-cell members: no one-cell member',
     '        (lambda *_: None)("    D_X without one-cell members: no one-cell member', ["branches"], "self"),
    ("I01 member alias dropped (MMLU_PRO_LB != MMLU_PRO)", '    member_alias={"MMLU_PRO_LB": "MMLU_PRO"},', "    member_alias={},", ["e2e"], "io"),
    ("I02 manifest sha check off", '    if msh != C()["manifest_sha"]:', "    if False:", ["refusals"], "io"),
    ("I03 EVAL denominator check off", '    if (len(items), comps) != (c["n_eval"], c["comp_eval"]):', "    if False:", ["refusals"], "io"),
    ("I04 pool check refusal off", "    if rc != 0:", "    if False:", ["refusals"], "io"),
    ("I05 K_0 cell_member misparses K-names", '    if c.startswith("K") and c.count(":") == 2:', '    if False:', ["e2e"], "io"),
)

if __name__ == "__main__":
    sys.exit(main())
