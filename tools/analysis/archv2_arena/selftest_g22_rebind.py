"""Selftest for G22-REBIND-1 (56751fa): the additive per-replicate storage, the validity-v2 REPLAY mode and the print
lines of ruling 2. Synthetic worlds only; single process; each new branch executed; the mutants store_draws_random,
replay_touches_one_shot, replay_mints_token and bias_line_missing must be KILLED. The storage is ADDITIVE: the output
text of every leg is byte-identical with and without a store (v1: equal to the golden computed at 4c2d2b5)."""
import hashlib
import json
import os
import random

import numpy as np

from . import data, g22, report, synth
from .report import HITS
from .streams import Streams


def mutant_killed(mod, name, fn):
    saved = mod.MUTANT
    mod.MUTANT = name
    try:
        ok = bool(fn())
    except SystemExit:
        ok = False
    finally:
        mod.MUTANT = saved
    return not ok


def run(tmp, sb, check, expect_exit, golden_v1_sha):
    print("--- G22-REBIND-1 (56751fa): additive storage, the validity-v2 replay, the ruling-2 lines ---")
    rd = os.path.join(tmp, "rebind"); os.makedirs(rd)
    # ---------------------------------------------------------------- v1 additive: byte-identical with and without a store
    W5 = synth.make_world(seed=11, n_models=6, per_pair=40, u_sd=0.8, bad_model="m5", q_per_anchor=50)
    b5 = W5["board"]

    def v1_text(store):
        st = Streams("SELFTEST-G22")
        out = report.Out(None, echo=False)
        real_edges, aq = data.edges_fast(b5, 24, st, "selftest/real", floor=200)
        data.mark_established(real_edges, b5.K, aq, sb)
        est = {(e["anchor"], e["a"], e["b"]) for e in real_edges if e["est"]}
        m = g22.cert_metrics(real_edges, est, min_est=5)
        g22.validity_leg(out, b5, sb, st, R=10, B=24, family_alpha=1e-9, primary="fixed", floor=200,
                         targets=dict(f_raw_called=int(np.median([m["f_raw_called"]]))), ddev_targets=(),
                         edge_targets=dict(f=m["f_n"], u=m["u_n"], est=m["est_n"]), min_est=5,
                         modes=("fixed", "random", "retest"), store=store)
        return out.text(), st.digest()
    t0, s0 = v1_text(None)
    store1 = g22.RecordStore(os.path.join(rd, "v1"))
    t1, s1 = v1_text(store1)
    sha1 = hashlib.sha256(t1.encode()).hexdigest()
    check(t0 == t1 and s0 == s1 and sha1 == golden_v1_sha,
          "REBIND additive (v1): the output text and the streams log are byte-identical with and without the store, and equal"
          " the golden of 4c2d2b5 (%s...)" % sha1[:16])
    check([f[2] for f in store1.files] == [10, 10, 10] and all(os.path.exists(f[1]) for f in store1.files),
          "REBIND storage (v1): three write-once record files, 10 replicates each (%s)" % [(f[0], f[2]) for f in store1.files])
    expect_exit(lambda: store1.put("validity.fixed", [{}]), "exists", "REBIND storage: a record file is write-once")

    def rng_state():
        s_ = np.random.get_state()
        return (s_[0], s_[1].tobytes(), s_[2], s_[3], s_[4]), random.getstate()

    def rng_untouched():
        s = g22.RecordStore(os.path.join(rd, "rng_%d" % len(os.listdir(rd))))
        before = rng_state()
        s.put("probe", [{"x": 1}])
        return rng_state() == before
    check(rng_untouched() and mutant_killed(g22, "store_draws_random", rng_untouched),
          "REBIND storage consumes NO random number (numpy and random states unchanged); mutant store_draws_random KILLED")
    # ---------------------------------------------------------------- v2 additive
    W = synth.make_world(seed=13, n_models=6, per_pair=40, u_sd=0.8, q_per_anchor=50, beta=4.0, kappa=1.5)
    b = W["board"]
    real, aq = data.edges_fast(b, 20, Streams("V2FIX-RB"), "x", floor=200)
    data.mark_established(real, b.K, aq, sb)
    est = {(e["anchor"], e["a"], e["b"]) for e in real if e["est"]}
    m = g22.cert_metrics(real, est, min_est=5)
    kw = dict(R=4, B=20, family_alpha=1e-9, floor=200, targets=dict(f_raw_called=m["f_raw_called"]), ddev_targets=(),
              edge_targets=dict(f=m["f_n"], u=m["u_n"], est=m["est_n"]), min_est=5, record_B=20)
    MASTER = "FIXTURE-REC-1"

    def v2_run(store, out=None):
        st = Streams(MASTER)
        out = out or report.Out(None, echo=False)
        tok, recs = g22.validity_v2_leg(out, b, sb, st, store=store, **kw)
        return out, st, tok
    o0, st0, tok0 = v2_run(None)
    store2 = g22.RecordStore(os.path.join(rd, "v2"))
    o1, st1, tok1 = v2_run(store2)
    check(o0.text() == o1.text() and st0.digest() == st1.digest() and tok0["vm_digest"] == tok1["vm_digest"],
          "REBIND additive (v2): output, streams log and verdict-model digest byte-identical with and without the store")
    check([(f[0], f[2]) for f in store2.files] == [("validity-v2.random", 4), ("validity-v2.fixed", 4), ("validity-v2.retest", 4),
                                                   ("validity-v2.heldout", 4)],
          "REBIND storage (v2): part A (3 modes) and part B stored, 4 replicates each")
    # ---------------------------------------------------------------- the fixture 'record' and its REPLAY
    rec_path = os.path.join(rd, "G22_validity_v2_fixture.txt")
    BOARD = "  board fixture: 1800 valid verdicts, 1800 routed, anchors 3, models 6; routing tree synth snapshot SNAP_SYNTH"
    report.write_once(rec_path, BOARD + "\n" + o0.text() + "\n".join(st0.summary()) + "\n")
    report.write_once(rec_path + ".validity_v2.json", json.dumps(g22.seal_token(dict(tok0, record=False)), default=str))
    g22.ONE_SHOT_PATH, saved_os = os.path.join(rd, "ONE_SHOT.json"), g22.ONE_SHOT_PATH

    def replay(tag, recorded=rec_path, board_line=None):
        st = Streams(MASTER)
        out = report.Out(None, echo=False)
        out(BOARD if board_line is None else board_line)          # the CLI prints the board line in the header (RB3)
        store = g22.RecordStore(os.path.join(rd, "replay_" + tag))
        rv = g22.replay_v2(out, b, sb, st, recorded, store, expect_master=MASTER, expect_streams_prefix=None, **kw)
        return rv, out, store
    try:
        rv, orp, srp = replay("ok")
        print("\n".join(l for l in orp.lines if "REPLAY" in l))
        check(rv["ok"] and rv["a"] and rv["b"] and rv["c"] and rv["witness"],
              "REBIND replay on the fixture: (a) block BYTE-IDENTICAL, (b) streams equal, (c) vm digest equal, witness"
              " (%d records re-read, %d quantile lines re-computed, %d missing)" % (rv["n_rec"], rv["n_chk"], len(rv["missing"])))
        check(not os.path.exists(g22.ONE_SHOT_PATH) and not os.path.exists(srp.prefix + ".validity_v2.json"),
              "REBIND replay: ONE_SHOT_PATH untouched and no token minted")
        no_one_shot = lambda: (lambda t: not os.path.exists(g22.ONE_SHOT_PATH))(replay("os%d" % len(os.listdir(rd))))
        check(no_one_shot() and mutant_killed(g22, "replay_touches_one_shot", no_one_shot),
              "REBIND replay: mutant replay_touches_one_shot KILLED")
        if os.path.exists(g22.ONE_SHOT_PATH):
            os.remove(g22.ONE_SHOT_PATH)

        def no_token():
            rv_, o_, s_ = replay("tk%d" % len(os.listdir(rd)))
            return not os.path.exists(s_.prefix + ".validity_v2.json")
        check(no_token() and mutant_killed(g22, "replay_mints_token", no_token), "REBIND replay: mutant replay_mints_token KILLED")
        bad = open(rec_path, encoding="utf-8").read()
        k = bad.index("    f_raw_called")
        bad = bad[:k] + bad[k:].replace("yes", "NO", 1)
        bad_path = os.path.join(rd, "G22_validity_v2_tampered.txt")
        report.write_once(bad_path, bad)
        report.write_once(bad_path + ".validity_v2.json", json.dumps(g22.seal_token(dict(tok0, record=False)), default=str))
        rvb, ob, _ = replay("bad", bad_path)
        check(not rvb["ok"] and not rvb["a"] and any("REFUSED" in l for l in ob.lines),
              "REBIND replay: one differing byte in the recorded block FAILS the replay (the re-binding REFUSED)")
        expect_exit(lambda: g22.replay_v2(report.Out(None, echo=False), b, sb, Streams("OTHER"), rec_path,
                                          g22.RecordStore(os.path.join(rd, "other")), expect_master=MASTER,
                                          expect_streams_prefix=None, **kw),
                    "recorded master", "REBIND replay: a replay under another master refuses")
    finally:
        g22.ONE_SHOT_PATH = saved_os
    # ---------------------------------------------------------------- ruling 2: the designs / stop print lines
    kv = W["keyview"]
    pools = {}
    for q, s_ in kv.cat.items():
        pools.setdefault(s_, []).append(q)
    pools = {s_: sorted(v) for s_, v in pools.items()}
    spec = {"T1": [dict(corpus="syn", roster="r6", strata=3, N=3)]}
    st = Streams("SELFTEST-REBIND-DESIGNS")
    dz = g22.resolve_designs(["T1"], {"r6": W["models"]}, {"syn": {s_: 50 for s_ in pools}}, {"syn": pools}, st, spec=spec)
    vm = g22.VerdictModel.from_params(tok1["verdict_model"])
    tokd = g22.seal_token(dict(tok1, status="PASS", record=False))

    def designs_text(store, name):
        o = report.Out(None, echo=False)
        g22.designs_leg(o, tokd, vm, dz, {"syn": kv}, Streams("SELFTEST-REBIND-D-" + name), R=3, B=12, floor=0,
                        deff_reps=1, bar=0.01, min_est=3, store=store)
        return o
    sd = g22.RecordStore(os.path.join(rd, "designs"))
    od = designs_text(sd, "a")
    print("\n".join(od.lines))
    bias_ok = lambda: any(l == g22.BIAS_LINE for l in designs_text(None, "m%d" % len(os.listdir(rd))).lines)
    check(bias_ok() and mutant_killed(g22, "bias_line_missing", bias_ok), "ruling 2 (iii): the bias line printed; mutant bias_line_missing KILLED")
    check(any("DEFLATED SENSITIVITY" in l and "x 1.06" in l and "computed from the stored replicates" in l for l in od.lines)
          and any("x 1.18" in l for l in od.lines), "ruling 2 (iii): the deflated sensitivity at 9 x 1.06 and 9 x 1.18, from the stored replicates")
    check(any("LOWER BOUND" in l for l in od.lines), "ruling 2 (iii): (g)'s DEFF labelled a LOWER BOUND")
    check(any("BOTH COUNTS" in l for l in od.lines), "ruling 2 (iii): both counts printed")
    check(any(g22.PASS_CHIP in l and tokd["token_digest"] in l for l in od.lines),
          "ruling 2 (iii) + D15: the PASS AT THE BOUNDARY chip and the token_digest IN FULL (%s...)" % tokd["token_digest"][:16])
    check(any("READINGS ADMISSIBLE ONLY AS" in l for l in od.lines), "ruling 2 (i): the admissibility sentence printed")
    check(sd.files and sd.files[0][2] == 3, "REBIND storage (designs): the replicates stored (%s)" % [(f[0], f[2]) for f in sd.files])
    part = g22.resolve_designs(["T9"], {"r6": W["models"]}, {"syn": {s_: 50 for s_ in pools}}, {"syn": pools},
                               Streams("SELFTEST-REBIND-STOP-R"), spec={"T9": [dict(corpus="syn", roster="r6", strata=3, N=3)]})["T9"][0]
    os_ = report.Out(None, echo=False)
    ss = g22.RecordStore(os.path.join(rd, "stop"))
    g22.stop_leg(os_, tokd, vm, part, kv, Streams("SELFTEST-REBIND-STOP"), R=2, B=12, floor=0, margins=(0.0,), bar=0.01,
                 stage2_bar=0.0, stage1_n=2, store=ss)
    check(any(l == g22.BIAS_LINE for l in os_.lines) and any(g22.PASS_CHIP in l and tokd["token_digest"] in l for l in os_.lines)
          and ss.files and ss.files[0][2] == 2, "stop leg: the bias line, the chip, the full token_digest, and the stored replicates")
    # ---------------------------------------------------------------- ruling 2 (iv): D0 / D2 declared deviation
    o7 = report.Out(None, echo=False)
    kept = g22.declared_deviation(["D4", "D0", "D1-full", "D2"], False, o7)
    check(kept == ["D4", "D1-full"] and sum("NOT RUN (declared deviation, ruling 2 (iv))" in l for l in o7.lines) == 2,
          "ruling 2 (iv): D0 and D2 print NOT RUN (declared deviation) and are not run")
    expect_exit(lambda: g22.declared_deviation(["D0"], False, report.Out(None, echo=False)), "only D0 / D2",
                "ruling 2 (iv): asking only D0 / D2 without the author's flag refuses")
    check(g22.declared_deviation(["D0", "D2"], True, report.Out(None, echo=False)) == ["D0", "D2"],
          "ruling 2 (iv): with the author's flag D0 / D2 run")
    mp = sd.write_manifest()
    check(mp is not None and os.path.exists(mp), "REBIND storage: the write-once manifest lists every stored file with its sha256")
    # ---------------------------------------------------------------- RB3: the header's board line is compared
    g22.ONE_SHOT_PATH, saved_os2 = os.path.join(rd, "ONE_SHOT_rb3.json"), g22.ONE_SHOT_PATH
    try:
        rvb3, ob3, _ = replay("rb3", board_line=BOARD.replace("1800 valid", "1799 valid"))
    finally:
        g22.ONE_SHOT_PATH = saved_os2
    check(not rvb3["ok"] and any("board line" in l and "DIFFER" in l for l in ob3.lines),
          "RB3: a different header board line (the data object) FAILS the replay")
    # ---------------------------------------------------------------- RB2: MEETS on P(nominal >= 9) is labelled
    o_m = report.Out(None, echo=False)
    g22.designs_leg(o_m, tokd, vm, dz, {"syn": kv}, Streams("SELFTEST-REBIND-D-MEETS"), R=3, B=12, floor=0, deff_reps=0,
                    bar=0.01, min_est=3, p_bar=0.3)
    check(any(": MEETS (optimistic by construction, ruling 2 (ii))" in l for l in o_m.lines),
          "RB2: every MEETS on P(nominal >= bar) carries 'optimistic by construction'")
    # ---------------------------------------------------------------- RB1: the rebind chain (ruling 1 (iii))
    live = g22.instrument_lf16()
    FAKE_OLD = "a" * 16
    rec_like = dict(tok1, status="PASS", partA="PASS", partB="PASS", master=g22.REC_MASTER_G22, R=1000, T=14, T2=12,
                    label=g22.POST_HOC, record=True)

    def seal_as(tok, lf16):
        t = json.loads(json.dumps(tok, default=str))
        t["instrument_lf16"] = lf16
        t["token_digest"] = g22._token_digest(t)
        return t
    t_old = seal_as(rec_like, FAKE_OLD)
    p_old = os.path.join(rd, "tok_old_record.json"); report.write_once(p_old, json.dumps(t_old, default=str))
    saved = (g22.REBIND_PINNED_DIGEST, g22.REBIND_OLD_LF16, g22.CHAIN_PATH)
    g22.REBIND_PINNED_DIGEST, g22.REBIND_OLD_LF16 = t_old["token_digest"], FAKE_OLD

    def chain(name, **over):
        c = dict(old_lf16=FAKE_OLD, new_lf16=live, token_digest=t_old["token_digest"], replay_output_sha="0" * 64,
                 registrar_commit="abc1234")
        c.update(over)
        path = os.path.join(rd, "chain_%s.json" % name)
        report.write_once(path, json.dumps(c))
        return path

    def admitted(tpath):
        try:
            g22.load_token(tpath, need_v2=True)
            return True
        except SystemExit:
            return False
    try:
        g22.CHAIN_PATH = os.path.join(rd, "chain_absent.json")
        refused_missing = lambda: not admitted(p_old)
        check(refused_missing() and mutant_killed(g22, "chain_missing_ok", refused_missing),
              "RB1: with NO chain file the token of record is REFUSED (fail-closed); mutant chain_missing_ok KILLED")
        g22.CHAIN_PATH = chain("ok")
        check(admitted(p_old) and HITS.get("TOKEN.REBIND_ADMITTED", 0) > 0,
              "RB1: pinned digest + frozen lf16 + a chain naming THIS instrument (%s) as successor -> ADMITTED" % live)
        t_other = seal_as(dict(rec_like, note="another token"), FAKE_OLD)
        p_other = os.path.join(rd, "tok_other_digest.json"); report.write_once(p_other, json.dumps(t_other, default=str))
        refused_digest = lambda: not admitted(p_other)
        check(refused_digest() and mutant_killed(g22, "chain_digest_unchecked", refused_digest),
              "RB1: a token whose digest is not the pinned one is REFUSED; mutant chain_digest_unchecked KILLED")
        t_bad_lf = seal_as(rec_like, "b" * 16)
        p_bad_lf = os.path.join(rd, "tok_bad_oldlf16.json"); report.write_once(p_bad_lf, json.dumps(t_bad_lf, default=str))
        g22.REBIND_PINNED_DIGEST = t_bad_lf["token_digest"]
        g22.CHAIN_PATH = chain("badlf", token_digest=t_bad_lf["token_digest"])
        refused_lf = lambda: not admitted(p_bad_lf)
        check(refused_lf() and mutant_killed(g22, "chain_oldlf16_unchecked", refused_lf),
              "RB1: a token whose instrument_lf16 is not the frozen build's is REFUSED; mutant chain_oldlf16_unchecked KILLED")
        g22.REBIND_PINNED_DIGEST = t_old["token_digest"]
        g22.CHAIN_PATH = chain("successor", new_lf16="c" * 16)
        refused_succ = lambda: not admitted(p_old)
        check(refused_succ() and mutant_killed(g22, "chain_successor_unchecked", refused_succ),
              "RB1: a chain naming ANOTHER successor refuses; mutant chain_successor_unchecked KILLED")
        for nm, over in (("oldfield", dict(old_lf16="d" * 16)), ("digestfield", dict(token_digest="e" * 64)),
                         ("replaysha", dict(replay_output_sha="not-a-sha")), ("commit", dict(registrar_commit="zz"))):
            g22.CHAIN_PATH = chain(nm, **over)
            check(not admitted(p_old), "RB1: a chain with a bad %s field refuses" % nm)
        badjson = os.path.join(rd, "chain_badjson.json"); report.write_once(badjson, "{not json")
        g22.CHAIN_PATH = badjson
        check(not admitted(p_old), "RB1: a malformed chain file refuses")
    finally:
        g22.REBIND_PINNED_DIGEST, g22.REBIND_OLD_LF16, g22.CHAIN_PATH = saved
    check(g22.REBIND_PINNED_DIGEST == "3069666d0f5e553ad61bd9cb8f178e2771d6fd683f63f01b8b35435cf56cdfc0"
          and g22.REBIND_OLD_LF16 == "f37145df9516b7ec"
          and g22.CHAIN_PATH.replace("\\", "/").endswith("experiment_configs/g22_rebind_chain.json"),
          "RB1: the pinned digest, the frozen lf16 and the chain path are the registered ones")
    for br in ("REPLAY.PASS", "REPLAY.FAIL", "DESIGNS.DECLARED_DEVIATION", "TOKEN.REBIND_ADMITTED"):
        check(HITS.get(br, 0) > 0, "branch executed: %s" % br)
