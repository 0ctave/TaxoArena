"""G13 comparator (RP12 ARCH-V2-E-T, "is the tree needed"; = F-TAX L-2). ZERO calls: no judge, no LLM, no embedding call.

REGISTRATION OF RECORD: docs/judge_v2_program.md, "## Registered 2026-09-29 (before any code or call) — ARCH-V2-E-T" (L22028-L22060
at 0a0361b), paragraphs "G13 COMPARATOR (fixed now)" and "READOUTS AND CRITERIA ... G13". This script implements them VERBATIM:

  KC_s: for each declared class c = (source, domain) with TRAIN members, spherical k-means (cosine; k-means++ init, n_init 1,
  max_iter 300) on c's TRAIN members in the same 512-d slice at k_c = max(1, number of B0 leaves whose TRAIN majority label is
  c) ("matched per-class prototypes"); an EVAL item is filed to the class of its nearest prototype. Seeds s = 0..4; KC_0 is the
  comparator of record; spread_KC = max - min over s of KC_s precision. Printed beside, never deciding: nearest class centroid,
  kNN-15, unconditional spherical k-means at k = B0's leaf count with TRAIN-majority labels (seeds 0..4).
  G13 (INTERVAL AND POINT jointly, one clause each way): D13 = P_fl - P(KC_0), paired on union EVAL. HELD (lever) iff the
  interval lies wholly above 0 AND D13 > spread_KC. FAILED iff the interval lies wholly below 0 AND D13 < -spread_KC.
  UNDETERMINED otherwise. Parity is never written (no TOST registered): an UNDETERMINED reads "neither a gain nor parity is
  shown". Intervals: 95% percentile, CK-CLOSE-component bootstrap, B 2,000.
  Support (a)-(e): union EVAL 6,153 items in 5,642 CK-CLOSE components (Kish mean 1.091); DEFF 1.269 TRANSPORTED (the run
  re-measures and prints it); n_eff 4,849; SE 0.00497; MDE80 0.0139. P4: D13 = -0.020 [-0.045, +0.005]; spread_KC = 0.004
  [0.001, 0.012]; HELD 0.15, FAILED 0.45, UNDETERMINED 0.40.

IMPLEMENTATION CHOICES (stated, for the READY to confirm or refuse):
  (i)   spherical k-means and k-means++ are flat_mix_mmlu.spherical_kmeans / kmeanspp (the FLAT-MIX-MMLU instrument of record,
        blob-pinned below; numpy default_rng(seed); stops when no assignment changes; an emptied cluster keeps its centroid).
  (ii)  the bootstrap draws whole CK-CLOSE components with replacement through flat_mix_mmlu.twin_boot_indices (groups = the
        component index), B 2,000, numpy default_rng(BOOT_SEED = 20260929, declared here); percentile convention of
        flat_mix_mmlu.twin_boot_ci (bs[int(0.025 B)], bs[int(0.975 B) - 1]); SE = the replicates' sd (ddof 1);
        DEFF = SE^2 / (var(diff, ddof 1) / n); n_eff = n / DEFF; MDE80 = 2.80 x SE.
  (iii) k_c > (TRAIN members of c) REFUSES (a failed precondition; k-means++ cannot seed more centres than points).
  (iv)  kNN-15 votes by count; a tie goes to the larger summed cosine, then to the smaller class name. Unconditional k-means
        labels a cluster by its TRAIN majority (tie: the smaller class name); a cluster with no TRAIN member cannot occur
        (k-means++ seeds on points; an emptied cluster keeps its centroid and its last label is recomputed on 0 members ->
        it is labelled "<empty>" and files as wrong).
  (v)   a prediction "X [lo, hi]" is HELD iff the point lies in [lo, hi], endpoints inclusive (V2-DECLARED-CELLS reading (b)).

INPUT: an input BUNDLE (the G13 contract), <stem>.npz (allow_pickle False) + <stem>.json:
  npz  eval_X float (n_e, d) | eval_y int (class index) | eval_comp int (CK-CLOSE component index) | eval_fl int 0/1 (B0's
       flatLeaf filing correct: the leaf's TRAIN-majority (source, domain) equals the item's declared class; G11's P_fl per
       item) | train_X float (n_t, d) | train_y int | classes str (class names) | leaf_major str (one per B0 leaf: its
       TRAIN-majority class) | eval_item str, train_item str (item ids; asserted disjoint: no EVAL item in any fit)
  json {"pool_id": "pv2_1575de61bb20e977", "n_eval": 6153, "n_components": 5642, "dim": 512, "b0_snapshot": ..., "sources":
       {...pins...}}
  The rows are unit-normalised here (flat_mix_mmlu.unit_rows) whatever the bundle holds. THE BUNDLE BUILDER IS NOT IN THIS
  FILE: B0's per-item flatLeaf filing needs an item key the engine's MAIN_union_routing_queries.csv does not carry today (see
  the commit message); a bundle that does not state pool pv2_1575de61bb20e977 with 6,153 / 5,642 is REFUSED.

  [DELTA 2026-10-01 rp12-pair-mc, MC-EXCLUDE (orchestrator ruling; the default rule); insertion only] the bundle json also
  carries n_eval_before_exclusion, n_components_before_exclusion and multiclass_excluded (rp12_pairing excludes items whose
  rows carry more than one declared class): the registered 6,153 / 5,642 are compared with the counts BEFORE the exclusion,
  the arrays must hold exactly that minus the listed EVAL exclusions (none of them scored), more than 1% excluded REFUSES
  (bar_refuses, integers), and --dry-run / --run print the exclusion block (counts by side, keys, the denominators). A bundle
  built before the rule lists none and reads as before. Mutants (H0 control survived): H1 the registered counts read after
  the exclusion, H2 the left-count check removed, H3 an excluded item still scored admitted, H4 the bar at >=, H5 the bar
  removed, H6 --run omits the block: 6 of 6 killed.

  python tools/analysis/g13_comparator.py --selftest
  python tools/analysis/g13_comparator.py --dry-run --bundle <stem>   # pool line first; counts, k_c table, pins; NO statistic
  python tools/analysis/g13_comparator.py --run --bundle <stem>       # the readout; outcome WRITE-ONCE (mode x)
Output: experiment_results/archv2/rp12/g13_outcome.txt (write-once; --out overrides).

SELFTEST MUTANTS (run 2026-09-29 by a harness, one temporary edit at a time, reverted; C0 is the control and survived):
  C1 spread_KC forced to 0 | C2 comparator KC_1 (not KC_0) | C3 k_c = 1 for every class | C4 an interval touching 0 read as
  above | C5 FAILED without the spread clause | C6 bootstrap by item (not by component) | C7 P4 endpoints exclusive | C8 the
  EVAL-in-a-fit refusal removed | C9 the registered-count refusal removed | C10 D13 sign flipped | C11 the write-once check
  removed | C12 spread over seeds 0..3 only | C13 HELD without the spread clause | C14 k_c > n_c not refused: 14 of 14 killed.
[DELTA 2026-09-30 rp12-et2, READY_rp12_et D-4 / D-5; insertion only] load_bundle(sides=) refuses an EVAL item that is not
EVAL, and a TRAIN item that is not TRAIN (a GATE item in the KC fit), in the committed side export (check_sides); --run
passes the committed export's mc6 items. D-5 (RA5): D13 == spread_KC is UNDETERMINED, boundary-tested on both sides.
Mutants: R4 check_sides removed, R5 (RA5) >= at the spread, R6 --run passes no sides, R6b GATE admitted among TRAIN items:
4 of 4 killed; C1-C14 re-run, 14 of 14 killed.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): --bundle and --out of the other lane REFUSE; in lane r2 they must lie inside experiment_configs/rp12_r2/
or experiment_results/archv2/rp12_r2/; the default outcome is experiment_results/archv2/rp12_r2/g13_outcome.txt.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import sys
import io
import json
import hashlib
import argparse
import contextlib
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[G13]"
POOL_UNION = "pv2_1575de61bb20e977"
N_EVAL, N_COMP = 6153, 5642
DIM = 512
SEEDS = (0, 1, 2, 3, 4)
KNN = 15
BOOT_B, BOOT_SEED = 2000, 20260929
MAX_ITER = 300
DEFF_TRANSPORTED, SE_REG, MDE_REG = 1.269, 0.00497, 0.0139
P4_D13 = (-0.045, 0.005)
P4_SPREAD = (0.001, 0.012)
FLAT_MIX_PIN = ("flat_mix_mmlu.py", "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2")
OUT_DEFAULT = os.path.join(ROOT, "experiment_results", "archv2", "rp12", "g13_outcome.txt")


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _blob(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


_fm_path = os.path.join(HERE, FLAT_MIX_PIN[0])
if _blob(_fm_path) != FLAT_MIX_PIN[1]:
    refuse("%s is blob:%s, not the pinned blob:%s" % (_fm_path, _blob(_fm_path), FLAT_MIX_PIN[1]))
import flat_mix_mmlu as FM  # noqa: E402  (the instrument of record for k-means and the whole-group bootstrap)


# ── the comparator ──────────────────────────────────────────────────────────────────────────────────────────────────

def k_per_class(classes, train_y, leaf_major):
    """k_c = max(1, #B0 leaves whose TRAIN-majority label is c), for every class with TRAIN members; REFUSES on k_c > n_c."""
    names = list(classes)
    for lab in leaf_major:
        if lab not in names:
            refuse("B0 leaf majority label %r is not a declared class" % lab)
    counts = {c: 0 for c in names}
    for lab in leaf_major:
        counts[lab] += 1
    out = {}
    for ci, c in enumerate(names):
        n_c = int((train_y == ci).sum())
        if n_c == 0:
            continue
        k = max(1, counts[c])
        if k > n_c:
            refuse("class %s: k_c = %d exceeds its %d TRAIN members" % (c, k, n_c))
        out[ci] = k
    return out


def kc_prototypes(Xt, yt, kc, seed):
    """Per-class spherical k-means prototypes -> (P (m, d), owner class index (m,))."""
    protos, owner = [], []
    for ci in sorted(kc):
        Xc = Xt[yt == ci]
        r = FM.spherical_kmeans(Xc, kc[ci], seed, max_iter=MAX_ITER)
        protos.append(r["centers"])
        owner.extend([ci] * kc[ci])
    return np.vstack(protos), np.array(owner, dtype=int)


def file_nearest(Q, P, owner):
    return owner[np.argmax(Q @ P.T, axis=1)]


def kc_correct(Xt, yt, Xe, ye, kc, seed):
    P, owner = kc_prototypes(Xt, yt, kc, seed)
    return (file_nearest(Xe, P, owner) == ye).astype(np.int64)


def ncc_correct(Xt, yt, Xe, ye):
    cls = sorted(set(int(c) for c in yt))
    P = FM.unit_rows(np.vstack([Xt[yt == c].sum(axis=0) for c in cls]))
    return (np.array(cls)[np.argmax(Xe @ P.T, axis=1)] == ye).astype(np.int64)


def knn_correct(Xt, yt, Xe, ye, classes, k=KNN, chunk=512):
    out = np.zeros(len(ye), dtype=np.int64)
    for a in range(0, len(ye), chunk):
        S = Xe[a:a + chunk] @ Xt.T
        top = np.argpartition(-S, kth=min(k, S.shape[1]) - 1, axis=1)[:, :k]
        for r in range(S.shape[0]):
            votes = {}
            for j in top[r]:
                c = int(yt[j])
                n, s = votes.get(c, (0, 0.0))
                votes[c] = (n + 1, s + float(S[r, j]))
            best = sorted(votes.items(), key=lambda kv: (-kv[1][0], -kv[1][1], classes[kv[0]]))[0][0]
            out[a + r] = int(best == ye[a + r])
    return out


def ukm_correct(Xt, yt, Xe, ye, L, seed, classes):
    r = FM.spherical_kmeans(Xt, L, seed, max_iter=MAX_ITER)
    lab = np.full(L, -1, dtype=int)
    for j in range(L):
        m = yt[r["labels"] == j]
        if len(m):
            cnt = np.bincount(m, minlength=len(classes))
            top = np.flatnonzero(cnt == cnt.max())
            lab[j] = min(top, key=lambda c: classes[c])
    return (lab[np.argmax(Xe @ r["centers"].T, axis=1)] == ye).astype(np.int64)


def comp_groups(comp):
    _, g = np.unique(np.asarray(comp), return_inverse=True)
    return g.astype(int)


def boot(diff, groups, B=BOOT_B, seed=BOOT_SEED):
    """Whole-component bootstrap of the mean paired difference: (lo, hi, se) with flat_mix_mmlu's draw and percentile rule."""
    diff = np.asarray(diff, dtype=np.float64)
    members = FM.group_members(groups)
    rng = np.random.default_rng(seed)
    reps = np.array([diff[FM.twin_boot_indices(groups, rng, members)].mean() for _ in range(B)])
    bs = sorted(float(x) for x in reps)
    return bs[int(0.025 * B)], bs[int(0.975 * B) - 1], float(reps.std(ddof=1))


def g13_verdict(d, lo, hi, spread_kc):
    if lo > 0 and d > spread_kc:
        return "HELD"
    if hi < 0 and d < -spread_kc:
        return "FAILED"
    return "UNDETERMINED"


def in_band(x, band):
    return "HELD" if band[0] <= x <= band[1] else "FAILED"


def compute(b):
    """The readout on a loaded bundle -> dict of every printed number."""
    classes = [str(c) for c in b["classes"]]
    Xt, yt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64)), np.asarray(b["train_y"], dtype=int)
    Xe, ye = FM.unit_rows(np.asarray(b["eval_X"], dtype=np.float64)), np.asarray(b["eval_y"], dtype=int)
    fl = np.asarray(b["eval_fl"], dtype=np.int64)
    groups = comp_groups(b["eval_comp"])
    kc = k_per_class(classes, yt, [str(x) for x in b["leaf_major"]])
    kcs = {s: kc_correct(Xt, yt, Xe, ye, kc, s) for s in SEEDS}
    p_kc = {s: float(kcs[s].mean()) for s in SEEDS}
    spread_kc = max(p_kc.values()) - min(p_kc.values())
    p_fl = float(fl.mean())
    diff = fl - kcs[0]
    d13 = float(diff.mean())
    lo, hi, se = boot(diff, groups)
    var_iid = float(diff.var(ddof=1)) / len(diff)
    deff = se ** 2 / var_iid if var_iid > 0 else float("nan")
    L = len(b["leaf_major"])
    beside = {"ncc": float(ncc_correct(Xt, yt, Xe, ye).mean()), "knn15": float(knn_correct(Xt, yt, Xe, ye, classes).mean())}
    for s in SEEDS:
        beside["ukm%d" % s] = float(ukm_correct(Xt, yt, Xe, ye, L, s, classes).mean())
    return dict(n=len(ye), n_comp=int(groups.max()) + 1, kish=FM.kish_mbar(groups), kc={classes[c]: k for c, k in kc.items()},
                n_train=len(yt), p_fl=p_fl, p_kc=p_kc, spread_kc=spread_kc, d13=d13, lo=lo, hi=hi, se=se, deff=deff,
                n_eff=len(ye) / deff if deff == deff and deff > 0 else float("nan"), mde=2.80 * se,
                verdict=g13_verdict(d13, lo, hi, spread_kc), beside=beside, L=L)


def render(r, meta):
    o = []
    o.append("%s pool %s (union EVAL %d items in %d CK-CLOSE components; Kish mean cluster size %.4f)"
             % (TAG, meta.get("pool_id"), r["n"], r["n_comp"], r["kish"]))
    o.extend(exclusion_lines(meta, r["n"], r["n_comp"]))
    o.append("%s TRAIN members %d; B0 leaves L = %d; k_c = max(1, #B0 leaves with TRAIN majority c):" % (TAG, r["n_train"], r["L"]))
    for c in sorted(r["kc"]):
        o.append("   k_c %-40s %d" % (c, r["kc"][c]))
    o.append("P_fl (B0 flatLeaf, (source, domain) precision) = %.4f" % r["p_fl"])
    for s in SEEDS:
        o.append("P(KC_%d) = %.4f%s" % (s, r["p_kc"][s], "   <- comparator of record" if s == 0 else ""))
    o.append("spread_KC = max - min over s = 0..4 = %.4f" % r["spread_kc"])
    o.append("D13 = P_fl - P(KC_0) = %+.4f  95%% percentile [%+.4f, %+.4f] (CK-CLOSE components whole, B %d, seed %d)"
             % (r["d13"], r["lo"], r["hi"], BOOT_B, BOOT_SEED))
    o.append("support: SE %.5f (registered %.5f); DEFF measured %.3f (transported %.3f); n_eff %.0f (registered 4,849); MDE80 %.4f"
             " (registered %.4f)" % (r["se"], SE_REG, r["deff"], DEFF_TRANSPORTED, r["n_eff"], r["mde"], MDE_REG))
    v = r["verdict"]
    if v == "HELD":
        o.append("G13: HELD (lever): the interval lies wholly above 0 AND D13 %+.4f > spread_KC %.4f" % (r["d13"], r["spread_kc"]))
    elif v == "FAILED":
        o.append("G13: FAILED: the interval lies wholly below 0 AND D13 %+.4f < -spread_KC %.4f" % (r["d13"], -r["spread_kc"]))
    else:
        o.append("G13: UNDETERMINED: neither a gain nor parity is shown (D13 %+.4f, interval [%+.4f, %+.4f], spread_KC %.4f)"
                 % (r["d13"], r["lo"], r["hi"], r["spread_kc"]))
    o.append("F-TAX L-2 reads this G13 line (scored by the registrar at F-TAX, not here)")
    o.append("P4 D13 = -0.020 [-0.045, +0.005]: observed %+.4f -> %s" % (r["d13"], in_band(r["d13"], P4_D13)))
    o.append("P4 spread_KC = 0.004 [0.001, 0.012]: observed %.4f -> %s" % (r["spread_kc"], in_band(r["spread_kc"], P4_SPREAD)))
    o.append("P4 verdict probabilities (HELD 0.15, FAILED 0.45, UNDETERMINED 0.40): observed %s" % v)
    o.append("PRINTED BESIDE, never deciding: nearest class centroid %.4f; kNN-15 %.4f; unconditional spherical k-means at k = %d"
             " with TRAIN-majority labels: %s" % (r["beside"]["ncc"], r["beside"]["knn15"], r["L"],
                                                   ", ".join("s%d %.4f" % (s, r["beside"]["ukm%d" % s]) for s in SEEDS)))
    return "\n".join(o) + "\n"


# ── bundle I/O and modes ────────────────────────────────────────────────────────────────────────────────────────────

REQUIRED = ("eval_X", "eval_y", "eval_comp", "eval_fl", "train_X", "train_y", "classes", "leaf_major", "eval_item", "train_item")


def check_sides(b, sides):
    """READY_rp12_et D-4: every EVAL item of the bundle is EVAL and every TRAIN item TRAIN in the side export ({item: side});
    a GATE item among the TRAIN items (the KC fit) or the EVAL items REFUSES, as an EVAL item among the TRAIN items does."""
    for arr, want in (("eval_item", "EVAL"), ("train_item", "TRAIN")):
        bad = Counter(sides.get(i, "ABSENT") for i in b[arr].tolist() if sides.get(i) != want)
        if bad:
            refuse("%d %s item(s) are not %s in the side export: %s" % (sum(bad.values()), arr, want, dict(sorted(bad.items()))))


def load_bundle(stem, expect=(POOL_UNION, N_EVAL, N_COMP), sides=None):
    npz, js = stem + ".npz", stem + ".json"
    for p in (npz, js):
        if not os.path.isfile(p):
            refuse("bundle file %s is missing" % p)
    with open(js, encoding="utf-8") as f:
        meta = json.load(f)
    z = np.load(npz, allow_pickle=False)
    b = {k: z[k] for k in z.files}
    missing = [k for k in REQUIRED if k not in b]
    if missing:
        refuse("bundle lacks %s" % missing)
    if expect is not None:
        pool, n, nc = expect
        if meta.get("pool_id") != pool:
            refuse("bundle pool %r is not %s" % (meta.get("pool_id"), pool))
        # MC-EXCLUDE (orchestrator ruling 2026-10-01): the registered 6,153 / 5,642 are the counts BEFORE rp12_pairing excluded
        # the multi-class items; the bundle must carry exactly those minus its listed EVAL exclusions (<= 1%)
        ne, nce = len(b["eval_y"]), len(set(b["eval_comp"].tolist()))
        ex_e = exclusions(meta)["EVAL"]
        nb, cb = meta.get("n_eval_before_exclusion", ne), meta.get("n_components_before_exclusion", nce)
        if (nb, cb) != (n, nc):
            refuse("bundle carries %d EVAL items in %d components before the multi-class exclusion, not the registered %d / %d"
                   % (nb, cb, n, nc))
        if ne != nb - len(ex_e) or nce > cb or set(ex_e) & set(b["eval_item"].tolist()):
            refuse("bundle carries %d EVAL items in %d components, not the %d / at most %d left after excluding its %d listed"
                   " multi-class EVAL item(s) (or an excluded item is still scored)" % (ne, nce, nb - len(ex_e), cb, len(ex_e)))
        if bar_refuses(len(ex_e), nb):
            refuse("%d of %d EVAL items excluded as multi-class: above the 1%% bar" % (len(ex_e), nb))
    n_e = len(b["eval_y"])
    if not (b["eval_X"].shape[0] == n_e == len(b["eval_comp"]) == len(b["eval_fl"]) == len(b["eval_item"])):
        refuse("EVAL arrays disagree in length")
    if not (b["train_X"].shape[0] == len(b["train_y"]) == len(b["train_item"])):
        refuse("TRAIN arrays disagree in length")
    if b["eval_X"].shape[1] != meta.get("dim", DIM) or b["train_X"].shape[1] != b["eval_X"].shape[1]:
        refuse("vector dimension %d / %d is not the declared %s" % (b["eval_X"].shape[1], b["train_X"].shape[1], meta.get("dim")))
    ov = set(b["eval_item"].tolist()) & set(b["train_item"].tolist())
    if ov:
        refuse("%d EVAL item(s) are also TRAIN items (no EVAL item may enter a fit): %s" % (len(ov), sorted(ov)[:3]))
    if not set(np.unique(b["eval_fl"]).tolist()) <= {0, 1}:
        refuse("eval_fl is not 0/1")
    if sides is not None:
        check_sides(b, sides)
    return b, meta


def bar_refuses(k, n):
    """MC-EXCLUDE's 1% bar in integers: refused iff 100 x excluded EVAL items > EVAL items before the exclusion."""
    return 100 * k > n


def exclusions(meta):
    """MC-EXCLUDE: the bundle's listed multi-class exclusions by side (a bundle built before the rule lists none)."""
    ex = meta.get("multiclass_excluded") or {}
    return {sd: dict(ex.get(sd) or {}) for sd in ("EVAL", "GATE", "TRAIN")}


def exclusion_lines(meta, n, ncomp):
    ex = exclusions(meta)
    o = ["%s MULTI-CLASS ITEMS EXCLUDED (orchestrator ruling 2026-10-01): EVAL %d, GATE %d, TRAIN %d"
         % (TAG, len(ex["EVAL"]), len(ex["GATE"]), len(ex["TRAIN"]))]
    for sd in ("EVAL", "GATE", "TRAIN"):
        for it in sorted(ex[sd]):
            o.append("%s   excluded %s %s %s" % (TAG, sd, it, ex[sd][it]))
    o.append("%s DENOMINATORS: EVAL %d items in %d components after the exclusion (before %s / %s; registered %d / %d)"
             % (TAG, n, ncomp, meta.get("n_eval_before_exclusion", n), meta.get("n_components_before_exclusion", ncomp), N_EVAL, N_COMP))
    return o


def dry_run(b, meta, out=print):
    classes = [str(c) for c in b["classes"]]
    out("%s pool %s (bundle; dry-run: NO statistic)" % (TAG, meta.get("pool_id")))
    out("%s EVAL %d items in %d components; TRAIN %d; classes %d; B0 leaves %d; dim %d"
        % (TAG, len(b["eval_y"]), len(set(b["eval_comp"].tolist())), len(b["train_y"]), len(classes), len(b["leaf_major"]),
           b["eval_X"].shape[1]))
    for ln in exclusion_lines(meta, len(b["eval_y"]), len(set(b["eval_comp"].tolist()))):
        out(ln)
    kc = k_per_class(classes, np.asarray(b["train_y"], dtype=int), [str(x) for x in b["leaf_major"]])
    out("%s k_c: %s" % (TAG, ", ".join("%s=%d" % (classes[c], k) for c, k in sorted(kc.items()))))
    out("%s sources: %s" % (TAG, json.dumps(meta.get("sources", {}), sort_keys=True)))


def main(argv=None, out=print):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--bundle")
    ap.add_argument("--out", default=None)
    import rp12_lane as LN
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    a.out = a.out or (OUT_DEFAULT if a.lane == "r1" else LN.out_path(a.lane, "g13_outcome.txt"))
    if not a.bundle:
        refuse("--bundle is required")
    LN.guard(a.lane, [("--bundle", a.bundle), ("--out", a.out)])                                   # rp12-r2-lane
    b, meta = load_bundle(a.bundle, expect=_EXPECT[0], sides=_SIDES[0]() if _SIDES[0] else None)
    if a.dry_run:
        dry_run(b, meta, out)
        return 0
    if os.path.exists(a.out):
        refuse("%s exists; the outcome is write-once" % a.out)
    text = render(compute(b), meta)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    out(text.rstrip("\n"))
    out("%s wrote %s (write-once)" % (TAG, a.out))
    return 0


_EXPECT = [(POOL_UNION, N_EVAL, N_COMP)]   # the selftest swaps in its fixture's expectation; nothing else writes it


def _committed_sides():
    """{item: side} of the committed side export's mc6-2026-09-11 items (v2_engine_pool.read_side, S1 checked)."""
    import v2_engine_pool as EP
    items, _meta = EP.read_side(os.path.join(ROOT, EP.DEFAULT_SIDE))
    return {i: s for i, (_c, s, cs) in items.items() if "mc6-2026-09-11" in cs}


_SIDES = [_committed_sides]                # the selftest swaps in its fixture's sides (or None); nothing else writes it


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _fixture(rng, n_train_per=60, n_eval_per=20, d=8):
    """3 classes, each two tight modes on its own axes; class 2's EVAL items sit on class 0's mode (KC files them wrong)."""
    def unit(v):
        return v / np.linalg.norm(v)
    axes = {0: (0, 1), 1: (2, 3), 2: (4, 5)}
    Xt, yt, Xe, ye, comp = [], [], [], [], []
    for c, (a1, a2) in axes.items():
        for m, ax in enumerate((a1, a2)):
            mu = np.zeros(d); mu[ax] = 1.0
            for _ in range(n_train_per // 2):
                Xt.append(unit(mu + 0.05 * rng.standard_normal(d))); yt.append(c)
            for _ in range(n_eval_per // 2):
                src = mu if c != 2 else np.eye(d)[0]
                Xe.append(unit(src + 0.05 * rng.standard_normal(d))); ye.append(c)
    Xe, ye = np.array(Xe), np.array(ye)
    comp = np.arange(len(ye)) // 2                       # components of two items
    return dict(train_X=np.array(Xt), train_y=np.array(yt), eval_X=Xe, eval_y=ye, eval_comp=comp,
                classes=np.array(["S/a", "S/b", "T/c"]), leaf_major=np.array(["S/a", "S/a", "S/b", "T/c", "T/c"]),
                eval_item=np.array(["e%d" % i for i in range(len(ye))]), train_item=np.array(["t%d" % i for i in range(len(yt))]))


LANE_ERR = "is an object of lane %s, the run is lane %s"


def selftest():
    import tempfile, shutil
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        try:
            fn()
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    rng = np.random.default_rng(7)
    fx = _fixture(rng)
    n = len(fx["eval_y"])

    def k_table():
        kc = k_per_class(list(fx["classes"]), fx["train_y"], list(fx["leaf_major"]))
        assert kc == {0: 2, 1: 1, 2: 2}, kc
        try:
            k_per_class(["S/a"], np.zeros(1, dtype=int), ["S/a", "S/a"])
            raise AssertionError("k_c > n_c not refused")
        except SystemExit as e:
            assert "k_c = 2 exceeds its 1 TRAIN members" in str(e), e

    def kc_values():
        # classes 0 and 1 file right, class 2 (sitting on class 0's mode) files to class 0: precision = 40 / 60 for every seed
        kc = k_per_class(list(fx["classes"]), fx["train_y"], list(fx["leaf_major"]))
        for s in SEEDS:
            c = kc_correct(FM.unit_rows(fx["train_X"]), fx["train_y"], FM.unit_rows(fx["eval_X"]), fx["eval_y"], kc, s)
            assert c.sum() == 40 and c[:40].all() and not c[40:].any(), (s, c.sum())
        assert ncc_correct(FM.unit_rows(fx["train_X"]), fx["train_y"], FM.unit_rows(fx["eval_X"]), fx["eval_y"]).sum() == 40

    def verdicts_end_to_end():
        tmp = tempfile.mkdtemp(prefix="g13st_")
        try:
            _EXPECT[0] = ("pv2_fixture", n, n // 2)
            # the --run path checks the bundle's items against the side export (D-4): here the fixture's own sides
            _SIDES[0] = lambda: dict([(i, "EVAL") for i in fx["eval_item"].tolist()] + [(i, "TRAIN") for i in fx["train_item"].tolist()])
            for label, fl, want in (("held", np.ones(n, dtype=int), "HELD"),
                                    ("failed", np.zeros(n, dtype=int), "FAILED"),
                                    ("undet", np.r_[np.ones(40, dtype=int), np.zeros(20, dtype=int)], "UNDETERMINED")):
                stem = os.path.join(tmp, label)
                np.savez(stem + ".npz", eval_fl=fl, **fx)
                with open(stem + ".json", "w") as f:
                    json.dump({"pool_id": "pv2_fixture", "dim": 8, "sources": {"fixture": 1}}, f)
                outp = os.path.join(tmp, label + "_outcome.txt")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = main(["--run", "--bundle", stem, "--out", outp])
                assert rc == 0
                text = open(outp, encoding="utf-8").read()
                g13 = [l for l in text.splitlines() if l.startswith("G13: ")]
                assert len(g13) == 1 and g13[0].startswith("G13: " + want), (label, g13)
                p_fl = fl.mean()
                assert "P_fl (B0 flatLeaf, (source, domain) precision) = %.4f" % p_fl in text
                assert "P(KC_0) = 0.6667   <- comparator of record" in text, text
                assert "spread_KC = max - min over s = 0..4 = 0.0000" in text
                assert "D13 = P_fl - P(KC_0) = %+.4f" % (p_fl - 40 / 60) in text
                if want == "UNDETERMINED":
                    assert "neither a gain nor parity is shown" in g13[0]
                    assert "D13 = P_fl - P(KC_0) = +0.0000  95% percentile [+0.0000, +0.0000]" in text
                if want == "HELD":
                    # every item's diff is 1 - kc0: the whole-component bootstrap of a 0/1 vector over 30 components
                    diff = fl - np.r_[np.ones(40, dtype=int), np.zeros(20, dtype=int)]
                    lo, hi, se = boot(diff, comp_groups(fx["eval_comp"]))
                    assert "[%+.4f, %+.4f]" % (lo, hi) in text and lo > 0
                    assert "P4 D13 = -0.020 [-0.045, +0.005]: observed +0.3333 -> FAILED" in text
                if want == "FAILED":
                    assert "P4 D13 = -0.020 [-0.045, +0.005]: observed -0.6667 -> FAILED" in text
                assert "P4 spread_KC = 0.004 [0.001, 0.012]: observed 0.0000 -> FAILED" in text
                assert "nearest class centroid 0.6667; kNN-15 0.6667; unconditional spherical k-means at k = 5" in text, text
                # write-once
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        main(["--run", "--bundle", stem, "--out", outp])
                        raise AssertionError("second write not refused")
                    except SystemExit as e:
                        assert str(e).endswith("exists; the outcome is write-once"), e
            # D-4 on the --run path: the sides given to --run are checked (a GATE item among the TRAIN items refuses)
            gate_sides = dict([(i, "EVAL") for i in fx["eval_item"].tolist()] + [(i, "TRAIN") for i in fx["train_item"].tolist()])
            gate_sides[fx["train_item"].tolist()[0]] = "GATE"
            _SIDES[0] = lambda: gate_sides
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    main(["--run", "--bundle", os.path.join(tmp, "held"), "--out", os.path.join(tmp, "gate_outcome.txt")])
                raise AssertionError("--run accepted a GATE TRAIN item")
            except SystemExit as e:
                assert "1 train_item item(s) are not TRAIN in the side export: {'GATE': 1}" in str(e), e
            assert not os.path.exists(os.path.join(tmp, "gate_outcome.txt"))
        finally:
            _EXPECT[0] = (POOL_UNION, N_EVAL, N_COMP)
            _SIDES[0] = _committed_sides
            shutil.rmtree(tmp, ignore_errors=True)

    def verdict_boundaries():
        assert g13_verdict(0.02, 0.001, 0.04, 0.01) == "HELD"
        assert g13_verdict(0.02, 0.0, 0.04, 0.01) == "UNDETERMINED"          # interval touching 0 is not wholly above
        assert g13_verdict(0.005, 0.001, 0.01, 0.01) == "UNDETERMINED"       # point inside the spread
        assert g13_verdict(-0.02, -0.04, -0.001, 0.01) == "FAILED"
        assert g13_verdict(-0.005, -0.04, -0.001, 0.01) == "UNDETERMINED"
        assert g13_verdict(-0.02, -0.04, 0.0, 0.01) == "UNDETERMINED"
        assert in_band(-0.045, P4_D13) == "HELD" and in_band(0.005, P4_D13) == "HELD" and in_band(0.0051, P4_D13) == "FAILED"
        # D-5 (READY RA5): D13 exactly equal to spread_KC is not above it (both are multiples of 1/n, a tie is possible)
        assert g13_verdict(0.01, 0.001, 0.02, 0.01) == "UNDETERMINED"
        assert g13_verdict(-0.01, -0.02, -0.001, 0.01) == "UNDETERMINED"

    def spread_and_seed():
        # a fixture where the seeds disagree: one class with 4 unequal modes and k_c = 2 -> KC depends on the seed
        r = np.random.default_rng(13)   # seeds give [0.90, 0.95, 0.95, 0.95, 0.80]: KC_1 != KC_0 and seed 4 is the minimum
        d = 6
        def unit(v):
            return v / np.linalg.norm(v)
        Xt, yt = [], []
        for ax in range(4):
            for _ in range(10):
                Xt.append(unit(np.eye(d)[ax] + 0.3 * r.standard_normal(d))); yt.append(0)
        for _ in range(40):
            Xt.append(unit(np.eye(d)[5] + 0.3 * r.standard_normal(d))); yt.append(1)
        Xe = np.array([unit(np.eye(d)[ax] * 0.6 + np.eye(d)[5] * 0.4 + 0.05 * r.standard_normal(d)) for ax in range(4) for _ in range(5)])
        ye = np.zeros(20, dtype=int)
        kc = {0: 2, 1: 1}
        ps = [kc_correct(np.array(Xt), np.array(yt), Xe, ye, kc, s).mean() for s in SEEDS]
        assert [round(x, 2) for x in ps] == [0.9, 0.95, 0.95, 0.95, 0.8], ps
        b = dict(train_X=np.array(Xt), train_y=np.array(yt), eval_X=Xe, eval_y=ye, eval_comp=np.arange(20), eval_fl=np.ones(20, dtype=int),
                 classes=np.array(["A", "B"]), leaf_major=np.array(["A", "A", "B"]), eval_item=np.array(["e%d" % i for i in range(20)]),
                 train_item=np.array(["t%d" % i for i in range(80)]))
        res = compute(b)
        assert abs(res["spread_kc"] - (max(ps) - min(ps))) < 1e-12, (res["spread_kc"], ps)
        assert abs(res["d13"] - (1 - ps[0])) < 1e-12, (res["d13"], ps[0])
        assert abs(res["spread_kc"] - 0.15) < 1e-12 and abs(res["d13"] - 0.10) < 1e-12, res

    def lane_paths():
        r1b, r2b = "experiment_results/archv2/rp12/B0_run/g13_bundle", "experiment_results/archv2/rp12_r2/B0_run/g13_bundle"
        for argv, needle in ((["--dry-run", "--lane", "r2", "--bundle", r1b], "--bundle %s %s" % (r1b, LANE_ERR % ("r1", "r2"))),
                             (["--dry-run", "--bundle", r2b], "--bundle %s %s" % (r2b, LANE_ERR % ("r2", "r1"))),
                             (["--run", "--lane", "r2", "--bundle", r2b, "--out", OUT_DEFAULT], "--out %s %s" % (OUT_DEFAULT, LANE_ERR % ("r1", "r2")))):
            try:
                main(argv, out=lambda x: None)
                raise AssertionError("not refused: %s" % argv)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e))

    def refusals():
        tmp = tempfile.mkdtemp(prefix="g13rf_")
        try:
            stem = os.path.join(tmp, "b")
            bad = dict(fx); bad["train_item"] = np.array(["e0"] + ["t%d" % i for i in range(1, len(fx["train_y"]))])
            np.savez(stem + ".npz", eval_fl=np.ones(n, dtype=int), **bad)
            with open(stem + ".json", "w") as f:
                json.dump({"pool_id": POOL_UNION, "dim": 8}, f)
            try:
                load_bundle(stem, expect=None)
                raise AssertionError("overlap not refused")
            except SystemExit as e:
                assert "1 EVAL item(s) are also TRAIN items" in str(e), e
            try:
                load_bundle(stem)
                raise AssertionError("count not refused")
            except SystemExit as e:
                assert "not the registered 6153 / 5642" in str(e), e
            # MC-EXCLUDE: the registered counts are read BEFORE the exclusion; the bundle must hold exactly that minus its list
            stem3 = os.path.join(tmp, "m")
            fx2 = _fixture(np.random.default_rng(5), n_eval_per=40)          # 120 EVAL items: 1 excluded of 121 is under 1%
            n2 = len(fx2["eval_y"])
            np.savez(stem3 + ".npz", eval_fl=np.ones(n2, dtype=int), **fx2)
            nc_fx = len(set(fx2["eval_comp"].tolist()))
            exm = {"EVAL": {"ex1": ["A", "B"]}, "GATE": {"ex2": ["A", "B"]}, "TRAIN": {}}
            for nb, cb, lst, want in ((n2 + 1, nc_fx + 1, exm, None), (n2 + 1, nc_fx + 1, dict(exm, EVAL={"ex1": ["A", "B"], "ex3": ["A", "B"]}),
                                       "not the %d / at most %d left" % (n2 - 1, nc_fx + 1)),
                                      (n2 + 1, nc_fx + 1, dict(exm, EVAL={"e0": ["A", "B"]}), "or an excluded item is still scored"),
                                      (n2 + 2, nc_fx + 1, exm, "before the multi-class exclusion, not the registered")):
                p3 = stem3 + ".json"
                if os.path.exists(p3):
                    os.remove(p3)
                with open(p3, "w") as f:
                    json.dump({"pool_id": POOL_UNION, "dim": 8, "n_eval_before_exclusion": nb, "n_components_before_exclusion": cb,
                               "multiclass_excluded": lst}, f)
                try:
                    bm, mm = load_bundle(stem3, expect=(POOL_UNION, n2 + 1, nc_fx + 1))
                    assert want is None, "not refused: %s" % want
                    t3 = "\n".join(exclusion_lines(mm, n2, nc_fx))
                    t3r = render(compute(bm), mm)              # the --run path prints the same block
                    assert ("%s DENOMINATORS: EVAL %d items in %d components after the exclusion (before %d / %d; registered 6153 / 5642)"
                            % (TAG, n2, nc_fx, n2 + 1, nc_fx + 1)) in t3r and "%s   excluded EVAL ex1 ['A', 'B']" % TAG in t3r, t3r
                    assert (bar_refuses(1, 100), bar_refuses(2, 200), bar_refuses(2, 199), bar_refuses(1, 99), bar_refuses(0, 0)) == \
                        (False, False, True, True, False)
                    assert "%s MULTI-CLASS ITEMS EXCLUDED (orchestrator ruling 2026-10-01): EVAL 1, GATE 1, TRAIN 0" % TAG in t3 and \
                        "%s   excluded EVAL ex1 ['A', 'B']" % TAG in t3 and "%s   excluded GATE ex2 ['A', 'B']" % TAG in t3 and \
                        "%s DENOMINATORS: EVAL %d items in %d components after the exclusion (before %d / %d; registered 6153 / 5642)" \
                        % (TAG, n2, nc_fx, n2 + 1, nc_fx + 1) in t3, t3
                except SystemExit as e:
                    assert want is not None and want in str(e), (want, e)
            # the 1% bar: 1 of 61 EVAL items excluded refuses (the 60-item fixture)
            np.savez(stem3 + ".npz", eval_fl=np.ones(n, dtype=int), **fx)
            nc_fx = len(set(fx["eval_comp"].tolist()))
            with open(stem3 + ".json", "w") as f:
                json.dump({"pool_id": POOL_UNION, "dim": 8, "n_eval_before_exclusion": n + 1, "n_components_before_exclusion": nc_fx + 1,
                           "multiclass_excluded": exm}, f)
            try:
                load_bundle(stem3, expect=(POOL_UNION, n + 1, nc_fx + 1))
                raise AssertionError("1 of %d not refused" % (n + 1))
            except SystemExit as e:
                assert str(e) == "%s REFUSED: 1 of %d EVAL items excluded as multi-class: above the 1%% bar" % (TAG, n + 1), e
            # D-4: a GATE item among the TRAIN items (the KC fit) refuses; so does a TRAIN item among the EVAL items
            stem2 = os.path.join(tmp, "g")
            np.savez(stem2 + ".npz", eval_fl=np.ones(n, dtype=int), **fx)
            with open(stem2 + ".json", "w") as f:
                json.dump({"pool_id": POOL_UNION, "dim": 8}, f)
            sides = dict([(i, "EVAL") for i in fx["eval_item"].tolist()] + [(i, "TRAIN") for i in fx["train_item"].tolist()])
            b_ok, _m = load_bundle(stem2, expect=None, sides=sides)
            cs = _committed_sides()          # the --run default: the committed export's mc6 items (6,153 EVAL of 20,537)
            assert len(cs) == 20537 and sum(1 for v in cs.values() if v == "EVAL") == 6153, (len(cs), Counter(cs.values()))
            for item, side, arr, want in (("t3", "GATE", "train_item", "TRAIN"), ("e5", "TRAIN", "eval_item", "EVAL")):
                s2 = dict(sides); s2[item] = side
                try:
                    load_bundle(stem2, expect=None, sides=s2)
                    raise AssertionError("%s %s not refused" % (arr, side))
                except SystemExit as e:
                    assert str(e) == "%s REFUSED: 1 %s item(s) are not %s in the side export: {'%s': 1}" % (TAG, arr, want, side), e
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    for nm, fn in [("k_c table and the k_c > n_c refusal", k_table), ("KC_s and NCC precision values", kc_values),
                   ("--run end to end: HELD / FAILED / UNDETERMINED lines, values, write-once", verdicts_end_to_end),
                   ("verdict and P4 boundaries", verdict_boundaries), ("seed spread and KC_0 as the comparator", spread_and_seed),
                   ("bundle refusals (EVAL in a fit; registered counts)", refusals), ("rp12-r2-lane: lane guards", lane_paths)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
