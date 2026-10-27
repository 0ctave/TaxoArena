"""LCB-D9-BYTE-INERTNESS operator helper 2/3, VERSION 2 (delta READY docs/reviews/READY_lcb_d9_delta1.md; supersedes
d9_leg_check.py 9ee6d43d for the rerun only; v1 is kept untouched). Per-leg validity readouts V3 (D9-R1 class counts),
V4 (D9-R2 [BOOT] jar line), V6 (sanity lines; Gradle result; recorded exit code), V7 (embedding misses), V8 (wall time,
read as deviation DEV-V8). Read-only. Appends to <stage>/d9_disc.txt; writes <stage>/d9_misses_<leg>.txt.

usage: python d9_leg_check_v2.py <A|B> <leg root> <bootRun transcript> <stage dir>
Exit 0 iff every check of the leg passes; the printed lines are the evidence.

Changes against v1 (nothing else differs; V3, V6 sanity strings, V7 are v1's code):
  V4  a [BOOT] line broken by a console wrap is re-joined (up to 3 continuation lines, no separator inserted), every
      "[BOOT] TaxoAdapt starting" occurrence must yield a jar token equal to the leg's own class dir, and at least one
      of them must follow "> Task :bootRun" (the JVM that wrote the outputs). A token that cannot be recovered is VOID.
  V6  adds the third conjunct of reading R5: the LAST "EXIT <n>" in <stage>/leg<L>_exit.txt must be 0 (v1 did not
      read it).
  V8  DEV-V8: the registered floor of 1 min is not applied (unreachable at warm cache; P4 = 0 misses); the ceiling of
      8 min is applied to BOTH run_manifest duration_ms and the Gradle "BUILD SUCCESSFUL in ..." wall time, and the
      construction must have run: duration_ms > 0 and >= 1 data row in diagnostics/iteration_metrics.csv. Both times
      and the floor comparison are printed.
"""
import json, os, re, sys

VERSION = "d9_leg_check_v2"
IDS = ("LIVECODEBENCH", "fetchLiveCodeBench", "lcbWorkDirGuard", "LcbWorkDirGuardState")
BAR_B = {"LIVECODEBENCH": 3, "fetchLiveCodeBench": 1, "lcbWorkDirGuard": 1, "LcbWorkDirGuardState": 1}
OUT = os.path.join("experiment_results", "topic_partition", "ag_news_smoke_s42", "seed_42")
SANITY = ("Fetched 2000 AG News queries across 4 categories", "[POOL] recorded p18579549e6d95873",
          "[SPLIT-SIDE] 1400 train (145 gate) / 600 test")
BOOT = "[BOOT] TaxoAdapt starting"
CEIL_S = 480


def decode(raw):
    if raw[:2] in (bytes([0xFF, 0xFE]), bytes([0xFE, 0xFF])):
        return raw.decode("utf-16")
    return raw.decode("utf-8", "replace")


def boot_jars(tx):
    """[(line index, jar token or None)] for every BOOT occurrence; wrap-tolerant, fail-closed."""
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
    m = re.findall(r"BUILD SUCCESSFUL in ((?:\d+h )?(?:\d+m )?(?:\d+s)?(?:\d+ms)?)", tx)
    if not m:
        return None
    s, t = 0.0, m[-1]
    for v, u in re.findall(r"(\d+)(h|ms|m|s)", t):
        s += int(v) * {"h": 3600, "m": 60, "s": 1, "ms": 0.001}[u]
    return s


def main(leg, root, transcript, stage):
    L, ok = [], True

    def say(s):
        L.append(s)
        print(s, flush=True)
    say("[%s] leg %s root %s transcript %s" % (VERSION, leg, root, transcript))
    cls = os.path.join(root, "build", "classes", "kotlin", "main")
    if not os.path.isdir(cls):
        say("[V3 %s] no compiled classes at %s" % (leg, cls))
        ok = False
    else:
        files = [os.path.join(d, f) for d, _s, fs in os.walk(cls) for f in fs if f.endswith(".class")]
        blobs = {p: open(p, "rb").read() for p in files}
        counts = {i: sum(1 for b in blobs.values() if i.encode() in b) for i in IDS}
        say("[V3 %s] %d class files; files containing %s" % (leg, len(files), counts))
        if leg == "A":
            ok &= all(v == 0 for v in counts.values())
        else:
            ok &= all(counts[i] >= BAR_B[i] for i in IDS)
    tx = decode(open(transcript, "rb").read())
    want = "file:/" + os.path.abspath(cls).replace("\\", "/") + "/"
    boots, lines = boot_jars(tx)
    task = [i for i, ln in enumerate(lines) if ln.strip() == "> Task :bootRun"]
    after = [j for (i, j) in boots if task and i > task[0]]
    say("[V4 %s] %d [BOOT] start line(s) at transcript lines %s; jar tokens %s; expected %s"
        % (leg, len(boots), [i + 1 for i, _ in boots], [j for _, j in boots], want))
    say("[V4 %s] '> Task :bootRun' at line(s) %s; [BOOT] after it: %d" % (leg, [i + 1 for i in task], len(after)))
    v4 = bool(boots) and all(j is not None and j.lower() == want.lower() for _, j in boots) and len(after) >= 1
    say("[V4 %s] %s" % (leg, "PASS" if v4 else "FAIL"))
    ok &= v4
    built = "BUILD SUCCESSFUL" in tx and "BUILD FAILED" not in tx
    say("[V6 %s] Gradle: %s" % (leg, "BUILD SUCCESSFUL" if built else "NOT SUCCESSFUL"))
    ok &= built
    exf = os.path.join(stage, "leg%s_exit.txt" % leg)
    exits = re.findall(r"EXIT (-?\d+)", decode(open(exf, "rb").read())) if os.path.isfile(exf) else []
    say("[V6 %s] recorded exit codes in %s: %s (the last must be 0)" % (leg, exf, exits))
    ok &= bool(exits) and exits[-1] == "0"
    log = os.path.join(root, OUT, "headless_run.log")
    hl = open(log, "rb").read().decode("utf-8", "replace") if os.path.isfile(log) else ""
    for s in SANITY:
        n = hl.count(s)
        say("[V6 %s] '%s' x%d" % (leg, s, n))
        ok &= n >= 1
    man = os.path.join(root, OUT, "diagnostics", "run_manifest.json")
    m = json.load(open(man, encoding="utf-8")) if os.path.isfile(man) else {}
    say("[V6 %s] run_manifest exit_reason %r (written in a finally block; not proof alone: R5)" % (leg, m.get("exit_reason")))
    ok &= m.get("exit_reason") == "completed"
    miss = sum(int(x) for x in re.findall(r"Computing and caching embeddings for (\d+) new queries", hl))
    cached = re.findall(r"All (\d+) requested embeddings are already cached on disk", hl)
    say("[V7 %s] embedding misses %d (cache-hit lines %s)" % (leg, miss, cached))
    dur = m.get("duration_ms")
    gs = gradle_seconds(tx)
    im = os.path.join(root, OUT, "diagnostics", "iteration_metrics.csv")
    rows = max(0, sum(1 for ln in open(im, encoding="utf-8") if ln.strip()) - 1) if os.path.isfile(im) else 0
    say("[V8 %s] duration_ms %s; Gradle wall %s s; iteration_metrics data rows %d" % (leg, dur, gs, rows))
    say("[V8 %s] registered bar [1, 8] min: floor 1 min NOT APPLIED (DEV-V8; below it: duration %s, Gradle %s); ceiling 8 min"
        " applied to both" % (leg, isinstance(dur, int) and dur < 60000, gs is not None and gs < 60))
    ok &= isinstance(dur, int) and 0 < dur <= CEIL_S * 1000 and gs is not None and gs <= CEIL_S and rows >= 1
    say("[LEG %s] %s" % (leg, "ALL VALIDITY CHECKS PASS" if ok else "A VALIDITY CHECK FAILED: the leg is VOID (failed precondition)"))
    with open(os.path.join(stage, "d9_disc.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(stage, "d9_misses_%s.txt" % leg), "w") as f:
        f.write("%d\n" % miss)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
