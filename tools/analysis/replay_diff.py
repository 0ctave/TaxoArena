"""Replay gate: compare a re-run's artifacts with a reference run, file by file.

  python tools/analysis/replay_diff.py <reference_run_dir> <replay_run_dir> [<replay_run_dir> ...]

Prints IDENTICAL / DIFFERS per artifact. Structure artifacts (dag_snapshots.jsonl,
fixed_point_certificate.txt, diagnostics/proposals.csv) must be IDENTICAL for the gate to pass;
timing/manifest files are skipped; evaluation-path files (iteration_metrics.csv, validation/*.csv)
are reported but carry the known P7 caveat (bootstrap-SE order instability, validation float
drift) — a difference there is shown with its first differing line so it can be classified.
"""
import os, sys, hashlib

STRUCTURE = ["dag_snapshots.jsonl", "fixed_point_certificate.txt", "diagnostics/proposals.csv",
             "diagnostics/dag_snapshots.jsonl"]
EVAL = ["diagnostics/iteration_metrics.csv", "diagnostics/rank_history.csv", "validation"]
SKIP = {"headless_run.log", "performance_report.json", "diagnostics/run_manifest.json",
        "diagnostics/headless_run.log", "diagnostics/config.toml"}


def files_under(root, rel):
    p = os.path.join(root, rel)
    if os.path.isdir(p):
        return sorted(os.path.join(rel, f) for f in os.listdir(p))
    return [rel] if os.path.exists(p) else []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def first_diff(a, b):
    with open(a, encoding="utf-8", errors="replace") as fa, open(b, encoding="utf-8", errors="replace") as fb:
        for i, (la, lb) in enumerate(zip(fa, fb), 1):
            if la != lb:
                return i, la.strip()[:110], lb.strip()[:110]
    return None


def compare(ref, rep):
    ok = True
    print("== %s vs %s ==" % (ref, rep))
    for group, rels in (("STRUCTURE (must be identical)", STRUCTURE), ("EVALUATION PATH (P7 caveat)", EVAL)):
        print("  -- %s" % group)
        for rel in rels:
            for f in files_under(ref, rel):
                if f in SKIP: continue
                a, b = os.path.join(ref, f), os.path.join(rep, f)
                if not os.path.exists(b):
                    print("     %-45s MISSING in replay" % f); ok = ok and group.startswith("EVAL"); continue
                same = sha(a) == sha(b)
                line = "" if same else "  first diff: %s" % (first_diff(a, b),)
                print("     %-45s %s%s" % (f, "IDENTICAL" if same else "DIFFERS", line))
                if not same and group.startswith("STRUCTURE"): ok = False
    print("  GATE: %s" % ("PASS (structure bit-identical)" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    ref = sys.argv[1]
    res = [compare(ref, r) for r in sys.argv[2:]]
    sys.exit(0 if all(res) else 1)
