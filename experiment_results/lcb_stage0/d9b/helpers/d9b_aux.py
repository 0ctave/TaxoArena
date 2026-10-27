"""LCB-D9B-BYTE-INERTNESS operator helper: V10 (class-file name lists, registration (iii)) and V11 (the CR-stripped probe
TOML compare, registration (iv)); registration docs/judge_v2_program.md L19642-L19714 (ab8aee9). Zero calls. Read-only on
the leg worktrees; writes only under <stage>\\classlists (write-once).

usage:
  python d9b_aux.py classlists <A|B|A2> <leg root> <$ST>
      after the leg's checker and BEFORE any worktree removal. For each id of LIVECODEBENCH, fetchLiveCodeBench,
      lcbWorkDirGuard, LcbWorkDirGuardState: the names of the files under <leg root>\\build\\classes\\kotlin\\main whose
      bytes contain the id (the semantics of `grep -rlaF <id> build/classes/kotlin/main`: every regular file, fixed
      string, binary as text) -> $ST\\classlists\\leg<L>_<id>.txt; the full .class list -> leg<L>_all.txt. One path per
      line, relative to the leg root, '/' separators, sorted, LF. Refuses if a list exists.
  python d9b_aux.py v10 <$ST>
      V10: the 15 lists exist for A, B, A2; each is listed in $ST\\SHA256SUMS UNDER ITS OWN PATH
      (classlists/leg<L>_<id>.txt after normalising case, separators, a leading '*' or './' and the $ST prefix) with its
      own sha256 (R5, READY d984724 B1; the pre-R5 test "the sha256 appears anywhere in the file" was vacuous; pre-R5
      file d9b_aux_r4.py, sha256-lf 28200e47...); each per-identifier
      count of lines ending ".class" EQUALS the checker's V3 count (registrar ruling A4, f13736a, required change R4; a
      non-.class hit, e.g. META-INF/*.kotlin_module, is printed and disclosed, never a V10 failure by itself; pre-patch
      file d9b_aux_prepatch.py, sha256-lf 58510ea5...) ([V3 A] and [V3 B] in $ST\\d9_disc.txt; A2 ran as "A" into $ST\\a2, so its
      [V3 A] line is in $ST\\a2\\d9_disc.txt), and leg<L>_all.txt's count equals the checker's class-file count.
      exit 0 = V10 met; 1 = not met (VOIDS the run).
  python d9b_aux.py v11 <arm toml> <probe toml>
      V11: after stripping every CR, the two files have the same number of lines and differ in EXACTLY 2 lines, whose
      keys are datasetType and outputDir. exit 0 = met; 1 = not met.
"""
import hashlib, os, re, sys

IDS = ("LIVECODEBENCH", "fetchLiveCodeBench", "lcbWorkDirGuard", "LcbWorkDirGuardState")
LEGS = ("A", "B", "A2")
CLS = os.path.join("build", "classes", "kotlin", "main")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def classlists(leg, root, stage):
    if leg not in LEGS:
        print("[V10] refusing: leg must be one of %s" % (LEGS,))
        return 2
    base = os.path.join(root, CLS)
    d = os.path.join(stage, "classlists")
    if not os.path.isdir(base) or not os.path.isdir(d):
        print("[V10] refusing: %s or %s missing" % (base, d))
        return 2
    outs = [os.path.join(d, "leg%s_%s.txt" % (leg, i)) for i in IDS] + [os.path.join(d, "leg%s_all.txt" % leg)]
    for p in outs:
        if os.path.exists(p):
            print("[V10] refusing: %s exists (write-once)" % p)
            return 2
    files = sorted(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/") for dp, _s, fs in os.walk(base) for f in fs)
    blobs = {f: open(os.path.join(root, f), "rb").read() for f in files}
    for i, p in zip(IDS, outs):
        hit = [f for f in files if i.encode() in blobs[f]]
        with open(p, "x", encoding="utf-8", newline="\n") as fh:
            fh.write("".join(h + "\n" for h in hit))
        print("[V10 %s] %-22s %d file(s) (%d .class, %d other: %s) -> %s sha256 %s"
              % (leg, i, len(hit), sum(h.endswith(".class") for h in hit), sum(not h.endswith(".class") for h in hit),
                 [h for h in hit if not h.endswith(".class")] or "none", p, sha(p)))
    cls = [f for f in files if f.endswith(".class")]
    with open(outs[-1], "x", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(h + "\n" for h in cls))
    print("[V10 %s] all .class files: %d (of %d files under %s) -> %s sha256 %s" % (leg, len(cls), len(files), CLS, outs[-1], sha(outs[-1])))
    return 0


def v3_line(disc, tag):
    txt = open(disc, encoding="utf-8").read() if os.path.isfile(disc) else ""
    ms = re.findall(r"^\[V3 %s\] (\d+) class files; files containing (\{.*\})$" % tag, txt, re.M)
    if len(ms) != 1:
        return None
    n, d = ms[0]
    counts = dict(re.findall(r"'(\w+)': (\d+)", d))
    return int(n), {k: int(v) for k, v in counts.items()}


def norm_path(path, stage):
    """R5: a SHA256SUMS path -> the 'classlists/legA_all.txt' form: lower case, '/' separators, any leading '*' and './'
    stripped, and the stage prefix stripped in every rendering S10 can write (Windows absolute 'c:/...' from the
    Get-FileHash line, Git-bash '/c/...'; relative './...' from sha256sum)."""
    q = path.strip().replace("\\", "/").lower()
    st = os.path.abspath(stage).replace("\\", "/").lower().rstrip("/") + "/"
    prefixes = [st]
    if len(st) > 2 and st[1] == ":":
        prefixes.append("/" + st[0] + st[2:])
    changed = True
    while changed:
        changed = False
        for pre in ["*", "./"] + prefixes:
            if q.startswith(pre):
                q, changed = q[len(pre):], True
    return q


def parse_sums(sums_p, stage):
    """R5: SHA256SUMS -> ({normalised path: sha256}, [paths listed twice with different sha256], n unparsed lines).
    Accepts '<hex>  <path>', '<hex> *<path>' (sha256sum) and '<hex>  <absolute path>' (S10's Get-FileHash line, any hex
    case); UTF-8, or UTF-16 with a BOM."""
    raw = open(sums_p, "rb").read()
    txt = raw.decode("utf-16") if raw[:2] in (bytes([0xFF, 0xFE]), bytes([0xFE, 0xFF])) else raw.decode("utf-8", "replace")
    out, conflict, bad = {}, set(), 0
    for ln in txt.replace("\r", "").split("\n"):
        if not ln.strip():
            continue
        m = re.match(r"^\s*([0-9A-Fa-f]{64})\s+(.+?)\s*$", ln)
        if not m:
            bad += 1
            continue
        k, h = norm_path(m.group(2), stage), m.group(1).lower()
        if k in out and out[k] != h:
            conflict.add(k)
        out[k] = h
    return out, sorted(conflict), bad


def v10(stage):
    ok = True
    sums_p = os.path.join(stage, "SHA256SUMS")
    sums, conflict, bad = parse_sums(sums_p, stage) if os.path.isfile(sums_p) else ({}, [], 0)
    print("[V10] %s: %d path entries parsed, %d unparsed line(s), paths listed twice with different sha256: %s"
          % (sums_p, len(sums), bad, conflict or "none"))
    if not sums:
        print("[V10] %s absent or empty" % sums_p)
        ok = False
    src = {"A": (os.path.join(stage, "d9_disc.txt"), "A"), "B": (os.path.join(stage, "d9_disc.txt"), "B"),
           "A2": (os.path.join(stage, "a2", "d9_disc.txt"), "A")}
    for leg in LEGS:
        v3 = v3_line(*src[leg])
        print("[V10 %s] checker V3 from %s [V3 %s]: %s" % (leg, src[leg][0], src[leg][1], v3 if v3 else "NOT FOUND EXACTLY ONCE"))
        ok &= v3 is not None
        for i in IDS + ("all",):
            p = os.path.join(stage, "classlists", "leg%s_%s.txt" % (leg, i))
            if not os.path.isfile(p):
                print("[V10 %s] %s MISSING" % (leg, p))
                ok = False
                continue
            names = [ln.strip() for ln in open(p, encoding="utf-8") if ln.strip()]
            n = sum(1 for x in names if x.endswith(".class"))
            other = [x for x in names if not x.endswith(".class")]
            h = sha(p)
            want = (v3[0] if i == "all" else v3[1].get(i)) if v3 else None
            key = ("classlists/leg%s_%s.txt" % (leg, i)).lower()
            listed = sums.get(key)
            hashed = listed == h and key not in conflict
            state = ("ABSENT" if listed is None else "LISTED TWICE WITH DIFFERENT sha256" if key in conflict
                     else "own sha256" if listed == h else "WRONG sha256 " + listed[:16])
            print("[V10 %s] %-22s list .class %d (non-.class hits %d, DISCLOSED, not compared: %s), checker %s, sha256 %s;"
                  " SHA256SUMS entry %s: %s -> %s" % (leg, i, n, len(other), other or "none", want, h[:16], key, state,
                                                      "EQUAL" if n == want and hashed else "FAIL"))
            ok &= n == want and hashed
    print("[V10] %s" % ("MET" if ok else "NOT MET: VOIDS the run (failed precondition)"))
    return 0 if ok else 1


def v11(arm, probe):
    a, b = (open(p, "rb").read().decode("utf-8").replace("\r", "").split("\n") for p in (arm, probe))
    print("[V11] %s: %d lines; %s: %d lines (CR stripped)" % (arm, len(a), probe, len(b)))
    if len(a) != len(b):
        print("[V11] NOT MET: line counts differ")
        return 1
    diff = [(k + 1, x, y) for k, (x, y) in enumerate(zip(a, b)) if x != y]
    for k, x, y in diff:
        print("[V11] line %d: arm %r | probe %r" % (k, x, y))
    keys = sorted(re.match(r"\s*([A-Za-z_]+)\s*=", x).group(1) if re.match(r"\s*([A-Za-z_]+)\s*=", x) else "?" for _k, x, _y in diff)
    ok = len(diff) == 2 and keys == ["datasetType", "outputDir"]
    print("[V11] %d line(s) differ, keys %s -> %s" % (len(diff), keys, "MET" if ok else "NOT MET"))
    return 0 if ok else 1


def main(argv):
    if len(argv) == 4 and argv[0] == "classlists":
        return classlists(*argv[1:4])
    if len(argv) == 2 and argv[0] == "v10":
        return v10(argv[1])
    if len(argv) == 3 and argv[0] == "v11":
        return v11(*argv[1:3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
