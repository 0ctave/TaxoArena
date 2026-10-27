"""EVAL-METRIC-DETERMINISM operator helper: the per-leg validity readouts (registration docs/judge_v2_program.md
L20311-L20389, 55a6ce1; VALIDITY V3-V8) and the leg's class lists, derived from d9_leg_check_v2.py (blob:e5f2ff7a,
sha256-lf16:b2d1ae8df0d1bd35) and d9b_aux.py classlists; the originals are untouched. Zero calls. Read-only on the leg.

usage: python emd_leg_check.py <P1|R1|R2|P2|R3> <leg root> <bootRun transcript> <$ST>
Writes (write-once): $ST/leg_<L>.json, $ST/classlists/leg<L>_canonicalByRawText.txt, $ST/classlists/leg<L>_all.txt;
appends the printed lines to $ST/emd_disc.txt (UTF-8). Run it after the leg and BEFORE any worktree removal.
Exit 0 iff every per-leg check passes; 1 = a check failed (the leg is VOID); 2 = refusal (bad arguments, outputs exist).

CHECKS (the bars are the registration's):
  V3 per leg (X1): the number of files under build/classes/kotlin/main whose bytes contain `canonicalByRawText`
     (`grep -rlaF` semantics; .class files counted): P legs 0; R legs >= 1. The cross-leg parts (R1 = R2 = R3, the class-name
     lists R1 = R2 = R3 and P1 = P2) are the verdict's. The build's declared count (3) is PRINTED beside, not a bar.
  V4 every "[BOOT] TaxoAdapt starting" jar token names this leg's own classes dir, and >= 1 follows "> Task :bootRun".
  V5 compileKotlin EXECUTED: a line exactly "> Task :compileKotlin" (not UP-TO-DATE, FROM-CACHE, SKIPPED, NO-SOURCE).
  V6 BUILD SUCCESSFUL, no BUILD FAILED, last EXIT 0 in $ST/leg<L>_exit.txt, the three sanity lines in headless_run.log,
     run_manifest exit_reason completed, commit = the leg's assigned commit (BASE or FIX) and dirty False.
  V7 embedding misses counted and recorded (the equality across the five legs is the verdict's).
  V8 run_manifest duration_ms and the Gradle "BUILD SUCCESSFUL in" time each under 8 min (strict), duration_ms > 0, >= 1 data row in
     diagnostics/iteration_metrics.csv.
  TC (re-cut 2026-09-30, B-EM-1 (4)): every "[THREAD-CAP] requested=<r> availableProcessors=<n>" line of the transcript reads
     requested=12 availableProcessors=12, and there is at least one; the witness set is recorded (thread_cap) and its equality
     across the five legs is the verdict's.
  Recorded for P9 and the mechanism readout: duration_ms, Gradle seconds, the three fields from both files.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emd_common as E  # noqa: E402
import emd_compare as C  # noqa: E402

VERSION = "emd_leg_check-2"
BOOT = "[BOOT] TaxoAdapt starting"
CLS = os.path.join("build", "classes", "kotlin", "main")


def boot_jars(tx):
    lines = tx.replace("\r", "").split("\n")
    out = []
    for i, ln in enumerate(lines):
        if BOOT not in ln:
            continue
        logical, k = ln[ln.index(BOOT):], i
        while "jar=" not in logical and k < i + 3 and k + 1 < len(lines):
            k += 1
            logical += lines[k]
        m = re.search(r"jar=(\S+)", logical)
        out.append((i, m.group(1) if m else None))
    return out, lines


def gradle_seconds(tx):
    """The last 'BUILD SUCCESSFUL in <t>' as seconds; None when <t> is not wholly made of '<n>h' / '<n>m' / '<n>s' / '<n>ms'
    tokens (d9_leg_check_v2's pattern read 'in 8m' as 0 s: a fail-open, fixed here)."""
    m = re.findall(r"BUILD SUCCESSFUL in ([^\r\n]*)", tx)
    if not m:
        return None
    t = m[-1].strip()
    toks = re.findall(r"(\d+)(ms|h|m|s)(?![A-Za-z])", t)
    if not toks or re.sub(r"\s*\d+(?:ms|h|m|s)(?![A-Za-z])\s*", "", t):
        return None
    return sum(int(v) / 1000 if u == "ms" else int(v) * {"h": 3600, "m": 60, "s": 1}[u] for v, u in toks)


def main(leg, root, transcript, stage):
    if leg not in E.LEGS:
        print("[%s] refusing: leg must be one of %s" % (VERSION, E.LEGS))
        return 2
    cl = os.path.join(stage, "classlists")
    lj = os.path.join(stage, "leg_%s.json" % leg)
    outs = [os.path.join(cl, "leg%s_%s.txt" % (leg, E.X1)), os.path.join(cl, "leg%s_all.txt" % leg)]
    for p in [lj] + outs:
        if os.path.exists(p):
            print("[%s] refusing: %s exists (write-once)" % (VERSION, p))
            return 2
    if not os.path.isfile(transcript):
        print("[%s] refusing: transcript %s absent" % (VERSION, transcript))
        return 2
    os.makedirs(cl, exist_ok=True)
    L, checks = [], {}

    def say(s):
        L.append(s)
        print(s, flush=True)
    say("[%s] leg %s root %s transcript %s commit expected %s" % (VERSION, leg, root, transcript, E.COMMIT[leg]))
    # V3 (X1) and the class lists
    base = os.path.join(root, CLS)
    x1n, ncls = None, 0
    if not os.path.isdir(base):
        say("[V3 %s] no compiled classes at %s" % (leg, base))
        checks["V3"] = False
        for p in outs:
            E.write_once(p, "")
    else:
        files = sorted(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/") for dp, _s, fs in os.walk(base) for f in fs)
        hit = [f for f in files if E.X1.encode() in open(os.path.join(root, f), "rb").read()]
        cls = [f for f in files if f.endswith(".class")]
        x1n, ncls = sum(h.endswith(".class") for h in hit), len(cls)
        E.write_once(outs[0], "".join(h + "\n" for h in hit))
        E.write_once(outs[1], "".join(h + "\n" for h in cls))
        want = "0" if leg in E.P_LEGS else ">= 1"
        checks["V3"] = (x1n == 0) if leg in E.P_LEGS else (x1n >= 1)
        say("[V3 %s] %d class files; %d .class file(s) contain %s (non-.class hits: %s); bar %s -> %s ; declared count %d: %s"
            % (leg, ncls, x1n, E.X1, [h for h in hit if not h.endswith(".class")] or "none", want,
               "PASS" if checks["V3"] else "FAIL", E.X1_DECLARED_COUNT,
               "n/a (P leg)" if leg in E.P_LEGS else ("match" if x1n == E.X1_DECLARED_COUNT else "DOES NOT MATCH (printed)")))
        for h in hit:
            say("[V3 %s]   %s" % (leg, h))
    tx = E.decode(open(transcript, "rb").read())
    # V4
    want = "file:/" + os.path.abspath(base).replace("\\", "/") + "/"
    boots, lines = boot_jars(tx)
    task = [i for i, ln in enumerate(lines) if ln.strip() == "> Task :bootRun"]
    after = [j for (i, j) in boots if task and i > task[0]]
    checks["V4"] = bool(boots) and all(j is not None and j.lower() == want.lower() for _, j in boots) and len(after) >= 1
    say("[V4 %s] %d [BOOT] line(s), jar tokens %s, expected %s; after '> Task :bootRun': %d -> %s"
        % (leg, len(boots), sorted({j for _, j in boots}, key=str), want, len(after), "PASS" if checks["V4"] else "FAIL"))
    # V5
    ck = [ln.rstrip() for ln in lines if ln.startswith("> Task :compileKotlin")]
    checks["V5"] = "> Task :compileKotlin" in ck and len(ck) == 1
    say("[V5 %s] compileKotlin lines %s -> %s" % (leg, ck, "EXECUTED (PASS)" if checks["V5"] else "NOT EXECUTED (FAIL)"))
    # V6
    ok6 = "BUILD SUCCESSFUL" in tx and "BUILD FAILED" not in tx
    say("[V6 %s] Gradle: %s" % (leg, "BUILD SUCCESSFUL" if ok6 else "NOT SUCCESSFUL"))
    exf = os.path.join(stage, "leg%s_exit.txt" % leg)
    exits = re.findall(r"EXIT (-?\d+)", E.decode(open(exf, "rb").read())) if os.path.isfile(exf) else []
    say("[V6 %s] recorded exit codes in %s: %s (the last must be 0)" % (leg, exf, exits))
    ok6 &= bool(exits) and exits[-1] == "0"
    log = os.path.join(root, E.OUT, "seed_42", "headless_run.log")
    hl = open(log, "rb").read().decode("utf-8", "replace") if os.path.isfile(log) else ""
    for s in E.SANITY:
        n = hl.count(s)
        say("[V6 %s] '%s' x%d" % (leg, s, n))
        ok6 &= n >= 1
    man = os.path.join(root, E.OUT, "seed_42", "diagnostics", "run_manifest.json")
    try:
        m = json.load(open(man, encoding="utf-8")) if os.path.isfile(man) else {}
    except ValueError:
        m = {}
    say("[V6 %s] run_manifest exit_reason %r commit %r dirty %r (expected completed / %s / False)"
        % (leg, m.get("exit_reason"), m.get("commit"), m.get("dirty"), E.COMMIT[leg]))
    ok6 &= m.get("exit_reason") == "completed" and m.get("commit") == E.COMMIT[leg] and m.get("dirty") is False
    checks["V6"] = ok6
    say("[V6 %s] %s" % (leg, "PASS" if ok6 else "FAIL"))
    # V7
    miss = sum(int(x) for x in re.findall(r"Computing and caching embeddings for (\d+) new queries", hl))
    cached = re.findall(r"All (\d+) requested embeddings are already cached on disk", hl)
    say("[V7 %s] embedding misses %d (cache-hit lines %s); equality across legs: the verdict" % (leg, miss, cached))
    # V8
    dur = m.get("duration_ms")
    gs = gradle_seconds(tx)
    im = os.path.join(root, E.OUT, "seed_42", "diagnostics", "iteration_metrics.csv")
    rows = max(0, sum(1 for ln in open(im, encoding="utf-8") if ln.strip()) - 1) if os.path.isfile(im) else 0
    checks["V8"] = (isinstance(dur, int) and not isinstance(dur, bool) and 0 < dur < E.CEIL_S * 1000
                    and gs is not None and gs < E.CEIL_S and rows >= 1)
    say("[V8 %s] duration_ms %s; Gradle wall %s s; iteration_metrics data rows %d; ceiling %d s -> %s"
        % (leg, dur, gs, rows, E.CEIL_S, "PASS" if checks["V8"] else "FAIL"))
    # TC: the THREAD-CAP witness on EVERY such line (a fork without the cap, or a second fork with another count, fails)
    caps = re.findall(E.TC_RE, tx)
    tcw = sorted({"requested=%s availableProcessors=%s" % c for c in caps})
    checks["TC"] = bool(caps) and all(c == (str(E.THREAD_CAP_N), str(E.THREAD_CAP_N)) for c in caps)
    say("[TC %s] %d [THREAD-CAP] line(s), witness %s (bar: every line %s) -> %s"
        % (leg, len(caps), tcw, E.TC_WITNESS, "PASS" if checks["TC"] else "FAIL"))
    vals = C.dropped_values(root)
    for k in sorted(vals):
        say("[FIELDS %s] %s = %s" % (leg, k, vals[k]))
    ok = all(checks.get(k) is True for k in ("V3", "V4", "V5", "V6", "V8", "TC"))
    say("[LEG %s] %s" % (leg, "ALL PER-LEG CHECKS PASS" if ok else "A CHECK FAILED: the leg is VOID (failed precondition): %s"
                         % [k for k in ("V3", "V4", "V5", "V6", "V8", "TC") if checks.get(k) is not True]))
    E.write_json_once(lj, {"version": VERSION, "leg": leg, "root": root, "commit_expected": E.COMMIT[leg], "checks": checks,
                           "x1_count": x1n, "class_files": ncls, "classlist_x1_sha": E.sha(outs[0]),
                           "classlist_all_sha": E.sha(outs[1]), "misses": miss, "duration_ms": dur, "gradle_s": gs, "thread_cap": tcw,
                           "values": vals})
    with open(os.path.join(stage, "emd_disc.txt"), "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(*sys.argv[1:5]))
