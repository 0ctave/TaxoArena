"""data_v2.build: M1 -> M2 -> M3 in one command, zero calls, with a write-once manifest (ARCH-v2 E-D).

    TAXOARENA_DATA_ROOT=<main checkout> python tools/analysis/data_v2/build.py --seed DEV-<tag> [--out-dir DIR]
    python tools/analysis/data_v2/build.py --seed <registered seed> --registration <record entry>   # the real draw

READ-ONLY on the data root: the two source DBs are opened through data_v2.ro.open_ro (the -wal / -journal check, then
mode=ro&immutable=1, query_only). EVERY OUTPUT IS A NEW FILE (data_v2.ro.create_new refuses an existing path):
    <out-dir>/corpus_v2_mmlu_pro_v2.db, corpus_v2_union_mc6.db       M1, sealed
    <out-dir>/split_v2_<DEV|REG>_<seed>.db                            M2, sealed
    <out-dir>/gen_view_<DEV|REG>.db, eval_view_<DEV|REG>.db           M3, sealed
    data_v2/manifests/<label>.json and <label>_transcript.txt         written once (open mode "x"), COMMITTED; the DBs are
                                                                       gitignored (*.db) and listed there with sha256-bytes
                                                                       and per-table shas
The default out-dir is data_v2/<label> inside THIS checkout. An out-dir inside the data root is refused unless it is
also inside this checkout (a worktree sits under the main checkout, so the check is on this checkout's top level).
R1 (SPLIT-DRAW-PROCESS-HYGIENE D1): every input DB is hashed at launch and AFTER the run (UNCHANGED / CHANGED printed), and
the python / java process list is sampled at launch, after every stage, every 20 s from a background thread DURING the run,
and AFTER it; the samples are printed ([R1] lines, the runlog) and kept in the manifest (r1_process_samples).
[FAILS CLOSED, 2026-09-24, READY_ck_close_v2 D3: a CHANGED input, or any FOREIGN python / java process in any sample (a
process that is neither this build nor its own launch chain), makes the build VOID: the manifest is written with
r1_void = true, its reasons and an of_record label starting "VOID (R1)", the transcript is written, and the build exits with
status 3. Before this, R1 only printed a warning.]
A DEV seed ("DEV-...") labels every output "DEV, NOT OF RECORD"; any other seed runs only as the exact pair pinned in
split.REGISTERED_DRAWS (split.check_draw compares values). The per-item side table is exported to
data_v2/manifests/<label>_side.tsv (LF, deterministic, verified against the sealed split's table_sha): the draw's evidence.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "data_v2"
    import data_v2  # noqa: F401

from . import common as C  # noqa: E402
from . import ingest, ro, split, views  # noqa: E402

CORPORA = ("mmlu-pro-v2", "mc6-2026-09-11")
MANIFEST_DIR = os.path.join(C.ROOT, "data_v2", "manifests")


def _git(*args):
    try:
        return subprocess.run(["git", "-C", C.ROOT] + list(args), capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as e:
        return "unavailable (%s)" % e


def _inside(path, root):
    p = os.path.normcase(os.path.realpath(path))
    r = os.path.normcase(os.path.realpath(root))
    return p == r or p.startswith(r + os.sep)


def code_pins():
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for f in sorted(os.listdir(here)):
        if f.endswith(".py"):
            p = os.path.join(here, f)
            out["tools/analysis/data_v2/" + f] = {"blob": ro.git_blob_lf(p), "sha256-lf16": ro.sha256_lf16(p)}
    for name, pin in C.PINS.items():
        p = os.path.join(C.ANALYSIS, name + ".py")
        out["tools/analysis/%s.py" % name] = {"blob": ro.git_blob_lf(p), "sha256-lf16": ro.sha256_lf16(p), "pinned": pin}
    return out


PROC_NAMES = ("python.exe", "java.exe", "javaw.exe", "gradle", "python", "java")


def process_snapshot():
    """R1 (SPLIT-DRAW-PROCESS-HYGIENE D1): the python / java processes now running, as [pid, name, command line[:240]].
    Windows: PowerShell Get-CimInstance; elsewhere: ps. A failure is recorded, never fatal."""
    try:
        if os.name == "nt":
            cmd = ["powershell", "-NoProfile", "-Command",
                   "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|pythonw|java|javaw)\\.exe$' }"
                   " | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            d = json.loads(r.stdout) if r.stdout.strip() else []
            d = d if isinstance(d, list) else [d]
            return sorted([p["ProcessId"], p["Name"], (p.get("CommandLine") or "")[:240]] for p in d)
        r = subprocess.run(["ps", "-eo", "pid,comm,args"], capture_output=True, text=True, timeout=60)
        rows = []
        for ln in r.stdout.splitlines()[1:]:
            parts = ln.split(None, 2)
            if len(parts) >= 2 and any(n in parts[1] for n in ("python", "java")):
                rows.append([int(parts[0]), parts[1], (parts[2] if len(parts) > 2 else "")[:240]])
        return sorted(rows)
    except Exception as e:  # noqa: BLE001  (a sampling failure is evidence too)
        return [["?", "sampling failed", repr(e)[:200]]]


def ancestor_pids(pid=None):
    """The chain of parent processes of `pid` (default: this process), from the OS process table; [] when unavailable.
    The build's own launch chain (the shell or wrapper that started it) is ADMITTED by R1; nothing else is."""
    pid = pid or os.getpid()
    try:
        if os.name == "nt":
            r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process | Select-Object"
                                " ProcessId,ParentProcessId | ConvertTo-Json -Compress"], capture_output=True, text=True, timeout=60)
            rows = json.loads(r.stdout) if r.stdout.strip() else []
            parent = {p["ProcessId"]: p["ParentProcessId"] for p in (rows if isinstance(rows, list) else [rows])}
        else:
            r = subprocess.run(["ps", "-eo", "pid,ppid"], capture_output=True, text=True, timeout=60)
            parent = {int(a): int(b) for a, b in (ln.split() for ln in r.stdout.splitlines()[1:] if ln.strip())}
    except Exception:  # noqa: BLE001
        return []
    chain, seen = [], {pid}
    p = parent.get(pid)
    while p and p not in seen:
        chain.append(p)
        seen.add(p)
        p = parent.get(p)
    return chain


class ProcessLog:
    """Samples the process list at named points AND every `period` seconds from a background thread (during the run);
    each sample is printed with a [R1] prefix and kept for the manifest. ADMITTED: this build's pid and its own launch
    chain (ancestors); every other python / java process in any sample is FOREIGN and voids the build (r1_verdict)."""

    def __init__(self, out, period=20.0):
        import threading
        self.out, self.period, self.samples = out, period, []
        self.admitted = [os.getpid()] + ancestor_pids()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._t = threading.Thread(target=self._loop, daemon=True)

    def sample(self, stage):
        snap = process_snapshot()
        me = os.getpid()
        others = [p for p in snap if p[0] not in self.admitted]
        rec = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "stage": stage, "self_pid": me,
               "admitted_pids": self.admitted, "processes": snap, "foreign": others}
        with self._lock:
            self.samples.append(rec)
            self.out("[R1] %s %s: %d FOREIGN python/java process(es) besides this build (pid %d) and its launch chain:"
                     " %s" % (rec["utc"], stage, len(others), me,
                              "; ".join("%s %s %s" % (p[0], p[1], p[2][:120]) for p in others) or "none"))

    def _loop(self):
        while not self._stop.wait(self.period):
            self.sample("during (periodic)")

    def start(self):
        self.sample("launch")
        self._t.start()

    def stop(self):
        self._stop.set()
        self._t.join(timeout=120)
        self.sample("AFTER the run")


def r1_verdict(inputs_before, inputs_after, samples):
    """R1 FAILS CLOSED (READY_ck_close_v2 D3): the build is VOID when any input DB changed between launch and the end, or
    when any sample holds a FOREIGN python / java process (not this build, not its launch chain). Returns
    (void, [reasons])."""
    reasons = []
    for rel in sorted(set(inputs_before) | set(inputs_after)):
        if inputs_before.get(rel) != inputs_after.get(rel):
            reasons.append("input %s CHANGED (%s -> %s)" % (rel, (inputs_before.get(rel) or "absent")[:16],
                                                            (inputs_after.get(rel) or "absent")[:16]))
    foreign = {}
    for s in samples:
        for p in s.get("foreign", []):
            foreign.setdefault(p[0], (p[1], p[2][:120], s["stage"]))
    for pid, (name, cmd, stage) in sorted(foreign.items(), key=lambda kv: str(kv[0])):
        reasons.append("FOREIGN process %s %s (first seen: %s): %s" % (pid, name, stage, cmd))
    return bool(reasons), reasons


def input_files():
    """Every DB the build reads (data root relative): the corpus sources and the legacy reference caches."""
    rel = [ingest.SPECS[cv]["db"] for cv in CORPORA]
    for cv in CORPORA:
        rel += [r["db"] for r in ingest.LEGACY_REFERENCES.get(cv, ())]
    return rel


def main(argv):
    if "--seed" not in argv:
        print(__doc__)
        return 2
    seed = argv[argv.index("--seed") + 1]
    registration = argv[argv.index("--registration") + 1] if "--registration" in argv else None
    dev, _label = split.check_draw(seed, registration)   # the value-compared guard (READY_archv2_ED D1)
    label = ("DEV_" if dev else "REG_") + "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in seed)
    out_dir = argv[argv.index("--out-dir") + 1] if "--out-dir" in argv else os.path.join(C.ROOT, "data_v2", label)
    # --manifest-dir / --repo-root exist for the selftest's end-to-end R1 run on the synthetic fixture (defaults unchanged)
    man_dir = argv[argv.index("--manifest-dir") + 1] if "--manifest-dir" in argv else MANIFEST_DIR
    repo_root = argv[argv.index("--repo-root") + 1] if "--repo-root" in argv else None
    if _inside(out_dir, C.DATA_ROOT) and not _inside(out_dir, C.ROOT):
        C._refuse("out-dir %s is inside the data root %s and outside this checkout %s" % (out_dir, C.DATA_ROOT, C.ROOT))
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(man_dir, exist_ok=True)
    man_path = os.path.join(man_dir, label + ".json")
    tr_path = os.path.join(man_dir, label + "_transcript.txt")
    for p in (man_path, tr_path, os.path.join(man_dir, label + "_side.tsv")):
        if os.path.exists(p):
            C._refuse("%s exists: a manifest is written once" % p)
    lines = []

    def out(s):
        print(s, flush=True)
        lines.append(s)
    t0 = time.time()
    of_record = C.OF_RECORD_DEV if dev else "registered seed (%s)" % registration
    out("[BUILD] data_v2 E-D; label %s; %s; seed %r; data root %s (read-only); out-dir %s"
        % (label, of_record, seed, C.DATA_ROOT, out_dir))
    out("[BUILD] git HEAD %s; dirty paths: %s" % (_git("rev-parse", "HEAD"), _git(
        "status", "--porcelain", "--", "tools/analysis/data_v2", "tools/analysis/passage_closure.py",
        "tools/analysis/content_closure.py", "tools/analysis/split_side.py") or "none"))
    inputs_before = {rel: ro.file_sha256(os.path.join(C.DATA_ROOT, rel)) for rel in input_files()}
    for rel, h in inputs_before.items():
        out("[R1] input BEFORE %-52s sha256-bytes %s" % (rel, h))
    plog = ProcessLog(out)
    plog.start()
    try:
        corp = []
        for cv in CORPORA:
            corp.append(ingest.build_corpus(cv, out_dir, out=out, repo_root=repo_root))
            plog.sample("after M1 %s" % cv)
        sp = split.build_split([c["path"] for c in corp], out_dir, seed, registration=registration, out=out)
        plog.sample("after M2 (the draw)")
        side_path = os.path.join(man_dir, label + "_side.tsv")
        side_sha, side_rows = split.export_side(sp["path"], side_path)
        split.verify_side_export(side_path, sp["path"])
        out("[BUILD] side-table export %s: %d rows, table_sha %s (equal to the sealed split's; verified from the text)"
            % (_rel(side_path), side_rows, side_sha))
        gv = views.build_view("gen", [c["path"] for c in corp], sp["path"], out_dir, out=out)
        ev = views.build_view("eval", [c["path"] for c in corp], sp["path"], out_dir, out=out)
    finally:
        plog.stop()
    inputs_after = {rel: ro.file_sha256(os.path.join(C.DATA_ROOT, rel)) for rel in input_files()}
    for rel, h in inputs_after.items():
        out("[R1] input AFTER  %-52s sha256-bytes %s %s" % (rel, h, "UNCHANGED" if h == inputs_before[rel] else "CHANGED"))
    void, reasons = r1_verdict(inputs_before, inputs_after, plog.samples)
    for r in reasons:
        out("[R1] VOID: %s" % r)
    out("[R1] verdict: %s" % ("VOID (the build fails closed: manifest marked VOID, exit status 3)" if void
                              else "CLEAN (no input changed; no foreign python / java process in %d samples)" % len(plog.samples)))
    if void:
        of_record = "VOID (R1): " + of_record
    wall = time.time() - t0
    outputs = []
    for e in corp + [sp, gv, ev]:
        outputs.append({"file": _rel(e["path"]), "kind": e["kind"],
                        "bytes": os.path.getsize(e["path"]), "sha256_bytes": e["sha256_bytes"], "tables": e["tables"],
                        **{k: e[k] for k in ("counts", "record", "source_db", "source_db_sha256_bytes", "checks", "pools",
                                             "content_check") if k in e}})
    manifest = {
        "item": "E-D, the v2 data layer (ARCH-v2 SYNTHESIS §2 Stage D + Stage S; data §1-§3)",
        "label": label, "of_record": of_record, "seed": seed, "registration": registration,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "wall_seconds": round(wall, 1),
        "git_head": _git("rev-parse", "HEAD"), "data_root": C.DATA_ROOT,
        "inputs": {c["source_db"]: c["source_db_sha256_bytes"] for c in corp},
        "code": code_pins(), "rule": split.RULE, "eval_ratio": split.DEFAULT_EVAL_RATIO, "gate_ratio": split.DEFAULT_GATE_RATIO,
        "outputs": outputs,
        "side_export": {"file": _rel(side_path), "rows": side_rows,
                        "table_sha": side_sha, "sha256_bytes": ro.file_sha256(side_path)},
        "r1_inputs": {rel: {"before": inputs_before[rel], "after": inputs_after[rel]} for rel in inputs_before},
        "r1_inputs_unchanged": inputs_after == inputs_before,
        "r1_process_samples": plog.samples,
        "r1_void": void, "r1_void_reasons": reasons,
        "note": "The DBs are not in git (*.db is ignored); this manifest is their record: rebuild with the same code and"
                " inputs and compare sha256_bytes (no wall-clock value is written into any DB).",
    }
    out("[BUILD] done in %.0f s; manifest %s%s" % (wall, _rel(man_path), " [VOID]" if void else ""))
    with open(man_path, "x", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(tr_path, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    if void:
        # the evidence is written (manifest marked VOID, transcript), then the build FAILS: exit status 3
        raise SystemExit(3)
    return 0


def _rel(path):
    """The path relative to this checkout, '/'-separated; the absolute path when it lies elsewhere (another drive)."""
    try:
        r = os.path.relpath(path, C.ROOT)
    except ValueError:
        return os.path.abspath(path).replace("\\", "/")
    return r.replace("\\", "/") if not r.startswith("..") else os.path.abspath(path).replace("\\", "/")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
