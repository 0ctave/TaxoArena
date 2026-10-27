"""cell_flips.py: CELL-FLIPS -- on the union routing data, in how many cells (AF-U, K_0 k-means, declared) does a TRAIN-chosen
cell challenger beat the TRAIN-chosen best single model on EVAL beyond noise (one-sided component bootstrap, BH q 0.05 over
cells)? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU readout of keyed correctness.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-FLIPS: on the union routing data, in how
  many cells (AF-U, K_0 k-means, declared) does a TRAIN-chosen cell challenger beat the TRAIN-chosen best single model on EVAL
  beyond noise ..." L24143-L24154 (_as_of fac3d50b): CF1 (DECIDING), Support (a)-(g), P1-P4, F-CF.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or from anywhere with --data-root <main checkout>; never beside a
construction: --dry-run and --run are pool readers):
  0. python tools/analysis/cell_flips.py --selftest        # synthetic sealed fixture views under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/cell_flips.py --mutants         # the mutant table below, re-run
  1. python tools/analysis/cell_flips.py --dry-run         # POOL line first; pins; the frozen policy; the cells; the EVAL set's
                                                           #   denominators and the TESTED counts (structure only, key sealed)
  2. python tools/analysis/cell_flips.py --run             # ONE EVAL key read (B1 marker); outcome WRITE-ONCE:
       experiment_results/archv2/cell_flips/cell_flips_outcome.txt (+ cell_flips.READ_STARTED); never committed (sha256 + E:)
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line (the B0-2 pool check, g13_breakdown.pool_check_v2); the write-once paths absent; (2) script pins (blob of the LF
  rendering of this file, union_cells_io.py, union_af_route.py bf3f17db, v2_declared_cells.py f0f56805); (3) the frozen TRAIN
  policy of UNION-AF-ROUTE, sha256-bytes 8d68018c... (refused otherwise): g = best_single, the AF-U tree_cell, K0 xtree_cell and
  declared true_source_domain picks, never refitted; (4) the inputs manifest 53021e26... through union_af_route.load_inputs (every
  AF-U / input file re-hashed), af_cells.tsv and k_cells_s0.tsv against its pins; (5) the eval view (sha256-bytes pinned by
  v2_declared_cells), its pool row, the ACTIVE roster = the policy's 18 models (Llama-3-70B absent), the B1 marker written
  write-once, the ONE key read (UNUSABLE_CELL, MATH-FIX overlay; v2_declared_cells.read_key); the set REFUSED unless 5,907 items /
  5,404 components and key-complete = structurally complete; (6) the cells of every EVAL item (AF-U: af_cells.tsv, R1 modal
  flatLeaf leaf over all 123 cells; K_0: k_cells_s0.tsv, filed by source (mirrored), as UNION-AF-ROUTE; declared: the view's
  (stratum_source, stratum_domain)); (7) per arm and cell, D_c, the bootstrap p_c, BH; (8) CF1, F-CF, the descriptive lines, the
  predictions, the Support block; the outcome written write-once (mode "x").

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  CF-R1 challenger_c = the frozen policy's pick for c; a cell absent from the policy (or a None pick) falls back to g (the policy's
        absent_group rule) and is then "challenger = g", never TESTED.
  CF-R2 TESTED iff challenger_c != g and n_EVAL(c) >= 20 (n counted on the 5,907-item set; 20 itself is TESTED).
  CF-R3 D_c = mean over c's EVAL items of A[i, challenger_c] - A[i, g] (item-paired). Bootstrap: B = 10,000 replicates; each
        draws c's components (the components of c's EVAL items; a component split across cells contributes only its items in c)
        with replacement, D*_c = sum of drawn d / number of drawn items; p_c = max(k / B, 1 / (B + 1)), k = #{D*_c <= 0}.
        Streams: numpy default_rng(20261004 + j), j = 0 AF-U, 1 K_0, 2 declared; cells in sorted name order; only TESTED cells
        draw. One-sided toward the challenger.
  CF-R4 BH step-up at q 0.05 over the TESTED cells of ONE arm (m = that arm's TESTED count): reject the k smallest p, k = the
        largest i with p_(i) <= i q / m; ties in p broken by cell name (stable order). FLIP_c iff rejected.
  CF-R5 Kendall tau = scipy.stats.kendalltau (tau-b, ties) between a cell's 18 EVAL accuracies and the 18 global EVAL accuracies
        (5,907 items), cells with n >= 50; a cell with a constant accuracy vector is NaN, counted and dropped from the median. P4
        is scored on the AF-U arm (the deciding arm); K_0 and declared printed beside.
  CF-R6 DEFF (Support (b)) MEASURED per TESTED cell = Var_boot(D*_c) / (Var(d) / n); median printed beside the planning 1.10
        and the two-stage 1.595 (D-PR-1, not recomputed here: the policy is frozen); SE_c = SD of D*_c.
  CF-R7 Predictions: "X [lo, hi]" HELD iff lo <= X <= hi (closed); CF1's probability scored by Brier (p - outcome)^2.
  Not applicable (stated): no judge verdict enters (keyed correctness), so no wrong(established) count and no tie convention A /
  B; no call cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; fixtures under tempfile.mkdtemp(dir=E:/TaxoArena_tmp), removed afterwards): a sealed synthetic eval view
(v2_declared_cells._mk_view; 5 models, twins, an item missing one response and a multi-response cell both out of the set), the
fixture policy / manifest / cells files; the pool check stubbed. Cases:
  e2e        run() end to end: hand values for every AF-U cell (D_c, n, TESTED, p at the floor 0.00010 and at 1.00000, the
             boundary cell n = 20 TESTED, the small cell and the challenger = g cell untested, a cell whose EVAL-best model is not
             the frozen pick), CF1 FLIPS-EXIST 2 of 4, F-CF NOT FIRED, K_0 / declared counts and D_c against an independent loop
             oracle, the Kendall tau median against a plain-loop tau-b, the share of items in FLIP cells, the predictions' words
             and Brier; the outcome file equals the printed text; a second --run REFUSED with the outcome unchanged
  none_e2e   run() on a fixture with no AF-U flip: CF1 NONE ... FAILS (rule 8), F-CF FIRED, the CF1 Brier 0.4225
  zero       run() with NO TESTED AF-U cell: "no AF-U cell is TESTED", CF1 NONE, F-CF FIRED
  branches   bh() step-up vs step-down and vs Bonferroni, ties; flips_of() over TESTED cells only, per arm; p floor; every
             prediction band at both closed ends; the CF1 / F-CF / prediction lines by value (synthetic st)
  refusals   the policy sha, the manifest sha, the EVAL-set denominator, the B1 marker present, the write-once outcome present,
             the pool check rc 1 (POOL line still first), a pick outside the roster; no outcome written by any of them
  dry_run    POOL line first, pins, denominators, TESTED counts; no key column read (the tripwire sealed), nothing written
  branch_cover  every print branch of the registry was hit by the cases above
MUTANTS: see MUTANTS at the end (run with --mutants; the table with the result is in the commit message).
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import io
import json
import math
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

TAG = "[CELL-FLIPS]"
TEST_ID = "CELL-FLIPS"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-FLIPS: on the union routing'
           ' data, in how many cells (AF-U, K_0 k-means, declared) ..." L24143-L24154 (_as_of fac3d50b)')
ARMS = ("AF-U", "K_0", "declared")
RP_ = dict(B=10000, q=0.05, n_min=20, tau_n=50, seed=20261004, out_dir="experiment_results/archv2/cell_flips",
           outcome="cell_flips_outcome.txt", marker="cell_flips.READ_STARTED")
_RP = [RP_]
SUPPORT = dict(kish=1.09, n_cell=48, deff=1.10, deff2=1.595, se=0.083, d_first=0.27, t_plan=100)
PRED = dict(P1_tested=(45, 100), P1_flip=(0, 6), P1_prob=0.65, P2_flip=(1, 10), P3_flip=(0, 6), P4_tau=(0.55, 0.90))
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


# ── the computation ─────────────────────────────────────────────────────────────────────────────────────────────────────

def cell_boot(d, comp, B, rng):
    """CF-R3: component bootstrap of the item-paired mean D_c -> (D*_c replicates (B,), point)."""
    keys = sorted(set(comp))
    pos = {k: j for j, k in enumerate(keys)}
    g = np.array([pos[c] for c in comp], dtype=np.int64)
    sd = np.bincount(g, weights=d, minlength=len(keys))
    sn = np.bincount(g, minlength=len(keys)).astype(np.float64)
    idx = rng.integers(0, len(keys), size=(B, len(keys)))
    return sd[idx].sum(axis=1) / sn[idx].sum(axis=1), float(d.mean())


def p_of(reps, B):
    """CF-R3: p_c = max(k / B, 1 / (B + 1)), k = #{D* <= 0}."""
    k = int((reps <= 0).sum())
    return max(k / B, 1.0 / (B + 1))


def bh(pvals, q):
    """CF-R4: Benjamini-Hochberg step-up -> rejected flags (aligned with pvals); stable order on ties."""
    m = len(pvals)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvals[i])
    kmax = -1
    for r, i in enumerate(order):
        if pvals[i] <= (r + 1) * q / m:
            kmax = r
    rej = [False] * m
    for r in range(kmax + 1):
        rej[order[r]] = True
    return rej


def flips_of(rows, q):
    """BH over the TESTED rows of one arm only; writes row['flip']; returns the number of rejections."""
    t = [r for r in rows if r["tested"]]
    for r in rows:
        r["flip"] = False
    for r, f in zip(t, bh([r["p"] for r in t], q)):
        r["flip"] = bool(f)
    return sum(1 for r in t if r["flip"])


def tau_b(x, y):
    from scipy.stats import kendalltau
    t = kendalltau(x, y)
    v = float(getattr(t, "statistic", t[0]))
    return v


def arm_rows(A, models, g, cells, comp, pick, B, rng, n_min):
    """Per cell of one arm: n, challenger, D_c, TESTED, p_c (TESTED only), SE_c, DEFF_c."""
    by = defaultdict(list)
    for k, c in enumerate(cells):
        by[c].append(k)
    gi = models.index(g)
    rows = []
    for c in sorted(by):
        idx = np.array(by[c], dtype=np.int64)
        ch = pick.get(c)
        absent = ch is None
        if absent:
            ch = g
        if ch not in models:
            refuse("the frozen pick %r of cell %s is not in the roster" % (ch, c))
        ci = models.index(ch)
        d = (A[idx, ci] - A[idx, gi]).astype(np.float64)
        n = len(idx)
        same = ch == g
        tested = (not same) and n >= n_min
        r = dict(cell=c, n=n, ch=ch, absent=absent, same=same, tested=tested, D=float(d.mean()), p=None, se=None, deff=None,
                 idx=idx)
        if tested:
            reps, _pt = cell_boot(d, [comp[k] for k in idx], B, rng)
            r["p"] = p_of(reps, B)
            r["se"] = float(reps.std(ddof=1))
            vi = float(d.var(ddof=1)) / n if n > 1 else 0.0
            r["deff"] = (r["se"] ** 2 / vi) if vi > 0 else float("nan")
        rows.append(r)
    return rows


def analyze(A, models, g, cells_by_arm, comp, picks):
    """-> st: per arm rows, counts, flips, shares, tau; the global accuracies."""
    c = R()
    acc = A.mean(axis=0)
    st = dict(N=A.shape[0], G=len(set(comp)), models=list(models), g=g, acc=acc, arms={})
    for j, arm in enumerate(ARMS):
        rng = np.random.default_rng(c["seed"] + j)
        rows = arm_rows(A, models, g, cells_by_arm[arm], comp, picks[arm], c["B"], rng, c["n_min"])
        k = flips_of(rows, c["q"])
        taus, nan_tau = [], 0
        for r in rows:
            if r["n"] >= c["tau_n"]:
                t = tau_b(A[r["idx"]].mean(axis=0), acc)
                r["tau"] = t
                if t == t:
                    taus.append(t)
                else:
                    nan_tau += 1
        T = [r for r in rows if r["tested"]]
        a = dict(rows=rows, n_cells=len(rows), tested=len(T), flips=k, same=[r["cell"] for r in rows if r["same"]],
                 absent=sum(1 for r in rows if r["absent"]), small=sum(1 for r in rows if not r["same"] and r["n"] < c["n_min"]),
                 flip_items=sum(r["n"] for r in rows if r["flip"]), tau_med=(float(np.median(taus)) if taus else float("nan")),
                 tau_n=len(taus), tau_nan=nan_tau, mean_n=float(np.mean([r["n"] for r in rows])))
        a["share_flip"] = a["flip_items"] / st["N"]
        if T:
            dv = [r["deff"] for r in T if r["deff"] == r["deff"]]
            a["deff_med"] = float(np.median(dv)) if dv else float("nan")
            a["n_med"] = float(np.median([r["n"] for r in T]))
            a["se_med"] = float(np.median([r["se"] for r in T]))
        st["arms"][arm] = a
    sizes = Counter(comp)
    st["kish"] = U.kish(sizes.values())
    return st


def f(x, d=4):
    return ("%+." + str(d) + "f") % x


def verdict_lines(st):
    """CF1, F-CF, the descriptive lines, the predictions and the Support block (every print branch registered in HIT)."""
    from scipy.stats import norm
    c = R()
    a = st["arms"]["AF-U"]
    L = ["", "== CF1 (DECIDING; the BH rejection count over the TESTED AF-U cells decides) =="]
    L.append("  g (the TRAIN-chosen best single model, frozen) = %s; TESTED = challenger != g and n_EVAL >= %d; BH q %.2f per arm;"
             " B = %d component replicates; p = max(k / B, 1 / (B + 1))" % (st["g"], c["n_min"], c["q"], c["B"]))
    exist = bool(a["flips"] >= 1)
    if a["tested"] == 0:
        hit("CF1.ZERO_TESTED")
        L.append("CF1: NONE: no AF-U cell is TESTED (0 of %d cells with challenger != g and n_EVAL >= %d); 0 rejections; CF1 FAILS"
                 " (rule 8: an outcome with 0 rejections)" % (a["n_cells"], c["n_min"]))
    elif exist:
        hit("CF1.FLIPS_EXIST")
        L.append("CF1: FLIPS-EXIST: %d of %d TESTED AF-U cells are BH-surviving FLIPs at q %.2f" % (a["flips"], a["tested"], c["q"]))
    else:
        hit("CF1.NONE")
        L.append("CF1: NONE: 0 of %d TESTED AF-U cells survive BH at q %.2f; CF1 FAILS (rule 8: an outcome with 0 rejections)"
                 % (a["tested"], c["q"]))
    if not exist:
        hit("FCF.FIRED")
        L.append("F-CF: FIRED (CF1 NONE): no AF-U cell reorders the best model beyond noise on EVAL; cell-conditional reporting at"
                 " the tree's cells adds no order information at this n; the E1 framing narrows to declared cells or to descriptive"
                 " differences")
    else:
        hit("FCF.NOT_FIRED")
        L.append("F-CF: NOT FIRED (CF1 FLIPS-EXIST)")
    L.append("")
    L.append("== PER ARM (AF-U deciding; K_0 and declared DESCRIPTIVE comparators: K_0 is not like with like on labels) ==")
    for arm in ARMS:
        b = st["arms"][arm]
        L.append("  %-8s cells %3d (mean EVAL n %.1f); TESTED %3d; FLIP %2d; challenger = g %3d (of them absent / None picks %d);"
                 " challenger != g but n < %d: %d; EVAL items in FLIP cells %d of %d = %.4f" % (
                     arm, b["n_cells"], b["mean_n"], b["tested"], b["flips"], len(b["same"]), b["absent"], c["n_min"], b["small"],
                     b["flip_items"], st["N"], b["share_flip"]))
    for arm in ARMS:
        b = st["arms"][arm]
        fl = [r for r in b["rows"] if r["flip"]]
        if fl:
            hit("DESC.FLIP_LIST")
            for r in fl:
                L.append("  FLIP %-8s %-30s n %4d  challenger %-30s D_c %s  p %.5f" % (arm, r["cell"], r["n"], r["ch"], f(r["D"]), r["p"]))
        else:
            hit("DESC.NO_FLIP_LIST")
            L.append("  FLIP %-8s none" % arm)
    for arm in ARMS:
        b = st["arms"][arm]
        L.append("  %-8s cells where challenger = g (%d): %s" % (arm, len(b["same"]), ", ".join(b["same"]) or "none"))
    L.append("  KENDALL TAU (tau-b; a cell's 18 EVAL accuracies vs the global 18; cells n >= %d): %s" % (c["tau_n"], "; ".join(
        "%s median %s over %d cells (NaN, constant: %d)" % (arm, ("%.4f" % st["arms"][arm]["tau_med"]) if st["arms"][arm]["tau_n"] else "n/a",
                                                          st["arms"][arm]["tau_n"], st["arms"][arm]["tau_nan"]) for arm in ARMS)))
    L.append("")
    L.append("== PREDICTIONS (registrar's priors; bands closed) ==")
    L.append("  P1 AF-U TESTED cells 70 [45, 100]: %d -> %s" % (a["tested"], hw(a["tested"], PRED["P1_tested"])))
    L.append("  P1 AF-U FLIP cells 2 [0, 6]: %d -> %s" % (a["flips"], hw(a["flips"], PRED["P1_flip"])))
    o = 1.0 if exist else 0.0
    L.append("  P1 CF1 FLIPS-EXIST 0.65: outcome %s -> Brier %.4f" % ("FLIPS-EXIST" if exist else "NONE", (PRED["P1_prob"] - o) ** 2))
    L.append("  P2 declared FLIP cells 4 [1, 10] (descriptive): %d -> %s" % (st["arms"]["declared"]["flips"],
                                                                             hw(st["arms"]["declared"]["flips"], PRED["P2_flip"])))
    L.append("  P3 K_0 FLIP cells 2 [0, 6] (descriptive): %d -> %s" % (st["arms"]["K_0"]["flips"], hw(st["arms"]["K_0"]["flips"], PRED["P3_flip"])))
    if a["tau_n"]:
        hit("P4.SCORED")
        L.append("  P4 median Kendall tau (AF-U cells n >= %d) 0.75 [0.55, 0.90] (descriptive): %.4f -> %s" % (
            c["tau_n"], a["tau_med"], hw(a["tau_med"], PRED["P4_tau"])))
    else:
        hit("P4.UNSCORED")
        L.append("  P4 median Kendall tau (AF-U cells n >= %d) 0.75 [0.55, 0.90] (descriptive): NOT SCOREABLE (no AF-U cell with n >= %d)"
                 % (c["tau_n"], c["tau_n"]))
    L.append("")
    L.append("== SUPPORT (registered planning numbers; MEASURED beside) ==")
    L.append("  (a) EVAL %d items / %d components; Kish mean cluster size %.4f (registered %.2f); AF-U cells %d, mean EVAL n %.1f"
             " (registered about %d)" % (st["N"], st["G"], st["kish"], SUPPORT["kish"], a["n_cells"], a["mean_n"], SUPPORT["n_cell"]))
    for arm in ARMS:
        b = st["arms"][arm]
        if b["tested"]:
            hit("SUP.MEASURED")
            m = b["tested"]
            z = float(norm.ppf(1 - c["q"] / m))
            L.append("  (b)-(e) %-8s DEFF per TESTED cell median %.3f (planning 1.10 one-stage; two-stage 1.595 D-PR-1 beside, not"
                     " recomputed: the policy is frozen); median n %.0f, n_eff %.1f; median SE(D_c) %.4f (registered 0.083 at n 48);"
                     " first BH rejection needs p <= q / %d = %.5f (z %.2f): D_c >= %.4f at the median SE (registered 0.27 at n 48,"
                     " 0.15 at n 150)" % (arm, b["deff_med"], b["n_med"], b["n_med"] / b["deff_med"] if b["deff_med"] > 0 else float("nan"),
                                         b["se_med"], m, c["q"] / m, z, z * b["se_med"]))
        else:
            hit("SUP.NONE")
            L.append("  (b)-(e) %-8s no TESTED cell: no measured DEFF / SE" % arm)
    L.append("  (f) VERDICT LINE (registered): SCOREABLE but THIN: FLIPS-EXIST needs at least one cell with a large challenger gain"
             " (>= 15-27pp); U1 (+1.52pp pooled, thin) does not by itself imply a surviving cell. (g) STRUCTURAL: reachable.")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (keyed correctness; no judge verdict enters).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): strata the declared labels do not reveal; a full-order flip (best vs"
             " challenger only); judged orders; anything beyond the union roster and one draw.")
    return L


def table_lines(st):
    c = R()
    L = ["", "== PER-CELL TABLE (descriptive; every cell of every arm; p only for TESTED cells) =="]
    L.append("  arm      cell                            n  challenger                      D_c      TESTED  p        FLIP  tau")
    for arm in ARMS:
        for r in st["arms"][arm]["rows"]:
            L.append("  %-8s %-30s %4d  %-30s %s  %-6s  %-7s  %-4s  %s" % (
                arm, r["cell"], r["n"], r["ch"] + (" (absent->g)" if r["absent"] else ""), f(r["D"]), "yes" if r["tested"] else "no",
                ("%.5f" % r["p"]) if r["p"] is not None else "-", "FLIP" if r["flip"] else "-",
                ("%.4f" % r["tau"]) if "tau" in r and r["tau"] == r["tau"] else "-"))
    L.append("  global EVAL accuracies (n %d): %s" % (st["N"], ", ".join("%s %.4f" % (m, x) for m, x in zip(st["models"], st["acc"]))))
    return L


# ── the modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def out_paths(root, out_dir):
    d = out_dir or U.P(root, R()["out_dir"])
    return os.path.join(d, R()["outcome"]), os.path.join(d, R()["marker"])


def assign(E, af, k0):
    """The cell of every EVAL item per arm (refused on a missing / no-routing-row cell)."""
    out = {}
    for arm, getc in (("AF-U", lambda i: af.get(i)), ("K_0", lambda i: k0.get(i)),
                      ("declared", lambda i: "%s/%s" % (E["meta"][i][1], E["meta"][i][2]))):
        cl = [getc(i) for i in E["items"]]
        bad = [i for i, x in zip(E["items"], cl) if x is None or x in (U.UA.NO_ROW, U.UA.UNROUTED)]
        if bad:
            refuse("arm %s: %d EVAL item(s) of the set carry no cell (first %s)" % (arm, len(bad), bad[:3]))
        out[arm] = cl
    return out


def picks_of(pol):
    return {"AF-U": pol["tree_cell"], "K_0": pol["xtree_cell"]["K0"], "declared": pol["true_source_domain"]}


def prelude(root, out_dir, say, dry):
    U.pool_line(say, TAG)
    outp, mark = out_paths(root, out_dir)
    if not dry:
        U.write_once_check([outp, mark], TAG)
    say("%s %s (zero calls; %s) | registration %s" % (TAG, TEST_ID, "DRY-RUN" if dry else "RUN", REG_TXT))
    U.script_pins(say, TAG, [os.path.abspath(__file__), os.path.join(HERE, "union_cells_io.py"), os.path.join(HERE, "union_af_route.py"),
                             os.path.join(HERE, "v2_declared_cells.py")])
    say("%s data root %s; outputs %s, %s (write-once; never committed)" % (TAG, root, outp, mark))
    pol = U.load_policy(root, say, TAG)
    _man, af, k0 = U.load_cells(root, say, TAG)
    return pol, af, k0, outp, mark


def dry_run(root, out_dir=None, out=print):
    pol, af, k0, _o, _m = prelude(root, out_dir, out, True)
    E = U.eval_set(root, out, TAG, roster=pol["roster"], key=False)
    cells = assign(E, af, k0)
    picks = picks_of(pol)
    for arm in ARMS:
        cnt = Counter(cells[arm])
        t = sum(1 for cc, n in cnt.items() if n >= R()["n_min"] and picks[arm].get(cc, pol["best_single"]) not in (None, pol["best_single"]))
        out("%s DENOMINATOR %-8s %d cells on the %d-item EVAL set; TESTED (challenger != g = %s and n >= %d): %d (structure only)" % (
            TAG, arm, len(cnt), len(E["items"]), pol["best_single"], R()["n_min"], t))
    out("%s PLANNED: B = %d per TESTED cell (default_rng(%d + arm)), BH q %.2f per arm; tau cells n >= %d" % (
        TAG, R()["B"], R()["seed"], R()["q"], R()["tau_n"]))
    out("%s DRY-RUN complete: the key column was never selected (tripwire sealed); no statistic; nothing written" % TAG)
    hit("DRY.DONE")


def write_outcome(path, text):
    """The outcome of record: mode "x" (v2_reader_guards.write_once); an existing path is REFUSED and left unchanged."""
    return U.G.write_once(path, text)


def run(root, out_dir=None, out=print):
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    pol, af, k0, outp, mark = prelude(root, out_dir, say, False)
    say("%s g = %s (frozen best_single); picks: AF-U %d cells, K0 %d cells, declared %d cells (frozen; never refitted)" % (
        TAG, pol["best_single"], len(pol["tree_cell"]), len(pol["xtree_cell"]["K0"]), len(pol["true_source_domain"])))
    E = U.eval_set(root, say, TAG, roster=pol["roster"], key=True, marker=mark)
    models = E["models"]
    A = np.array([[E["K"][i][m] for m in models] for i in E["items"]], dtype=np.int64)
    comp = [E["meta"][i][0] for i in E["items"]]
    cells = assign(E, af, k0)
    st = analyze(A, models, pol["best_single"], cells, comp, picks_of(pol))
    for l in verdict_lines(st) + table_lines(st):
        say(l)
    text = "\n".join(lines) + "\n"
    write_outcome(outp, text)
    out("%s OUTCOME written write-once: %s" % (TAG, outp))
    hit("RUN.DONE")
    return st, text


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
TMP_BASE = "E:/TaxoArena_tmp"
NL = chr(10)
FX_MODELS = ["m0", "m1", "m2", "m3", "m4"]


def _fx_af_cells():
    """(cell, n, pick, fn(k) -> {model: 0/1}) with hand-known D_c."""
    def a1(k):   # D = 0.75: m0 right on the first 15 of 60, m1 always
        return dict(m0=int(k < 15), m1=1, m2=0, m3=0, m4=int(k % 3 == 0))

    def a2(k):   # D = 0: the pick m2 equals m0; m4 (EVAL-best here) always right
        return dict(m0=int(k % 2 == 0), m1=0, m2=int(k % 2 == 0), m3=0, m4=1)

    def a3(k):   # n 15 < 20: untested though D = 1
        return dict(m0=0, m1=1, m2=0, m3=0, m4=0)

    def a4(k):   # the pick is g
        return dict(m0=int(k % 2 == 0), m1=1, m2=1, m3=1, m4=1)

    def a5(k):   # D = -1
        return dict(m0=1, m1=0, m2=0, m3=0, m4=int(k % 2 == 0))

    def a6(k):   # n = 20 exactly, D = +0.5
        return dict(m0=0, m1=0, m2=int(k < 10), m3=0, m4=int(k < 5))
    return [("BBH:n00000001", 60, "m1", a1), ("BBH:n00000002", 40, "m2", a2), ("MATH:n00000003", 15, "m1", a3),
            ("MATH:n00000004", 30, "m0", a4), ("MMLU_PRO_LB:n00000005", 50, "m3", a5), ("MMLU_PRO_LB:n00000006", 20, "m2", a6)]


AF_HAND = {"BBH:n00000001": (60, 0.75, True, "0.00010", True), "BBH:n00000002": (40, 0.0, True, "1.00000", False),
           "MATH:n00000003": (15, 1.0, False, None, False), "MATH:n00000004": (30, 0.0, False, None, False),
           "MMLU_PRO_LB:n00000005": (50, -1.0, True, "1.00000", False), "MMLU_PRO_LB:n00000006": (20, 0.5, True, "0.00010", True)}


def _fixture(tmp, variant="main"):
    """A complete layout under tmp: the sealed eval view, the frozen policy, the inputs manifest, the two cells files. Returns
    (root, expectation dict)."""
    V = U.V
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    spec_cells = _fx_af_cells()
    if variant == "none":       # no flip: A1 / A6 made null
        spec_cells = [(c, n, p, (lambda k: dict(m0=1, m1=1, m2=1, m3=0, m4=0)) if c in ("BBH:n00000001", "MMLU_PRO_LB:n00000006") else fn)
                      for c, n, p, fn in spec_cells]
    if variant == "zero":       # nothing TESTED in AF-U: every pick g or small
        spec_cells = [(c, n, "m0", fn) for c, n, p, fn in spec_cells]
    items, responses, af, k0, rows = [], [], {}, {}, []
    nid = [0]
    for ci, (cell, n, _pick, fn) in enumerate(spec_cells):
        src = {"BBH": "BBH", "MATH": "MATH", "MMLU_PRO_LB": "MMLU_PRO"}[cell.split(":")[0]]
        k = 0
        while k < n:
            twins = 2 if (k % 7 == 3 and k + 1 < n) else 1
            cid = "c:%05d" % (nid[0] + 1)
            for _t in range(twins):
                nid[0] += 1
                iid = "i:%05d" % nid[0]
                dom = "d%d" % (k % 2 if src != "MATH" else 0)
                items.append(dict(id=iid, comp=cid, side="EVAL", src=src, dom=dom, cvs=["fx"]))
                corr = fn(k)
                for m in FX_MODELS:
                    ov = src == "MATH" and m == "m1"          # the MATH-FIX overlay carries the value of record
                    responses.append(dict(cv="fx", model=m, item=iid, side="EVAL", src=src, c=(1 - corr[m]) if ov else corr[m],
                                          mf=corr[m] if ov else None))
                af[iid] = cell
                k0[iid] = "K0:%s:%03d" % (cell.split(":")[0], (k + ci) % 2)
                rows.append((iid, cid, cell, src, dom, corr))
                k += 1
    # two items out of the set: one missing m4's response, one with a multi-response cell (UNUSABLE_CELL)
    for j, kind in enumerate(("missing", "multi")):
        nid[0] += 1
        iid = "i:%05d" % nid[0]
        items.append(dict(id=iid, comp="c:x%d" % j, side="EVAL", src="BBH", dom="d0", cvs=["fx"]))
        for m in FX_MODELS:
            if kind == "missing" and m == "m4":
                continue
            responses.append(dict(cv="fx", model=m, item=iid, side="EVAL", src="BBH", c=1, mf=None))
        if kind == "multi":
            responses.append(dict(cv="fx", model="m0", item=iid, side="EVAL", src="BBH", c=0, mf=None))
        af[iid] = "BBH:n00000001"
        k0[iid] = "K0:BBH:000"
    ev = [it for it in items if it["side"] == "EVAL"]
    n_comp_all = len(set(i["comp"] for i in ev))
    spec = dict(items=items, responses=responses, registry=[("fx", m, "ACTIVE") for m in FX_MODELS] + [("fx", U.V.EXCLUDED, "QUARANTINED")],
                pools=[("pv_fx", "fx", n_comp_all, json.dumps({"fx": len(ev)}))])
    vdir = os.path.join(root, "data_v2")
    os.makedirs(vdir)
    esha = V._mk_view(os.path.join(vdir, "eval_view_fx.db"), "eval", ("EVAL",), spec)
    pick = {c: p for c, _n, p, _f in spec_cells}
    k0pick = {"K0:BBH:000": "m4", "K0:BBH:001": "m1", "K0:MATH:000": "m0", "K0:MATH:001": "m1", "K0:MMLU_PRO_LB:000": "m3",
              "K0:MMLU_PRO_LB:001": "m2"}
    dpick = {"BBH/d0": "m1", "BBH/d1": "m4", "MATH/d0": "m1", "MMLU_PRO/d0": "m2", "MMLU_PRO/d1": "m0"}
    pol = dict(best_single="m0", roster=FX_MODELS, tree_cell=pick, xtree_cell={"K0": k0pick}, true_source_domain=dpick,
               test="SELFTEST")
    pp = U.P(root, U.CONST["policy_rel"])
    os.makedirs(os.path.dirname(pp))
    ptxt = json.dumps(pol, sort_keys=True, indent=1) + "\n"
    with open(pp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(ptxt)
    inp = U.P(root, U.UA.RES + "/inputs")
    os.makedirs(inp)
    shas = {}
    for rel, cells, hdr in ((U.CONST["af_rel"], af, "fixture af"), (U.CONST["k0_rel"], k0, "fixture k0")):
        txt = U.UA.cells_text(cells, hdr)
        with open(U.P(root, rel), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
        shas[rel] = U.UA.sha256_lf(U.P(root, rel))
    mtxt = json.dumps(dict(afu_files={}, inputs=shas), indent=1, sort_keys=True) + "\n"
    mp = U.P(root, U.UA.RES + "/inputs/inputs_manifest.json")
    with open(mp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(mtxt)
    n_set = len(rows)
    const = dict(U.CONST, pool="pv_fx", cv="fx", n_eval=n_set, comp_eval=len(set(r[1] for r in rows)), pool_items=len(ev),
                 pool_comp=n_comp_all, roster=len(FX_MODELS), eval_rel="data_v2/eval_view_fx.db", eval_sha=esha,
                 policy_sha=U.sha256_bytes(pp), manifest_sha=U.UA.sha256_lf(mp))
    return root, dict(const=const, rows=rows, pick=pick, k0pick=k0pick, dpick=dpick, af=af, k0=k0)


@contextlib.contextmanager
def _patched(const, pool=(0, "SELFTEST stub: pool check not run")):
    old_c, old_p, old_r = U._C[0], U._POOL[0], U.UA._ROOT[0]
    U._C[0] = const
    U._POOL[0] = lambda _pool: pool
    try:
        yield
    finally:
        U._C[0], U._POOL[0], U.UA._ROOT[0] = old_c, old_p, old_r


def _capture(fn, *a, **k):
    buf = []
    res = fn(*a, out=buf.append, **k)
    return res, "\n".join(buf)


def _need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def _oracle(rows, arm_cell, pickmap, g="m0", n_min=20):
    """INDEPENDENT plain-loop D_c / n / TESTED per cell."""
    by = defaultdict(list)
    for r in rows:
        by[arm_cell(r)].append(r)
    out = {}
    for c, rs in by.items():
        ch = pickmap.get(c) or g
        n = len(rs)
        D = sum(r[5][ch] - r[5][g] for r in rs) / n
        out[c] = (n, D, ch != g and n >= n_min)
    return out


def _tau_b_loop(x, y):
    n = len(x)
    con = dis = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = x[i] - x[j], y[i] - y[j]
            if a == 0 and b == 0:
                continue
            if a == 0:
                tx += 1
            elif b == 0:
                ty += 1
            elif (a > 0) == (b > 0):
                con += 1
            else:
                dis += 1
    den = math.sqrt((con + dis + tx) * (con + dis + ty))
    return (con - dis) / den if den else float("nan")


def _cell_line(text, arm, cell):
    for ln in text.split("\n"):
        p = ln.split()
        if len(p) > 3 and p[0] == arm and p[1] == cell:
            return p
    raise AssertionError("no table line for %s %s" % (arm, cell))


def st_e2e(tmp):
    root, X = _fixture(tmp)
    od = os.path.join(tmp, "out")
    with _patched(X["const"]):
        (st, text), printed = _capture(run, root, od)
        outp = os.path.join(od, R()["outcome"])
        assert open(outp, encoding="utf-8").read() == text, "the outcome equals the printed text"
        mk = os.path.join(od, R()["marker"])
        assert os.path.isfile(mk) and "B1" in open(mk, encoding="utf-8").read(), "the B1 marker written"
        assert printed.split("\n")[0].startswith(TAG + " POOL pv_fx"), "POOL line first"
        # AF-U hand values, from the PRINTED table
        for cell, (n, D, tested, p, flip) in AF_HAND.items():
            ln = _cell_line(text, "AF-U", cell)
            assert int(ln[2]) == n, (cell, ln)
            assert ln[4] == f(D), (cell, ln[4], D)
            assert ln[5] == ("yes" if tested else "no"), (cell, ln)
            assert ln[6] == (p or "-"), (cell, ln[6], p)
            assert ln[7] == ("FLIP" if flip else "-"), (cell, ln)
        _need(text, "CF1: FLIPS-EXIST: 2 of 4 TESTED AF-U cells are BH-surviving FLIPs at q 0.05", "F-CF: NOT FIRED (CF1 FLIPS-EXIST)",
              "  P1 AF-U TESTED cells 70 [45, 100]: 4 -> FAILED", "  P1 AF-U FLIP cells 2 [0, 6]: 2 -> HELD",
              "  P1 CF1 FLIPS-EXIST 0.65: outcome FLIPS-EXIST -> Brier 0.1225")
        # share of EVAL items in AF-U FLIP cells = (60 + 20) / N
        N = len(X["rows"])
        _need(text, "EVAL items in FLIP cells 80 of %d = %.4f" % (N, 80.0 / N))
        # K_0 and declared against the independent oracle (D, n, TESTED)
        for arm, cellf, pm in (("K_0", lambda r: X["k0"][r[0]], X["k0pick"]), ("declared", lambda r: "%s/%s" % (r[3], r[4]), X["dpick"])):
            orc = _oracle(X["rows"], cellf, pm)
            for c, (n, D, t) in orc.items():
                ln = _cell_line(text, arm, c)
                assert int(ln[2]) == n and ln[4] == f(D) and ln[5] == ("yes" if t else "no"), (arm, c, ln, (n, D, t))
            tested = sum(1 for v in orc.values() if v[2])
            _need(text, "  %-8s cells %3d" % (arm, len(orc)))
            assert st["arms"][arm]["tested"] == tested, (arm, st["arms"][arm]["tested"], tested)
        # Kendall tau median over AF-U cells n >= 50 (A1 n 60, A5 n 50) against a plain-loop tau-b
        acc = [sum(r[5][m] for r in X["rows"]) / N for m in FX_MODELS]
        taus = []
        for cell in ("BBH:n00000001", "MMLU_PRO_LB:n00000005"):
            rs = [r for r in X["rows"] if r[2] == cell]
            taus.append(_tau_b_loop([sum(r[5][m] for r in rs) / len(rs) for m in FX_MODELS], acc))
        tm = float(np.median(taus))
        _need(text, "AF-U median %.4f over 2 cells" % tm, "P4 median Kendall tau (AF-U cells n >= 50) 0.75 [0.55, 0.90] (descriptive): %.4f -> %s"
              % (tm, "HELD" if 0.55 <= tm <= 0.90 else "FAILED"))
        _need(text, "AF-U     cells where challenger = g (1): MATH:n00000004")
        # a second run refused, outcome unchanged
        try:
            _capture(run, root, od)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e
        assert open(outp, encoding="utf-8").read() == text


def st_none(tmp):
    root, X = _fixture(tmp, "none")
    od = os.path.join(tmp, "out")
    with _patched(X["const"]):
        (st, text), _p = _capture(run, root, od)
    _need(text, "CF1: NONE: 0 of 4 TESTED AF-U cells survive BH at q 0.05; CF1 FAILS (rule 8: an outcome with 0 rejections)",
          "F-CF: FIRED (CF1 NONE)", "P1 CF1 FLIPS-EXIST 0.65: outcome NONE -> Brier 0.4225", "  FLIP AF-U     none")


def st_zero(tmp):
    root, X = _fixture(tmp, "zero")
    od = os.path.join(tmp, "out")
    with _patched(X["const"]):
        (st, text), _p = _capture(run, root, od)
    _need(text, "CF1: NONE: no AF-U cell is TESTED (0 of 6 cells", "F-CF: FIRED (CF1 NONE)", "(b)-(e) AF-U     no TESTED cell",
          "P1 AF-U TESTED cells 70 [45, 100]: 0 -> FAILED")


def st_bh_e2e(tmp):
    """BH inside run(): with q swapped to 0.75 the K_0 arm (TESTED p 0.0001, 0.0001, 0.3513, 1, 1) rejects exactly 3; the FLIP column
    equals an independent BH over the printed p of every arm."""
    root, X = _fixture(tmp)
    od = os.path.join(tmp, "out")
    old = _RP[0]
    _RP[0] = dict(RP_, q=0.75)
    try:
        with _patched(X["const"]):
            (st, text), _p = _capture(run, root, od)
    finally:
        _RP[0] = old
    _need(text, "K_0      cells   6 (mean EVAL n 35.8); TESTED   5; FLIP  3;", "  K_0      K0:BBH:001                       50  m1")
    for arm in ARMS:
        ps, fl = [], []
        for ln in text.split(NL):
            q_ = ln.split()
            if len(q_) > 7 and q_[0] == arm and q_[5] == "yes":
                ps.append(float(q_[6]))
                fl.append(q_[7] == "FLIP")
        m = len(ps)
        srt = sorted(ps)
        kk = max([r + 1 for r in range(m) if srt[r] <= (r + 1) * 0.75 / m] or [0])
        cut = srt[kk - 1] if kk else -1.0
        assert fl == [p_ <= cut for p_ in ps], (arm, ps, fl)


def _syn_st(tested=70, flips=2, dflips=4, kflips=2, tau=0.75, tau_n=5):
    def arm(t, k, tm, tn):
        rows = [dict(cell="c%d" % i, n=48, ch="x", absent=False, same=False, tested=i < t, D=0.3 if i < k else 0.0,
                     p=(0.0001 if i < k else 0.5) if i < t else None, se=0.08, deff=1.1, flip=i < k, idx=None) for i in range(max(t, 1))]
        return dict(rows=rows, n_cells=len(rows), tested=t, flips=k, same=[], absent=0, small=0, flip_items=48 * k, share_flip=48 * k / 5907,
                    tau_med=tm, tau_n=tn, tau_nan=0, mean_n=48.0, deff_med=1.1, n_med=48.0, se_med=0.08)
    return dict(N=5907, G=5404, models=["a", "b"], g="a", acc=np.array([0.5, 0.4]), kish=1.09,
                arms={"AF-U": arm(tested, flips, tau, tau_n), "K_0": arm(50, kflips, 0.7, 3), "declared": arm(40, dflips, 0.7, 3)})


def st_branches():
    # BH: step-up (not step-down), not Bonferroni, ties
    assert bh([0.02, 0.03, 0.035, 0.04], 0.05) == [True] * 4, "step-up rejects all four"
    assert bh([0.01, 0.02, 0.03, 0.5], 0.05) == [True, True, True, False], "BH, not Bonferroni"
    assert bh([0.5, 0.0170, 0.9], 0.05) == [False, False, False], "0.0170 > 0.05 / 3 at rank 1"
    assert bh([0.0166, 0.5, 0.9], 0.05) == [True, False, False], "0.0166 <= 0.05 / 3 at rank 1"
    assert bh([0.025, 0.025, 0.9], 0.05) == [True, True, False] and bh([0.03, 0.03], 0.05) == [True, True], "ties"
    assert bh([], 0.05) == []
    # flips_of over TESTED only: an untested row's p is never in m
    rows = [dict(tested=True, p=0.02), dict(tested=True, p=0.04), dict(tested=False, p=0.9), dict(tested=False, p=0.9)]
    assert flips_of(rows, 0.05) == 2 and [r["flip"] for r in rows] == [True, True, False, False], "m = TESTED rows only"
    # the bootstrap draws COMPONENTS: d = (1, 1, 0) with the first two items one component -> D* in {0, 2/3, 1} only
    reps, pt = cell_boot(np.array([1.0, 1.0, 0.0]), ["a", "a", "b"], 400, np.random.default_rng(1))
    assert abs(pt - 2.0 / 3) < 1e-12 and set(np.round(reps, 9).tolist()) <= {0.0, round(2.0 / 3, 9), 1.0}, set(reps.tolist())
    assert len(set(np.round(reps, 9).tolist())) == 3
    # p floor and the k / B form
    assert p_of(np.array([0.1, 0.2, 0.3]), 3) == 0.25 and p_of(np.array([0.0, 0.2, -0.1, 0.3]), 4) == 0.5, "floor / k over B"
    assert abs(p_of(np.array([0.1] * 9999), 9999) - 1.0 / 10000) < 1e-15
    # bands closed at both ends; lines by value
    for (t, k, d, kk, tau), want in (((45, 0, 1, 0, 0.55), ("70 [45, 100]: 45 -> HELD", "2 [0, 6]: 0 -> HELD", "4 [1, 10] (descriptive): 1 -> HELD",
                                                           "2 [0, 6] (descriptive): 0 -> HELD", "0.5500 -> HELD")),
                                     ((100, 6, 10, 6, 0.90), ("100 -> HELD", "6 -> HELD", "10 -> HELD", "(descriptive): 6 -> HELD", "0.9000 -> HELD")),
                                     ((44, 7, 0, 7, 0.5499), ("44 -> FAILED", "7 -> FAILED", "0 -> FAILED", "(descriptive): 7 -> FAILED", "0.5499 -> FAILED")),
                                     ((101, 1, 11, 1, 0.9001), ("101 -> FAILED", "1 -> HELD", "11 -> FAILED", "0.9001 -> FAILED"))):
        L = "\n".join(verdict_lines(_syn_st(t, k, d, kk, tau)))
        for w in want:
            _need(L, w)
    L = "\n".join(verdict_lines(_syn_st(70, 1)))
    _need(L, "CF1: FLIPS-EXIST: 1 of 70 TESTED AF-U cells", "F-CF: NOT FIRED", "Brier 0.1225")
    L = "\n".join(verdict_lines(_syn_st(70, 0)))
    _need(L, "CF1: NONE: 0 of 70 TESTED AF-U cells survive BH", "F-CF: FIRED (CF1 NONE)", "Brier 0.4225")
    L = "\n".join(verdict_lines(_syn_st(70, 2, tau_n=0)))
    _need(L, "NOT SCOREABLE (no AF-U cell with n >= 50)")
    L = "\n".join(verdict_lines(_syn_st(100, 2)))
    _need(L, "first BH rejection needs p <= q / 100 = 0.00050 (z 3.29): D_c >= 0.2632")


def st_refusals(tmp):
    def expect(mut_const, needle, pool=(0, "stub"), pre=None, existed=False):
        root, X = _fixture(os.path.join(tmp, "r%d" % len(os.listdir(tmp))))
        od = os.path.join(root, "out")
        const = dict(X["const"], **mut_const)
        if pre:
            pre(root, od, X)
        buf = []
        with _patched(const, pool):
            try:
                run(root, od, out=buf.append)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e)[:300])
        op = os.path.join(od, R()["outcome"])
        if existed:
            assert os.path.getsize(op) == 0, "a pre-existing outcome is left unchanged"
        else:
            assert not os.path.exists(op), "no outcome after a refusal"
        return buf
    os.makedirs(tmp, exist_ok=True)
    expect(dict(policy_sha="0" * 64), "frozen TRAIN policy is sha256")
    expect(dict(manifest_sha="0" * 64), "inputs manifest is sha256")
    expect(dict(n_eval=10 ** 6), "the EVAL set is")
    buf = expect({}, "B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf and buf[0].startswith(TAG + " POOL"), "POOL line first even on refusal"

    def mk_marker(root, od, X):
        os.makedirs(od, exist_ok=True)
        open(os.path.join(od, R()["marker"]), "w").close()
    expect({}, "write-once output(s) exist", pre=mk_marker)

    def mk_out(root, od, X):
        os.makedirs(od, exist_ok=True)
        open(os.path.join(od, R()["outcome"]), "w").close()
    expect({}, "write-once output(s) exist", pre=mk_out, existed=True)

    def bad_pick(root, od, X):
        pp = U.P(root, U.CONST["policy_rel"])
        pol = json.load(open(pp, encoding="utf-8"))
        pol["tree_cell"]["BBH:n00000001"] = "zz"
        os.chmod(pp, 0o666)
        with open(pp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
        X["const"]["policy_sha"] = U.sha256_bytes(pp)
    wp = os.path.join(tmp, "existing.txt")
    with open(wp, "w", encoding="utf-8") as fh:
        fh.write("kept")
    try:
        write_outcome(wp, "new")
        raise AssertionError("write_outcome overwrote")
    except SystemExit as e:
        assert "write-once" in str(e)
    assert open(wp, encoding="utf-8").read() == "kept", "an existing outcome is left unchanged"

    def extra_model(root, od, X):
        pp = U.P(root, U.CONST["policy_rel"])
        pol = json.load(open(pp, encoding="utf-8"))
        pol["roster"] = pol["roster"] + ["m9"]
        with open(pp, "w", encoding="utf-8", newline=NL) as fh:
            fh.write(json.dumps(pol, sort_keys=True, indent=1) + NL)
        X["const"]["policy_sha"] = U.sha256_bytes(pp)
    root, X = _fixture(os.path.join(tmp, "rroster"))
    od = os.path.join(root, "out")
    extra_model(root, od, X)
    with _patched(X["const"]):
        try:
            run(root, od, out=lambda s: None)
            raise AssertionError("roster mismatch not refused")
        except SystemExit as e:
            assert "ACTIVE roster" in str(e), e
    assert not os.path.exists(os.path.join(od, R()["outcome"]))
    root, X = _fixture(os.path.join(tmp, "rpick"))
    od = os.path.join(root, "out")
    bad_pick(root, od, X)
    with _patched(X["const"]):
        try:
            run(root, od, out=lambda s: None)
            raise AssertionError("bad pick not refused")
        except SystemExit as e:
            assert "is not in the roster" in str(e), e
    assert not os.path.exists(os.path.join(od, R()["outcome"]))


def st_dry(tmp):
    root, X = _fixture(tmp)
    od = os.path.join(tmp, "out")

    def files():
        return sorted(os.path.join(a, f_) for a, _d, fs in os.walk(tmp) for f_ in fs)
    before = files()
    with _patched(X["const"]):
        _r, text = _capture(dry_run, root, od)
    assert files() == before, "the dry-run writes no file anywhere"
    assert "key cells single" not in text, "the dry-run never reads the key"
    assert text.split("\n")[0].startswith(TAG + " POOL pv_fx"), "POOL line first"
    N = len(X["rows"])
    _need(text, "EVAL SET (G14's", "%d items / %d components" % (N, X["const"]["comp_eval"]),
          "DENOMINATOR AF-U     6 cells on the %d-item EVAL set; TESTED (challenger != g = m0 and n >= 20): 4" % N,
          "PIN tools/analysis/cell_flips.py blob:", "FROZEN TRAIN POLICY", "DRY-RUN complete")
    assert "CF1:" not in text and "D_c" not in text and "KENDALL" not in text, "no statistic in the dry-run"
    assert not os.path.exists(od), "the dry-run writes nothing"


BRANCHES = ("CF1.ZERO_TESTED", "CF1.FLIPS_EXIST", "CF1.NONE", "FCF.FIRED", "FCF.NOT_FIRED", "DESC.FLIP_LIST", "DESC.NO_FLIP_LIST",
            "P4.SCORED", "P4.UNSCORED", "SUP.MEASURED", "SUP.NONE", "DRY.DONE", "RUN.DONE")


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print branches never executed: %s" % miss


CASES = (("branches", st_branches, "plain"), ("e2e", st_e2e, "tmp"), ("none_e2e", st_none, "tmp"), ("bh_e2e", st_bh_e2e, "tmp"), ("zero", st_zero, "tmp"),
         ("refusals", st_refusals, "tmp"), ("dry_run", st_dry, "tmp"), ("branch_cover", st_branch_cover, "plain"))


def selftest(only=None, quiet=False):
    import tempfile
    os.makedirs(TMP_BASE, exist_ok=True)
    HIT.clear()
    fails, ran, made = [], 0, []
    try:
        for name, fn, kind in CASES:
            if only is not None and name not in only and name != "branch_cover":
                continue
            if name == "branch_cover" and only is not None:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    if kind == "tmp":
                        d = tempfile.mkdtemp(prefix="cell_flips_", dir=TMP_BASE)
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
    ns = {"__name__": "cell_flips_mutant", "__file__": os.path.abspath(__file__)}
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
    cut = src.index("\nMUTANTS = (")
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
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    ap.add_argument("--data-root", default=U.ROOT, help="the checkout holding experiment_results/ and data_v2/ (default: this one)")
    ap.add_argument("--out-dir", default=None, help="default <data-root>/experiment_results/archv2/cell_flips")
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
    # the p-value form (RP06 X3 class: a p or denominator changed from the registered form)
    ("M01 p = k / B without the floor", "    return max(k / B, 1.0 / (B + 1))", "    return k / B", ["branches", "e2e"], "self"),
    ("M02 p = (k + 1) / (B + 1)", "    return max(k / B, 1.0 / (B + 1))", "    return (k + 1) / (B + 1)", ["branches", "e2e"], "self"),
    ("M03 D* < 0 instead of <= 0", "    k = int((reps <= 0).sum())", "    k = int((reps < 0).sum())", ["e2e"], "self"),
    ("M04 bootstrap over items, not components", "    keys = sorted(set(comp))\n    pos", "    comp = list(range(len(comp)))\n    keys = sorted(set(comp))\n    pos",
     ["branches"], "self"),
    # BH
    ("M05 BH step-down (stop at the first non-rejection)", "            kmax = r\n", "            kmax = r\n        else:\n            break\n", ["branches"], "self"),
    ("M06 Bonferroni instead of BH", "        if pvals[i] <= (r + 1) * q / m:", "        if pvals[i] <= q / m:", ["branches", "e2e"], "self"),
    ("M07 BH m over every cell with a p (untested included)", '    t = [r for r in rows if r["tested"]]', '    t = [r for r in rows if r["tested"] or r["p"] is not None]',
     ["branches"], "self"),
    ("M08 BH pooled over the three arms' order (q x 3)", '        k = flips_of(rows, c["q"])', '        k = flips_of(rows, c["q"] * 3)', ["bh_e2e"], "self"),
    # TESTED / challenger / g (wrong population, boundary)
    ("M09 n_EVAL > 20 (boundary cell dropped)", '        tested = (not same) and n >= n_min', '        tested = (not same) and n > n_min', ["e2e"], "self"),
    ("M10 challenger re-chosen on EVAL (cell's EVAL-best)", "        ci = models.index(ch)", "        ci = int(np.argmax(A[idx].sum(axis=0)))", ["e2e"], "self"),
    ("M11 g = the EVAL-best single model", "    gi = models.index(g)", "    gi = int(np.argmax(A.sum(axis=0)))", ["e2e"], "self"),
    ("M12 D_c sign reversed", "        d = (A[idx, ci] - A[idx, gi]).astype(np.float64)", "        d = (A[idx, gi] - A[idx, ci]).astype(np.float64)", ["e2e"], "self"),
    ("M13 small cells (n < 20) TESTED", '        tested = (not same) and n >= n_min', '        tested = (not same)', ["e2e"], "self"),
    ("M14 challenger = g cells TESTED", '        tested = (not same) and n >= n_min', '        tested = n >= n_min', ["e2e"], "self"),
    # the arms (wrong arm / wrong population)
    ("M15 CF1 read from the declared arm", '    a = st["arms"]["AF-U"]\n    L = ["", "== CF1', '    a = st["arms"]["declared"]\n    L = ["", "== CF1', ["e2e"], "self"),
    ("M16 K_0 cells read from the AF-U file", '("K_0", lambda i: k0.get(i))', '("K_0", lambda i: af.get(i))', ["e2e"], "self"),
    ("M17 declared cells = source only", '"%s/%s" % (E["meta"][i][1], E["meta"][i][2]))', '"%s/%s" % (E["meta"][i][1], "d0"))', ["e2e"], "self"),
    ("M18 K_0 picks taken from the AF-U policy", '"K_0": pol["xtree_cell"]["K0"]', '"K_0": pol["tree_cell"]', ["e2e"], "self"),
    # verdict words / print branches / predictions
    ("M19 FLIPS-EXIST needs >= 2 rejections", '    exist = bool(a["flips"] >= 1)', '    exist = bool(a["flips"] >= 2)', ["branches"], "self"),
    ("M20 identity test on the verdict (numpy-bool class)", "    elif exist:\n", "    elif exist is np.True_:\n", ["e2e", "branches"], "self"),
    ("M21 F-CF FIRED line omitted", '        L.append("F-CF: FIRED (CF1 NONE): no AF-U cell', '        (lambda *_: None)("F-CF: FIRED (CF1 NONE): no AF-U cell',
     ["none_e2e"], "self"),
    ("M22 zero-TESTED branch omitted", '    if a["tested"] == 0:', '    if False:', ["zero"], "self"),
    ("M23 Brier against 1 - p", '(PRED["P1_prob"] - o) ** 2', '(1 - PRED["P1_prob"] - o) ** 2', ["e2e"], "self"),
    ("M24 prediction bands open at the ends", "    return band[0] <= x <= band[1]", "    return band[0] < x < band[1]", ["branches"], "self"),
    ("M25 share of FLIP items over TESTED items, not N", '    a["share_flip"] = a["flip_items"] / st["N"]',
     '    a["share_flip"] = a["flip_items"] / max(1, sum(r["n"] for r in rows if r["tested"]))', ["e2e"], "self"),
    ("M26 tau over every cell (n >= 50 dropped)", '            if r["n"] >= c["tau_n"]:', '            if r["n"] >= 0:', ["e2e"], "self"),
    ("M27 tau median -> min", 'tau_med=(float(np.median(taus))', 'tau_med=(float(np.min(taus))', ["e2e"], "self"),
    ("M28 P4 unscoreable line omitted", '        L.append("  P4 median Kendall tau (AF-U cells n >= %d) 0.75 [0.55, 0.90] (descriptive): NOT SCOREABLE',
     '        (lambda *_: None)("  P4 median Kendall tau (AF-U cells n >= %d) 0.75 [0.55, 0.90] (descriptive): NOT SCOREABLE', ["branches"], "self"),
    # write-once / modes
    ("M29 outcome opened 'w'", "    return U.G.write_once(path, text)", "    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"], "self"),
    ("M30 prelude write-once check removed", "        U.write_once_check([outp, mark], TAG)", "        pass", ["e2e", "refusals"], "self"),
    ("M31 dry-run reads the key", "    E = U.eval_set(root, out, TAG, roster=pol[\"roster\"], key=False)", "    E = U.eval_set(root, out, TAG, roster=pol[\"roster\"], key=True, marker=os.path.join(root, 'mk'))",
     ["dry_run"], "self"),
    # union_cells_io (gates, the EVAL set, the key read)
    ("I01 policy sha check off", '    if sh != C()["policy_sha"]:', "    if False:", ["refusals"], "io"),
    ("I02 manifest sha check off", '    if msh != C()["manifest_sha"]:', "    if False:", ["refusals"], "io"),
    ("I03 EVAL denominator check off", '    if (len(items), comps) != (c["n_eval"], c["comp_eval"]):', "    if False:", ["refusals"], "io"),
    ("I04 pool check refusal off", "    if rc != 0:", "    if False:", ["refusals"], "io"),
    ("I05 roster check vs the policy off", " or (roster is not None and list(roster) != models):", ":", ["refusals"], "io"),
    ("I06 B1 marker not written", '        G.read_marker(marker, "%s: the EVAL key read started (B1); policy sha256 %s" % (tag, c["policy_sha"]))',
     "        pass", ["e2e"], "io"),
    ("I07 MATH-FIX overlay off", '        K, kst = V.read_key(tw, "response", c["cv"], models, meta, True, c["rule"])',
     '        K, kst = V.read_key(tw, "response", c["cv"], models, meta, False, c["rule"])', ["e2e"], "io"),
    ("I08 variant rule AGREE_OR_UNUSABLE", '    rule="UNUSABLE_CELL",', '    rule="AGREE_OR_UNUSABLE",', ["e2e"], "io"),
    ("I09 POOL line printed after the policy", "    rc, msg = _POOL[0](C()[\"pool\"])\n    say(", "    rc, msg = _POOL[0](C()[\"pool\"])\n    (lambda *_: None)(",
     ["refusals", "dry_run"], "io"),
)

if __name__ == "__main__":
    sys.exit(main())
