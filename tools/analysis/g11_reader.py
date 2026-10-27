"""g11_reader.py: G11 of RP12 ARCH-V2-E-T (filing), item-level, on the keyed union readouts (READY_rp12_et C-7). ZERO calls.

REGISTRATION OF RECORD: docs/judge_v2_program.md L22028-L22060 (0a0361b): "G11 (filing; the INTERVAL decides both clauses,
conjunctive): P_fl = flatLeaf (source, domain) precision on union EVAL; D_fd = P_fl - P_descent, paired. HELD iff lower(P_fl) >=
0.75 AND lower(D_fd) > 0. FAILED iff upper(P_fl) < 0.75 OR upper(D_fd) <= 0. UNDETERMINED otherwise. The attenuation slope is
printed (descriptive)." Intervals: 95% percentile, CK-CLOSE-component bootstrap, B 2,000. Support: union EVAL 6,153 items in
5,642 components; DEFF 1.269 TRANSPORTED (re-measured and printed); n_eff 4,849; SE P_fl 0.00574 (at p 0.80), D_fd 0.00554
(discordance 0.158 transported); MDE80 0.0161 / 0.0155. P2: P_fl = 0.80 [0.77, 0.84]; D_fd = +0.08 [+0.05, +0.11]; G11 HELD:
0.85. F1 fires iff G11 FAILED.

WHY A NEW READER (C-7): the engine's MAIN_union_routing.csv aggregates count rows, and in a v2 build the held-out rows are EVAL
AND GATE (GATE sits in split.test) and twins are separate rows, so its Top-1 is never G11. This reader works per ITEM on the
item-keyed readouts (unionRoutingItemKey = true) of the two B0 grafts: graft_flatleaf and graft_descent.

RULES (declared; the same as rp12_pairing's P1-P3, imported from it, blob-pinned):
  - an item's cell under a rule = the modal leaf_dominant over its rows (ties to the smallest; unrouted = "<unrouted>");
    correct iff the cell equals its declared class (true_key); rows of one item with two classes refuse.
  - EVAL = the committed side export's EVAL items tagged mc6-2026-09-11; GATE rows are dropped and counted; a held-out row of
    a TRAIN item refuses. Both readouts must carry exactly the same EVAL item set, and it must be the registered 6,153 items in
    5,642 components, or the reader REFUSES (no read on another set).
  - the bootstrap draws whole CK-CLOSE components with replacement (numpy default_rng(20260929), B 2,000), the SAME draws for
    P_fl and D_fd; percentile rule bs[int(0.025 B)], bs[int(0.975 B) - 1] (flat_mix_mmlu.twin_boot_ci's, asserted equal in
    the selftest); SE = sd of the replicates; DEFF = SE^2 / (var / n); n_eff = n / DEFF; MDE80 = 2.80 x SE.
  - the attenuation slope is printed as OWED: the registration names it without defining it (the registrar defines it before
    G11 is scored); per-source P_fl is printed beside, descriptive.
    [CORRECTED 2026-09-30 rp12-et4 per ruling R-1 (390f9c6; READY_rp12_et3 D-16): the slope is printed "NOT COMPUTED (no
    pre-data definition; R-1, 390f9c6)"; it is never defined after data.]

  python tools/analysis/g11_reader.py --selftest
  python tools/analysis/g11_reader.py --dry-run --flatleaf <B0 graft_flatleaf>/seed_42/validation --descent <B0 graft_descent>/seed_42/validation
  python tools/analysis/g11_reader.py --run ... [--out experiment_results/archv2/rp12/g11_outcome.txt]    # write-once
The readouts are text files (no DB is opened).

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; X0 control survived): X1 the bar strict |
X2 HELD on P_fl alone | X3 FAILED needing both clauses | X4 the D_fd upper bound strict | X5 GATE rows kept as EVAL | X6 the
item-set equality removed | X7 the registered counts removed | X8 bootstrap by item | X9 the percentile index off by one | X10
F1 fired on UNDETERMINED | X11 descent correctness read from flatLeaf | X12 write-once removed: 12 of 12 killed.
[DELTA 2026-10-01 rp12-pair-mc, MC-EXCLUDE (orchestrator ruling; the default rule, no flag); insertion only] multi-class
items (rows under more than one declared class) are not scored: eval_correct takes rp12_pairing's exclusion (re-pinned) and
files it by side; both readouts must exclude the same EVAL items; the registered 6,153 / 5,642 are compared with the counts
BEFORE the exclusion; rp12_pairing.check_exclusion's 1% bar applies; the outcome prints the exclusion block (counts by side,
keys, the denominators after / before / registered) above SUPPORT, whose n is the post-exclusion one. Mutants (G0 control
survived): G1 the registered counts read after the exclusion, G2 the 1% bar not applied, G3 differing exclusions admitted, G4
the block omitted from the outcome, G5 GATE exclusions filed as EVAL: 5 of 5 killed.
[DELTA 2026-09-30 rp12-et3, READY_rp12_et2 D-11; insertion only] the SUPPORT line prints the mean component size n/G (registered
1.091) and names the Sum m^2 / Sum m ICC-1 bound beside it. Mutant D11 (n/G replaced by the bound): killed.
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): --flatleaf, --descent and --out of the other lane REFUSE; in lane r2 they must lie inside
experiment_configs/rp12_r2/ or experiment_results/archv2/rp12_r2/; the default outcome is
experiment_results/archv2/rp12_r2/g11_outcome.txt.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import sys
import io
import hashlib
import argparse
import contextlib
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[G11]"
PAIRING_PIN = ("rp12_pairing.py", "35214b3f11c3ffe4c1174885316f89775442f5c3")
N_EVAL, N_COMP = 6153, 5642
BOOT_B, BOOT_SEED = 2000, 20260929
BAR = 0.75
DEFF_T, SE_FL_REG, SE_D_REG, MDE_FL_REG, MDE_D_REG, DISC_T = 1.269, 0.00574, 0.00554, 0.0161, 0.0155, 0.158
P2_FL, P2_D = (0.77, 0.84), (0.05, 0.11)
OUT_DEFAULT = os.path.join(ROOT, "experiment_results", "archv2", "rp12", "g11_outcome.txt")


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _blob(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


_pp = os.path.join(HERE, PAIRING_PIN[0])
if _blob(_pp) != PAIRING_PIN[1]:
    refuse("%s is blob:%s, not the pinned blob:%s" % (_pp, _blob(_pp), PAIRING_PIN[1]))
import rp12_pairing as RP  # noqa: E402
import rp12_lane as LN  # noqa: E402


def eval_correct(validation, side, expect):
    """{item: (correct 0/1, declared class)} for the EVAL items of one keyed readout; and its counts."""
    held, disagree, uties, multi = RP.item_cells(RP.read_rows(os.path.join(validation, RP.QUERIES)))
    ex = RP.multi_by_side(multi, {}, side)          # MC-EXCLUDE (ruling 2026-10-01): multi-class items are not scored
    ev, gate = {}, 0
    for it, (cell, key, _n) in held.items():
        s = side.get(it, (None, "ABSENT"))[1]
        if s == "EVAL":
            ev[it] = (int(cell == key), key)
        elif s == "GATE":
            gate += 1
        else:
            refuse("%s: held-out row of item %s whose side is %s (a split defect)" % (validation, it, s))
    return ev, dict(gate_dropped=gate, disagree=disagree, unrouted_ties=uties, excluded=ex)


def boot_both(fl, d, groups, B=BOOT_B, seed=BOOT_SEED):
    """The SAME whole-component draws for P_fl and D_fd -> ((lo, hi, se) for fl, (lo, hi, se) for d)."""
    members = [np.flatnonzero(groups == g) for g in range(int(groups.max()) + 1)]
    rng = np.random.default_rng(seed)
    rf, rd = np.empty(B), np.empty(B)
    G = len(members)
    for b in range(B):
        idx = np.concatenate([members[g] for g in rng.integers(0, G, size=G)])
        rf[b], rd[b] = fl[idx].mean(), d[idx].mean()
    out = []
    for r in (rf, rd):
        s = sorted(float(x) for x in r)
        out.append((s[int(0.025 * B)], s[int(0.975 * B) - 1], float(r.std(ddof=1))))
    return out


def verdict(fl_lo, fl_hi, d_lo, d_hi):
    if fl_lo >= BAR and d_lo > 0:
        return "HELD"
    if fl_hi < BAR or d_hi <= 0:
        return "FAILED"
    return "UNDETERMINED"


def compute(flatleaf, descent, side, expect=(N_EVAL, N_COMP)):
    ef, cf = eval_correct(flatleaf, side, expect)
    ed, cd = eval_correct(descent, side, expect)
    if set(ef) != set(ed):
        refuse("the two readouts carry different EVAL item sets (flatLeaf %d, descent %d; only in flatLeaf %d, only in descent %d)"
               % (len(ef), len(ed), len(set(ef) - set(ed)), len(set(ed) - set(ef))))
    xf, xd = cf["excluded"], cd["excluded"]
    if set(xf["EVAL"]) != set(xd["EVAL"]):
        refuse("the two readouts exclude different multi-class EVAL items (flatLeaf %d, descent %d)" % (len(xf["EVAL"]), len(xd["EVAL"])))
    items = sorted(ef)
    comps = [side[i][0] for i in items]
    n_c = len(set(comps))
    # MC-EXCLUDE: the registered 6,153 / 5,642 are the counts BEFORE the exclusion; the 1% bar is rp12_pairing's
    n_b = len(items) + len(xf["EVAL"])
    c_b = len(set(comps) | {side[i][0] for i in xf["EVAL"]})
    if expect is not None and (n_b, c_b) != tuple(expect):
        refuse("the readouts carry %d EVAL items in %d components (before the multi-class exclusion), not the registered %d / %d"
               % ((n_b, c_b) + tuple(expect)))
    RP.check_exclusion(len(xf["EVAL"]), n_b, TAG)
    fl = np.array([ef[i][0] for i in items], dtype=np.float64)
    de = np.array([ed[i][0] for i in items], dtype=np.float64)
    d = fl - de
    _, groups = np.unique(np.array(comps), return_inverse=True)
    (fl_lo, fl_hi, fl_se), (d_lo, d_hi, d_se) = boot_both(fl, d, groups)
    n = len(items)
    def deff(se, x):
        v = float(x.var(ddof=1)) / n
        return se ** 2 / v if v > 0 else float("nan")
    per_src = {}
    for i, x in zip(items, fl):
        s = ef[i][1].split("/")[0]
        per_src.setdefault(s, []).append(x)
    kish = float((np.bincount(groups) ** 2).sum() / n)
    return dict(n=n, n_comp=n_c, n_before=n_b, c_before=c_b, excluded=xf, kish=kish, p_fl=float(fl.mean()), p_de=float(de.mean()), d=float(d.mean()),
                fl_ci=(fl_lo, fl_hi), d_ci=(d_lo, d_hi), fl_se=fl_se, d_se=d_se, fl_deff=deff(fl_se, fl), d_deff=deff(d_se, d),
                disc=float(np.mean(fl != de)), verdict=verdict(fl_lo, fl_hi, d_lo, d_hi), counts=dict(flatleaf=cf, descent=cd),
                per_source={s: (len(v), float(np.mean(v))) for s, v in sorted(per_src.items())})


def _band(x, band):
    return "HELD" if band[0] <= x <= band[1] else "FAILED"


def render(r, meta):
    o = []
    say = o.append
    say("POOL pv2_1575de61bb20e977 (union EVAL; the first line)")
    say("%s G11 filing, item level | registration docs/judge_v2_program.md L22028-L22060 (0a0361b)" % TAG)
    for k in sorted(meta):
        say("  %s: %s" % (k, meta[k]))
    for ln in RP.exclusion_lines(dict(r["excluded"], TRAIN={}), r["n"], r["n_comp"], r["n_before"], r["c_before"], TAG):
        say(ln)
    say("SUPPORT: %d EVAL items in %d CK-CLOSE components (registered %d / %d); mean component size n/G %.4f (registered 1.091);"
        " Sum m^2 / Sum m %.4f (the ICC-1 DEFF bound with variable sizes; READY_rp12_et2 D-11); GATE rows dropped: flatLeaf %d,"
        " descent %d; items with disagreeing rows: flatLeaf %d, descent %d; ties to <unrouted>: flatLeaf %d, descent %d"
        % (r["n"], r["n_comp"], N_EVAL, N_COMP, r["n"] / r["n_comp"], r["kish"], r["counts"]["flatleaf"]["gate_dropped"], r["counts"]["descent"]["gate_dropped"],
           r["counts"]["flatleaf"]["disagree"], r["counts"]["descent"]["disagree"], r["counts"]["flatleaf"]["unrouted_ties"],
           r["counts"]["descent"]["unrouted_ties"]))
    for name, se, deff, se_reg, mde_reg in (("P_fl", r["fl_se"], r["fl_deff"], SE_FL_REG, MDE_FL_REG), ("D_fd", r["d_se"], r["d_deff"], SE_D_REG, MDE_D_REG)):
        say("  %s: SE %.5f (registered %.5f); DEFF measured %.3f (transported %.3f); n_eff %.0f (registered 4,849); MDE80 %.4f"
            " (registered %.4f)" % (name, se, se_reg, deff, DEFF_T, r["n"] / deff if deff == deff and deff > 0 else float("nan"),
                                   2.80 * se, mde_reg))
    say("  discordance flatLeaf vs descent %.4f (transported %.3f)" % (r["disc"], DISC_T))
    say("P_fl = flatLeaf (source, domain) precision = %.4f  95%% [%.4f, %.4f] (components whole, B %d, seed %d)"
        % (r["p_fl"], r["fl_ci"][0], r["fl_ci"][1], BOOT_B, BOOT_SEED))
    say("P_descent = %.4f" % r["p_de"])
    say("D_fd = P_fl - P_descent = %+.4f  95%% [%+.4f, %+.4f] (paired, the same draws)" % (r["d"], r["d_ci"][0], r["d_ci"][1]))
    v = r["verdict"]
    if v == "HELD":
        say("G11: HELD (lower(P_fl) %.4f >= %.2f AND lower(D_fd) %+.4f > 0)" % (r["fl_ci"][0], BAR, r["d_ci"][0]))
    elif v == "FAILED":
        say("G11: FAILED (upper(P_fl) %.4f < %.2f OR upper(D_fd) %+.4f <= 0)" % (r["fl_ci"][1], BAR, r["d_ci"][1]))
    else:
        say("G11: UNDETERMINED (neither clause decides: P_fl [%.4f, %.4f], D_fd [%+.4f, %+.4f])" % (r["fl_ci"] + r["d_ci"]))
    say("F1: %s" % ("FIRES: it overturns 'the taxonomy buys filing' for the presented tree (MC-ROOT's id-disjoint 81.58% / +9.50pp"
                    " stays recorded, not revised)" if v == "FAILED" else "does not fire (G11 is not FAILED)"))
    say("P2 P_fl = 0.80 [0.77, 0.84]: observed %.4f -> %s" % (r["p_fl"], _band(r["p_fl"], P2_FL)))
    say("P2 D_fd = +0.08 [+0.05, +0.11]: observed %+.4f -> %s" % (r["d"], _band(r["d"], P2_D)))
    say("P2 G11 HELD (0.85): observed %s" % v)
    say("attenuation slope: NOT COMPUTED (no pre-data definition; R-1, 390f9c6)")
    say("per source (descriptive): " + "; ".join("%s n %d P_fl %.4f" % (s, n_, p) for s, (n_, p) in r["per_source"].items()))
    return o


def main(argv=None, out=print):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true"); g.add_argument("--run", action="store_true")
    ap.add_argument("--flatleaf"); ap.add_argument("--descent"); ap.add_argument("--side", default=os.path.join(ROOT, RP.EP.DEFAULT_SIDE))
    ap.add_argument("--out", default=None)
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    a.out = a.out or (OUT_DEFAULT if a.lane == "r1" else LN.out_path(a.lane, "g11_outcome.txt"))
    if not (a.flatleaf and a.descent):
        refuse("--flatleaf and --descent (the two graft validation dirs) are required")
    LN.guard(a.lane, [("--flatleaf", a.flatleaf), ("--descent", a.descent), ("--out", a.out)])     # rp12-r2-lane
    side, smeta = RP.sides(a.side)
    if a.dry_run:
        ef, cf = eval_correct(a.flatleaf, side, None)
        ed, cd = eval_correct(a.descent, side, None)
        out("POOL pv2_1575de61bb20e977 (dry-run: counts only, NO statistic)")
        out("%s flatLeaf EVAL items %d (GATE rows dropped %d); descent EVAL items %d (GATE rows dropped %d); same set: %s; registered %d / %d"
            % (TAG, len(ef), cf["gate_dropped"], len(ed), cd["gate_dropped"], set(ef) == set(ed), N_EVAL, N_COMP))
        for nm, c_ in (("flatLeaf", cf), ("descent", cd)):
            out("%s %s multi-class items EXCLUDED: EVAL %d %s, GATE %d %s" % (TAG, nm, len(c_["excluded"]["EVAL"]), sorted(c_["excluded"]["EVAL"]),
                                                                       len(c_["excluded"]["GATE"]), sorted(c_["excluded"]["GATE"])))
        return 0
    if os.path.exists(a.out):
        refuse("%s exists; the outcome is write-once" % a.out)
    r = compute(a.flatleaf, a.descent, side, expect=_EXPECT[0])
    meta = {"flatleaf_queries_sha256_lf": RP.sha_lf(os.path.join(a.flatleaf, RP.QUERIES)),
            "descent_queries_sha256_lf": RP.sha_lf(os.path.join(a.descent, RP.QUERIES)), "side_export": smeta["sha256_lf"],
            "script_blob": _blob(os.path.abspath(__file__))}
    text = "\n".join(render(r, meta)) + "\n"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    out(text.rstrip("\n"))
    return 0


_EXPECT = [(N_EVAL, N_COMP)]          # the selftest swaps in its fixture's expectation; nothing else writes it


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _write(val, rows):
    os.makedirs(val, exist_ok=True)
    head = ("true_key,true_source,rule,leaf_id,leaf_label,leaf_depth,leaf_dominant,leaf_purity,routed_source,routed_domain,top1,"
            "source_ok,domain_ok,item_id\n")
    body = "".join("%s,%s,r,%s,L,3,%s,0.9,S,%s,0,0,0,%s\n" % (k, k.split("/")[0], "L" if dom else "", dom, dom, it) for it, k, dom in rows)
    with open(os.path.join(val, RP.QUERIES), "w", encoding="utf-8", newline="\n") as f:
        f.write(head + body)


LANE_ERR = "is an object of lane %s, the run is lane %s"


def selftest():
    import tempfile, shutil; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="g11st_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def fixture(tmp, n=200, fl_ok=0.9, de_ok=0.7, gate=3, ncomp_div=2):
        """n EVAL items (2 per component), declared class A/x or B/y; flatLeaf correct on the first fl_ok share, descent on de_ok."""
        side, rf, rd = {}, [], []
        for i in range(n):
            it = "i:%04d" % i
            key = "A/x" if i % 2 else "B/y"
            wrong = "B/y" if key == "A/x" else "A/x"
            side[it] = ("c:%04d" % (i // ncomp_div), "EVAL")
            rf.append((it, key, key if i < fl_ok * n else wrong))
            rd.append((it, key, key if i < de_ok * n else wrong))
        for j in range(gate):
            it = "i:g%d" % j
            side[it] = ("c:g%d" % j, "GATE")
            rf.append((it, "A/x", "A/x")); rd.append((it, "A/x", "B/y"))
        fv, dv = os.path.join(tmp, "fl"), os.path.join(tmp, "de")
        _write(fv, rf); _write(dv, rd)
        return fv, dv, side, (n, n // ncomp_div)

    def held(tmp):
        fv, dv, side, exp = fixture(tmp)
        r = compute(fv, dv, side, expect=exp)
        assert (r["n"], r["n_comp"], abs(r["p_fl"] - 0.9) < 1e-12, abs(r["d"] - 0.2) < 1e-12) == (200, 100, True, True), r
        assert r["verdict"] == "HELD" and r["fl_ci"][0] >= 0.75 and r["d_ci"][0] > 0, r
        assert r["counts"]["flatleaf"]["gate_dropped"] == 3 and abs(r["disc"] - 0.2) < 1e-12
        # the percentile rule and the draws equal flat_mix_mmlu.twin_boot_ci's on the P_fl vector
        import sqlite3
        before = sqlite3.connect
        import flat_mix_mmlu as FM
        sqlite3.connect = getattr(sqlite3.connect, "_raw", before)
        fl = np.array([1.0 if i < 180 else 0.0 for i in range(200)])
        groups = np.arange(200) // 2
        assert FM.twin_boot_ci(fl, groups, B=BOOT_B, seed=BOOT_SEED) == boot_both(fl, fl * 0, groups)[0][:2]
        # the reader's own P_fl interval IS flat_mix_mmlu's whole-component interval on the fixture's items (components = i // 2)
        assert tuple(r["fl_ci"]) == FM.twin_boot_ci(fl, groups, B=BOOT_B, seed=BOOT_SEED), r["fl_ci"]
        # a continuous vector (no tied order statistics): the percentile indices themselves are pinned
        v = np.random.default_rng(11).uniform(size=200)
        assert boot_both(v, v * 0, groups)[0][:2] == FM.twin_boot_ci(v, groups, B=BOOT_B, seed=BOOT_SEED)
        t = "\n".join(render(r, {"x": "y"}))
        assert t.splitlines()[0] == "POOL pv2_1575de61bb20e977 (union EVAL; the first line)"
        assert "G11: HELD (lower(P_fl) %.4f >= 0.75 AND lower(D_fd) %+.4f > 0)" % (r["fl_ci"][0], r["d_ci"][0]) in t, t
        assert "F1: does not fire (G11 is not FAILED)" in t and "P2 P_fl = 0.80 [0.77, 0.84]: observed 0.9000 -> FAILED" in t
        assert "P2 D_fd = +0.08 [+0.05, +0.11]: observed +0.2000 -> FAILED" in t
        assert "attenuation slope: NOT COMPUTED (no pre-data definition; R-1, 390f9c6)" in t.splitlines() and "OWED" not in t, t
        assert "per source (descriptive): A n 100 P_fl 0.9000; B n 100 P_fl 0.9000" in t, t
        # D-11: both cluster-size figures, named (200 items in 100 components of 2: n/G 2.0000, Sum m^2 / Sum m 2.0000)
        assert "mean component size n/G 2.0000 (registered 1.091); Sum m^2 / Sum m 2.0000 (the ICC-1 DEFF bound" in t, t
        t2 = "\n".join(render(dict(r, n=6153, n_comp=5642, kish=1.2), {}))
        assert "mean component size n/G 1.0906 (registered 1.091); Sum m^2 / Sum m 1.2000 (the ICC-1 DEFF bound" in t2, t2

    def failed(tmp):
        fv, dv, side, exp = fixture(tmp, fl_ok=0.6, de_ok=0.5)          # P_fl 0.60: upper < 0.75
        r = compute(fv, dv, side, expect=exp)
        assert r["verdict"] == "FAILED" and r["fl_ci"][1] < 0.75, r
        t = "\n".join(render(r, {}))
        assert "G11: FAILED (upper(P_fl)" in t and "F1: FIRES" in t, t
        os.makedirs(os.path.join(tmp, "b"))
        fv2, dv2, side2, exp2 = fixture(os.path.join(tmp, "b"), fl_ok=0.9, de_ok=0.95)   # descent better: upper(D_fd) <= 0
        r2 = compute(fv2, dv2, side2, expect=exp2)
        assert r2["verdict"] == "FAILED" and r2["d_ci"][1] <= 0, r2

    def undetermined(tmp):
        fv, dv, side, exp = fixture(tmp, n=200, fl_ok=0.76, de_ok=0.70)   # P_fl 0.76: the interval straddles 0.75
        r = compute(fv, dv, side, expect=exp)
        assert r["verdict"] == "UNDETERMINED" and r["fl_ci"][0] < 0.75 <= r["fl_ci"][1], r
        tu = "\n".join(render(r, {}))
        assert "G11: UNDETERMINED (neither clause decides" in tu and "F1: does not fire (G11 is not FAILED)" in tu, tu

    def boundaries(tmp):
        assert verdict(0.75, 0.8, 0.001, 0.1) == "HELD"
        assert verdict(0.7499, 0.8, 0.001, 0.1) == "UNDETERMINED"
        assert verdict(0.76, 0.8, 0.0, 0.1) == "UNDETERMINED"
        assert verdict(0.6, 0.7499, 0.1, 0.2) == "FAILED" and verdict(0.6, 0.75, 0.1, 0.2) == "UNDETERMINED"
        assert verdict(0.8, 0.9, -0.1, 0.0) == "FAILED"
        assert _band(0.77, P2_FL) == "HELD" and _band(0.84, P2_FL) == "HELD" and _band(0.8401, P2_FL) == "FAILED"

    def refusals(tmp):
        fv, dv, side, exp = fixture(tmp)
        try:
            compute(fv, dv, side, expect=(6153, 5642))
            raise AssertionError("counts not refused")
        except SystemExit as e:
            assert str(e) == ("%s REFUSED: the readouts carry 200 EVAL items in 100 components (before the multi-class exclusion), not"
                              " the registered 6153 / 5642" % TAG), e
        side2 = dict(side); side2["i:0003"] = ("c:x", "TRAIN")
        try:
            compute(fv, dv, side2, expect=None)
            raise AssertionError("TRAIN held-out not refused")
        except SystemExit as e:
            assert "held-out row of item i:0003 whose side is TRAIN" in str(e), e
        rows = open(os.path.join(dv, RP.QUERIES)).read().splitlines()
        with open(os.path.join(dv, RP.QUERIES), "w", newline="\n") as f:
            f.write("\n".join(rows[:-4]) + "\n")                      # descent loses an EVAL item
        try:
            compute(fv, dv, side, expect=None)
            raise AssertionError("different sets not refused")
        except SystemExit as e:
            assert "the two readouts carry different EVAL item sets (flatLeaf 200, descent 199" in str(e), e

    def mc_exclude(tmp):
        """MC-EXCLUDE through compute() and render(): one EVAL and one GATE multi-class item in both readouts are not scored;
        the registered counts are read before the exclusion; the lines by value; the 1% bar; different exclusions refuse."""
        fv, dv, side, exp = fixture(tmp)
        side["i:m1"] = ("c:m1", "EVAL"); side["i:m2"] = ("c:m2", "GATE")
        for v in (fv, dv):
            with open(os.path.join(v, RP.QUERIES), "a", encoding="utf-8", newline="\n") as f:
                # the multi-class EVAL item is filed CORRECTLY by flatLeaf and WRONGLY by descent under its first class:
                # re-included, it would move P_fl, D_fd and n
                f.write("A/x,A,r,L,L,3,A/x,0.9,S,A/x,0,0,0,i:m1\nB/y,B,r,L,L,3,%s,0.9,S,B/y,0,0,0,i:m1\n" % ("A/x" if v == fv else "B/y"))
                f.write("A/x,A,r,L,L,3,A/x,0.9,S,A/x,0,0,0,i:m2\nB/y,B,r,L,L,3,A/x,0.9,S,A/x,0,0,0,i:m2\n")
        r = compute(fv, dv, side, expect=(201, 101))
        assert (r["n"], r["n_comp"], r["n_before"], r["c_before"]) == (200, 100, 201, 101), r
        assert abs(r["p_fl"] - 0.9) < 1e-12 and abs(r["d"] - 0.2) < 1e-12 and r["counts"]["flatleaf"]["gate_dropped"] == 3, r
        t = "\n".join(render(r, {}))
        assert "%s MULTI-CLASS ITEMS EXCLUDED (orchestrator ruling 2026-10-01; every per-item pairing readout that excludes: G11" \
               " D_fd, G13 D13 (G14: disclosure only, ruling (b))): EVAL 1, GATE 1, TRAIN 0" % TAG in t and ", G14):" not in t, t
        assert "%s   excluded EVAL i:m1 ['A/x', 'B/y']" % TAG in t and "%s   excluded GATE i:m2 ['A/x', 'B/y']" % TAG in t, t
        assert "%s DENOMINATORS: EVAL 200 items in 100 components after the exclusion (before 201 / 101; registered 6153 / 5642);" \
               " EVAL excluded 1 of 201 = 0.4975%% (bar: refused above 1%%)" % TAG in t, t
        try:
            compute(fv, dv, side, expect=(200, 100))
            raise AssertionError("post-exclusion counts accepted as the registered ones")
        except SystemExit as e:
            assert "carry 201 EVAL items in 101 components (before the multi-class exclusion), not the registered 200 / 100" in str(e), e
        # descent lacks the multi-class item entirely: the kept sets agree, the exclusions do not -> REFUSED
        rows = [l for l in open(os.path.join(dv, RP.QUERIES), encoding="utf-8").read().splitlines() if not l.endswith(",i:m1")]
        with open(os.path.join(dv, RP.QUERIES), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(rows) + "\n")
        try:
            compute(fv, dv, side, expect=None)
            raise AssertionError("different exclusions not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: the two readouts exclude different multi-class EVAL items (flatLeaf 1, descent 0)" % TAG, e
        # the 1% bar: 1 multi-class EVAL item beside 50 kept (1 of 51) REFUSES
        os.makedirs(os.path.join(tmp, "s"))
        fv3, dv3, side3, _e3 = fixture(os.path.join(tmp, "s"), n=50)
        side3["i:m1"] = ("c:m1", "EVAL")
        for v in (fv3, dv3):
            with open(os.path.join(v, RP.QUERIES), "a", encoding="utf-8", newline="\n") as f:
                f.write("A/x,A,r,L,L,3,A/x,0.9,S,A/x,0,0,0,i:m1\nB/y,B,r,L,L,3,A/x,0.9,S,A/x,0,0,0,i:m1\n")
        try:
            compute(fv3, dv3, side3, expect=None)
            raise AssertionError("1 of 51 not refused")
        except SystemExit as e:
            assert str(e) == ("%s REFUSED: 1 of 51 EVAL items (1.9608%%) carry more than one declared class; the exclusion rule admits"
                              " at most 1%%" % TAG), e

    def lane_paths(tmp):
        r1v, r2v = "experiment_results/archv2/rp12/B0/graft_flatleaf/seed_42/validation", "experiment_results/archv2/rp12_r2/B0/graft_flatleaf/seed_42/validation"
        for argv, needle in ((["--dry-run", "--lane", "r2", "--flatleaf", r1v, "--descent", r2v], "--flatleaf %s %s" % (r1v, LANE_ERR % ("r1", "r2"))),
                             (["--dry-run", "--flatleaf", r2v, "--descent", r2v], "--flatleaf %s %s" % (r2v, LANE_ERR % ("r2", "r1"))),
                             (["--run", "--lane", "r2", "--flatleaf", r2v, "--descent", r2v, "--out", os.path.join(tmp, "o.txt")], "is outside lane r2's roots"),
                             (["--run", "--lane", "r2", "--flatleaf", r2v, "--descent", r2v, "--out", OUT_DEFAULT], LANE_ERR % ("r1", "r2"))):
            try:
                main(argv, out=lambda x: None)
                raise AssertionError("not refused: %s" % argv)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e))
        assert OUT_DEFAULT == os.path.join(ROOT, "experiment_results", "archv2", "rp12", "g11_outcome.txt")

    def cli(tmp):
        fv, dv, side, exp = fixture(tmp)
        sp = os.path.join(tmp, "side.tsv")
        from data_v2 import split as S
        rows = sorted((it, c, s, "S", "d", "mc6-2026-09-11") for it, (c, s) in side.items())
        with open(sp, "w", encoding="utf-8", newline="\n") as f:
            f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (S.SIDE_EXPORT_FORMAT, S._side_rows_sha(rows), len(rows), "0" * 64))
            f.write("\t".join(S.SIDE_COLS) + "\n" + "".join("\t".join(r) + "\n" for r in rows))
        out_p = os.path.join(tmp, "o.txt")
        _EXPECT[0] = exp
        try:
            lines = []
            assert main(["--dry-run", "--flatleaf", fv, "--descent", dv, "--side", sp], out=lines.append) == 0
            assert lines[1] == "%s flatLeaf EVAL items 200 (GATE rows dropped 3); descent EVAL items 200 (GATE rows dropped 3); same set: True;" \
                " registered 6153 / 5642" % TAG, lines
            with contextlib.redirect_stdout(io.StringIO()):
                assert main(["--run", "--flatleaf", fv, "--descent", dv, "--side", sp, "--out", out_p], out=lambda s: None) == 0
            assert any(l.startswith("G11: HELD") for l in open(out_p).read().splitlines())
            try:
                main(["--run", "--flatleaf", fv, "--descent", dv, "--side", sp, "--out", out_p], out=lambda s: None)
                raise AssertionError("write-once not refused")
            except SystemExit as e:
                assert str(e).endswith("exists; the outcome is write-once"), e
        finally:
            _EXPECT[0] = (N_EVAL, N_COMP)

    for nm, fn in [("HELD: values, lines, the bootstrap equals flat_mix_mmlu's", held), ("FAILED on either clause; F1 fires", failed),
                   ("UNDETERMINED when P_fl straddles the bar", undetermined), ("verdict and P2 boundaries", boundaries),
                   ("refusals: counts, a TRAIN held-out row, different item sets", refusals),
                   ("MC-EXCLUDE: not scored, counts before the exclusion, lines by value, the 1% bar", mc_exclude),
                   ("CLI end to end: dry-run counts, run, write-once", cli),
                   ("rp12-r2-lane: R1 and R2 paths never mixed; lane r2's default outcome path", lane_paths)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
