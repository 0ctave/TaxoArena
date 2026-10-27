"""LCB-D9-BYTE-INERTNESS operator helper 2/3: the per-leg validity readouts V3 (D9-R1 class counts), V4 (D9-R2 [BOOT]
jar line), V6 (sanity lines; exit code), V7 (embedding misses), V8 (wall time). Read-only. Appends to <stage>/d9_disc.txt.

usage: python d9_leg_check.py <A|B> <leg root> <bootRun transcript> <stage dir>
Exit 0 iff every check of the leg passes; the printed lines are the evidence.
"""
import json, os, re, sys

IDS = ("LIVECODEBENCH", "fetchLiveCodeBench", "lcbWorkDirGuard", "LcbWorkDirGuardState")
BAR_B = {"LIVECODEBENCH": 3, "fetchLiveCodeBench": 1, "lcbWorkDirGuard": 1, "LcbWorkDirGuardState": 1}
OUT = os.path.join("experiment_results", "topic_partition", "ag_news_smoke_s42", "seed_42")
SANITY = ("Fetched 2000 AG News queries across 4 categories", "[POOL] recorded p18579549e6d95873",
          "[SPLIT-SIDE] 1400 train (145 gate) / 600 test")


def main(leg, root, transcript, stage):
    L, ok = [], True

    def say(s):
        L.append(s)
        print(s, flush=True)
    cls = os.path.join(root, "build", "classes", "kotlin", "main")
    if not os.path.isdir(cls):
        say("[V3 %s] no compiled classes at %s" % (leg, cls))
        ok = False
        counts = {i: -1 for i in IDS}
    else:
        files = [os.path.join(d, f) for d, _s, fs in os.walk(cls) for f in fs if f.endswith(".class")]
        blobs = {p: open(p, "rb").read() for p in files}
        counts = {i: sum(1 for b in blobs.values() if i.encode() in b) for i in IDS}
        say("[V3 %s] %d class files; files containing %s" % (leg, len(files), counts))
        if leg == "A":
            ok &= all(v == 0 for v in counts.values())
        else:
            ok &= all(counts[i] >= BAR_B[i] for i in IDS)
    raw = open(transcript, "rb").read()
    tx = raw.decode("utf-16") if raw[:2] in (bytes([0xFF, 0xFE]), bytes([0xFE, 0xFF])) else raw.decode("utf-8", "replace")
    boot = [m for m in re.findall(r"\[BOOT\][^\n]*jar=(\S+)", tx)]
    want = "file:/" + os.path.abspath(cls).replace("\\", "/") + "/"
    say("[V4 %s] [BOOT] jar lines: %s; expected %s" % (leg, boot, want))
    ok &= bool(boot) and all(b.lower() == want.lower() for b in boot)
    built = "BUILD SUCCESSFUL" in tx and "BUILD FAILED" not in tx
    say("[V6 %s] Gradle: %s" % (leg, "BUILD SUCCESSFUL" if built else "NOT SUCCESSFUL"))
    ok &= built
    log = os.path.join(root, OUT, "headless_run.log")
    hl = open(log, "rb").read().decode("utf-8", "replace") if os.path.isfile(log) else ""
    for s in SANITY:
        n = hl.count(s)
        say("[V6 %s] '%s' x%d" % (leg, s, n))
        ok &= n >= 1
    man = os.path.join(root, OUT, "diagnostics", "run_manifest.json")
    m = json.load(open(man, encoding="utf-8")) if os.path.isfile(man) else {}
    say("[V6 %s] run_manifest exit_reason %r (NOTE: written in a finally block; 'completed' alone is not proof: the Gradle exit above is)"
        % (leg, m.get("exit_reason")))
    ok &= m.get("exit_reason") == "completed"
    miss = sum(int(x) for x in re.findall(r"Computing and caching embeddings for (\d+) new queries", hl))
    cached = re.findall(r"All (\d+) requested embeddings are already cached on disk", hl)
    say("[V7 %s] embedding misses %d (cache-hit lines %s)" % (leg, miss, cached))
    dur = m.get("duration_ms")
    say("[V8 %s] duration_ms %s (bar 60,000-480,000)" % (leg, dur))
    ok &= isinstance(dur, int) and 60000 <= dur <= 480000
    say("[LEG %s] %s" % (leg, "ALL VALIDITY CHECKS PASS" if ok else "A VALIDITY CHECK FAILED: the leg is VOID (failed precondition)"))
    with open(os.path.join(stage, "d9_disc.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(stage, "d9_misses_%s.txt" % leg), "w") as f:
        f.write("%d\n" % miss)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
