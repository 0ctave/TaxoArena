"""data_v2.lint_connect: count direct sqlite3.connect calls under tools/ (data §3 V11 / SYNTHESIS G9), changing nothing.

    python tools/analysis/data_v2/lint_connect.py            # report; exit 1 only if the data_v2 package itself breaks
                                                             # the rule (a connect outside data_v2/ro.py)
    python tools/analysis/data_v2/lint_connect.py --strict   # exit 1 on ANY direct connect outside data_v2/ro.py

A "direct connect" is a line matching the regex CALL below: the module's connect function followed by an open
parenthesis, or its import by name (comment and docstring lines are counted too when they carry the call pattern; the
report shows each package hit, and the per-file list can be printed with --list, so a reader can discount them). The report prints the totals, the per-directory counts, the files that never pass mode=ro, and the files
that use immutable=1. The existing scripts are NOT changed by this item (the orchestrator's constraint); the count is the
baseline for the migration to data_v2.ro.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TOOLS = os.path.join(ROOT, "tools")
ALLOWED = os.path.normcase(os.path.join(HERE, "ro.py"))
CALL = re.compile(r"sqlite3\s*\.\s*connect\s*\(|from\s+sqlite3\s+import\s+[^\n]*\bconnect\b")


def scan(root=TOOLS):
    hits = []
    files = 0
    for d, _dirs, fs in os.walk(root):
        if "__pycache__" in d:
            continue
        for f in sorted(fs):
            if not f.endswith(".py"):
                continue
            files += 1
            p = os.path.join(d, f)
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for i, line in enumerate(text.splitlines(), 1):
                if CALL.search(line):
                    hits.append((p, i, line.strip()))
    return files, hits


def main(argv):
    strict = "--strict" in argv
    files, hits = scan()
    by_file = {}
    for p, i, line in hits:
        by_file.setdefault(p, []).append((i, line))
    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    outside = {p: v for p, v in by_file.items() if os.path.normcase(p) != ALLOWED}
    pkg = {p: v for p, v in outside.items() if os.path.normcase(p).startswith(os.path.normcase(HERE) + os.sep)}
    by_dir = {}
    for p, v in outside.items():
        by_dir[os.path.dirname(rel(p))] = by_dir.get(os.path.dirname(rel(p)), 0) + len(v)
    no_ro, immut = [], []
    for p in outside:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            t = fh.read()
        if "mode=ro" not in t:
            no_ro.append(rel(p))
        if "immutable=1" in t:
            immut.append(rel(p))
    print("[LINT-CONNECT] scanned %d .py files under tools/" % files)
    print("[LINT-CONNECT] direct sqlite3.connect call sites outside data_v2/ro.py: %d, in %d files"
          % (sum(len(v) for v in outside.values()), len(outside)))
    for d in sorted(by_dir):
        print("    %-40s %4d call sites" % (d, by_dir[d]))
    print("[LINT-CONNECT] files with a direct connect that never contain 'mode=ro': %d; that contain 'immutable=1': %d"
          % (len(no_ro), len(immut)))
    for p in sorted(no_ro):
        print("    no mode=ro: %s" % p)
    if "--list" in argv:
        for p in sorted(outside, key=rel):
            print("    %-60s %d" % (rel(p), len(outside[p])))
    print("[LINT-CONNECT] inside the data_v2 package, outside ro.py: %d call sites %s"
          % (sum(len(v) for v in pkg.values()), "(OK)" if not pkg else "(VIOLATION)"))
    for p, v in sorted(pkg.items()):
        for i, line in v:
            print("    %s:%d %s" % (rel(p), i, line))
    if pkg or (strict and outside):
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
