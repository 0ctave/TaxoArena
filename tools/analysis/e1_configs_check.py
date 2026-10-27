"""E1 configs check (C-E1R-4, READY_e1_route2 29e19199): EMBEDDER-CROSS-FLAT E1's two build configs.

REGISTRATION. docs/judge_v2_program.md, EMBEDDER-CROSS-FLAT "E1-minimal (= RP09; W2): arm N-raw (PRIMARY) and N-card
(SECONDARY) ... both built from af_clean_s42.toml"; the E1 ROUTE (E1-ROUTE registration, READY_e1_route2 29e19199) refuses
af_clean_s42.toml itself as an outputDir, so C-E1R-4 requires E1's two configs committed and declared before E1:
af_clean_s42.toml with ONLY outputDir changed, two distinct outputDirs outside every object of record (a non-treatment key).

THE TWO CONFIGS (committed beside this script):
  experiment_configs/e1_route/E1_nomic_raw_af_clean_s42.toml   outputDir "experiment_results/e1_route/E1_nomic_raw"   (N-raw)
  experiment_configs/e1_route/E1_nomic_card_af_clean_s42.toml  outputDir "experiment_results/e1_route/E1_nomic_card"  (N-card)
Each = a header comment, the line '# ---- BASE ----', then experiment_configs/anchorfree/redraw/af_clean_s42.toml line for line
(line endings normalised) except EXACTLY ONE line: the outputDir line.

WHAT check() ASSERTS (prints "[E1-CONFIGS] OK <arm>" or "[E1-CONFIGS] REFUSED: <reason>", rc 2):
  (a) text: below the BASE marker, same line count as the base and exactly 1 differing line, which is the base's outputDir line;
  (b) TOML: the parsed key diff against af_clean_s42.toml is exactly ["outputDir"], with the expected value;
  (c) the two outputDirs are distinct, under experiment_results/e1_route/, and not L1's experiment_results/e1_route/L1_short;
  (d) the launcher (tools/analysis/e1_route_launch.py, unchanged) ADMITS it: check_config on this checkout's root with the real P
      (protected_set over the pins file of record) returns the expected outputDir; and run() on a fixture data root with a fake
      JVM reaches exactly one launch whose last argument is "--args=--config <the config>".
LAUNCH (not by this script): python tools/analysis/e1_route_launch.py --arm nomic_raw|nomic_card --config <the config>, from the
main checkout, after E1-ROUTE C1-C5 HELD, in one rule-7 window with a backup first. Zero calls; no JVM; nothing written but temp.

  python tools/analysis/e1_configs_check.py            # check the two committed configs (rc 0 / 2)
  python tools/analysis/e1_configs_check.py --selftest # 11 cases: the committed configs pass (values asserted); 10 refusals

SELFTEST MUTANTS (2026-10-01; one temporary in-place edit of this file at a time, selftest run, bytes restored; K = killed):
  M1 (a) "!= 1 differing line" -> "> 1" (0 lines admitted) K [SURVIVED first; case "(a) a 0-line diff" added] | M2 (a) the differing line not required to be the outputDir line K |
  M3 (b) key diff check removed K | M4 (c) distinctness check removed K | M5 (c) L1_short exclusion removed K |
  M6 (d) the fixture run()'s refusal check disabled K [SURVIVED first; case "(d) a fixture-launch refusal" added] | M7 (d) check_config on the real root removed K   -> 7 / 7 KILLED
"""
import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import e1_route_launch as L  # noqa: E402

TAG = "[E1-CONFIGS]"
MARK = "# ---- BASE ----"
BASE = os.path.join(ROOT, "experiment_configs", "anchorfree", "redraw", "af_clean_s42.toml")
CFG_DIR = os.path.join(ROOT, "experiment_configs", "e1_route")
CONFIGS = {"nomic_raw": ("E1_nomic_raw_af_clean_s42.toml", "experiment_results/e1_route/E1_nomic_raw"),
           "nomic_card": ("E1_nomic_card_af_clean_s42.toml", "experiment_results/e1_route/E1_nomic_card")}
L1_OUT = "experiment_results/e1_route/L1_short"
OUT_PREFIX = "experiment_results/e1_route/"


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refused(2)


def _lines(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8").splitlines()


def _toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def _rel(p, root):
    try:
        return os.path.relpath(p, root).replace(os.sep, "/")
    except ValueError:                                     # another drive (a temp fixture): the path as given
        return p


def text_diff(base, cfg):
    """(a): the indices of the lines differing below MARK; refuses on a missing marker or a length change."""
    b, c = _lines(base), _lines(cfg)
    if MARK not in c:
        refuse("(a) %s has no '%s' line" % (cfg, MARK))
    body = c[c.index(MARK) + 1:]
    if len(body) != len(b):
        refuse("(a) %s: %d lines below the BASE marker, the base has %d" % (cfg, len(body), len(b)))
    return [i for i in range(len(b)) if b[i] != body[i]], b, body


def fake_root(tmp):
    """A data root with P (pins file pinning the four DIR files; small real SQLite main cache), as the launcher's own fixture."""
    import embedder_arms as EA
    from data_v2 import ro
    droot = os.path.join(tmp, "root")
    os.makedirs(os.path.join(droot, L.DIR_REL))
    arms = {}
    for a in L.PIN_ARMS:
        fn = EA.cache_file(EA.ARMS[a])
        p = os.path.join(droot, L.DIR_REL, fn)
        with open(p, "wb") as f:
            f.write(("arm file %s\n" % a).encode() * 50)
        arms[a] = {"sha256": L.sha256_file(p), "file": fn, "model_digest": "d-" + a}
    for s in L.SOURCE_DBS + (L.FROZEN,):
        with open(os.path.join(droot, s), "wb") as f:
            f.write(b"source " + s.encode())
    c = ro.create_new(os.path.join(droot, L.MAIN_CACHE))
    c.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY, t TEXT)"); c.execute("INSERT INTO queries VALUES (1, 'x')")
    c.execute("CREATE TABLE reserved_pool_meta (pool_id TEXT PRIMARY KEY)"); c.commit(); c.close()
    pf = os.path.join(tmp, "pins.json")
    with open(pf, "w") as f:
        json.dump({"schema": EA.ARM_PINS_SCHEMA, "arms": arms}, f)
    return droot, pf


class FakeJvm:
    def __init__(self):
        self.calls = []

    def __call__(self, cmd, cwd):
        self.calls.append(cmd)
        return 0


def launcher_admits(arm, cfg, want_out, root=ROOT, fixture=None):
    """(d): check_config on the real root and P, then run() on a fixture data root with a fake JVM (one launch)."""
    pins = L.load_pins()
    members = L.protected_set(root, pins)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            odp, _ = L.check_config(cfg, root, members, os.path.join(root, L.DIR_REL))
        except SystemExit:
            odp = None
    if odp is None:
        refuse("(d) the launcher refuses %s on this checkout: %s" % (cfg, buf.getvalue().strip()))
    if L._norm(odp) != L._norm(os.path.join(root, want_out)):
        refuse("(d) the launcher reads outputDir %s, not %s" % (odp, want_out))
    tmp = tempfile.mkdtemp(prefix="e1cfg_")
    try:
        droot, pf = (fixture or fake_root)(tmp)
        jvm = FakeJvm()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = L.run(arm, cfg, droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="cfg", pids=lambda: [])
            except SystemExit:
                rc = None
        if rc != 0 or len(jvm.calls) != 1 or jvm.calls[0][-1] != "--args=--config %s" % cfg:
            refuse("(d) the launcher did not admit %s on a fixture root (rc %r, %d launches): %s"
                   % (cfg, rc, len(jvm.calls), buf.getvalue().strip()[-400:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check(configs=None, base=BASE, root=ROOT, fixture=None):
    """Returns {arm: outputDir}; prints OK lines; refuses (rc 2) on any failed assertion."""
    configs = configs or {a: (os.path.join(CFG_DIR, f), od) for a, (f, od) in CONFIGS.items()}
    a = _toml(base)
    base_out_idx = [i for i, l in enumerate(_lines(base)) if l.startswith("outputDir")]
    if len(base_out_idx) != 1:
        refuse("(a) the base %s has %d outputDir lines" % (base, len(base_out_idx)))
    seen = {}
    for arm, (cfg, want) in sorted(configs.items()):
        idx, b_lines, body = text_diff(base, cfg)
        if len(idx) != 1:
            refuse("(a) %s differs from af_clean_s42.toml in %d lines below the BASE marker, not 1: %s" % (cfg, len(idx), idx))
        if idx != base_out_idx:
            refuse("(a) %s: the differing line %d is not the outputDir line %d" % (cfg, idx[0] + 1, base_out_idx[0] + 1))
        b = _toml(cfg)
        kd = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if kd != ["outputDir"] or b.get("outputDir") != want:
            refuse("(b) %s: key diff %s, outputDir %r (want ['outputDir'], %r)" % (cfg, kd, b.get("outputDir"), want))
        od = b["outputDir"]
        if not od.startswith(OUT_PREFIX) or od.rstrip("/") == L1_OUT or od in seen.values():
            refuse("(c) %s: outputDir %s must lie under %s, differ from %s and from the other arm's" % (cfg, od, OUT_PREFIX, L1_OUT))
        launcher_admits(arm, cfg, od, root, fixture)
        seen[arm] = od
        print("%s OK %s: %s = af_clean_s42.toml + 1 line (L%d outputDir = %s); the launcher admits it"
              % (TAG, arm, _rel(cfg, root), base_out_idx[0] + 1, od))
    return seen


def selftest():
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="e1cfgst_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %r" % (name, type(e).__name__, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def quiet(fn, *a, **k):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                return fn(*a, **k), buf.getvalue(), None
            except SystemExit as e:
                return None, buf.getvalue(), e

    real = {a: (os.path.join(CFG_DIR, f), od) for a, (f, od) in CONFIGS.items()}

    def committed(tmp):
        got, text, err = quiet(check)
        assert err is None, text
        assert got == {"nomic_raw": "experiment_results/e1_route/E1_nomic_raw",
                       "nomic_card": "experiment_results/e1_route/E1_nomic_card"}, got
        assert text.count("%s OK " % TAG) == 2 and "L44 outputDir" in text, text

    def mutate(tmp, arm, fn, name="m.toml"):
        src, od = real[arm]
        with open(src, "rb") as f:
            t = f.read().decode("utf-8")
        p = os.path.join(tmp, name)
        with open(p, "wb") as f:
            f.write(fn(t).encode("utf-8"))
        return p, od

    def refused(cfgs, want):
        got, text, err = quiet(check, cfgs)
        assert isinstance(err, Refused) and err.code == 2 and ("REFUSED: %s" % want) in text, (want, text)

    def zero_lines(tmp):                                   # the base itself below the marker: 0 differing lines
        p, od = mutate(tmp, "nomic_raw", lambda t: t.replace('"experiment_results/e1_route/E1_nomic_raw"',
                       '"experiment_results/anchorfree/redraw/af_clean_s42"'))
        refused({"nomic_raw": (p, od)}, "(a) %s differs from af_clean_s42.toml in 0 lines" % p)

    def fixture_refusal(tmp):                              # (d) run() refuses on the fixture root (seed dir exists): surfaced
        def fx(t):
            droot, pf = fake_root(t)
            os.makedirs(os.path.join(droot, real["nomic_raw"][1], "seed_42"))
            return droot, pf
        got, text, err = quiet(check, {"nomic_raw": real["nomic_raw"]}, fixture=fx)
        want = "REFUSED: (d) the launcher did not admit %s on a fixture root (rc None, 0 launches)" % real["nomic_raw"][0]
        assert isinstance(err, Refused) and want in text and "seed_42 exists" in text, text

    def two_lines(tmp):                                    # numIterations also changed (the L1 shape): 2 lines
        p, od = mutate(tmp, "nomic_raw", lambda t: t.replace("numIterations         = 50", "numIterations         = 2"))
        refused({"nomic_raw": (p, od)}, "(a) %s differs from af_clean_s42.toml in 2 lines" % p)

    def other_line(tmp):                                   # outputDir restored, another line changed: 1 line, not outputDir
        p, od = mutate(tmp, "nomic_raw", lambda t: t.replace('"experiment_results/e1_route/E1_nomic_raw"',
                       '"experiment_results/anchorfree/redraw/af_clean_s42"').replace("numIterations         = 50", "numIterations         = 2"))
        refused({"nomic_raw": (p, od)}, "(a) %s: the differing line" % p)

    def key_value(tmp):                                    # the text line differs but declares another value than expected
        p, _ = mutate(tmp, "nomic_raw", lambda t: t)
        refused({"nomic_raw": (p, "experiment_results/e1_route/OTHER")}, "(b) %s: key diff ['outputDir'], outputDir" % p)

    def same_out(tmp):                                     # both arms on one outputDir
        p1, od = mutate(tmp, "nomic_raw", lambda t: t, "a.toml")
        p2, _ = mutate(tmp, "nomic_raw", lambda t: t, "b.toml")
        refused({"nomic_card": (p1, od), "nomic_raw": (p2, od)}, "(c) %s: outputDir" % p2)

    def l1_out(tmp):                                       # the L1 short stop's outputDir
        p, _ = mutate(tmp, "nomic_raw", lambda t: t.replace("E1_nomic_raw\"", "L1_short\""))
        refused({"nomic_raw": (p, L1_OUT)}, "(c) %s: outputDir" % p)

    def no_marker(tmp):
        p, od = mutate(tmp, "nomic_card", lambda t: t.replace(MARK, "# ---- base ----"))
        refused({"nomic_card": (p, od)}, "(a) %s has no '%s' line" % (p, MARK))

    def launcher_refuses(tmp):                             # passes (a)-(c) with a fake e1_route prefix, but the launcher refuses
        cfgs = {}
        p, _ = mutate(tmp, "nomic_raw", lambda t: t.replace('"experiment_results/e1_route/E1_nomic_raw"',
                      '"experiment_results/e1_route/../embedder_cross/x"'))
        cfgs["nomic_raw"] = (p, "experiment_results/e1_route/../embedder_cross/x")
        refused(cfgs, "(d) the launcher refuses %s on this checkout" % p)

    def fixture_launch(tmp):                               # (d)'s second leg: a fresh seed dir is required on the fixture root
        jvm = FakeJvm()
        droot, pf = fake_root(tmp)
        cfg = real["nomic_card"][0]
        os.makedirs(os.path.join(droot, real["nomic_card"][1], "seed_42"))
        rc, text, err = quiet(L.run, "nomic_card", cfg, droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="x", pids=lambda: [])
        assert isinstance(err, SystemExit) and "seed_42 exists" in text and jvm.calls == [], text
        shutil.rmtree(os.path.join(droot, real["nomic_card"][1]))
        rc, text, err = quiet(L.run, "nomic_card", cfg, droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="y", pids=lambda: [])
        assert err is None and rc == 0 and len(jvm.calls) == 1, text
        assert "outputDir %s" % os.path.join(droot, "experiment_results/e1_route/E1_nomic_card") in text, text

    for name, fn in (("the two committed configs pass, values of record", committed),
                     ("(a) a 0-line diff refused", zero_lines), ("(d) a fixture-launch refusal surfaces", fixture_refusal),
                     ("(a) a 2-line diff refused", two_lines), ("(a) a 1-line diff off the outputDir line refused", other_line),
                     ("(b) an unexpected outputDir value refused", key_value), ("(c) one outputDir for both arms refused", same_out),
                     ("(c) L1_short as outputDir refused", l1_out), ("(a) a missing BASE marker refused", no_marker),
                     ("(d) a launcher refusal surfaces", launcher_refuses), ("(d) fixture launch: fresh dir admitted, existing refused", fixture_launch)):
        case(name, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
