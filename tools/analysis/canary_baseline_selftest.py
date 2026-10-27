"""Fixture selftest for canary_baseline.py --analyze (written 2026-09-23 after the post-run review 2026-09-22, defects 1-4; zero calls).

  python tools/analysis/canary_baseline_selftest.py        (synthetic caches in a temp directory; posts nothing, reads no cache of
                                                            record, writes nothing under experiment_results/)

NOT a registered test: a fixture that proves what --analyze must now print by itself, so that re-running it can never lose a line of
record (defect 2: the outcome is opened in mode "w"). It checks

  1. the machine-readable "ALARM STATE: <NO ALARM|ALARM|UNDETERMINED>" line is FLUSH-LEFT at column 0 and sits immediately after the
     ALARM line, and that placement_steps.py's consumer pattern (line.startswith("ALARM STATE:") on the UNSTRIPPED line) finds it;
  2. the registered rule (ii) (pre-run bracket 96bd3d7, programme L3631) decides it on the CONTESTED floor under BOTH conventions:
     <= 0.114 -> NO ALARM, above -> UNDETERMINED; ALARM is never emitted by this script (passes 1-2 only);
  3. the convention-A floor line (INVALID or non-terminated in either pass = disagreement, the pair kept) is printed beside the
     convention-B floors with the full paired denominators and the dropped-pair count (rule (iv));
  4. the MDE line is computed from the MEASURED SE (1.96 x SE at n = 300 and at n ~ 1,000, and the one-sided 3-SE threshold), not from
     DECOMP's 0.057 literal;
  5. idempotence: two consecutive --analyze passes over the same complete pass-1 + pass-2 pair write byte-identical files.
[CORRECTED 2026-09-23 by READY_canary_analyze_fix_and_leaf.md (ad65d09), insertion only] (a) item 1 overstates the consumer: NOTHING reads
this outcome's ALARM STATE line today - placement_steps.py:142 reads ARM-B-VINTAGE's ref_remint_outcome.txt. The fixture asserts only that
the line is FORMAT-COMPATIBLE with that reader's pattern (exact-equality startswith on the unstripped line, hence column 0). (b) item 3's
"the pair kept" is convention A's rule; convention B drops a pair only when either pass is INVALID, so a NON-TERMINATED pass-2 row stays in
B's denominator - the dropped-pair count counts INVALID pairs only. check_conventions_differ asserts that asymmetry (296 / 4, not 292 / 8).
(c) item 2 is decided at 3 dp (the floor as printed), which check_alarm_state_bar pins on both sides of the 0.114 bar. (d) the degraded
readouts (no ALARM STATE line) must never touch the outcome of record: check_write_guard pins the diversion to the partial file.

[ADDED 2026-09-24, CANARY-EPOCH2-RUNG build, insertion only] 6. write-once (post-run review 2026-09-22 D2 completed): --analyze now writes
the outcome of record with mode "x" and never overwrites an existing one; item 5's "idempotent" therefore reads "a re-run leaves the file
byte-identical because it is not rewritten", and check_write_once proves that an existing outcome carrying a hand-inserted line survives.

SAFETY. canary_baseline.OUT, OUT_PARTIAL, cache_path and freeze_set, and rejudge_grok.EVAL_DB, are redirected into a temporary
directory before analyze() is called, and the run REFUSES if any of them still resolves inside the repository. No pool is read (the
pool guard lives under canary_baseline's __main__ and is not executed by an import).
"""
import os, sys, json, time, shutil, sqlite3, tempfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import canary_baseline as cb
import rejudge_grok as rj

COLS = 26
MODELS = ("Model-Alpha", "Model-Beta")


def ensure(cond, msg=""):
    """[ADDED 2026-09-24, READY_canary_epoch2_rung D5 / queue CANARY-SELFTEST-ASSERTS] every former `assert` of this file: an EXPLICIT
    raise, so the fixture checks under `python -O` too (an assert statement is compiled away there and checked nothing)."""
    if not cond:
        raise AssertionError(msg)


def inside_repo(p):
    try: return not os.path.relpath(os.path.abspath(p), ROOT).startswith(os.pardir)
    except ValueError: return False


def make_matches(n_per):
    """A synthetic frozen set: n_per contested + n_per cross, questions shared in pairs so the clustered bootstrap has clusters."""
    ms = []
    for i, s in enumerate(("contested", "cross")):
        for j in range(n_per):
            mid = 1000 * (i + 1) + j
            ms.append(dict(match_id=mid, qid=10000 + i * 1000 + j // 2, model_a=MODELS[0], model_b=MODELS[1],
                           node_id="n0", anchor="anchor0", stratum=s, pair_kind="frontier" if s == "contested" else "cross"))
    return ms


def row(m, winner, invalid=0, finish=("stop", "stop"), vote=("Model A", "Model B")):
    return (m["match_id"], m["model_a"], m["model_b"], m["node_id"], m["qid"], m["anchor"], "A", 1, vote[0], vote[1], None, None,
            winner, 0, int(invalid), "", "", 0.0, finish[0], finish[1], 10, 10, m["stratum"], m["pair_kind"],
            cb.EXPECTED_FINGERPRINT, cb.EXPECTED_FINGERPRINT)


def write_cache(path, rows, meta):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                "raw1 TEXT, raw2 TEXT, ts REAL, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, stratum TEXT, pair_kind TEXT, "
                "provider1 TEXT, provider2 TEXT)")
    con.execute("CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO verdicts VALUES (%s)" % ",".join("?" * COLS), rows)
    con.executemany("INSERT INTO run_meta VALUES (?,?)", sorted(meta.items()))
    con.commit(); con.close()


def write_eval_db(path, matches):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, is_correct INTEGER)")
    seen = set()
    for m in matches:
        if m["qid"] in seen: continue
        seen.add(m["qid"])
        con.execute("INSERT INTO eval_results VALUES (?,?,1)", (m["qid"], MODELS[0]))
        con.execute("INSERT INTO eval_results VALUES (?,?,0)", (m["qid"], MODELS[1]))
    con.commit(); con.close()


def assert_owns(tmp, tag, out, pass2=True):
    """EVERY case owns its own state: the outcome path, the three redirected globals and the two caches must all be the ones
    this case built under its OWN tag. Called inside scenario() just before analyze() and again at the top of each case, so a
    case can never read another case's leftover caches, another case's patched cache_path, or a pass-1-only fixture."""
    d = os.path.join(tmp, tag)
    ensure(not inside_repo(d), "the fixture must live outside the repository: %s" % d)
    ensure(out == os.path.join(d, "outcome.txt") and cb.OUT == out, (out, cb.OUT))
    ensure(cb.OUT_PARTIAL == os.path.join(d, "outcome_partial.txt"), cb.OUT_PARTIAL)
    ensure(rj.EVAL_DB == os.path.join(d, "eval.db"), rj.EVAL_DB)
    ensure(cb.cache_path(1) == os.path.join(d, "pass1.db") and os.path.exists(cb.cache_path(1)), cb.cache_path(1))
    ensure(cb.cache_path(2) == os.path.join(d, "pass2.db"), cb.cache_path(2))
    ensure(os.path.exists(cb.cache_path(2)) == pass2, "case %r expects pass-2 cache present=%s, found %s" % (tag, pass2, os.path.exists(cb.cache_path(2))))


def scenario(tmp, tag, n_per, dis_contested, dis_cross, bad_pass1=0, bad_pass2=0, pass2=True):
    """Build a pass-1 / pass-2 pair with an exact number of verdict disagreements per stratum and, optionally, rows that carry no
    committed verdict (INVALID in pass 1, finish_reason=length in pass 2). The uncommitted rows sit at the tail of the contested
    stratum, DISJOINT from the disagreeing rows, so convention A and convention B must differ. Returns (out_path, matches)."""
    d = os.path.join(tmp, tag); os.makedirs(d, exist_ok=True)
    matches = make_matches(n_per)
    ensure(dis_contested + bad_pass1 + bad_pass2 <= n_per, "the fixture needs disjoint disagreeing and uncommitted rows")
    dis = set(range(dis_contested)) | set(range(n_per, n_per + dis_cross))
    bad1 = set(range(n_per - bad_pass1, n_per))
    bad2 = set(range(n_per - bad_pass1 - bad_pass2, n_per - bad_pass1))
    ensure(not (dis & (bad1 | bad2)) and not (bad1 & bad2))
    r1, r2 = [], []
    for i, m in enumerate(matches):
        r1.append(row(m, MODELS[0], invalid=1 if i in bad1 else 0))
        r2.append(row(m, MODELS[1] if i in dis else MODELS[0], finish=("length", "stop") if i in bad2 else ("stop", "stop")))
    meta = dict(test="CANARY-BASELINE", pool_id=cb.POOL, judge=cb.JUDGE, reference=cb.REFERENCE, protocol=cb.protocol(),
                max_tokens="8192", temperature="omitted", set_hash="deadbeefdeadbeef", started="2026-01-01 00:00:00",
                resumed=json.dumps([]), script_sha256_16="0" * 16)
    write_cache(os.path.join(d, "pass1.db"), r1, dict(meta, pass_no="1"))
    if pass2: write_cache(os.path.join(d, "pass2.db"), r2, dict(meta, pass_no="2"))
    write_eval_db(os.path.join(d, "eval.db"), matches)

    out = os.path.join(d, "outcome.txt"); out_partial = os.path.join(d, "outcome_partial.txt")
    for p in (out, out_partial, os.path.join(d, "pass1.db"), os.path.join(d, "eval.db")):
        ensure(not inside_repo(p), "REFUSED: the fixture would write or read inside the repository: %s" % p)
    cb.OUT, cb.OUT_PARTIAL = out, out_partial
    cb.cache_path = lambda n=None: os.path.join(d, "pass%d.db" % (n or cb.NPASS))
    cb.freeze_set = lambda allow_freeze=False: (matches, dict(set_hash="deadbeefdeadbeef", pool_id=cb.POOL, matches=matches))
    rj.EVAL_DB = os.path.join(d, "eval.db")
    assert_owns(tmp, tag, out, pass2)                    # the state analyze() is about to read is the one this case just built
    cb.analyze()
    if pass2:
        ensure(os.path.exists(out) and not os.path.exists(out_partial), "the fixture pair is complete: the outcome of record path must be used")
    return out, matches


def lines_of(path):
    return open(path, encoding="utf-8").read().split("\n")


def find(ls, prefix, strip=True):
    hits = [i for i, l in enumerate(ls) if (l.strip() if strip else l).startswith(prefix)]
    ensure(len(hits) == 1, "expected exactly one %r line, found %d" % (prefix, len(hits)))
    return hits[0]


def check_no_alarm(tmp):
    out, _ = scenario(tmp, "no_alarm", 150, 13, 13)
    assert_owns(tmp, "no_alarm", out)
    ls = lines_of(out)
    i = find(ls, "ALARM (Stage 9 arm A")
    # (1) flush-left, at column 0, immediately after the ALARM line; the consumer pattern is an unstripped startswith
    ensure(ls[i + 1] == "ALARM STATE: NO ALARM", repr(ls[i + 1]))
    ensure(next(l.strip() for l in ls if l.startswith("ALARM STATE:")) == "ALARM STATE: NO ALARM")
    ensure(ls[i + 2] == cb.ALARM_STATE_NOTE, "the 4178a7c record bracket must be reproduced verbatim")
    # (3) convention A beside convention B: 13/150, 13/150, 26/300, 0 dropped, and it is the line after the "all" floor
    j = find(ls, "all       n=300 matches")
    a = ls[j + 1].strip()
    ensure(a.startswith("CONVENTION A (INVALID or non-terminated in either pass = disagreement; denominators 150 / 150 / 300): "
                        "contested 13/150 = 0.087, cross 13/150 = 0.087, all 26/300 = 0.087; pairs dropped by the script 0 "
                        "(pass 1 INVALID 0, pass 2 INVALID 0); convention B as printed above."), a)
    ensure(a.endswith(cb.CONV_A_NOTE.strip()))
    # (4) the MDE line is read from the measured SE, not from a literal
    mde = ls[find(ls, "(a single pass pair of")]
    se = float(ls[j].split("SE ")[1].split()[0])            # the SE printed on the "all" floor line, rounded to 4 dp
    got = float(mde.split("MDE 1.96 x SE = ")[1].split("pp")[0])
    ensure(abs(got - 196 * se) <= 0.07, (got, se))           # the printed SE is rounded to 4 dp: |196*d(SE)| <= 0.0098, plus 0.05 of MDE rounding
    ensure("~2.7pp" not in mde and "0.057" not in mde)
    ensure("the strata compare at n=150 each and are descriptive, not a test)" in mde)
    thr = ls[i].split("(one epoch) threshold ")[1].split()[0]
    ensure(("3-SE alarm at n=300 fires at %s" % thr) in mde, (mde, thr))
    ensure("at n ~ 1,000 at the same DEFF" in mde)
    print("  [OK] NO ALARM: flush-left state line, record bracket verbatim, convention A = convention B, MDE from the measured SE")
    return out


def check_undetermined(tmp):
    out, _ = scenario(tmp, "undetermined", 150, 30, 5)      # contested 0.200 > 0.114
    assert_owns(tmp, "undetermined", out)
    ls = lines_of(out)
    i = find(ls, "ALARM (Stage 9 arm A")
    ensure(ls[i + 1] == "ALARM STATE: UNDETERMINED", repr(ls[i + 1]))
    ensure("contested 30/150 = 0.200" in "\n".join(ls))
    ensure(not any(l == "ALARM STATE: ALARM" for l in ls), "ALARM is not a permitted state at pass 2")
    print("  [OK] UNDETERMINED: a contested floor of 0.200 > %.3f refuses NO ALARM" % cb.CONTESTED_ALARM_BAR)


def check_boundary(tmp):
    """The bar is inclusive: 17/150 = 0.1133 <= 0.114 -> NO ALARM; 18/150 = 0.120 -> UNDETERMINED."""
    for dis, want in ((17, "NO ALARM"), (18, "UNDETERMINED")):
        out, _ = scenario(tmp, "bar_%d" % dis, 150, dis, 0)
        assert_owns(tmp, "bar_%d" % dis, out)
        ls = lines_of(out)
        got = ls[find(ls, "ALARM (Stage 9 arm A") + 1]
        ensure(got == "ALARM STATE: " + want, (dis, got))
    print("  [OK] the 0.114 bar is inclusive: 17/150 -> NO ALARM, 18/150 -> UNDETERMINED")


def check_conventions_differ(tmp):
    """4 pass-1 INVALID rows and 4 pass-2 non-terminated rows, disjoint from the disagreeing rows. THE ASYMMETRY OF RECORD
    (READY ad65d09 defect 1): convention B's `paired` filter tests r["inv"] ONLY, so it drops the 4 INVALID pairs and KEEPS
    the 4 non-terminated ones in its denominator (300 -> 296, floor 26/296); convention A counts BOTH kinds as a
    disagreement and keeps every pair (26 + 8 = 34 over 300). The dropped-pair count is therefore 4, not 8."""
    out, _ = scenario(tmp, "conv", 150, 13, 13, bad_pass1=4, bad_pass2=4)
    assert_owns(tmp, "conv", out)
    ls = lines_of(out); txt = "\n".join(ls)
    a = ls[find(ls, "CONVENTION A (")].strip()
    ensure("denominators 150 / 150 / 300" in a, a)            # convention A never drops a pair
    # the verbatim 4178a7c wording says "INVALID" but the two counts are bad_row counts (INVALID or non-terminated): 4 and 4
    ensure("pairs dropped by the script 4 (pass 1 INVALID 4, pass 2 INVALID 4)" in a, a)
    all_b = ls[find(ls, "all       n=296 matches")]
    nb = int(all_b.split("n=")[1].split()[0])
    fb = float(all_b.split("floor ")[1].split()[0])
    da = int(a.split(", all ")[1].split("/")[0])
    fa = float(a.split(", all ")[1].split(" = ")[1].split(";")[0])
    ensure(nb == 296 and 300 - nb == 4, (nb,))                # only the INVALID pairs leave convention B's denominator
    ensure(da == 34 and da - 26 == 8, (da,))                  # all 8 uncommitted pairs enter convention A's numerator
    ensure(abs(fb - 26 / 296) < 5e-4 and abs(fa - 34 / 300) < 5e-4, (fb, fa))
    ensure(fa > fb, (fa, fb))
    # [ADDED 2026-10-01, READY_canary_analyze_fix_delta D1 (c6ee6155; kills its M7): A contested 21/150 = 0.140 > 0.114 while B is
    # 13/146 = 0.089: rule (ii) needs both, so analyze() must print UNDETERMINED here; a rule (ii) fed convention B twice prints NO ALARM]
    ensure(ls[find(ls, "ALARM (Stage 9 arm A") + 1] == "ALARM STATE: UNDETERMINED", ls[find(ls, "ALARM (Stage 9 arm A") + 1])
    ensure("GUARD" in txt)
    print("  [OK] the asymmetry of record: convention B drops the 4 INVALID pairs only (n=296, floor %.3f) while convention A counts all 8 "
          "uncommitted pairs as disagreements (34/300 = %.3f)" % (fb, fa))


def check_alarm_state_bar():
    """cb.alarm_state directly: the bar is read on the floor AS PRINTED (3 dp), it needs BOTH conventions, and a missing
    floor is UNDETERMINED, never NO ALARM. 0.1144 prints 0.114 (NO ALARM); 0.1146 prints 0.115 (UNDETERMINED)."""
    cases = [((0.0867, 0.0867), "NO ALARM"), ((0.114, 0.114), "NO ALARM"), ((0.1144, 0.1144), "NO ALARM"),
             ((0.11449, 0.0867), "NO ALARM"), ((0.1146, 0.0867), "UNDETERMINED"), ((0.115, 0.115), "UNDETERMINED"),
             ((0.0867, 0.2000), "UNDETERMINED"), ((0.0867, None), "UNDETERMINED"), ((None, None), "UNDETERMINED")]
    for (b, a), want in cases:
        got = cb.alarm_state(b, a)
        ensure(got == want, (b, a, got, want))
        ensure(got in cb.ALARM_STATES)
    ensure(cb.alarm_state(0.0867, 0.0867) != "ALARM", "ALARM is not a permitted state at pass 2")
    print("  [OK] rule (ii) at 3 dp: 0.1144 -> NO ALARM, 0.1146 -> UNDETERMINED, a missing convention -> UNDETERMINED (%d cases)" % len(cases))


def check_write_guard(tmp):
    """A degraded readout (here: pass 2 not judged) carries no ALARM STATE line. It must NOT be written to the outcome of
    record in mode "w" - that is what erased the two verbatim brackets before - but diverted, loudly, to the partial file."""
    out, _ = scenario(tmp, "guard", 150, 13, 13, pass2=False)
    assert_owns(tmp, "guard", out, pass2=False)
    partial = cb.OUT_PARTIAL
    # the diversion target is the module global OUT_PARTIAL, whose real value is the record's canary_baseline_outcome_partial.txt:
    # prove the fixture's diversion lands inside tmp and can never reach that file (main() re-checks its existence/mtime/sha too)
    ensure(partial == os.path.join(tmp, "guard", "outcome_partial.txt") and not inside_repo(partial), partial)
    ensure(not os.path.exists(out), "the outcome of record must NOT be written by a readout with no ALARM STATE line")
    ensure(os.path.exists(partial), "the degraded readout must be diverted to the partial file")
    txt = open(partial, encoding="utf-8").read()
    ensure("[WRITE-GUARD]" in txt and "was NOT overwritten" in txt)
    ensure(not any(l.startswith("ALARM STATE:") for l in txt.split("\n")))
    ensure("FLOOR: pass 2 not judged yet" in txt)
    print("  [OK] write guard: the pass-1-only readout was diverted to %s and the outcome of record was not created" % os.path.basename(partial))


def check_idempotent(tmp):
    """Two consecutive --analyze passes over the same complete pair write the file byte for byte identically."""
    out, _ = scenario(tmp, "idem", 150, 13, 13)                 # its OWN complete pass-1 + pass-2 pair, its own tag
    assert_owns(tmp, "idem", out, pass2=True)
    first = open(out, "rb").read()
    cb.analyze()
    second = open(out, "rb").read()
    ensure(first == second, "analyze() is not idempotent: %d vs %d bytes" % (len(first), len(second)))
    # newline-agnostic: analyze() opens the outcome in TEXT mode, so on Windows every "\n" is written as "\r\n" and a
    # b"\n...\n" literal can never match. Read the lines back through universal newlines and test them exactly.
    ls = lines_of(out)
    ensure("ALARM STATE: NO ALARM" in ls, "the complete readout must carry the state line at column 0")
    ensure(any(l.endswith(cb.CONV_A_NOTE.strip()) for l in ls), "the convention-A line and its verbatim bracket must be there")
    ensure(any(l == cb.ALARM_STATE_NOTE for l in ls), "the verbatim rule (ii) bracket must be there")
    print("  [OK] idempotent: %d bytes, sha256[:16] %s, reproduced exactly on a re-run" % (len(first), hashlib.sha256(first).hexdigest()[:16]))


def check_write_once(tmp):
    """[ADDED 2026-09-24, CANARY-EPOCH2-RUNG build: post-run review 2026-09-22 D2 completed] --analyze never opens the outcome of
    record in mode "w": an EXISTING outcome - here one carrying a hand-inserted line, the 4178a7c hazard - is left byte for byte
    unchanged by a complete re-run, and the refusal is printed. The fixture's own scenario() writes the file first (it is absent)."""
    out, _ = scenario(tmp, "once", 150, 13, 13)
    assert_owns(tmp, "once", out, pass2=True)
    with open(out, "a", encoding="utf-8") as f:
        f.write("  [INSERTED BY HAND - must survive every --analyze]\n")
    before = open(out, "rb").read(); mt = os.path.getmtime(out)
    cb.analyze()
    ensure(open(out, "rb").read() == before and os.path.getmtime(out) == mt, "--analyze overwrote an existing outcome of record")
    ensure(b"INSERTED BY HAND" in before)
    print("  [OK] write-once: an existing outcome with a hand-inserted line is left byte-identical by a complete --analyze (D2)")


def stamp(paths):
    """Existence + mtime + content hash of the real outcome files, so the fixture can prove it neither changed NOR CREATED
    them. The write-guard's diversion target is canary_baseline_outcome_partial.txt, a real (untracked) file of the 2026-09-22
    pilot on the main checkout: it must stay exactly as it was, and must not be created here if it is absent."""
    out = {}
    for p in paths:
        out[p] = (os.path.exists(p), os.path.getmtime(p) if os.path.exists(p) else None,
                  hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None)
    return out


def main():
    print("[SELFTEST] canary_baseline.py --analyze | script sha256[:16] %s | zero calls, temp fixtures only" % cb.script_hash())
    tmp = tempfile.mkdtemp(prefix="canary_selftest_")
    real_out, real_partial, real_eval = cb.OUT, cb.OUT_PARTIAL, rj.EVAL_DB
    before = stamp((real_out, real_partial))
    print("  files of record watched: %s" % ", ".join("%s (%s)" % (os.path.basename(p), "exists" if v[0] else "absent") for p, v in before.items()))
    try:
        check_alarm_state_bar()
        check_no_alarm(tmp); check_undetermined(tmp); check_boundary(tmp); check_conventions_differ(tmp)
        check_write_guard(tmp); check_idempotent(tmp); check_write_once(tmp)
    finally:
        cb.OUT, cb.OUT_PARTIAL, rj.EVAL_DB = real_out, real_partial, real_eval
        after = stamp((real_out, real_partial))
        for p in before:
            ensure(before[p] == after[p], "the fixture touched a file of record: %s (%r -> %r)" % (p, before[p], after[p]))
        print("  files of record unchanged (existence, mtime and sha256): %s" % ", ".join(os.path.basename(p) for p in before))
        shutil.rmtree(tmp, ignore_errors=True)
    print("[SELFTEST] all checks passed; nothing of record was read or written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
