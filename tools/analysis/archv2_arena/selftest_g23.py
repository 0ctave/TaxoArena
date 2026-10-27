"""The G23 selftest. A synthetic world is written to a temp dir as the four objects systematic_budget.build() reads; the
RECORDED build() runs on it through the same read-only shims the real identity leg uses (with systematic_budget.B and
rubric_p8.ARENA12 patched for the fixture and restored after). No DB of record is opened; single process; every check
is an explicit raise-free comparison collected into a verdict (python -O safe)."""
import contextlib
import io
import os
import shutil
import tempfile
import time

import numpy as np

from . import cert, data, g23, report, synth
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
        check(needle in str(e), "%s (refused: %s)" % (label, str(e)[:100]))
        return
    check(False, "%s (did NOT refuse)" % label)


def run():
    t0 = time.time()
    print("=== archv2_g23_replay --selftest (synthetic world on disk; no DB of record opened) ===")
    tmp = tempfile.mkdtemp(prefix="archv2_g23_")
    sb = data.import_sb()
    import rubric_p8 as p8
    saved = (sb.B, list(p8.ARENA12))
    try:
        _run(tmp, sb, p8)
    finally:
        sb.B = saved[0]
        p8.ARENA12[:] = saved[1]
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for ok, _ in RESULTS if not ok)
    print("SELFTEST: %d checks, %d failed | branches executed: %s | %.1f s"
          % (len(RESULTS), n_fail, ", ".join("%s x%d" % (k, v) for k, v in sorted(HITS.items())), time.time() - t0))
    return 1 if n_fail else 0


def _render_record(sb, paths, where):
    """A 'recorded' table for the fixture: systematic_budget.main('filtered') on the RECORDED build() (shims), as the
    file of record was produced."""
    saved = sb.OUT
    sb.OUT = where
    try:
        with g23.recorded_env(sb, paths), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            sb.main("filtered")
    finally:
        sb.OUT = saved
    return open(where, encoding="utf-8").read()


def _run(tmp, sb, p8):
    names = ["Meta-Llama-3_1-70B-Instruct", "gpt-x", "qwen-y", "yi-z", "ds-v", "cmd-w"]
    # seed 49: a fixture on which the RECORDED renderer's LOAO folds stay finite (searched; seeds 44-59 at B 12: b0 -1.34,
    # b1 +4.23, max |b0| + |b1| over folds 7.4); smaller or other fixtures overflow math.exp inside systematic_budget.cbud
    FIX = dict(seed=49, model_names=names, per_pair=14, u_sd=0.8, bad_model="Meta-Llama-3_1-70B-Instruct", q_per_anchor=40,
               anchors=("AncA", "AncB", "AncC", "AncD", "AncE"))
    W = synth.make_world(**FIX)
    p8.ARENA12[:] = W["models"]
    sb.B = 8
    files = synth.write_dbs(W, tmp, tree=data.TREE)
    paths = dict(eval=files["eval"], cache=files["cache"], snapshots=files["snapshots"], promoted=files["promoted"], root=tmp)
    # ------------------------------------------------------------ the recorded table and the record's values for the fixture
    rec_path = os.path.join(tmp, "recorded_table.txt")
    rec_txt = _render_record(sb, paths, rec_path)
    check("=== (1) THE FIT" in rec_txt, "fixture: the recorded renderer ran on the recorded build() through the shims")
    # the record's values for the fixture: v1_readout on the RECORDED build()'s own edges
    with g23.recorded_env(sb, paths):
        v1 = sb.build()
    rd0 = g23.v1_readout(sb, [dict(e) for e in v1[4]], v1[1], v1[5])
    record = {"f": dict(rd0["f"]), "u": dict(rd0["u"])}
    # PASS with the record's integers given
    out1 = report.Out(None, echo=False)
    r1 = g23.identity_leg(out1, sb, paths, recorded_table=rec_path, record=record, models=W["models"])
    print("\n".join(out1.lines))
    check(r1["status"] == "PASS" and any("BYTE-IDENTICAL (" in s for s in out1.lines),
          "identity: recorded build() and the new builder give byte-identical edge tables; PASS")
    check(any("(3) recorded table" in s and s.endswith("BYTE-IDENTICAL") for s in out1.lines),
          "identity: the recorded renderer fed by the NEW builder reproduces the recorded table byte for byte")
    check(any("EXECUTION WITNESS (this leg)" in s and "the new code ran" in s for s in out1.lines),
          "identity: the execution witness shows the new paths ran")
    check(any("ALL REPRODUCED" in s for s in out1.lines), "identity: the record's integers reproduced through the new LOAO driver")
    # the declared criterion-(1) difference only
    lines = rec_txt.split("\n")
    i = next(k for k, s in enumerate(lines) if s.startswith(g23.CRIT1_START))
    j = next(k for k, s in enumerate(lines) if s.startswith(g23.CRIT1_END))
    old = lines[:i] + ["   (1) LOAO calibration, realised at or below nominal: PASS in aggregate (0 wrong vs 0.10 nominal)"] + lines[j:]
    old_path = os.path.join(tmp, "recorded_old_format.txt")
    report.write_once(old_path, "\n".join(old))
    out2 = report.Out(None, echo=False)
    r2 = g23.identity_leg(out2, sb, paths, recorded_table=old_path, record=record, models=W["models"])
    check(r2["status"] == "PASS" and any("DECLARED CRITERION-(1) BLOCK" in s for s in out2.lines),
          "identity: only the declared criterion-(1) block differs -> PASS with the difference printed")
    bad = list(lines); bad[2] = bad[2] + " (tampered)"
    bad_path = os.path.join(tmp, "recorded_tampered.txt")
    report.write_once(bad_path, "\n".join(bad))
    out3 = report.Out(None, echo=False)
    r3 = g23.identity_leg(out3, sb, paths, recorded_table=bad_path, record=record, models=W["models"])
    check(r3["status"] == "FAIL" and any("DIFFERS OUTSIDE THE DECLARED BLOCK" in s for s in out3.lines),
          "identity: a difference outside the declared block FAILS")
    out4 = report.Out(None, echo=False)
    r4 = g23.identity_leg(out4, sb, paths, recorded_table=rec_path, record=record, models=W["models"], v2_seed=43)
    check(r4["status"] == "FAIL" and any("EDGE TABLES DIFFER" in s for s in out4.lines),
          "identity: a mutated new builder (seed 43) is caught (tables differ -> FAIL)")
    wrong_rec = {"f": dict(record["f"], raw_called=10 ** 6), "u": dict(record["u"])}
    out5 = report.Out(None, echo=False)
    r5 = g23.identity_leg(out5, sb, paths, recorded_table=rec_path, record=wrong_rec, models=W["models"])
    check(r5["status"] == "FAIL" and any("NOT REPRODUCED" in s for s in out5.lines), "identity: a wrong record integer FAILS")
    got, ok = data.build_pin(sb)
    check(ok and got == data.BUILD_SRC_SHA16, "identity: build()'s LF source still hashes to the pin %s" % data.BUILD_SRC_SHA16)
    saved_pin = data.BUILD_SRC_SHA16
    data.BUILD_SRC_SHA16 = "0" * 16
    try:
        expect_exit(lambda: g23.identity_leg(report.Out(None, echo=False), sb, paths, recorded_table=rec_path, record=record,
                                             models=W["models"]), "build() changed", "identity: a changed build() pin refuses")
    finally:
        data.BUILD_SRC_SHA16 = saved_pin
    check(__import__("sys").modules["stack_judge"].OPENS > 0 and all(p.endswith(".db") for p in data.ro.LOG),
          "identity: the stack cache was opened only through the stub's open_ro (%d opens)" % __import__("sys").modules["stack_judge"].OPENS)
    # ------------------------------------------------------------ certAB with two draws of the same judge
    board = r1["board"]
    e1 = r1["edges"]
    data.mark_established(e1, board.K, r1["anchor_qs"], sb)
    W2 = synth.make_world(**FIX)
    rng = np.random.default_rng(99)
    from .g22 import board_matrix, with_verdicts
    anchors, S, obs, meta = board_matrix(board, floor=200)
    sim = W2["vm"].simulate(S, rng, mode="fixed")
    board2 = with_verdicts(board, meta, sim)
    e2, aq2 = data.edges_exact(board2, B=8, floor=200)
    data.mark_established(e2, board2.K, aq2, sb)
    out6 = report.Out(None, echo=False)
    res = g23.certab_leg(out6, sb, [("draw-1", e1), ("draw-2", e2)], fit=cert.fit_v)
    print("\n".join(out6.lines))
    check(len(res) == 2 and any("CROSS-DRAW STABILITY" in s for s in out6.lines), "certab: A vs B on two draws with cross-draw stability")
    out6b = report.Out(None, echo=False)
    g23.certab_leg(out6b, sb, [("draw-1", e1)], util_bar=0.0, fit=cert.fit_v)
    g23.certab_leg(out6b, sb, [("draw-1", e1)], util_bar=1.01, fit=cert.fit_v)
    check(HITS.get("CERTAB.A.UTIL_OK", 0) > 0 and HITS.get("CERTAB.A.UTIL_BELOW", 0) > 0, "certab: both utility branches executed")
    w_ok = g23.b_admissible(3, 3, 70, 100); w_bad1 = g23.b_admissible(3, 4, 70, 100); w_bad2 = g23.b_admissible(3, 2, 59, 100)
    check(w_ok.startswith("B ADMISSIBLE") and w_bad1.startswith("B NOT") and w_bad2.startswith("B NOT"),
          "certab: the registered criterion (b): admissible iff wrong(est) <= A's AND utility >= 60%% (%s | %s | %s)"
          % (w_ok[:14], w_bad1[:18], w_bad2[:18]))
    check(any("CRITERION (b), draw" in s for s in out6.lines), "certab: criterion (b) printed per draw")
    import archv2_g23_replay as cli23
    expect_exit(lambda: cli23.main(["--leg", "holm", "--out", os.path.join(tmp, "never.txt"), "--master", "OTHER"]),
                "not the registered", "record params: a G23 run under another master refuses (before any open)")
    check(cli23.REC_MASTER == "ARCHV2-G23-REC-1", "record params: the G23 registered master is the default")
    fw = [g23.falsifier_words("B", 10, 3, 1, "A", 100), g23.falsifier_words("B", 70, 0, 1, "A", 100)]
    check("RISES" in fw[0][1] and "BELOW" in fw[0][0] and "does not rise" in fw[1][1] and "at or above" in fw[1][0],
          "certab: the falsifier words, both branches each (%s)" % [x[1][:30] for x in fw])
    # ------------------------------------------------------------ conjuncts
    out7 = report.Out(None, echo=False)
    rc = g23.conjuncts_leg(out7, sb, board, e1, Streams("SELFTEST-CONJ"), B=12, fit=cert.fit_v)
    print("\n".join(out7.lines))
    check(rc["n"] >= 0 and any("per-order conjunct drops" in s for s in out7.lines), "conjuncts: length and per-order conjuncts evaluated")
    check(data.WITNESS.get("edges_fast.order_boards", 0) > 0 and data.WITNESS.get("edges_fast.length_boards", 0) > 0,
          "conjuncts: per-order and length-offset boards were fitted (witness)")
    # a planted length channel is recovered by beta_len (a board whose verdicts follow length only)
    W3 = synth.make_world(seed=5, n_models=4, per_pair=60, kappa=0.0, lam=1.5, u_sd=0.0, pi=0.0, q_per_anchor=40)
    bl, se, n, nG, bk = g23.beta_len(W3["board"], floor=200)
    check(bl > 0.5 and abs(bk) < 0.6, "conjuncts: beta_len recovers a planted length channel (%.3f, key %.3f)" % (bl, bk))
    # ------------------------------------------------------------ residue
    out8 = report.Out(None, echo=False)
    g23.residue_leg(out8, sb, e1, e2, "draw-1", "draw-2", fit=cert.fit_v)
    g23.residue_leg(out8, sb, e1, [dict(e, right=True) for e in e1], "draw-1", "all-right", fit=cert.fit_v)
    g23.residue_leg(out8, sb, e1, [dict(e, anchor="elsewhere") for e in e1], "draw-1", "disjoint", fit=cert.fit_v)
    g23.residue_leg(out8, sb, e1, e1, "draw-1", "draw-1-itself", fit=cert.fit_v)
    print("\n".join(out8.lines))
    _res_hits = lambda: {k: HITS.get("RESIDUE.%s" % k, 0) for k in ("BOTH", "PART", "NONE")}
    check(HITS.get("RESIDUE.CALLED_DEFINITION", 0) >= 4 and any("THE DECIDING DEFINITION (ruling 4" in s for s in out8.lines),
          "residue: the four legacy synthetic calls ran through the CALLED definition (%d)" % HITS.get("RESIDUE.CALLED_DEFINITION", 0))
    check(any("ALL-WRONG population" in s and "Meta-Llama-3_1-70B-Instruct" in s for s in out8.lines),
          "residue: the planted model heads the ALL-WRONG population (printed under its own name)")
    # ruling 4 (83f431b): the deciding residue is the CALLED wrong(established) population; a fixture with two called
    # wrong edges drives the three verdict branches (tau ~ 0, so c~ = c_raw and p = 1.0 edges are called)
    def E(anc, a_, b_, p, right):
        return dict(anchor=anc, a=a_, b=b_, p=p, m=(3.0 if p > 0.9 else 0.1), s=0.3, agree=0.5, right=right, est=True,
                    gap=0.1, mc_p=0.001)
    fx = [E("A1", "Y", "m1", 1.0, False), E("A2", "Y", "m2", 1.0, False), E("A3", "m1", "m2", 1.0, True),
          E("A1", "X", "m2", 0.6, False), E("A2", "m1", "m3", 1.0, True)]
    fitc = lambda E_, x0=(-3.0, 3.0): (-50.0, 0.0)
    out8b = report.Out(None, echo=False)
    r_both = g23.residue_leg(out8b, sb, fx, fx, "fx", "fx-same", fit=fitc)
    r_part = g23.residue_leg(out8b, sb, fx, [dict(e, right=True) if e["anchor"] == "A2" and e["a"] == "Y" else e for e in fx],
                             "fx", "fx-part", fit=fitc)
    r_none = g23.residue_leg(out8b, sb, fx, [dict(e, anchor="elsewhere") for e in fx], "fx", "fx-disjoint", fit=fitc)
    print("\n".join(out8b.lines))
    check(r_both["top"] == ["Y"] and r_both["word"].startswith("a second judge buys nothing")
          and r_part["word"].startswith("the second judge disagrees") and r_none["word"].startswith("not comparable"),
          "residue: the CALLED definition decides ({Y}); BOTH / PART / NONE verdicts on the fixture")
    check(all(v > 0 for v in _res_hits().values()), "residue: all three verdict branches executed (%s)" % _res_hits())
    # ------------------------------------------------------------ holm
    A = cert.loao_v(cert.EdgeArrays(e1), fit=cert.fit_v)
    called = {(e["anchor"], e["a"], e["b"]) for e, c in zip(e1, A["called"]) if c}
    out9 = report.Out(None, echo=False)
    h = g23.holm_leg(out9, sb, e1, board.K, r1["anchor_qs"], called)
    print("\n".join(out9.lines))
    check(h["holm"] <= h["unadjusted"] and h["pooled"] <= h["unadjusted"], "holm: Holm never establishes more than unadjusted")
    # ------------------------------------------------------------ multi-stream
    out10 = report.Out(None, echo=False)
    cnt = g23.mcstreams_leg(out10, board, Streams("SELFTEST-MC"), S=3, B=12)
    print("\n".join(out10.lines))
    check(sum(cnt.values()) > 0, "mcstreams: every edge classed over 3 streams")
    for b in ("CERTAB.B_ADMISSIBLE", "CERTAB.B_NOT_ADMISSIBLE", "IDENTITY.PASS", "IDENTITY.FAIL", "IDENTITY.TABLES_IDENTICAL", "IDENTITY.TABLES_DIFFER",
              "IDENTITY.RENDER_IDENTICAL", "IDENTITY.RENDER_DECLARED_ONLY", "IDENTITY.RENDER_DIFFERS",
              "IDENTITY.INTEGERS_MATCH", "IDENTITY.INTEGERS_DIFFER", "IDENTITY.PIN_REFUSED", "CERTAB.CROSSDRAW",
              "HOLM.DONE", "MC.DONE"):
        check(HITS.get(b, 0) > 0, "branch executed: %s" % b)
    check(HITS.get("CONJ.CATCHES_WRONG", 0) + HITS.get("CONJ.CATCHES_NONE", 0) > 0, "branch executed: a conjunct word")
