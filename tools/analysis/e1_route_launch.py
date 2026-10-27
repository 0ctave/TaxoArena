"""e1_route_launch.py: E1-ROUTE's working-copy launcher (R1) for EMBEDDER-CROSS-FLAT E1's JVM builds. ZERO judge / LLM calls.

REGISTRATION OF RECORD: docs/judge_v2_program.md, "## Registered 2026-09-30 (before any code or call) — E1-ROUTE: can
EMBEDDER-CROSS-FLAT E1's JVM builds read a pinned nomic arm file only through a per-run WORKING COPY ..." (L22182-L22206 _as_of
7ea9ec1). C-ET2-1 (READY_emb_target2 f66c360): the JVM mutates any file it opens, so -Dtaxoarena.embeddingCacheFile never names
a pinned DIR file. For arm A in {nomic_raw, nomic_card} this launcher:
  (i)   checks sha256(DIR file) = the registrar's pin (embedder_arms.registrar_pin) and REFUSES (rc 2) BEFORE any copy or launch;
  (ii)  copies it to a fresh per-run working path and checks the copy's sha256 = the pin;
  (iii) REFUSES (rc 2) if the resolved target (realpath, case-folded) equals or lies under any member of the protected set P
        or the DIR;
  (iv)  launches the build: gradlew bootRun -PjvmThreads=12 -Dtaxoarena.embeddingCacheFile=<working path>
        -Dtaxoadapt.llm.embedding-model=<the arm's pinned tag> -Dtaxoarena.embeddingCacheSourceSha256=<the pin> (the manifest
        records it: embedding_cache_source_sha256, R2) --args="--config <toml>"; the tag's model digest (the pins file's) is printed;
  (v)   after the JVM exits, re-hashes P (and the DIR file used) and REFUSES "PIN BREACH" (rc 2) on any change;
  (vi)  keeps the working copy (its post-run sha256 printed; a change there is expected, not a breach).
PATH RULE (declared): the working path is <DATA_ROOT>/experiment_results/e1_route_work/<run id>/<the arm's cache file name> (the
JVM requires the model's own file name or its __card twin, EmbeddingCache.resolveCacheFile); the run directory must not exist
(fresh per run, never reused); the target must not be, or lie under, experiment_results/embedder_cross/ or any member of P.
PROTECTED SET P (each: sha256 of the bytes, size, and the absence of -wal / -shm / -journal; before and after every leg):
  the four DIR arm files experiment_results/embedder_cross/<file> (nomic_raw, nomic_card, gemma_raw, gemma_card);
  the source per-model DBs embeddings_cache_nomic-embed-text_latest.db and embeddings_cache_embeddinggemma_latest.db;
  embeddings_cache.db (file sha256 AND per-table sha256 of queries and reserved_pool_meta, data_v2.ro.table_sha);
  snapshots_frozen.db.
All under DATA_ROOT (TAXOARENA_DATA_ROOT, default this checkout). A member absent from disk is recorded as ABSENT and must stay
absent (a new file appearing is a change). The per-table view opens embeddings_cache.db through data_v2.ro.open_ro (mode=ro&
immutable=1 after the non-empty -wal / -journal refusal).

  python tools/analysis/e1_route_launch.py --selftest                 # L0: the fixture legs and C5's four mutants (no JVM)
  python tools/analysis/e1_route_launch.py --arm nomic_raw --config experiment_configs/anchorfree/redraw/af_clean_s42.toml --dry-run
  python tools/analysis/e1_route_launch.py --arm nomic_raw --config <toml> [--dir-file <scratch copy>]   # L1 / E1
  python tools/analysis/e1_route_launch.py --arm nomic_raw --config <toml> --target <path> --dry-run     # L2 (refusal expected)
--dir-file names the "DIR" file under test (L1's scratch copy of nomic_raw, sha256 = the pin); it joins the hashed set.
--target overrides the working path (L2 only: each member of P and the DIR itself must be REFUSED before launch).

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; R0 control survived). C5's four
registered mutants: R1 the pin check removed, R2 the post-run re-hash removed, R3 the target-in-P check removed, R4 the JVM
given the DIR path instead of the copy: 4 of 4 killed. Beside them: R5 the copy's hash unchecked, R6 sidecars not viewed, R7 the
main cache's per-table view dropped: 3 of 3 killed.

[ADDED 2026-09-30, branch e1-route2 (the fixes of docs/reviews/READY_backfill_2026-09-30.md, b938c14); the lines above stay as
written; where they disagree with this block, this block governs.]
  B-E1-1 SIDECARS. The registered "absence of -wal / -shm / -journal" is ENFORCED: before any copy or launch (dry-run included)
    the launcher REFUSES (rc 2) when any member of P or the DIR file under test has a -wal, -shm or -journal beside it, whatever
    its size. view() records each sidecar's size and sha256 (not only its name), so a WAL-tail write is a change (probe P-E1a).
  B-E1-2 L1 CONFIG. L1's declared short stop is experiment_configs/e1_route/L1_short_af_clean_s42.toml: af_clean_s42.toml with
    exactly two keys changed, numIterations = 2 and outputDir = "experiment_results/e1_route/L1_short" (outside every object of
    record). The launcher parses --config (tomllib) and REFUSES a config with no outputDir, one whose outputDir equals or lies
    under experiment_results/anchorfree/redraw/af_clean_s42 (the tree of record; so the docstring's example above is REFUSED),
    experiment_results/promoted/bareq512_s42, experiment_results/anchorfree/af, experiment_results/embedder_cross or a member of
    P, and one whose <outputDir>/seed_<seed> already exists (a build writes a fresh directory). E1's real builds therefore need
    their own configs (af_clean_s42.toml with its own outputDir), declared under EMBEDDER-CROSS-FLAT, never af_clean_s42.toml.
    DECLARED ADDITION (not in the review): the JVM gets -Dranking.db.path=<the fresh run dir>/ratings_e1route.db, so a build
    never writes the checkout's default ratings.db (af_clean_s42.toml's header: each arm has its own -Dranking.db.path).
  C-E1-3 DATA ROOT. REFUSED unless normcase(realpath(TAXOARENA_DATA_ROOT)) == normcase(realpath(<the JVM's cwd>)), the
    checkout the launcher runs from (bootRun workingDir = rootDir), so P is hashed where the JVM opens its relative DBs.
  C-E1-4 CODE PINS. REFUSED unless tools/analysis/embedder_arms.py = blob:2073d1315981a30464037913b85ce2bf8838aa00 and
    tools/analysis/embedder_cross_flat.py = blob:7868e8589fee107b15d3c535966b840cd648f771 (git blob of the LF rendering, main at
    2f080e0), and the imported embedder_arms is that file.
  Order of the checks: C-E1-3, C-E1-4, arm set, (i) pin, (iii) target, the config (B-E1-2), the sidecars (B-E1-1), then the
  views; every refusal precedes any copy and any launch.
  SELFTEST 15 cases. MUTANTS of e1-route2 (2026-09-30; one temporary in-place edit at a time, the selftest run, the bytes
  restored and compared; control R0 SURVIVED): 24 of 24 KILLED.
    R1 pin check removed K | R2 post-run re-hash removed K | R3 target-in-P check removed K | R4 JVM given the DIR path K |
    R5 copy hash unchecked K | R6 sidecars not viewed K | R7 main per-table view dropped K |
    N1 sidecar pre-check removed K | N2 sidecar view = names only (P-E1a's blind spot) K | N3 pre-check on the first suffix only K |
    N4 pre-check over P only, not the DIR under test K | N5 pre-check on the first site only K | N6 data-root check removed K |
    N7 data-root check prefix-only (a sub-directory admitted) K | N8 code blob check removed K | N9 imported-module check removed K |
    N10 code pins on the first file only K | N11 af_clean_s42 dropped from the forbidden outputDirs K |
    N12 outputDir equality only (a sub-directory admitted) K | N13 fresh seed-dir check removed K |
    N14 a missing outputDir admitted (default) K | N15 config check removed K | N16 ranking.db.path dropped K |
    N17 the main cache dropped from P K.
  (A first run left N6 / N7 SURVIVING: the C-E1-3 case matched "(C-E1-3)", which the admission line also prints; every refusal
  assertion now matches "REFUSED: (<id>)".)
"""
import os
import sys
import json
import shutil
import hashlib
import argparse
import datetime
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[E1-ROUTE]"
DIR_REL = os.path.join("experiment_results", "embedder_cross")
WORK_REL = os.path.join("experiment_results", "e1_route_work")
PINS_FILE = os.path.join(ROOT, "experiment_configs", "embedder_cross_arm_pins.json")
ROUTE_ARMS = ("nomic_raw", "nomic_card")
PIN_ARMS = ("nomic_raw", "nomic_card", "gemma_raw", "gemma_card")
SOURCE_DBS = ("embeddings_cache_nomic-embed-text_latest.db", "embeddings_cache_embeddinggemma_latest.db")
MAIN_CACHE = "embeddings_cache.db"
MAIN_TABLES = ("queries", "reserved_pool_meta")
FROZEN = "snapshots_frozen.db"
SIDECARS = ("-wal", "-shm", "-journal")
JVM_THREADS = 12
PROP_RANKING = "ranking.db.path"
RANKING_DB = "ratings_e1route.db"
# C-E1-4: the code of record E1 is pinned to (git blob of the LF rendering; main 2f080e0)
CODE_PINS = {"embedder_arms.py": "2073d1315981a30464037913b85ce2bf8838aa00",
             "embedder_cross_flat.py": "7868e8589fee107b15d3c535966b840cd648f771"}
# B-E1-2: a build's outputDir may not equal or lie under any of these (objects of record), nor under a member of P
FORBIDDEN_OUTPUT_REL = (os.path.join("experiment_results", "anchorfree", "redraw", "af_clean_s42"),
                        os.path.join("experiment_results", "promoted", "bareq512_s42"),
                        os.path.join("experiment_results", "anchorfree", "af"),
                        DIR_REL)
PROP_FILE = "taxoarena.embeddingCacheFile"
PROP_SRC = "taxoarena.embeddingCacheSourceSha256"
PROP_MODEL = "taxoadapt.llm.embedding-model"


class Refusal(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refusal(2)


def data_root():
    return os.environ.get("TAXOARENA_DATA_ROOT", ROOT)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pins(pins_file=PINS_FILE):
    with open(pins_file, encoding="utf-8") as f:
        return json.load(f)


def protected_set(droot, pins):
    """{label: path} of P (8 members)."""
    p = {}
    for a in PIN_ARMS:
        p["DIR/" + a] = os.path.join(droot, DIR_REL, pins["arms"][a]["file"])
    for s in SOURCE_DBS:
        p["source/" + s] = os.path.join(droot, s)
    p["main/" + MAIN_CACHE] = os.path.join(droot, MAIN_CACHE)
    p["frozen/" + FROZEN] = os.path.join(droot, FROZEN)
    return p


def _table_shas(path):
    from data_v2 import ro
    conn = ro.open_ro(path)
    try:
        out = {}
        present = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for t in MAIN_TABLES:
            out[t] = ro.table_sha(conn, t)[0] if t in present else "ABSENT"
        return out
    finally:
        conn.close()


def sidecars(path):
    """{suffix: {size, sha256}} of every -wal / -shm / -journal beside path (B-E1-1: content, not only the name)."""
    out = {}
    for s in SIDECARS:
        q = path + s
        if os.path.isfile(q):
            out[s] = {"size": os.path.getsize(q), "sha256": sha256_file(q)}
        elif os.path.exists(q):
            out[s] = {"state": "NOT-A-FILE"}
    return out


def view(path, tables=False):
    """One member's view: (sha256, size, sidecars with size and sha256[, per-table shas]) or ABSENT."""
    sc = sidecars(path)
    if not os.path.isfile(path):
        return {"state": "ABSENT", "sidecars": sc}
    v = {"sha256": sha256_file(path), "size": os.path.getsize(path), "sidecars": sc}
    if tables:
        v["tables"] = _table_shas(path)
    return v


def snapshot_views(members):
    return {k: view(p, tables=k.startswith("main/")) for k, p in members.items()}


def _norm(p):
    return os.path.normcase(os.path.realpath(os.path.abspath(p)))


def _under(t, q):
    return t == q or t.startswith(q.rstrip(os.sep) + os.sep)


def check_data_root(droot, root):
    """C-E1-3: P is hashed under DATA_ROOT; the JVM opens its relative DBs in its cwd (root). They must be one directory."""
    if _norm(droot) != _norm(root):
        refuse("(C-E1-3) the data root %s is not the JVM's working directory %s: P would be hashed where the JVM does not open "
               "its DBs; run from the checkout that holds the DBs with TAXOARENA_DATA_ROOT unset or equal to it" % (droot, root))


def check_code_pins(code_dir=HERE, pins=None):
    """C-E1-4: embedder_arms.py / embedder_cross_flat.py must be the blobs of record; the imported embedder_arms must be that file."""
    from data_v2 import ro
    pins = CODE_PINS if pins is None else pins
    for fn, want in sorted(pins.items()):
        p = os.path.join(code_dir, fn)
        got = ro.git_blob_lf(p) if os.path.isfile(p) else "ABSENT"
        if got != want:
            refuse("(C-E1-4) %s is blob:%s, not the pinned blob:%s" % (p, got, want))
    import embedder_arms as EA
    if _norm(EA.__file__) != _norm(os.path.join(code_dir, "embedder_arms.py")):
        refuse("(C-E1-4) the imported embedder_arms is %s, not the pinned %s" % (EA.__file__, os.path.join(code_dir, "embedder_arms.py")))
    return dict(pins)


def check_config(config, root, members, dir_path):
    """B-E1-2: the build's outputDir (relative to the JVM's cwd = root) must be outside every object of record and fresh."""
    import tomllib
    cpath = config if os.path.isabs(config) else os.path.join(root, config)
    if not os.path.isfile(cpath):
        refuse("(B-E1-2) the config %s does not exist" % cpath)
    try:
        with open(cpath, "rb") as f:
            cfg = tomllib.load(f)
    except Exception as e:
        refuse("(B-E1-2) the config %s does not parse: %s" % (cpath, e))
    od = cfg.get("outputDir")
    if not isinstance(od, str) or not od.strip():
        refuse("(B-E1-2) the config %s declares no outputDir" % cpath)
    odp = od if os.path.isabs(od) else os.path.join(root, od)
    t = _norm(odp)
    forbidden = [(r, os.path.join(root, r)) for r in FORBIDDEN_OUTPUT_REL] + list(members.items()) + [("DIR", dir_path)]
    for label, q in forbidden:
        if _under(t, _norm(q)):
            refuse("(B-E1-2) the config's outputDir %s is, or lies under, %s (%s): a build would write an object of record" % (od, label, q))
    seed = cfg.get("seed", 42)
    sd = os.path.join(odp, "seed_%s" % seed)
    if os.path.exists(sd):
        refuse("(B-E1-2) the build directory %s exists; a build writes a fresh directory" % sd)
    return odp, cfg


def check_no_sidecars(hashed):
    """B-E1-1: the registered ABSENCE of -wal / -shm / -journal beside every member of P and the DIR file, before any copy/launch."""
    found = ["%s%s (%d B)" % (p, s, os.path.getsize(p + s) if os.path.isfile(p + s) else -1)
             for k, p in sorted(hashed.items()) for s in SIDECARS if os.path.exists(p + s)]
    if found:
        refuse("(B-E1-1) %d sidecar(s) beside protected files (the registration requires their absence before the leg): %s"
               % (len(found), "; ".join(found)))


def check_target(target, members, dir_path):
    """(iii): the target must not equal, or lie under, a member of P or the DIR (realpath, case-folded)."""
    t = _norm(target)
    for label, p in list(members.items()) + [("DIR", dir_path)]:
        q = _norm(p)
        if _under(t, q):
            refuse("(iii) the target %s is, or lies under, the protected %s (%s): no launch" % (target, label, p))
    return t


def launch_cmd(root, target, model, pin, config, ranking_db):
    gradlew = os.path.join(root, "gradlew.bat" if os.name == "nt" else "gradlew")
    return [gradlew, "bootRun", "--console=plain", "--offline", "-PjvmThreads=%d" % JVM_THREADS,
            "-D%s=%s" % (PROP_FILE, target), "-D%s=%s" % (PROP_MODEL, model), "-D%s=%s" % (PROP_SRC, pin),
            "-D%s=%s" % (PROP_RANKING, ranking_db), "--args=--config %s" % config]


def default_launch(cmd, cwd):
    return subprocess.call(cmd, cwd=cwd)


def java_pids():
    """Printed before / after (C1's 'no new java.exe'); best effort, never a decision."""
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq java.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
        return sorted(l.split(",")[1].strip('"') for l in out.splitlines() if l.startswith('"java'))
    except Exception:
        return ["unavailable"]


def run(arm, config, dir_file=None, target=None, dry_run=False, droot=None, pins_file=PINS_FILE, launch=default_launch,
        root=ROOT, run_id=None, out=print, pids=java_pids, copy=shutil.copyfile, code_dir=HERE, code_pins=None):
    """The launcher; returns 0, or raises Refusal(2); a JVM failure returns its rc (after the re-hash)."""
    droot = droot or data_root()
    check_data_root(droot, root)                                              # C-E1-3
    cp = check_code_pins(code_dir, code_pins)                                 # C-E1-4
    out("%s (C-E1-3) data root = JVM cwd %s; (C-E1-4) code pins %s" % (TAG, root, json.dumps(cp, sort_keys=True)))
    import embedder_arms as EA
    if arm not in ROUTE_ARMS:
        refuse("arm %r is not one of %s" % (arm, ROUTE_ARMS))
    pins = load_pins(pins_file)
    members = protected_set(droot, pins)
    dir_path = os.path.join(droot, DIR_REL)
    src = dir_file or members["DIR/" + arm]
    hashed = dict(members)
    hashed["DIR-under-test"] = src
    out("%s arm %s; DIR file under test %s; java PIDs before: %s" % (TAG, arm, src, pids()))
    # (i) the pin, before anything else
    if not os.path.isfile(src):
        refuse("(i) the DIR file %s does not exist" % src)
    sha = sha256_file(src)
    try:
        pin = EA.registrar_pin(EA.ARMS[arm], sha, pins_file)
    except Refusal:
        raise
    except SystemExit as e:                     # embedder_arms.refuse carries its message; the launcher's code is rc 2
        refuse("(i) the registrar's pin check failed before any copy or launch: %s" % e)
    out("%s (i) pin: sha256 %s == the registrar's pin" % (TAG, sha))
    # the working path (path rule) and (iii)
    run_id = run_id or "%s_%s" % (datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), arm)
    work_dir = os.path.join(droot, WORK_REL, run_id)
    tgt = target or os.path.join(work_dir, EA.cache_file(EA.ARMS[arm]))
    check_target(tgt, members, dir_path)
    if dir_file is not None:
        check_target(tgt, {"DIR-under-test": dir_file}, dir_path)
    odp, _cfg = check_config(config, root, hashed, dir_path)                  # B-E1-2
    ranking_db = os.path.join(work_dir, RANKING_DB)
    out("%s (B-E1-2) config %s outputDir %s (fresh; outside every object of record); ranking DB %s" % (TAG, config, odp, ranking_db))
    check_no_sidecars(hashed)                                                 # B-E1-1
    out("%s (B-E1-1) no -wal / -shm / -journal beside any of the %d hashed files" % (TAG, len(hashed)))
    model = EA.ARMS[arm].model
    out("%s (iv) model %s (pinned digest %s); JVM threads %d" % (TAG, model, pins["arms"][arm].get("model_digest"), JVM_THREADS))
    before = snapshot_views(hashed)
    for k, v in before.items():
        out("%s P before %-44s %s%s" % (TAG, k, v.get("sha256", v.get("state")),
                                         "; tables %s" % json.dumps(v["tables"], sort_keys=True) if "tables" in v else ""))
    cmd = launch_cmd(root, tgt, model, pin, config, ranking_db)
    if dry_run:
        out("%s DRY RUN: pin and target checks passed; nothing copied, nothing launched; command: %s" % (TAG, " ".join(cmd)))
        return 0
    # (ii) the fresh working copy
    if target is None:
        if os.path.exists(work_dir):
            refuse("(ii) the run directory %s exists; a working copy is fresh per run" % work_dir)
        os.makedirs(work_dir)
    elif os.path.exists(tgt):
        refuse("(ii) the target %s exists; a working copy is fresh per run" % tgt)
    copy(src, tgt)
    csha = sha256_file(tgt)
    if csha != pin:
        refuse("(ii) the working copy %s hashes to %s, not the pin %s" % (tgt, csha, pin))
    out("%s (ii) working copy %s sha256 %s == the pin" % (TAG, tgt, csha))
    rc = launch(cmd, root)
    out("%s (iv) JVM exited rc %s; java PIDs after: %s" % (TAG, rc, pids()))
    # (v) the re-hash of P and the DIR file
    after = snapshot_views(hashed)
    breach = sorted(k for k in hashed if before[k] != after[k])
    if breach:
        for k in breach:
            out("%s PIN BREACH %s: before %s after %s" % (TAG, k, before[k], after[k]))
        refuse("PIN BREACH: %d protected file(s) changed: %s" % (len(breach), breach))
    out("%s (v) P and the DIR file unchanged after the run (%d members, sha256 + size + sidecars; main cache per table)" % (TAG, len(hashed)))
    out("%s (vi) working copy kept: %s post-run sha256 %s (a change here is expected)" % (TAG, tgt, sha256_file(tgt)))
    return rc


# ── selftest (L0) ───────────────────────────────────────────────────────────────────────────────────────────────────

def selftest():
    import io
    import tempfile
    import contextlib
    import embedder_arms as EA
    from data_v2 import ro
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="e1route_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %r" % (name, type(e).__name__, e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def fixture(tmp):
        """A data root with the 8 protected members (small real SQLite files) and a pins file pinning the four DIR files."""
        droot = os.path.join(tmp, "root")
        os.makedirs(os.path.join(droot, DIR_REL))
        arms = {}
        for a in PIN_ARMS:
            fn = EA.cache_file(EA.ARMS[a])
            p = os.path.join(droot, DIR_REL, fn)
            with open(p, "wb") as f:
                f.write(("arm file %s\n" % a).encode() * 50)
            arms[a] = {"sha256": sha256_file(p), "file": fn, "model_digest": "d-" + a}
        for s in SOURCE_DBS + (FROZEN,):
            with open(os.path.join(droot, s), "wb") as f:
                f.write(b"source " + s.encode())
        c = ro.create_new(os.path.join(droot, MAIN_CACHE))
        c.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY, t TEXT)"); c.execute("INSERT INTO queries VALUES (1, 'x')")
        c.execute("CREATE TABLE reserved_pool_meta (pool_id TEXT PRIMARY KEY)"); c.commit(); c.close()
        pf = os.path.join(tmp, "pins.json")
        with open(pf, "w") as f:
            json.dump({"schema": EA.ARM_PINS_SCHEMA, "arms": arms}, f)
        write_cfg(droot, "cfg.toml", 'outputDir = "out/L1"\nseed = 42\nnumIterations = 2\n')
        return droot, pf, arms

    def write_cfg(droot, name, text):
        with open(os.path.join(droot, name), "w", encoding="utf-8") as f:
            f.write(text)
        return name

    class Jvm:
        """A fake JVM: records its command and, like the probe PR1, MUTATES the file it is given (appends a byte)."""
        def __init__(self, extra=None, rc=0):
            self.calls, self.extra, self.rc = [], extra, rc

        def __call__(self, cmd, cwd):
            self.calls.append(cmd)
            path = [c for c in cmd if c.startswith("-D%s=" % PROP_FILE)][0].split("=", 1)[1]
            with open(path, "ab") as f:
                f.write(b"!")
            if self.extra:
                self.extra()
            return self.rc

    def quiet(fn, *a, **k):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                return fn(*a, **k), buf.getvalue(), None
            except SystemExit as e:
                return None, buf.getvalue(), e

    def admitted(tmp):
        droot, pf, arms = fixture(tmp)
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="r1", pids=lambda: [])
        assert err is None and rc == 0, (err, text)
        wp = os.path.join(droot, WORK_REL, "r1", "embeddings_cache_nomic-embed-text_latest.db")
        assert len(jvm.calls) == 1 and "-D%s=%s" % (PROP_FILE, wp) in jvm.calls[0], jvm.calls
        assert "-D%s=%s" % (PROP_SRC, arms["nomic_raw"]["sha256"]) in jvm.calls[0] and "-PjvmThreads=12" in jvm.calls[0]
        assert "-D%s=nomic-embed-text:latest" % PROP_MODEL in jvm.calls[0]
        assert "-D%s=%s" % (PROP_RANKING, os.path.join(droot, WORK_REL, "r1", RANKING_DB)) in jvm.calls[0], jvm.calls[0]
        assert "(B-E1-1) no -wal / -shm / -journal beside any of the 9 hashed files" in text, text
        assert '"embedder_arms.py": "2073d1315981a30464037913b85ce2bf8838aa00"' in text and '"embedder_cross_flat.py": "7868e858' in text, text
        # the JVM mutated its working copy (expected), and nothing protected changed
        assert sha256_file(wp) != arms["nomic_raw"]["sha256"] and "(vi) working copy kept" in text
        assert sha256_file(os.path.join(droot, DIR_REL, arms["nomic_raw"]["file"])) == arms["nomic_raw"]["sha256"]
        assert "(v) P and the DIR file unchanged after the run (9 members" in text, text

    def c1_mutant(tmp):
        # C1 / mutant 1: a one-byte mutant of the scratch "DIR" copy is refused BEFORE any copy and any launch
        droot, pf, arms = fixture(tmp)
        scratch = os.path.join(tmp, "scratch_nomic_raw.db")
        shutil.copyfile(os.path.join(droot, DIR_REL, arms["nomic_raw"]["file"]), scratch)
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dir_file=scratch, droot=droot, pins_file=pf, launch=jvm, root=droot,
                              run_id="ok", pids=lambda: [])
        assert err is None and rc == 0 and len(jvm.calls) == 1, (err, text)      # the unmutated scratch copy is ADMITTED
        with open(scratch, "r+b") as f:
            b = f.read(1); f.seek(0); f.write(bytes([b[0] ^ 1]))
        jvm2 = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dir_file=scratch, droot=droot, pins_file=pf, launch=jvm2, root=droot,
                              run_id="mut", pids=lambda: [])
        assert isinstance(err, SystemExit) and err.code == 2 and "registrar's pin" in text, (err, text)
        assert jvm2.calls == [] and not os.path.exists(os.path.join(droot, WORK_REL, "mut")), "a mutant reached a copy or a launch"

    def c2_breach(tmp):
        # mutant 2's killer: a JVM that also writes a protected member -> PIN BREACH (rc 2)
        droot, pf, arms = fixture(tmp)
        def touch():
            with open(os.path.join(droot, SOURCE_DBS[0]), "ab") as f:
                f.write(b"x")
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(extra=touch), root=droot, run_id="b",
                              pids=lambda: [])
        assert isinstance(err, SystemExit) and err.code == 2, (err, text)
        assert "PIN BREACH source/embeddings_cache_nomic-embed-text_latest.db" in text and "PIN BREACH: 1 protected file(s)" in text, text

    def c2_sidecar_and_table(tmp):
        # a sidecar appearing, or a row written into the main cache's queries table, is a breach too
        droot, pf, arms = fixture(tmp)
        def side():
            open(os.path.join(droot, FROZEN + "-wal"), "wb").close()
        rc, text, err = quiet(run, "nomic_card", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(extra=side), root=droot, run_id="s",
                              pids=lambda: [])
        assert isinstance(err, SystemExit) and "PIN BREACH frozen/snapshots_frozen.db" in text, text
        os.remove(os.path.join(droot, FROZEN + "-wal"))
        import sqlite3
        def row():
            c = sqlite3.connect(os.path.join(droot, MAIN_CACHE)); c.execute("INSERT INTO queries VALUES (2, 'y')"); c.commit(); c.close()
        rc, text, err = quiet(run, "nomic_card", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(extra=row), root=droot, run_id="t",
                              pids=lambda: [])
        assert isinstance(err, SystemExit) and "PIN BREACH main/embeddings_cache.db" in text, text

    def l2_targets(tmp):
        # C2's L2 / mutant 3: each member of P and the DIR itself as the target -> refused before launch (9 of 9)
        droot, pf, arms = fixture(tmp)
        members = protected_set(droot, load_pins(pf))
        targets = list(members.values()) + [os.path.join(droot, DIR_REL)]
        assert len(targets) == 9
        refused = 0
        for t in targets:
            jvm = Jvm()
            rc, text, err = quiet(run, "nomic_raw", "cfg.toml", target=t, droot=droot, pins_file=pf, launch=jvm, root=droot, pids=lambda: [])
            if isinstance(err, SystemExit) and err.code == 2 and "(iii) the target" in text and not jvm.calls:
                refused += 1
        assert refused == 9, refused
        # a path UNDER the DIR (a new file name inside it) is refused too; case-folded
        t = os.path.join(droot, DIR_REL, "sub", "embeddings_cache_nomic-embed-text_latest.db")
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", target=t.upper() if os.name == "nt" else t, droot=droot, pins_file=pf,
                              launch=Jvm(), root=droot, pids=lambda: [])
        assert isinstance(err, SystemExit) and "(iii) the target" in text, text

    def m4_dir_path(tmp):
        # mutant 4's killer: the JVM must be given the WORKING path; with the DIR path it would mutate the DIR (PR1)
        droot, pf, arms = fixture(tmp)
        jvm = Jvm()
        quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="m4", pids=lambda: [])
        given = [c for c in jvm.calls[0] if c.startswith("-D%s=" % PROP_FILE)][0].split("=", 1)[1]
        assert _norm(given).startswith(_norm(os.path.join(droot, WORK_REL))) and _norm(given) != _norm(os.path.join(droot, DIR_REL, arms["nomic_raw"]["file"]))

    def dry_and_fresh(tmp):
        droot, pf, arms = fixture(tmp)
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dry_run=True, droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="d",
                              pids=lambda: [])
        assert rc == 0 and jvm.calls == [] and not os.path.exists(os.path.join(droot, WORK_REL, "d")) and "DRY RUN" in text, text
        os.makedirs(os.path.join(droot, WORK_REL, "again"))
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="again", pids=lambda: [])
        assert isinstance(err, SystemExit) and "exists; a working copy is fresh per run" in text and jvm.calls == [], text
        rc, text, err = quiet(run, "gemma_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, pids=lambda: [])
        assert isinstance(err, SystemExit) and "is not one of" in text

    def copy_checked(tmp):
        # (ii): a working copy that does not hash to the pin is refused before the launch
        droot, pf, arms = fixture(tmp)
        def bad_copy(a, b):
            shutil.copyfile(a, b)
            with open(b, "ab") as f:
                f.write(b"?")
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="cc", pids=lambda: [],
                              copy=bad_copy)
        assert isinstance(err, SystemExit) and err.code == 2 and "(ii) the working copy" in text and jvm.calls == [], text
        # both views of the main cache are printed (the file sha and the per-table sha of queries and reserved_pool_meta)
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dry_run=True, droot=droot, pins_file=pf, launch=jvm, root=droot, pids=lambda: [])
        line = [l for l in text.splitlines() if "P before main/embeddings_cache.db" in l][0]
        assert '"queries": "' in line and '"reserved_pool_meta": "' in line, line

    def jvm_rc(tmp):
        droot, pf, arms = fixture(tmp)
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(rc=1), root=droot, run_id="rc", pids=lambda: [])
        assert rc == 1 and err is None and "(v) P and the DIR file unchanged" in text, (rc, err, text)


    def b1_sidecar_refused(tmp):
        # B-E1-1 (1): a -wal / -shm / -journal (even 0 bytes) beside ANY hashed file refuses before copy and launch, dry-run too
        droot, pf, arms = fixture(tmp)
        scratch = os.path.join(tmp, "scratch_nomic_raw.db")
        shutil.copyfile(os.path.join(droot, DIR_REL, arms["nomic_raw"]["file"]), scratch)
        members = protected_set(droot, load_pins(pf))
        sites = list(members.values()) + [scratch]
        assert len(sites) == 9
        refused, k = 0, 0
        for site in sites:
            for suf in SIDECARS:
                k += 1
                open(site + suf, "wb").close()
                for dry in (False, True):
                    jvm = Jvm()
                    rid = "sc%d%s" % (k, "d" if dry else "")
                    rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dir_file=scratch, dry_run=dry, droot=droot, pins_file=pf,
                                          launch=jvm, root=droot, run_id=rid, pids=lambda: [])
                    if (isinstance(err, SystemExit) and err.code == 2 and "REFUSED: (B-E1-1) 1 sidecar(s)" in text and site + suf in text
                            and jvm.calls == [] and not os.path.exists(os.path.join(droot, WORK_REL, rid))):
                        refused += 1
                os.remove(site + suf)
        assert refused == 9 * 3 * 2, refused
        # and with none of them, the same call is admitted
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", dir_file=scratch, droot=droot, pins_file=pf, launch=Jvm(), root=droot,
                              run_id="clean", pids=lambda: [])
        assert err is None and rc == 0, (err, text)

    def p_e1a(tmp):
        # the reviewer's probe P-E1a: -wal and -shm existed BEFORE the launch and the JVM appends to the -wal: never rc 0
        droot, pf, arms = fixture(tmp)
        src = os.path.join(droot, SOURCE_DBS[0])
        open(src + "-wal", "wb").close()
        with open(src + "-shm", "wb") as f:
            f.write(b"\0" * 64)
        def wal_tail():
            with open(src + "-wal", "ab") as f:
                f.write(b"frame")
        jvm = Jvm(extra=wal_tail)
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="pe",
                              pids=lambda: [])
        assert isinstance(err, SystemExit) and err.code == 2 and "REFUSED: (B-E1-1) 2 sidecar(s)" in text and jvm.calls == [], (rc, err, text)

    def b1_view_content(tmp):
        # B-E1-1 (2): view() records each sidecar's size and sha256; a same-size content change is a change
        p = os.path.join(tmp, "x.db")
        with open(p, "wb") as f:
            f.write(b"db")
        with open(p + "-wal", "wb") as f:
            f.write(b"AAAA")
        v1 = view(p)
        with open(p + "-wal", "wb") as f:
            f.write(b"BBBB")
        v2 = view(p)
        assert v1["sidecars"]["-wal"]["size"] == 4 and v1["sidecars"]["-wal"]["sha256"] == hashlib.sha256(b"AAAA").hexdigest(), v1
        assert v1 != v2 and v2["sidecars"]["-wal"]["sha256"] == hashlib.sha256(b"BBBB").hexdigest(), (v1, v2)
        for suf in ("-shm", "-journal"):
            with open(p + suf, "wb") as f:
                f.write(b"C")
            v3 = view(p)
            with open(p + suf, "wb") as f:
                f.write(b"D")
            assert v3 != view(p) and v3["sidecars"][suf] == {"size": 1, "sha256": hashlib.sha256(b"C").hexdigest()}, v3
        os.remove(p)
        assert view(p)["state"] == "ABSENT" and set(view(p)["sidecars"]) == {"-wal", "-shm", "-journal"}

    def b2_config(tmp):
        # B-E1-2: the config's outputDir is checked before any copy or launch
        droot, pf, arms = fixture(tmp)
        bad = [("af", 'outputDir = "experiment_results/anchorfree/redraw/af_clean_s42"\n', "lies under"),
               ("af_sub", 'outputDir = "experiment_results/anchorfree/redraw/af_clean_s42/x"\n', "lies under"),
               ("bq", 'outputDir = "experiment_results/promoted/bareq512_s42"\n', "lies under"),
               ("afs", 'outputDir = "experiment_results/anchorfree/af"\n', "lies under"),
               ("dir", 'outputDir = "experiment_results/embedder_cross/o"\n', "lies under"),
               ("frozen", 'outputDir = "snapshots_frozen.db"\n', "lies under"),
               ("none", 'seed = 42\n', "declares no outputDir"),
               ("empty", 'outputDir = ""\n', "declares no outputDir")]
        refused = 0
        for nm, body, why in bad:
            write_cfg(droot, nm + ".toml", body)
            jvm = Jvm()
            rc, text, err = quiet(run, "nomic_raw", nm + ".toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="c" + nm,
                                  pids=lambda: [])
            if (isinstance(err, SystemExit) and err.code == 2 and "REFUSED: (B-E1-2)" in text and why in text and jvm.calls == []
                    and not os.path.exists(os.path.join(droot, WORK_REL, "c" + nm))):
                refused += 1
            else:
                print("    b2 %s not refused: %r %s" % (nm, err, text[-300:]))
        assert refused == len(bad), refused
        # a missing config, and the fresh build directory
        rc, text, err = quiet(run, "nomic_raw", "nope.toml", droot=droot, pins_file=pf, launch=Jvm(), root=droot, pids=lambda: [])
        assert isinstance(err, SystemExit) and "REFUSED: (B-E1-2) the config" in text and "does not exist" in text, text
        os.makedirs(os.path.join(droot, "out", "L1", "seed_42"))
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="fr", pids=lambda: [])
        assert isinstance(err, SystemExit) and "seed_42 exists" in text and jvm.calls == [], text
        # the REAL af_clean_s42.toml is refused; the committed L1 TOML is admitted and differs from it in exactly two keys
        import tomllib
        real = os.path.join(ROOT, "experiment_configs", "anchorfree", "redraw", "af_clean_s42.toml")
        l1 = os.path.join(ROOT, "experiment_configs", "e1_route", "L1_short_af_clean_s42.toml")
        rc, text, err = quiet(run, "nomic_raw", real, dry_run=True, droot=droot, pins_file=pf, launch=Jvm(), root=droot, pids=lambda: [])
        assert isinstance(err, SystemExit) and "REFUSED: (B-E1-2)" in text and "af_clean_s42" in text, text
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", l1, droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="l1", pids=lambda: [])
        assert err is None and rc == 0 and len(jvm.calls) == 1 and jvm.calls[0][-1] == "--args=--config %s" % l1, (err, text)
        assert "outputDir %s" % os.path.join(droot, "experiment_results/e1_route/L1_short") in text, text
        with open(real, "rb") as f:
            a = tomllib.load(f)
        with open(l1, "rb") as f:
            b = tomllib.load(f)
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        assert diff == ["numIterations", "outputDir"] and b["numIterations"] == 2 and a["numIterations"] == 50, diff
        assert b["outputDir"] == "experiment_results/e1_route/L1_short" and a["outputDir"] == "experiment_results/anchorfree/redraw/af_clean_s42"

    def c3_root(tmp):
        # C-E1-3: the data root must be the JVM's cwd; otherwise refused before anything (no copy, no launch)
        droot, pf, arms = fixture(tmp)
        other = os.path.join(tmp, "elsewhere")
        os.makedirs(other)
        jvm = Jvm()
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=other, run_id="r3",
                              pids=lambda: [])
        assert isinstance(err, SystemExit) and err.code == 2 and "REFUSED: (C-E1-3)" in text and jvm.calls == [], text
        assert not os.path.exists(os.path.join(droot, WORK_REL, "r3")) and not os.path.exists(os.path.join(other, WORK_REL))
        # a sub-directory of the root is not the root either
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(), root=os.path.join(droot, DIR_REL),
                              dry_run=True, pids=lambda: [])
        assert isinstance(err, SystemExit) and "REFUSED: (C-E1-3)" in text, text
        # the same directory spelled differently (case on Windows, a trailing separator) is admitted
        alt = (droot.upper() if os.name == "nt" else droot) + os.sep
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(), root=alt, dry_run=True, pids=lambda: [])
        assert err is None and rc == 0, text

    def c4_code_pins(tmp):
        # C-E1-4: the launcher runs only on embedder_arms 2073d131 / embedder_cross_flat 7868e858 (LF blobs)
        assert CODE_PINS == {"embedder_arms.py": "2073d1315981a30464037913b85ce2bf8838aa00",
                             "embedder_cross_flat.py": "7868e8589fee107b15d3c535966b840cd648f771"}
        assert check_code_pins() == CODE_PINS
        droot, pf, arms = fixture(tmp)
        for fn in CODE_PINS:
            jvm = Jvm()
            wrong = dict(CODE_PINS)
            wrong[fn] = "0" * 40
            rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=jvm, root=droot, run_id="p" + fn[:5],
                                  pids=lambda: [], code_pins=wrong)
            assert isinstance(err, SystemExit) and err.code == 2 and "(C-E1-4) %s is blob:" % os.path.join(HERE, fn) in text, text
            assert jvm.calls == [] and not os.path.exists(os.path.join(droot, WORK_REL, "p" + fn[:5])), text
        # a code dir whose embedder_arms.py differs by one line is refused; an exact copy is refused as not the imported module
        cd = os.path.join(tmp, "code")
        os.makedirs(cd)
        for fn in CODE_PINS:
            shutil.copyfile(os.path.join(HERE, fn), os.path.join(cd, fn))
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(), root=droot, pids=lambda: [],
                              code_dir=cd, dry_run=True)
        assert isinstance(err, SystemExit) and "(C-E1-4) the imported embedder_arms" in text, text
        with open(os.path.join(cd, "embedder_cross_flat.py"), "ab") as f:
            f.write(b"# x\n")
        rc, text, err = quiet(run, "nomic_raw", "cfg.toml", droot=droot, pins_file=pf, launch=Jvm(), root=droot, pids=lambda: [],
                              code_dir=cd, dry_run=True)
        assert isinstance(err, SystemExit) and "(C-E1-4) %s is blob:" % os.path.join(cd, "embedder_cross_flat.py") in text, text

    for nm, fn in [("admitted: the working copy is given, mutated, kept; P unchanged", admitted),
                   ("C1: the unmutated scratch copy admitted, a one-byte mutant refused before copy and launch", c1_mutant),
                   ("C2: a protected file written by the JVM -> PIN BREACH rc 2", c2_breach),
                   ("C2: a sidecar or a main-cache row -> PIN BREACH", c2_sidecar_and_table),
                   ("C2 L2: 9 of 9 protected targets refused before launch; a path under the DIR too", l2_targets),
                   ("mutant 4: the JVM is given the working path, never the DIR's", m4_dir_path),
                   ("dry-run and the fresh-run rule; arm set", dry_and_fresh), ("a JVM failure passes its rc after the re-hash", jvm_rc),
                   ("(ii) a copy off the pin refused; both main-cache views printed", copy_checked),
                   ("B-E1-1: a sidecar beside any of the 9 hashed files refused (3 kinds x 9 sites x run/dry-run = 54)", b1_sidecar_refused),
                   ("B-E1-1: probe P-E1a (pre-existing -wal/-shm, a WAL-tail write) refused before launch", p_e1a),
                   ("B-E1-1: view() records sidecar size and sha256", b1_view_content),
                   ("B-E1-2: outputDir of record / missing / non-fresh refused; the L1 TOML admitted, 2 keys off af_clean_s42", b2_config),
                   ("C-E1-3: data root != JVM cwd refused", c3_root),
                   ("C-E1-4: code blobs 2073d131 / 7868e858 enforced", c4_code_pins)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--arm", choices=ROUTE_ARMS)
    ap.add_argument("--config")
    ap.add_argument("--dir-file")
    ap.add_argument("--target")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.arm and a.config):
        refuse("--arm and --config are required")
    if a.target and not a.dry_run:
        refuse("--target is the L2 refusal leg only (with --dry-run)")
    try:
        return run(a.arm, a.config, dir_file=a.dir_file, target=a.target, dry_run=a.dry_run)
    except Refusal as e:
        return e.code


if __name__ == "__main__":
    sys.exit(main())
