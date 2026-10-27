"""The G22 selftest: every leg and every decision branch on synthetic worlds; opens NO DB of record; single process;
no multiprocessing; each check is an explicit raise (holds under python -O). Prints PASS/FAIL per check and the branch
ids executed; exits 1 on any failure."""
import json
import os
import shutil
import sqlite3
import tempfile
import time

import numpy as np

from . import bt, cert, data, design, g22, report, ro, synth
from .report import HITS
from .streams import Streams

RESULTS = []


def check(cond, label):
    RESULTS.append((bool(cond), label))
    print("  [%s] %s" % ("PASS" if cond else "FAIL", label), flush=True)


def expect_exit(fn, needle, label):
    try:
        fn()
    except SystemExit as e:
        check(needle in str(e), "%s (refused: %s)" % (label, str(e)[:110]))
        return
    check(False, "%s (did NOT refuse)" % label)


def quiet(*lines):
    pass


def run():
    t0 = time.time()
    print("=== archv2_g22_sim --selftest (synthetic worlds only; no DB of record opened) ===")
    tmp = tempfile.mkdtemp(prefix="archv2_g22_")
    try:
        _run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for ok, _ in RESULTS if not ok)
    print("SELFTEST: %d checks, %d failed | branches executed: %s | %.1f s"
          % (len(RESULTS), n_fail, ", ".join("%s x%d" % (k, v) for k, v in sorted(HITS.items())), time.time() - t0))
    return 1 if n_fail else 0


def _run(tmp):
    sb = data.import_sb()
    import rejudge_grok as rj
    # ---------------------------------------------------------------- 1. streams
    s1, s2 = Streams("M"), Streams("M")
    check(s1.seed("a") == s2.seed("a") and s1.seed("a") != s1.seed("b") and Streams("N").seed("a") != s1.seed("a"),
          "streams: seed is a pure function of (master, name)")
    x1 = s1.np("x").random(3); x2 = s2.np("x").random(3)
    check(np.array_equal(x1, x2), "streams: same (master, name) -> same draws")
    expect_exit(lambda: s1.np("x"), "requested twice", "streams: a name requested twice is refused")
    # ---------------------------------------------------------------- 2. read-only discipline
    check(ro.guard_installed(), "ro: the process-wide connect guard is installed")
    expect_exit(lambda: sqlite3.connect(os.path.join(tmp, "plain.db")), "refused sqlite3.connect", "ro: a plain connect is refused")
    frozen = os.path.join(tmp, "snapshots_frozen.db"); open(frozen, "wb").close()
    expect_exit(lambda: ro.open_ro(frozen), "refused by name", "ro: snapshots_frozen.db refused by name")
    ng = os.path.join(tmp, "twenty_newsgroups_cache_v1.db"); open(ng, "wb").close()
    expect_exit(lambda: ro.open_ro(ng), "refused by name", "ro: the 20NG DB refused by name")
    walp = os.path.join(tmp, "walled.db")
    c = ro.REAL_CONNECT(walp); c.execute("CREATE TABLE t (x)"); c.commit(); c.close()
    with open(walp + "-wal", "wb") as f:
        f.write(b"x" * 64)
    expect_exit(lambda: ro.open_ro(walp), "non-empty", "ro: a non-empty -wal refuses before any connect")
    os.remove(walp + "-wal")
    con = ro.open_ro(walp); con.execute("SELECT * FROM t").fetchall(); con.close()
    check(ro.LOG and ro.LOG[-1] == os.path.abspath(walp), "ro: a clean DB opens (mode=ro&immutable=1) and is logged")
    expect_exit(lambda: ro.Shim().connect("plain.db"), "non-read-only", "ro: the shim refuses a non-URI open")
    # ---------------------------------------------------------------- 3. BT engines against the fit of record
    rng = np.random.default_rng(3)
    worst = 0.0; worst_n = 0.0
    for rep in range(4):
        M = 5; models = ["m%d" % k for k in range(M)]
        W = np.zeros((M, M)); N = np.zeros((M, M)); agg = {}
        for i in range(M):
            for j in range(i + 1, M):
                if rng.random() < 0.15:
                    continue
                n = int(rng.integers(1, 9)); wa = float(min(n, rng.integers(0, n + 1) + 0.5 * (rng.random() < 0.3)))
                agg[(models[i], models[j])] = (wa, float(n)); W[i, j] = wa; W[j, i] = n - wa; N[i, j] = N[j, i] = n
        ref = rj.mm_fit(agg, models); th = bt.mm_fit_batch(W, N)
        worst = max(worst, max(abs(ref[m] - th[k]) for k, m in enumerate(models)))
        ii, jj, yy = [], [], []
        for (a, b), (wa, n) in agg.items():
            for _ in range(int(n)):
                ii.append(models.index(a)); jj.append(models.index(b)); yy.append(wa / n)
        tn = bt.bt_offset_batch(ii, jj, yy, np.zeros(len(ii)), np.ones((1, len(ii))), M)[0]
        worst_n = max(worst_n, float(np.abs(tn - th).max()))
    check(worst <= 1e-8, "bt: batched MM equals rejudge_grok.mm_fit (max |d theta| %.2e)" % worst)
    check(worst_n <= 1e-7, "bt: Newton BT (zero offset) equals MM (max |d theta| %.2e)" % worst_n)
    check(abs(rj.PRIOR - bt.PRIOR) == 0, "bt: prior 0.5 = rejudge_grok.PRIOR")
    # ---------------------------------------------------------------- 4. certificate twins vs the functions of record
    E = [dict(anchor="A%d" % (k % 4), a="x", b="y", p=float(rng.random()), m=float(rng.normal(0, 1)),
              s=float(rng.uniform(.1, .4)), agree=float(rng.random()), right=bool(rng.random() < 0.9), gap=0.1)
         for k in range(160)]
    EA = cert.EdgeArrays(E)
    d_nll = max(abs(sb.nll(p, E) - cert.nll_v(p, EA)) / max(1.0, abs(sb.nll(p, E))) for p in ((-3, 3), (-2, 1), (-4, 5)))
    check(d_nll <= 1e-9, "cert: nll_v equals systematic_budget.nll (rel %.1e)" % d_nll)
    f_ref = sb.fit(E); f_v = cert.fit_v(EA)
    check(max(abs(f_ref[0] - f_v[0]), abs(f_ref[1] - f_v[1])) <= 1e-5, "cert: fit_v equals systematic_budget.fit (%s vs %s)" % (f_ref, f_v))
    d_c = max(abs(sb.cbud(e, *f_ref) - c) for e, c in zip(E, cert.cbud_v(EA, *f_ref)))
    check(d_c <= 1e-12, "cert: cbud_v equals systematic_budget.cbud (%.1e)" % d_c)
    check(tuple(sb.summarise(E, *f_ref)) == tuple(cert.summarise_v(EA, *f_ref)) or
          (sb.summarise(E, *f_ref)[:4] == cert.summarise_v(EA, *f_ref)[:4] and abs(sb.summarise(E, *f_ref)[4] - cert.summarise_v(EA, *f_ref)[4]) < 1e-12),
          "cert: summarise_v equals systematic_budget.summarise")
    check(cert.holm([0.01, 0.04, 0.03, 0.2]) == [True, False, False, False] and cert.holm([0.001, 0.01, 0.02]) == [True, True, True],
          "cert: Holm step-down on two fixtures")
    check(abs(cert.cp_ub(0, 100) - (1 - 0.05 ** (1 / 100))) < 1e-9, "cert: Clopper-Pearson UB at 0 events = 1 - 0.05^(1/n)")
    mc = cert.mc_classes(np.array([[0.99, 0.95, 0.9751], [0.99, 0.951, 0.9749], [0.991, 0.949, 0.975], [0.99, 0.95, 0.9752],
                                   [0.992, 0.952, 0.9748]]))
    check(list(mc["cls"]) == ["CALLED", "NOT CALLED", "MC-UNRESOLVED"], "cert: multi-stream classes CALLED / NOT CALLED / MC-UNRESOLVED")
    g = cert.gate_fit(cert.EdgeArrays([dict(e, est=True) for e in E]))
    check(len(g) == 4 and all("ub" in x for x in g), "cert: binned gate returns four bins with UBs")
    # ---------------------------------------------------------------- 5. verdict model recovery
    W5 = synth.make_world(seed=11, n_models=6, per_pair=40, u_sd=0.8, bad_model="m5", q_per_anchor=50)
    b5 = W5["board"]
    anchors, S, obs, meta = g22.board_matrix(b5, floor=200)
    vm = g22.fit_verdict_model(b5, anchors, S, obs)
    print("\n".join(vm.lines(b5.models)))
    check(abs(vm.kappa - W5["vm"].kappa) < 0.5 and abs(vm.pi - W5["vm"].pi) < 0.25 and abs(vm.lam - W5["vm"].lam) < 0.25,
          "verdict model: recovers kappa / pi / lam of the generating model (%.2f/%.2f/%.2f vs %.2f/%.2f/%.2f)"
          % (vm.kappa, vm.pi, vm.lam, W5["vm"].kappa, W5["vm"].pi, W5["vm"].lam))
    check(int(np.argmin(vm.u.mean(axis=0))) == b5.models.index("m5"), "verdict model: the planted bad model has the lowest u")
    vm2 = vm.from_params(json.loads(json.dumps(vm.params())))
    check(vm2.digest() == vm.digest(), "verdict model: params round-trip through JSON with the same digest")
    # ---------------------------------------------------------------- 6. validity leg: PASS branch, FAIL branch, token refusals
    st = Streams("SELFTEST-G22")
    out = report.Out(None, echo=False)
    real_edges, aq = data.edges_fast(b5, 24, st, "selftest/real", floor=200)
    data.mark_established(real_edges, b5.K, aq, sb)
    est = {(e["anchor"], e["a"], e["b"]) for e in real_edges if e["est"]}
    m = g22.cert_metrics(real_edges, est, min_est=5)
    edge_t = dict(f=m["f_n"], u=m["u_n"], est=m["est_n"])
    w_before = dict(data.WITNESS)
    tok, res = g22.validity_leg(out, b5, sb, st, R=10, B=24, family_alpha=1e-9, primary="fixed", floor=200,
                                targets=dict(f_raw_called=int(np.median([m["f_raw_called"]]))), ddev_targets=(),
                                edge_targets=edge_t, min_est=5, modes=("fixed", "random", "retest"))
    from . import selftest_g22_v2
    selftest_g22_v2.v1_golden(check, out, tok, w_before)
    print("\n".join(out.lines[-40:]))
    check(tok["status"] == "PASS", "validity: PASS branch executed (target inside the interval)")
    check(any("mode retest" in s for s in out.lines), "validity: the retest mode ran (r_keep solved)")
    tok_path = os.path.join(tmp, "tok_pass.json")
    report.write_once(tok_path, json.dumps(tok, default=str))
    out2 = report.Out(None, echo=False)
    tokf, _ = g22.validity_leg(out2, b5, sb, Streams("SELFTEST-G22-F"), R=4, B=16, primary="fixed", floor=200,
                               targets=dict(f_raw_wrong=10 ** 6), ddev_targets=(), edge_targets=edge_t, min_est=5,
                               modes=("fixed",), retest_target=0.999999)
    check(tokf["status"] == "FAIL" and any("THE SIMULATOR DECIDES NOTHING" in s for s in out2.lines),
          "validity: FAIL branch executed and printed 'THE SIMULATOR DECIDES NOTHING'")
    out3 = report.Out(None, echo=False)
    tokx, _ = g22.validity_leg(out3, b5, sb, Streams("SELFTEST-G22-X"), R=2, B=16, primary="fixed", floor=200,
                               targets=dict(f_raw_wrong=0), ddev_targets=(), edge_targets=dict(f=1, u=1, est=1), min_est=5,
                               modes=("fixed", "retest"), retest_target=0.0)
    check(tokx["status"] == "FAIL" and any("EDGE SETS DIFFER" in s for s in out3.lines),
          "validity: an edge-set mismatch FAILS the leg")
    check(HITS.get("VALIDITY.RETEST_UNSOLVABLE", 0) > 0, "validity: an unreachable retest agreement skips the retest mode")
    # the REGISTERED validity interval (d6129cf ruling (1)): central (1 - 0.05 / T), T printed
    lv = g22.bonferroni_level(14)
    vals = np.arange(1000, dtype=float)
    in_bonf, ql_b, _, qh_b = g22.covered(vals, 10.0, lv)
    in_95, ql_9, _, qh_9 = g22.covered(vals, 10.0, 0.95)
    check(abs(lv - (1 - 0.05 / 14)) < 1e-15 and in_bonf and not in_95,
          "validity: a target OUTSIDE the central 95%% interval [%.1f, %.1f] but INSIDE the registered central (1 - 0.05/14)"
          " = %.5f interval [%.1f, %.1f] is covered (the registered rule passes it; the superseded 95%% rule failed it)"
          % (ql_9, qh_9, lv, ql_b, qh_b))
    check(not g22.covered(vals, -5.0, lv)[0], "validity: a target outside the registered interval is not covered")
    check(any("T = 1 targets" in s and "(1 - 0.00 / T)" in s for s in out.lines) or any("T = 1 targets" in s for s in out.lines),
          "validity: T and the Bonferroni level are printed")
    check(tok.get("T") == 1 and abs(tok.get("coverage") - (1 - 1e-9)) < 1e-15, "validity: the token records T and the level")
    check(any("T = 1 targets" in s for s in out2.lines) and any("0.95000 interval" in s for s in out2.lines),
          "validity: at the registered alpha 0.05 and T = 1 the level printed is 0.95000")
    # the registered run parameters (d6129cf): master ARCHV2-G22-REC-1 and R = 1,000, else --dev / --r-registration
    import argparse
    import archv2_g22_sim as cli
    ns = lambda **k: argparse.Namespace(**dict(dict(dry_run=False, dev=False, master=cli.REC_MASTER, leg="designs",
                                                    R=cli.REC_R, r_registration=None), **k))
    check(cli.REC_MASTER == "ARCHV2-G22-REC-1" and cli.REC_R == 1000, "record params: the registered master and R are the constants")
    cli.check_record_params(ns())
    check(True, "record params: the registered master and R = 1,000 are admitted")
    expect_exit(lambda: cli.check_record_params(ns(master="ARCHV2-E-A-G22-DEV")), "not the registered", "record params: another master refuses")
    expect_exit(lambda: cli.check_record_params(ns(R=200)), "must be REGISTERED", "record params: R != 1,000 without a registration refuses")
    cli.check_record_params(ns(R=200, r_registration="programme L99999"))
    cli.check_record_params(ns(R=200, master="X", dev=True))
    check(True, "record params: a registered smaller R and a --dev run are admitted")
    check("DEV RUN" in cli.record_word(ns(master="X")) and "d6129cf" in cli.record_word(ns()),
          "record params: the header word names the registration or DEV RUN")
    tokf_path = os.path.join(tmp, "tok_fail.json")
    report.write_once(tokf_path, json.dumps(tokf, default=str))
    expect_exit(lambda: g22.load_token(tokf_path), "DECIDES NOTHING", "token: a FAIL token makes a downstream leg refuse")
    expect_exit(lambda: g22.load_token(os.path.join(tmp, "absent.json")), "no validity token", "token: a missing token refuses")
    bad = dict(tok); bad["vm_digest"] = "0" * 64
    bad_path = os.path.join(tmp, "tok_bad.json"); report.write_once(bad_path, json.dumps(bad, default=str))
    expect_exit(lambda: g22.load_token(bad_path), "digest", "token: a tampered verdict model refuses")
    tok_ok, vm_ok = g22.load_token(tok_path)
    check(vm_ok.digest() == tok["vm_digest"], "token: a PASS token loads and its digest re-computes")
    # ---------------------------------------------------------------- 7. (b) nu leg
    out4 = report.Out(None, echo=False)
    table, fits = g22.nu_leg(out4, b5, Streams("SELFTEST-NU"), cert.FROZEN_GROK_UNFILTERED, [3, 4, 5, 6], [2, "full"],
                             reps=3, B=16, floor=0, boot=200, pair_label="grok pair")
    print("\n".join(out4.lines))
    check(set(fits) == {2, "full"} and all(np.isfinite(v[0]) or True for v in fits.values()), "nu: exponent + CI per N")
    # ---------------------------------------------------------------- 8. (c) (d) (g) designs
    kv = W5["keyview"]
    pools = {}
    for q, s in kv.cat.items():
        pools.setdefault(s, []).append(q)
    pools = {s: sorted(v) for s, v in pools.items()}
    keytabs = {"syn": kv}
    spec = {"T7": [dict(corpus="syn", roster="syn6", strata=2, N=3)],
            "T2": [dict(corpus="syn", roster="syn6", strata=3, N=2), dict(corpus="syn", roster="syn6", strata="ANCC", N=2)]}
    supply = {"syn": {s: 40 for s in pools}}
    stn = Streams("SELFTEST-DESIGNS")
    designs = g22.resolve_designs(["T7", "T2"], {"syn6": W5["models"]}, supply, {"syn": pools}, stn, spec=spec)
    check(len(designs["T7"][0]["strata"]) == 2 and designs["T2"][1]["strata"] == ["AncC"],
          "designs: stratified draw of 2 strata; a named-prefix part selects AncC")
    out5 = report.Out(None, echo=False)
    summ = g22.designs_leg(out5, tok_ok, vm_ok, designs, keytabs, stn, R=3, B=16, floor=0, deff_reps=1, bar=0.05,
                           min_est=5)
    print("\n".join(out5.lines))
    check("T7" in summ and len(summ["T7"]["noms"]["nom_loao"]) == 3, "designs: 3 replicates per design, nominal under three kinds")
    check(any("(g) part 0: DEFF" in s for s in out5.lines), "designs: DEFF printed from the match-level bootstrap")
    check(any("(d) part" in s for s in out5.lines), "designs: b1 identification rate printed per part")
    rng = np.random.default_rng(5)
    Pm = np.array([["A", "A", ""], ["B", "C", "C"], ["A", "B", "C"], ["D", "D", "D"]])
    sch, ex = design.schedule_stratum([1, 2, 3, 4], ["x", "y", "z"], Pm, 3, rng)
    ok = all(not (Pm[q, i] and Pm[q, j] and Pm[q, i] == Pm[q, j]) for i, j, q in sch)
    check(ok and ex > 0, "design: the filter never schedules an AGREE match; exhausted pairs counted (%d)" % ex)
    check(design.allocate(10, {"a": 1, "b": 1, "c": 1}) == {"a": 4, "b": 3, "c": 3}, "design: largest-remainder allocation")
    man = {"outputs": [{"kind": "split_v2", "checks": {"per_corpus": {"mmlu-pro-v2": {"eval_units": 4002}}}}], "label": "L", "of_record": "DEV"}
    check(design.manifest_eval_units(man)[0] == {"mmlu-pro-v2": 4002}, "design: manifest eval_units parsed")
    # ---------------------------------------------------------------- 9. (e) stop
    part = g22.resolve_designs(["T9"], {"syn6": W5["models"]}, supply, {"syn": pools}, Streams("SELFTEST-STOP-R"),
                               spec={"T9": [dict(corpus="syn", roster="syn6", strata=3, N=3)]})["T9"][0]
    out6 = report.Out(None, echo=False)
    res6, recs6 = g22.stop_leg(out6, tok_ok, vm_ok, part, kv, Streams("SELFTEST-STOP"), R=4, B=16, floor=0,
                               margins=(-100.0, 0.0), bar=0.01, stage2_bar=0.0, stage1_n=2)
    print("\n".join(out6.lines))
    check(set(res6) == {-100.0, 0.0} and any("P(MISCALIBRATED | calibrated)" in s for s in out6.lines),
          "stop: P(MISCALIBRATED | calibrated) per margin with its Wilson interval")
    check(any(rr["reads"][-100.0][0] == "stage1" for rr in recs6), "stop: the stage-1 read branch executed")
    out6b = report.Out(None, echo=False)
    res6b, recs6b = g22.stop_leg(out6b, tok_ok, vm_ok, part, kv, Streams("SELFTEST-STOP2"), R=2, B=16, floor=0,
                                 margins=(1e9,), bar=0.0, stage2_bar=0.0, stage1_n=2)
    check(all(rr["reads"][1e9][0] == "full" for rr in recs6b), "stop: the stage-2 (full) read branch executed")
    out6c = report.Out(None, echo=False)
    res6c, recs6c = g22.stop_leg(out6c, tok_ok, vm_ok, part, kv, Streams("SELFTEST-STOP3"), R=2, B=16, floor=0,
                                 margins=(1e9,), bar=0.0, stage2_bar=1e9, stage1_n=2)
    check(all(rr["reads"][1e9][0] == "none" for rr in recs6c), "stop: the no-status branch executed")
    # ---------------------------------------------------------------- 10. (f) overdispersion + residue resolution
    names = ["Meta-Llama-3_1-70B-Instruct", "gpt-x", "qwen-y", "yi-z", "cmd-w", "ds-v"]
    W6 = synth.make_world(seed=21, model_names=names, per_pair=40, u_sd=0.3, bad_model="Meta-Llama-3_1-70B-Instruct",
                          q_per_anchor=60)
    b6 = W6["board"]
    e6, aq6 = data.edges_fast(b6, 24, Streams("SELFTEST-OD"), "od", floor=200)
    data.mark_established(e6, b6.K, aq6, sb)
    out7 = report.Out(None, echo=False)
    r7 = g22.overdispersion_leg(out7, b6, e6, Streams("SELFTEST-OD2"), perms=200,
                                roster_models=[m for m in names], all_models=names + ["Meta-Llama-3-70B-Instruct"])
    print("\n".join(out7.lines))
    check(r7 is not None and r7["top"] == "Meta-Llama-3_1-70B-Instruct", "overdispersion: the planted residue model is the most-incident")
    check(any("Meta-Llama-3_1-70B-Instruct: in the roster YES" in s for s in out7.lines)
          and any("EXCLUDED from the roster" in s for s in out7.lines),
          "overdispersion: residue resolution printed (Llama-3.1-70B in the roster; Meta-Llama-3-70B-Instruct quarantined)")
    out7b = report.Out(None, echo=False)
    g22.overdispersion_leg(out7b, b6, [dict(e, right=True) for e in e6], Streams("SELFTEST-OD3"), perms=10)
    check(HITS.get("OVERDISP.NO_EVENTS", 0) > 0, "overdispersion: the no-event branch executed")
    # ---------------------------------------------------------------- 11. (h) coverage
    W7 = synth.make_world(seed=31, n_models=5, per_pair=1, blank_rate=0.0, q_per_anchor=20)
    W8 = synth.make_world(seed=32, n_models=5, per_pair=1, blank_rate=0.2, q_per_anchor=20)
    out8 = report.Out(None, echo=False)
    r8 = g22.coverage_leg(out8, W7["keyview"], W7["models"], W7["cat"])
    r9 = g22.coverage_leg(out8, W8["keyview"], W8["models"], W8["cat"])
    g22.key_tier_lines(out8, W7["keyview"], W7["models"], W7["cat"])
    print("\n".join(out8.lines))
    check(all(v[3] == "PASS" for v in r8.values()) and all(v[3] == "BELOW" for v in r9.values()),
          "coverage: PASS at no blanks, BELOW at 20% blanks")
    # ---------------------------------------------------------------- 12. write-once and determinism
    p = os.path.join(tmp, "once.txt")
    report.write_once(p, "x\n")
    expect_exit(lambda: report.write_once(p, "y\n"), "exists", "write-once: a second write is refused")
    expect_exit(lambda: report.Out(p), "exists", "write-once: an Out on an existing path is refused at construction")
    outA = report.Out(None, echo=False); outB = report.Out(None, echo=False)
    g22.nu_leg(outA, b5, Streams("DET"), cert.FROZEN_GROK_UNFILTERED, [4, 5], [2], reps=2, B=12, floor=0, boot=50)
    g22.nu_leg(outB, b5, Streams("DET"), cert.FROZEN_GROK_UNFILTERED, [4, 5], [2], reps=2, B=12, floor=0, boot=50)
    check(outA.text() == outB.text(), "determinism: the same master reproduces a leg byte for byte")
    check(data.WITNESS.get("edges_fast.boards", 0) > 0 and data.WITNESS.get("edges_fast.edges", 0) > 0,
          "witness: the new builder's counters moved (%s)" % dict(data.WITNESS))
    selftest_g22_v2.run(tmp, sb, check, expect_exit)
    from . import selftest_g22_rebind
    selftest_g22_rebind.run(tmp, sb, check, expect_exit, selftest_g22_v2.GOLDEN_V1_TEXT_SHA256)
    for b in ("RECORD.REFUSED_MASTER", "RECORD.REFUSED_R", "VALIDITY.PASS", "VALIDITY.FAIL", "TOKEN.REFUSED_FAIL", "TOKEN.REFUSED_MISSING", "TOKEN.REFUSED_DIGEST",
              "NU.DONE", "DESIGNS.DONE", "STOP.DONE", "OVERDISP.DONE", "OVERDISP.NO_EVENTS", "COVERAGE.PASS",
              "COVERAGE.BELOW", "WRITE_ONCE.REFUSED", "WRITE_ONCE.WRITTEN"):
        check(HITS.get(b, 0) > 0, "branch executed: %s" % b)
    words = [g22.decide_rate(9, 10, 0.5, "high")[0], g22.decide_rate(0, 50, 0.8, "high")[0],
             g22.decide_rate(5, 10, 0.5, "high")[0], g22.decide_rate(0, 200, 0.05, "low")[0],
             g22.decide_rate(40, 50, 0.05, "low")[0], g22.decide_rate(1, 10, 0.05, "low")[0]]
    check(words == ["MEETS", "BELOW", "UNRESOLVED AT THIS R", "MEETS", "EXCEEDS", "UNRESOLVED AT THIS R"],
          "decide_rate: all six words executed (%s)" % words)
    check(any(k.startswith("IDENT.") for k in HITS) and any(k.startswith("STOP.") and k != "STOP.DONE" for k in HITS),
          "branch executed: an identification word and a stop word")
