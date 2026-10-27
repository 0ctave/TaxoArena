"""e1sd_launch.py: E1-SPLIT-DRAWS' launcher for the six builds N_e1sd1..3 (nomic_raw) and Q_e1sd1..3 (qwen3), and THE LAUNCH PLAN.
ZERO judge / LLM / embedding calls (the build's embedder must cover every corpus text: misses = 0, checked before launch).

REGISTRATION OF RECORD: docs/judge_v2_program.md E1-SPLIT-DRAWS (L23831-L23859, a1c65848), HYGIENE / OPERATIONAL, verbatim in part:
"every build reads TRAIN only (TRAIN-ONLY guard), held-out never enters the JVM; verified with pool_guard.py --pool <id> before
each build; nomic builds through the E1-ROUTE launcher (working copy, pin-checked; misses = 0 required: the raw file covers the
corpus, 11,769 texts); backup and embeddings_cache per-table hashes before and after every construction; rule 7, 12 threads, one
construction at a time. OPERATIONAL: each split's first build rewrites the corpus DB's reserved-pool metadata and may leave a -wal
tail that only THE AUTHOR checkpoints (up to 3 checkpoints, one per split); pool readers refuse until then."

  python tools/analysis/e1sd_launch.py --selftest | --mutants
  python tools/analysis/e1sd_launch.py --plan                                     # prints THE LAUNCH PLAN below (no read)
  python tools/analysis/e1sd_launch.py --build N_e1sd1 --backup-dir <dir> --dry-run
  python tools/analysis/e1sd_launch.py --build N_e1sd1 --backup-dir <dir>
  python tools/analysis/e1sd_launch.py --verify --backup-dir <the backup taken before N_e1sd1>   # after the author's CP-1

THE LAUNCH PLAN (from the main checkout after the merge; one build per rule-7 window, W1-W5; 12 threads; backup first):
  ORDER (enforced): N_e1sd1, N_e1sd2, N_e1sd3, then Q_e1sd1, Q_e1sd2, Q_e1sd3. A Q build is REFUSED until all three N run dirs
    exist and completed; an N build is REFUSED once any Q run dir exists. Why: a qwen3 build opens embeddings_cache.db and leaves
    -wal / -shm beside it (EmbeddingCache never closes its connection), and e1_route_launch REFUSES any sidecar beside it (B-E1-1,
    whatever its size); nomic builds never open it (E1: P unchanged across N-raw and N-card). Interleaving would cost one author
    checkpoint per split; this order costs none between builds.
  WHERE A WAL TAIL CAN APPEAR (exactly):
    (T1) mmlu_pro_dataset_cache_v2.db-wal: EVERY build writes it at split time (ReservedPool.save: INSERT OR IGNORE reserved_pool
         rows of the split's pool, new content on the split's FIRST build only; INSERT OR REPLACE reserved_pool_meta, created_at =
         now, on every build). The next JVM checkpoints the previous tail on open (E1 C-PB-1: N-raw's row reached the main file when
         N-card ran; N-card left 8,272 B). So after build j the tail stays until the next JVM or the author.
    (T2) embeddings_cache.db-wal and -shm: Q builds only (queries INSERT OR REPLACE at saveSnapshot; never closed). N builds open
         the working copy (experiment_results/e1_route_work/<run id>/...), whose -wal is kept as evidence (C-PB-3), never read.
    (T3) snapshots.db-wal: EVERY build (the snapshot row; JDBC journal_mode=WAL). The readout reads snapshots.db (pool_guard.open_ro
         refuses a non-empty -wal).
    (T4) NOW (2026-10-03, before any build): embeddings_cache.db carries a 0-byte -wal and a 32 KB -shm (2026-10-02 21:47) and so
         does snapshots.db; mmlu_pro_dataset_cache_v2.db a 0-byte -wal. The 0-byte -wal is admitted by pool_guard; e1_route_launch
         REFUSES the main cache's sidecars whatever their size (B-E1-1).
  AUTHOR CHECKPOINTS REQUESTED (2 of the registered "up to 3"):
    CP-0 BEFORE N_e1sd1: remove the sidecars beside embeddings_cache.db (and any beside the P members: the four DIR arm files, the
         two per-model source DBs, snapshots_frozen.db) by a clean read-write open/close with no JVM alive, so e1_route_launch's
         B-E1-1 admits the N builds. (Its dry-run REFUSES until then: that refusal is the request.)
    CP-1 AFTER Q_e1sd3, BEFORE the readout: checkpoint mmlu_pro_dataset_cache_v2.db (T1), embeddings_cache.db (T2) and snapshots.db
         (T3); then --verify against the backup taken before N_e1sd1, then e1_split_draws.py --dry-run / --run.
    Between builds NO author checkpoint is needed: every Python view of a DB carrying a tail (T1/T2) reads a CHECKPOINTED SCRATCH
    COPY (db + -wal copied into a fresh directory under experiment_results/e1_split_draws_work/scratch_<ts>/, the originals re-hashed
    equal before and after the copy, the COPY checkpointed: a write to the scratch copy only, e1_readout.eval_db_copy's pattern),
    deleted after the view. A hot -journal (rollback writer) is never copied: REFUSED (the author's).
  POOL CHECK "before each build": a split's FIRST build (N_k) cannot find its pool recorded (the build records it): the check is
    FRESH-or-RECORDED (e1sd_split_draw.pool_state: no rows, or rows == the file's judgeable ids; anything else REFUSES) plus the
    engine's own [POOL-PIN] (the TOML's pool key: the JVM refuses unless its split hashes to it). Before Q_k: pool_guard.
    assert_pool_of_record(pid, db=<the corpus DB view>, id_file=<the split file>) MUST pass (N_k recorded it). After every build the
    same assert on the post-build view. (Builder declaration L1: the literal "pool_guard.py --pool <id> before each build" is
    unsatisfiable before a split's first build; flagged to the registrar.)
  PER BUILD (this launcher, in order; every refusal precedes any launch; rc 2):
    (1) C-E1-3 data root = JVM cwd (e1_route_launch.check_data_root); (2) DECLARED: the config is one of the six TOMLs with its
    declared LF blob, it passes e1sd_split_draw.check_toml, and the split file has its declared blob and re-derives byte-equal from
    the corpus view; (3) ORDER (above); (4) BACKUP: --backup-dir holds both caches (and their -wal when non-empty) whose sha256 equal
    the live files now; (5) COVERAGE: the build's embedder has a vector for every one of the 11,769 corpus texts (N: the pinned DIR
    nomic_raw file; Q: embeddings_cache.db), else REFUSED (a miss would be an embedding call); (6) POOL (above); (7) VIEWS BEFORE:
    every user table of the corpus DB (reserved_pool / reserved_pool_meta split into the three e1sd pools' rows and the rest) and,
    for Q, of embeddings_cache.db (blobs hashed raw); (8) LAUNCH: N = e1_route_launch.run(arm nomic_raw, the TOML) UNCHANGED (pin,
    working copy, P re-hash, its own 12-thread command); Q = gradlew bootRun --console=plain --offline -PjvmThreads=12
    -Dranking.db.path=<fresh work dir>/ratings_e1sd.db --args="--config <toml>" with P' (P minus the main cache) sidecar-free and
    re-hashed after; (9) VIEWS AFTER: every table equal except the build's own pool (reserved_pool rows == the file's judgeable ids;
    reserved_pool_meta row with corpus_size 12,000, seed NULL, test_ratio NULL, the file's domains and counts; created_at free); any
    other change -> PIN BREACH (restore from the backup); (10) RUN DIR: e1sd_split_draw.check_run_dir (pool, embedder, sizes ==
    the split's, closedByContent=0, no [SPLIT-CLOSURE], [TRAIN-ONLY] line, one snapshot id, config blob).
  AFTER EACH BUILD (run-operator): back up the run dir (and, for N, the working copy) to E:/TaxoArena_backup_<date>_e1sd/<build>
    with SHA256SUMS.txt; never commit outputs. Then the next build's backup of the two caches.

SELFTEST / MUTANTS: selftest() executes run() (N and Q) and verify() end to end on a fixture data root with a fake JVM and a fake
e1_route_launch.run; MUTANTS below (the table with results is in the commit message).
"""
import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
import argparse
import datetime
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[E1SD-LAUNCH]"


def _blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


RL_BLOB = "ba865debea7b286baaada89fe76889555944a6bb"           # tools/analysis/e1_route_launch.py of record (E1-ROUTE)
if _blob_lf(os.path.join(HERE, "e1_route_launch.py")) != RL_BLOB:
    print("%s REFUSED: tools/analysis/e1_route_launch.py is not the pinned blob:%s" % (TAG, RL_BLOB))
    raise SystemExit(2)
import e1_route_launch as RL  # noqa: E402
import e1sd_split_draw as SD  # noqa: E402
import pool_guard  # noqa: E402
Refusal = RL.Refusal


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refusal(2)


# the six declared TOMLs and the three split files (LF git blobs, written by e1sd_split_draw.py --write / --write-configs)
DECLARED = {"N_e1sd1": "4fac964f9b12946ade296f334e45f60a4c5a3176", "Q_e1sd1": "a910b359e089b4fcc7531dba3e1cbe2f59a01aaf",
            "N_e1sd2": "4ba063c134b2149e8d4084ed131a7c1d99cbc722", "Q_e1sd2": "f51ee5a6545773e5f88711fb884c8cf229eba4f0",
            "N_e1sd3": "00d2543e2d10169f9bf57af656859f07b6a44f61", "Q_e1sd3": "e5ffd8b91f9c90ca378b7fc05b8aa3135f2de87d"}
SPLIT_BLOBS = {1: "33ad1c550b30e874c66b1ca1b8ed846d3b9fbcb2", 2: "55231da055b763fcdd7eac52f2c68f919a2836fa",
               3: "5ad9c86ee55fc7e8569797343a8146e2582991b4"}
SPLIT_POOLS = {1: "p5fb86f1075d76e34", 2: "p6d15d913354f256d", 3: "p69d2762ac6223d93"}
CORPUS, MAIN = SD.CORPUS_DB, SD.EMB_DB
CACHES = (MAIN, CORPUS)
WORK_REL = os.path.join("experiment_results", "e1_split_draws_work")
RANKING_DB = "ratings_e1sd.db"
JVM_THREADS = 12
N_CORPUS_TEXTS = 11769
POOL_TABLES = ("reserved_pool", "reserved_pool_meta")


def sha256_file(path):
    return RL.sha256_file(path)


def parse_build(name):
    if name not in DECLARED:
        refuse("(DECLARED) build %r is not one of %s" % (name, sorted(DECLARED)))
    return name[0], int(name[-1])


# ------------------------------------------------------------------------------------------------ DB views (tail-safe)
def tail(path, suffix):
    p = path + suffix
    return p if (os.path.isfile(p) and os.path.getsize(p) > 0) else None


def view_path(path, scratch_parent, out):
    """-> (path to read, scratch dir to delete or None, label). A non-empty -wal: a checkpointed scratch COPY (db + -wal copied into
    a fresh dir, originals re-hashed equal before / after, the copy checkpointed). A non-empty -journal: REFUSED."""
    if tail(path, "-journal"):
        refuse("%s-journal is non-empty: a rollback writer's transaction is live or hot; the author's (never copied)" % path)
    if not tail(path, "-wal"):
        return path, None, "the file (no WAL tail)"
    os.makedirs(scratch_parent, exist_ok=True)
    d = os.path.join(scratch_parent, "scratch_%s_%d" % (datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), os.getpid()))
    n = 0
    while os.path.exists(d + ("_%d" % n if n else "")):
        n += 1
    d = d + ("_%d" % n if n else "")
    os.makedirs(d)
    dst = os.path.join(d, os.path.basename(path))
    before = {s: sha256_file(path + s) for s in ("", "-wal")}
    for s in before:
        shutil.copyfile(path + s, dst + s)
    after = {s: sha256_file(path + s) for s in before}
    copied = {s: sha256_file(dst + s) for s in before}
    if not (before == after == copied):
        shutil.rmtree(d, ignore_errors=True)
        refuse("%s changed during the scratch copy (before %s after %s copy %s)" % (path, before, after, copied))
    con = sqlite3.connect(dst)
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        con.close()
    if tail(dst, "-wal") or tail(dst, "-journal"):
        shutil.rmtree(d, ignore_errors=True)
        refuse("the scratch copy %s still has a non-empty sidecar after the checkpoint" % dst)
    out("%s VIEW %s: WAL tail %d B -> checkpointed scratch copy %s (originals sha256 %s / wal %s equal before, after, copy)"
        % (TAG, os.path.basename(path), os.path.getsize(path + "-wal"), dst, before[""][:16], before["-wal"][:16]))
    return dst, d, "a checkpointed scratch copy"


def _hash_rows(cur):
    h, n = hashlib.sha256(), 0
    for row in cur:
        for v in row:
            if isinstance(v, (bytes, bytearray)):
                h.update(b"B%d:" % len(v))
                h.update(bytes(v))
            else:
                h.update(repr(v).encode("utf-8"))
            h.update(b"\x1f")
        h.update(b"\n")
        n += 1
    return h.hexdigest(), n


def table_view(path, pools=()):
    """{table: (sha256, rows)} over every user table in primary-key order (blobs hashed raw); reserved_pool / reserved_pool_meta
    EXCLUDE the rows of `pools`, which appear as 'pool:<pid>:rows' (sorted (domain, id)) and 'pool:<pid>:meta' (the row minus
    created_at, or None)."""
    from data_v2 import ro
    con = pool_guard.open_ro(path)
    try:
        out = {}
        tables = ro.user_tables(con)
        for t in tables:
            order = ", ".join('"%s"' % c for c in ro._pk_cols(con, t))
            if t in POOL_TABLES and pools:
                q = 'SELECT * FROM "%s" WHERE pool_id NOT IN (%s) ORDER BY %s' % (t, ",".join("?" * len(pools)), order)
                out[t] = _hash_rows(con.execute(q, list(pools)))
            else:
                out[t] = _hash_rows(con.execute('SELECT * FROM "%s" ORDER BY %s' % (t, order)))
        for pid in pools:
            if "reserved_pool" in tables:
                rows = sorted(con.execute("SELECT domain, question_id FROM reserved_pool WHERE pool_id = ?", (pid,)).fetchall())
                out["pool:%s:rows" % pid] = (hashlib.sha256(repr(rows).encode()).hexdigest(), len(rows))
            if "reserved_pool_meta" in tables:
                m = con.execute("SELECT dataset, corpus_size, seed, test_ratio, domains, question_count, domain_count FROM "
                                "reserved_pool_meta WHERE pool_id = ?", (pid,)).fetchone()
                out["pool:%s:meta" % pid] = (repr(m[1:]) if m else None, 1 if m else 0)
        return out
    finally:
        con.close()


def expected_pool_entries(pid, ids, corpus_size=12000):
    j = pool_guard.judgeable(ids)
    rows = sorted((k, q) for k, v in j.items() for q in v)
    meta = (corpus_size, None, None, ",".join(sorted(j)), sum(len(v) for v in j.values()), len(j))
    return {"pool:%s:rows" % pid: (hashlib.sha256(repr(rows).encode()).hexdigest(), len(rows)),
            "pool:%s:meta" % pid: (repr(meta), 1)}


def compare_views(label, before, after, admitted, out):
    """admitted: {key: expected value after}; the key may also be absent / equal before. -> list of unexpected changes."""
    bad = []
    for key in sorted(set(before) | set(after)):
        b, a = before.get(key), after.get(key)
        if key in admitted:
            if a != admitted[key]:
                bad.append("%s %s after %s != the expected %s" % (label, key, a, admitted[key]))
            elif b != a:
                out("%s %s %s: %s -> %s (ADMITTED: this build's own pool, as the split file states)" % (TAG, label, key, b, a))
            continue
        if b != a:
            bad.append("%s %s %s -> %s" % (label, key, b, a))
    return bad


# ------------------------------------------------------------------------------------------------ checks
def check_declared(arm, k, root, out):
    name = "%s_e1sd%d" % (arm, k)
    cfg = os.path.join(root, *(SD.TOML_REL % (arm, k)).split("/"))
    sp = os.path.join(root, *(SD.SPLIT_REL % k).split("/"))
    for p, want, what in ((cfg, DECLARED[name], "config"), (sp, SPLIT_BLOBS[k], "split file")):
        got = _blob_lf(p) if os.path.isfile(p) else "ABSENT"
        if got != want:
            refuse("(DECLARED) the %s %s is blob:%s, not the declared blob:%s" % (what, p, got, want))
    with open(os.path.join(root, *SD.BASE_TOML.split("/")), encoding="utf-8") as f:
        base = f.read()
    with open(cfg, encoding="utf-8") as f:
        SD.check_toml(arm, k, SPLIT_POOLS[k], f.read(), base)
    with open(sp, "rb") as f:
        ids = json.loads(f.read().decode("utf-8"))
    if pool_guard.compute_pool_id(pool_guard.judgeable(ids)) != SPLIT_POOLS[k]:
        refuse("(DECLARED) %s does not hash to %s" % (sp, SPLIT_POOLS[k]))
    out("%s (2) DECLARED %s: config blob:%s, split file blob:%s -> pool %s; check_toml OK" % (TAG, name, DECLARED[name][:8],
                                                                                            SPLIT_BLOBS[k][:8], SPLIT_POOLS[k]))
    return os.path.relpath(cfg, root).replace(os.sep, "/"), ids


def run_dir_done(arm, k, droot):
    mp = os.path.join(SD.run_dir_of(arm, k, droot), "diagnostics", "run_manifest.json")
    if not os.path.isfile(mp):
        return False
    with open(mp, encoding="utf-8") as f:
        return json.load(f).get("exit_reason") == "completed"


def check_order(arm, droot, out):
    if arm == "N":
        q = [k for k in (1, 2, 3) if os.path.exists(SD.run_dir_of("Q", k, droot))]
        if q:
            refuse("(ORDER) an N build after a Q build (Q run dir(s) %s exist): a qwen3 build leaves sidecars beside "
                   "embeddings_cache.db, which e1_route_launch refuses; the order is N1, N2, N3, Q1, Q2, Q3" % q)
    else:
        missing = [k for k in (1, 2, 3) if not run_dir_done("N", k, droot)]
        if missing:
            refuse("(ORDER) a Q build before all three N builds completed (missing N_e1sd%s)" % missing)
    out("%s (3) ORDER admitted for an %s build" % (TAG, arm))


def check_backup(backup_dir, droot, out):
    if not backup_dir or not os.path.isdir(backup_dir):
        refuse("(BACKUP) --backup-dir %r is not an existing directory" % backup_dir)
    if RL._norm(backup_dir) == RL._norm(droot):
        refuse("(BACKUP) --backup-dir is the data root")
    for c in CACHES:
        live = os.path.join(droot, c)
        for s in ("", "-wal"):
            if s and not tail(live, "-wal"):
                continue
            bk = os.path.join(backup_dir, c + s)
            if not os.path.isfile(bk):
                refuse("(BACKUP) %s has no %s" % (backup_dir, c + s))
            ls, bs = sha256_file(live + s), sha256_file(bk)
            if ls != bs:
                refuse("(BACKUP) %s sha256 %s != the live %s %s: take a fresh backup before this build" % (bk, bs[:16], c + s, ls[:16]))
            out("%s (4) BACKUP %s == live %s (sha256 %s)" % (TAG, bk, c + s, ls))


def coverage(db, texts, label, out, dim=None):
    """(5) every corpus text has a vector in db (read by text, pool_guard.open_ro); misses REFUSE (a miss is an embedding call)."""
    con = pool_guard.open_ro(db)
    try:
        want, have = set(texts), set()
        for t, b in con.execute("SELECT query, vector FROM embeddings"):
            if t in want and isinstance(b, bytes) and (dim is None or len(b) == 4 * dim):
                have.add(t)
    finally:
        con.close()
    miss = len(want - have)
    out("%s (5) COVERAGE %s: %d of %d corpus texts have a vector; misses %d (0 required)" % (TAG, label, len(have), len(want), miss))
    if miss:
        refuse("(5) %s misses %d corpus texts: the JVM would embed them (an embedding call; zero calls registered)" % (label, miss))


def pool_check(k, ids, sp, view, first_build, out):
    pid = SPLIT_POOLS[k]
    con = pool_guard.open_ro(view)
    try:
        st = SD.pool_state(con, pid, ids)
    finally:
        con.close()
    if not first_build and st != "RECORDED":
        refuse("(6) pool %s is %s before a split's second build: its first build must have recorded it" % (pid, st))
    if st == "RECORDED":
        pool_guard.assert_pool_of_record(pid, db=view, id_file=sp)
        out("%s (6) POOL %s RECORDED: pool_guard.assert_pool_of_record(db=the corpus view, id_file=%s) passed"
            % (TAG, pid, os.path.basename(sp)))
    else:
        out("%s (6) POOL %s FRESH (no reserved_pool rows; the split's first build records it; the JVM's [POOL-PIN] checks it)"
            % (TAG, pid))
    return st


# ------------------------------------------------------------------------------------------------ the launcher
def default_launch(cmd, cwd):
    return subprocess.call(cmd, cwd=cwd)


def run(build, backup_dir, dry_run=False, root=ROOT, droot=None, pins_file=RL.PINS_FILE, launch=default_launch, rl_run=None,
        out=print, run_id=None, pids=RL.java_pids, keep_scratch=False):
    droot = droot or RL.data_root()
    arm, k = parse_build(build)
    RL.check_data_root(droot, root)                                                       # (1)
    out("%s (1) data root = JVM cwd %s; build %s (%s)" % (TAG, droot, build, SD.ARM_EMBEDDER[arm]))
    cfg_rel, ids = check_declared(arm, k, root, out)                                      # (2)
    check_order(arm, droot, out)                                                          # (3)
    check_backup(backup_dir, droot, out)                                                  # (4)
    scratch_parent = os.path.join(droot, WORK_REL)
    cleanup = []
    try:
        cview, cdir, clabel = view_path(os.path.join(droot, CORPUS), scratch_parent, out)
        cleanup.append(cdir)
        con = pool_guard.open_ro(cview)
        try:
            rows = SD.corpus_rows(con)
        finally:
            con.close()
        d = SD.draw(rows, SD.SALTS[k - 1])
        if SD.file_bytes(d["ids"]) != SD.file_bytes(ids) or d["pool"] != SPLIT_POOLS[k]:
            refuse("(2) the split file does not re-derive byte-equal from the corpus (%s)" % clabel)
        out("%s (2) split e1sd%d re-derived byte-equal from the corpus DB (%s): held-out %d rows / TRAIN %d rows"
            % (TAG, k, clabel, len(d["held"]), len(d["train"])))
        texts = sorted(set(r["text"] for r in rows))
        if len(texts) != N_CORPUS_TEXTS:
            refuse("(5) the corpus has %d distinct texts, the registration's raw file covers %d" % (len(texts), N_CORPUS_TEXTS))
        pins = RL.load_pins(pins_file)
        if arm == "N":
            coverage(os.path.join(droot, RL.DIR_REL, pins["arms"]["nomic_raw"]["file"]), texts, "nomic_raw DIR file", out, dim=768)
            mview = None
        else:
            mview, mdir, _ml = view_path(os.path.join(droot, MAIN), scratch_parent, out)
            cleanup.append(mdir)
            coverage(mview, texts, "embeddings_cache.db (qwen3)", out, dim=4096)
        sp = os.path.join(root, *(SD.SPLIT_REL % k).split("/"))
        pool_check(k, ids, sp, cview, arm == "N", out)                                     # (6)
        e1sd = tuple(SPLIT_POOLS[i] for i in (1, 2, 3))
        before_c = table_view(cview, e1sd)                                                # (7)
        before_m = table_view(mview) if mview else None
        out("%s (7) BEFORE corpus tables %s" % (TAG, json.dumps({t: v[1] for t, v in sorted(before_c.items())})))
        if before_m is not None:
            out("%s (7) BEFORE main tables %s" % (TAG, json.dumps({t: v[1] for t, v in sorted(before_m.items())})))
        for c in cleanup:
            if c and not keep_scratch:
                shutil.rmtree(c, ignore_errors=True)
        cleanup = []
        # (8) launch
        if arm == "N":
            rl = rl_run or RL.run
            rc = rl("nomic_raw", cfg_rel, dry_run=dry_run, droot=droot, pins_file=pins_file, root=root, out=out)
            if dry_run:
                out("%s DRY RUN (N): every pre-launch check passed, e1_route_launch's dry-run admitted; nothing launched" % TAG)
                return 0
        else:
            members = {kk: v for kk, v in RL.protected_set(droot, pins).items() if not kk.startswith("main/")}
            RL.check_no_sidecars(members)
            before_p = RL.snapshot_views(members)
            run_id = run_id or "%s_%s" % (datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), build)
            work = os.path.join(droot, WORK_REL, run_id)
            gradlew = os.path.join(root, "gradlew.bat" if os.name == "nt" else "gradlew")
            cmd = [gradlew, "bootRun", "--console=plain", "--offline", "-PjvmThreads=%d" % JVM_THREADS,
                   "-D%s=%s" % (RL.PROP_RANKING, os.path.join(work, RANKING_DB)), "--args=--config %s" % cfg_rel]
            out("%s (8) P' (%d members) sidecar-free; command: %s" % (TAG, len(members), " ".join(cmd)))
            if dry_run:
                out("%s DRY RUN (Q): every pre-launch check passed; nothing launched" % TAG)
                return 0
            if os.path.exists(work):
                refuse("the work dir %s exists (fresh per run)" % work)
            os.makedirs(work)
            out("%s java PIDs before: %s" % (TAG, pids()))
            rc = launch(cmd, root)
            out("%s JVM exited rc %s; java PIDs after: %s" % (TAG, rc, pids()))
            after_p = RL.snapshot_views(members)
            breach = sorted(kk for kk in members if before_p[kk] != after_p[kk])
            if breach:
                refuse("PIN BREACH: protected file(s) changed: %s" % breach)
            out("%s P' unchanged (%d members)" % (TAG, len(members)))
        # (9) views after
        cview, cdir, _ = view_path(os.path.join(droot, CORPUS), scratch_parent, out)
        cleanup.append(cdir)
        after_c = table_view(cview, e1sd)
        admitted = expected_pool_entries(SPLIT_POOLS[k], ids, corpus_size=len(rows))
        bad = compare_views("corpus", before_c, after_c, admitted, out)
        if arm == "Q":
            mview, mdir, _ = view_path(os.path.join(droot, MAIN), scratch_parent, out)
            cleanup.append(mdir)
            bad += compare_views("main", before_m, table_view(mview), {}, out)
        if bad:
            refuse("PIN BREACH: unexpected table change(s): %s (restore from %s)" % (bad, backup_dir))
        pool_guard.assert_pool_of_record(SPLIT_POOLS[k], db=cview, id_file=sp)
        out("%s (9) AFTER: every table equal except this build's pool %s (rows == the file's %d judgeable ids); pool_guard passed"
            % (TAG, SPLIT_POOLS[k], admitted["pool:%s:rows" % SPLIT_POOLS[k]][1]))
        # (10) run dir
        got = SD.check_run_dir(SD.run_dir_of(arm, k, droot), arm, k, d, DECLARED[build],
                               nomic_pin=pins["arms"]["nomic_raw"]["sha256"])
        out("%s (10) RUN DIR %s: snapshot %s; [POOL] %s gate %s closedByContent %s; rc %s"
            % (TAG, SD.run_dir_of(arm, k, droot), got["snapshot"], got["pool_line"][0], got["pool_line"][1], got["pool_line"][2], rc))
        return rc
    finally:
        for c in cleanup:
            if c and not keep_scratch:
                shutil.rmtree(c, ignore_errors=True)


def verify(backup_dir, root=ROOT, droot=None, out=print):
    """After CP-1: the live caches (no tail admitted) against the backup taken before N_e1sd1; the three e1sd pools admitted with
    exactly their files' rows and meta; every other table equal."""
    droot = droot or RL.data_root()
    if not backup_dir or not os.path.isdir(backup_dir):
        refuse("(BACKUP) --backup-dir %r is not an existing directory" % backup_dir)
    e1sd = tuple(SPLIT_POOLS[i] for i in (1, 2, 3))
    for c in CACHES:
        for s in ("-wal", "-journal"):
            if tail(os.path.join(droot, c), s):
                refuse("(VERIFY) %s%s is non-empty: the author's checkpoint CP-1 first" % (os.path.join(droot, c), s))
    con = pool_guard.open_ro(os.path.join(droot, CORPUS))
    try:
        n_rows = len(SD.corpus_rows(con))
    finally:
        con.close()
    admitted = {}
    for k in (1, 2, 3):
        with open(os.path.join(root, *(SD.SPLIT_REL % k).split("/")), "rb") as f:
            admitted.update(expected_pool_entries(SPLIT_POOLS[k], json.loads(f.read().decode("utf-8")), corpus_size=n_rows))
    bad = []
    for c in CACHES:
        live, bk = os.path.join(droot, c), os.path.join(backup_dir, c)
        for s in ("-wal", "-journal"):
            if tail(live, s):
                refuse("(VERIFY) %s%s is non-empty: the author's checkpoint CP-1 first" % (live, s))
        if tail(bk, "-wal") or tail(bk, "-journal"):
            refuse("(VERIFY) the backup %s carries a tail: verify against a checkpointed backup copy" % bk)
        pools = e1sd if c == CORPUS else ()
        bad += compare_views(c, table_view(bk, pools), table_view(live, pools), admitted if c == CORPUS else {}, out)
    if bad:
        refuse("PIN BREACH: the live caches differ from the backup: %s" % bad)
    out("%s VERIFY: both caches equal the backup table by table; the three e1sd pools hold exactly their files' rows" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest
def selftest(quiet=False):
    """End to end on a fixture data root (fake JVM, fake e1_route_launch.run), VALUE assertions:
    T1 Q dry-run admitted after three completed N run dirs: the command carries -PjvmThreads=12, the fresh ranking DB, the declared
       config and NO embedding property; the corpus pool state printed RECORDED (pool_guard passed).
    T2 Q build whose fake JVM writes exactly the engine's pool rows + meta (already recorded: no change) and a fake run dir: rc 0,
       run-dir line with the snapshot id. T2b N build (fake rl_run writes the pool rows as the first build of the split): the
       admission line names the pool; rc 0; rl_run received arm nomic_raw and the declared config path.
    T3 PIN BREACH on: another table changed; another pool's rows changed; the build's pool rows != the file (one id short); the meta
       row with a wrong question_count; the main cache's embeddings blob changed (Q); a P' member changed (Q).
    T4 a WAL tail: the corpus DB carries rows only in its -wal; the scratch-copy view SEES them (row count asserted; an immutable read
       of the main file would not); originals unchanged byte for byte after the view; the scratch dir is removed.
    T5 pre-launch refusals, each before any launch (the fake JVM / rl_run record calls; none made): undeclared build; tampered TOML;
       tampered split file; Q before the N builds; N after a Q run dir; stale backup; missing -wal backup when the live -wal is
       non-empty; a coverage miss; a pool CONFLICT; a Q build with the pool FRESH; a hot -journal beside the corpus DB.
    T6 verify: equal + admitted pools -> 0; a changed table -> PIN BREACH; a live tail -> REFUSED."""
    import io
    import tempfile
    import contextlib
    import struct
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)

    import embedder_arms as EA

    def fixture():
        tmp = tempfile.mkdtemp(prefix="e1sdl_")
        droot = os.path.join(tmp, "root")
        os.makedirs(os.path.join(droot, RL.DIR_REL))
        # the real corpus shape is replaced by a fixture whose split files are written here (pools differ from the declared ones,
        # so SPLIT_POOLS / DECLARED / SPLIT_BLOBS are patched for the fixture below)
        c = SD._fixture_db(os.path.join(droot, CORPUS))
        c.execute("CREATE TABLE reserved_pool_meta (pool_id TEXT PRIMARY KEY, dataset TEXT, corpus_size INTEGER, seed INTEGER, "
                  "test_ratio REAL, domains TEXT, question_count INTEGER NOT NULL, domain_count INTEGER NOT NULL, created_at INTEGER NOT NULL)")
        c.execute("CREATE TABLE eval_results (id INTEGER PRIMARY KEY, v TEXT)")
        c.execute("INSERT INTO eval_results VALUES (1, 'a')")
        c.execute("INSERT INTO reserved_pool VALUES ('pother', 1, 'Math')")
        c.commit()
        rows = SD.corpus_rows(c)
        c.close()
        texts = sorted(set(r["text"] for r in rows))
        m = sqlite3.connect(os.path.join(droot, MAIN))
        m.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        m.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, distilled_text TEXT)")
        m.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, struct.pack(">4096f", *([0.0] * 4095 + [1.0]))) for t in texts])
        m.commit()
        m.close()
        arms = {}
        for a in RL.PIN_ARMS:
            fn = EA.cache_file(EA.ARMS[a])
            p = os.path.join(droot, RL.DIR_REL, fn)
            if a == "nomic_raw":
                nc = sqlite3.connect(p)
                nc.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
                nc.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, struct.pack(">768f", *([0.0] * 767 + [1.0]))) for t in texts])
                nc.commit()
                nc.close()
            else:
                with open(p, "wb") as f:
                    f.write(("arm %s\n" % a).encode() * 20)
            arms[a] = {"sha256": sha256_file(p), "file": fn}
        for s in RL.SOURCE_DBS + (RL.FROZEN,):
            with open(os.path.join(droot, s), "wb") as f:
                f.write(b"src " + s.encode())
        pf = os.path.join(tmp, "pins.json")
        with open(pf, "w") as f:
            json.dump({"schema": EA.ARM_PINS_SCHEMA, "arms": arms}, f)
        draws = [SD.draw(rows, s) for s in SD.SALTS]
        SD.write_splits(draws, root=droot, out=lambda s: None)
        with open(os.path.join(ROOT, *SD.BASE_TOML.split("/")), encoding="utf-8") as f:
            base = f.read()
        os.makedirs(os.path.join(droot, *os.path.dirname(SD.BASE_TOML).split("/")), exist_ok=True)
        with open(os.path.join(droot, *SD.BASE_TOML.split("/")), "w", encoding="utf-8", newline="\n") as f:
            f.write(base)
        SD.write_configs([d["pool"] for d in draws], root=droot, out=lambda s: None)
        dec = {"%s_e1sd%d" % (a, k): _blob_lf(os.path.join(droot, *(SD.TOML_REL % (a, k)).split("/"))) for k in (1, 2, 3) for a in SD.ARMS}
        sb = {k: _blob_lf(os.path.join(droot, *(SD.SPLIT_REL % k).split("/"))) for k in (1, 2, 3)}
        sp = {k: draws[k - 1]["pool"] for k in (1, 2, 3)}
        bk = os.path.join(tmp, "backup")
        os.makedirs(bk)
        for cc in CACHES:
            shutil.copyfile(os.path.join(droot, cc), os.path.join(bk, cc))
        return dict(tmp=tmp, droot=droot, pf=pf, bk=bk, draws=draws, dec=dec, sb=sb, sp=sp, rows=rows, texts=texts, arms=arms)

    def engine_write(F, k, short=False, qcount=None):
        """The engine's ReservedPool.save for split k on the live corpus DB (rows of judgeable ids + meta)."""
        d = F["draws"][k - 1]
        j = pool_guard.judgeable(d["ids"])
        c = sqlite3.connect(os.path.join(F["droot"], CORPUS))
        first = True
        for dom, qs in j.items():
            for q in qs:
                if short and first:
                    first = False
                    continue
                c.execute("INSERT OR IGNORE INTO reserved_pool VALUES (?, ?, ?)", (d["pool"], q, dom))
        c.execute("INSERT OR REPLACE INTO reserved_pool_meta VALUES (?, 'mmlu-pro', 402, NULL, NULL, ?, ?, ?, ?)",
                  (d["pool"], ",".join(sorted(j)), qcount if qcount is not None else sum(len(v) for v in j.values()), len(j),
                   int(time.time() * 1000)))
        c.commit()
        c.close()

    def fake_rundir(F, arm, k, **kw):
        cfgp = os.path.join(F["droot"], *(SD.TOML_REL % (arm, k)).split("/"))
        with open(cfgp, encoding="utf-8") as f:
            txt = f.read()
        SD.fake_run_dir(SD.run_dir_of(arm, k, F["droot"]), arm, k, F["draws"][k - 1], txt,
                        nomic_pin=F["arms"]["nomic_raw"]["sha256"], **kw)

    calls = []

    def go(F, build, dry=False, launch=None, rl=None, backup=None):
        saved = (dict(DECLARED), dict(SPLIT_BLOBS), dict(SPLIT_POOLS), globals()["N_CORPUS_TEXTS"])
        DECLARED.update(F["dec"])
        SPLIT_BLOBS.update(F["sb"])
        SPLIT_POOLS.update(F["sp"])
        globals()["N_CORPUS_TEXTS"] = len(F["texts"])
        lines = []
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    rc = run(build, backup or F["bk"], dry_run=dry, root=F["droot"], droot=F["droot"], pins_file=F["pf"],
                             launch=launch or (lambda c, w: calls.append(c) or 0),
                             rl_run=rl or (lambda *a, **k: (None if k.get("dry_run") else calls.append(a)) or 0), out=lines.append, run_id="t%d" % len(calls),
                             pids=lambda: [])
                except SystemExit as e:                     # Refusal, SD.Refused and pool_guard's SystemExit(message)
                    print("REFUSAL: %s" % e)
                    rc = "REFUSED"
        finally:
            DECLARED.clear(); DECLARED.update(saved[0])
            SPLIT_BLOBS.clear(); SPLIT_BLOBS.update(saved[1])
            SPLIT_POOLS.clear(); SPLIT_POOLS.update(saved[2])
            globals()["N_CORPUS_TEXTS"] = saved[3]
        return rc, "\n".join(lines) + "\n" + buf.getvalue()

    def make_tail(F, sql):
        """The live corpus DB gets a REAL WAL tail: rows written with autocheckpoint off, both files copied while the writer is
        open (closing it would checkpoint), so the main file lacks them and the -wal holds them."""
        live = os.path.join(F["droot"], CORPUS)
        src = os.path.join(F["tmp"], "tail_src.db")
        shutil.copyfile(live, src)
        c = sqlite3.connect(src)
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA wal_autocheckpoint=0")
        c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        c.execute(sql)
        c.commit()
        shutil.copyfile(src, live)
        shutil.copyfile(src + "-wal", live + "-wal")
        c.close()

    def refresh_backup(F):
        for cc in CACHES:
            for s in ("", "-wal"):
                if os.path.exists(os.path.join(F["bk"], cc + s)):
                    os.remove(os.path.join(F["bk"], cc + s))
                if os.path.isfile(os.path.join(F["droot"], cc + s)) and (s == "" or os.path.getsize(os.path.join(F["droot"], cc + s)) > 0):
                    shutil.copyfile(os.path.join(F["droot"], cc + s), os.path.join(F["bk"], cc + s))

    # T2b first: the N build of split 1 (fake rl_run = the engine's split-time write + a run dir)
    F = fixture()
    seen = []

    def rl_n1(arm, cfg, dry_run=False, **kw):
        seen.append((arm, cfg, dry_run))
        if not dry_run:
            engine_write(F, 1)
            fake_rundir(F, "N", 1)
        return 0
    rc, text = go(F, "N_e1sd1", rl=rl_n1)
    ok(rc == 0 and "ADMITTED: this build's own pool" in text and ("pool:%s:rows" % F["sp"][1]) in text,
       "T2b N_e1sd1: the new pool's rows admitted by name; rc 0")
    ok(seen == [("nomic_raw", "experiment_configs/e1_split_draws/N_e1sd1.toml", False)], "T2b rl_run got nomic_raw + the declared config")
    ok("(6) POOL %s FRESH" % F["sp"][1] in text and "(10) RUN DIR" in text and "snapshot SNAP_N1" in text, "T2b FRESH before, run dir checked")
    ok("misses 0" in text, "T2b coverage misses 0 printed")
    for k in (2, 3):
        refresh_backup(F)
        def rl_nk(arm, cfg, dry_run=False, k=k, **kw):
            if not dry_run:
                engine_write(F, k)
                fake_rundir(F, "N", k)
            return 0
        rc, text = go(F, "N_e1sd%d" % k, rl=rl_nk)
        ok(rc == 0, "T2b N_e1sd%d rc 0" % k)
    # T1 Q dry-run
    refresh_backup(F)
    del calls[:]
    rc, text = go(F, "Q_e1sd1", dry=True)
    ok(rc == 0 and "-PjvmThreads=12" in text and "ratings_e1sd.db" in text and "Q_e1sd1.toml" in text and "embeddingCacheFile" not in text
       and "DRY RUN (Q)" in text and calls == [], "T1 Q dry-run admitted: 12 threads, own ranking DB, no embedding property, no launch")
    ok("(6) POOL %s RECORDED" % F["sp"][1] in text, "T1 pool RECORDED before Q_e1sd1 (pool_guard passed)")
    # T2 Q build
    def jvm_q1(cmd, cwd):
        engine_write(F, 1)
        fake_rundir(F, "Q", 1)
        return 0
    rc, text = go(F, "Q_e1sd1", launch=jvm_q1)
    ok(rc == 0 and "snapshot SNAP_Q1" in text and "P' unchanged" in text, "T2 Q_e1sd1 build: rc 0, run dir snapshot SNAP_Q1")
    shutil.rmtree(F["tmp"], ignore_errors=True)

    # T3 PIN BREACHes (each on a fresh fixture, as the N_e1sd1 build or a Q build)
    def n_fixture_with(mut):
        F = fixture()
        def rl(arm, cfg, dry_run=False, **kw):
            if not dry_run:
                mut(F)
                fake_rundir(F, "N", 1)
            return 0
        return F, go(F, "N_e1sd1", rl=rl)

    def other_table(F):
        engine_write(F, 1)
        c = sqlite3.connect(os.path.join(F["droot"], CORPUS)); c.execute("UPDATE eval_results SET v = 'b'"); c.commit(); c.close()

    def other_pool(F):
        engine_write(F, 1)
        c = sqlite3.connect(os.path.join(F["droot"], CORPUS)); c.execute("INSERT INTO reserved_pool VALUES ('pother', 2, 'Math')"); c.commit(); c.close()

    def other_e1sd(F):
        engine_write(F, 1)
        engine_write(F, 2)
    for what, mut, needle in (("another table", other_table, "eval_results"), ("another pool's rows", other_pool, "reserved_pool "),
                              ("the build's pool one id short", lambda F: engine_write(F, 1, short=True), "pool:"),
                              ("the meta question_count wrong", lambda F: engine_write(F, 1, qcount=1), ":meta"),
                              ("another e1sd pool written", other_e1sd, "pool:")):
        F, (rc, text) = n_fixture_with(mut)
        ok(rc == "REFUSED" and "PIN BREACH: unexpected table change" in text and needle in text.split("PIN BREACH")[-1],
           "T3 %s: PIN BREACH naming %s" % (what, needle.strip()))
        shutil.rmtree(F["tmp"], ignore_errors=True)
    # a build whose run dir shows an engine closure (closedByContent 3): REFUSED by the run-dir check (10)
    F = fixture()
    def rl_closed(arm, cfg, dry_run=False, **kw):
        if not dry_run:
            engine_write(F, 1)
            fake_rundir(F, "N", 1, closed=3)
        return 0
    rc, text = go(F, "N_e1sd1", rl=rl_closed)
    ok(rc == "REFUSED" and "[POOL] line" in text and "(10) RUN DIR" not in text, "T3 a run dir with closedByContent 3: REFUSED at (10)")
    shutil.rmtree(F["tmp"], ignore_errors=True)
    # Q-side breaches: main cache blob, a P' member
    for what, kind in (("the main cache's embeddings blob", "main"), ("a P' member (snapshots_frozen.db)", "p")):
        F = fixture()
        for k in (1, 2, 3):
            engine_write(F, k)
            fake_rundir(F, "N", k)
        refresh_backup(F)
        def jvm_bad(cmd, cwd, F=F, kind=kind):
            engine_write(F, 1)
            fake_rundir(F, "Q", 1)
            if kind == "main":
                m = sqlite3.connect(os.path.join(F["droot"], MAIN))
                m.execute("UPDATE embeddings SET vector = ? WHERE rowid = 1", (struct.pack(">4096f", *([1.0] + [0.0] * 4095)),))
                m.commit(); m.close()
            else:
                with open(os.path.join(F["droot"], RL.FROZEN), "ab") as f:
                    f.write(b"!")
            return 0
        rc, text = go(F, "Q_e1sd1", launch=jvm_bad)
        ok(rc == "REFUSED" and "PIN BREACH" in text and (("main embeddings" in text) if kind == "main" else ("protected file" in text)),
           "T3 Q build changing %s: PIN BREACH" % what)
        shutil.rmtree(F["tmp"], ignore_errors=True)

    # T4 a WAL tail: rows only in the -wal must be seen through the scratch copy
    F = fixture()
    src = os.path.join(F["tmp"], "w.db")
    c = sqlite3.connect(src)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA wal_autocheckpoint=0")
    c.execute("CREATE TABLE t (a INTEGER PRIMARY KEY)")
    c.commit()
    c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    c.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(50)])
    c.commit()
    walsz = os.path.getsize(src + "-wal")
    dst = os.path.join(F["tmp"], "live.db")
    shutil.copyfile(src, dst)
    shutil.copyfile(src + "-wal", dst + "-wal")
    c.close()
    before = (sha256_file(dst), sha256_file(dst + "-wal"))
    lines = []
    vp, vd, lab = view_path(dst, os.path.join(F["tmp"], "scr"), lines.append)
    v = table_view(vp)
    ok(walsz > 0 and v["t"][1] == 50 and lab == "a checkpointed scratch copy", "T4 the scratch-copy view sees the 50 rows held only in the -wal")
    ok((sha256_file(dst), sha256_file(dst + "-wal")) == before, "T4 the originals are unchanged byte for byte")
    shutil.rmtree(vd)
    ok(not os.path.exists(vd), "T4 the scratch dir is removable / removed")
    shutil.rmtree(F["tmp"], ignore_errors=True)

    # T5 pre-launch refusals
    F = fixture()
    del calls[:]
    cases = []
    cases.append(("undeclared build", go(F, "X_e1sd1"), "(DECLARED)"))
    cfgp = os.path.join(F["droot"], *(SD.TOML_REL % ("N", 1)).split("/"))
    orig = open(cfgp, encoding="utf-8").read()
    with open(cfgp, "a", encoding="utf-8") as f:
        f.write("# x\n")
    cases.append(("tampered TOML", go(F, "N_e1sd1"), "(DECLARED)"))
    with open(cfgp, "w", encoding="utf-8", newline="\n") as f:
        f.write(orig)
    spp = os.path.join(F["droot"], *(SD.SPLIT_REL % 3).split("/"))
    origs = open(spp, "rb").read()
    with open(spp, "ab") as f:
        f.write(b" ")
    cases.append(("tampered split file (the last)", go(F, "N_e1sd3"), "(DECLARED)"))
    with open(spp, "wb") as f:
        f.write(origs)
    cases.append(("Q before the N builds", go(F, "Q_e1sd1"), "(ORDER)"))
    os.makedirs(SD.run_dir_of("Q", 3, F["droot"]))
    cases.append(("N after a Q run dir (the last)", go(F, "N_e1sd1"), "(ORDER)"))
    shutil.rmtree(SD.run_dir_of("Q", 3, F["droot"]))
    c = sqlite3.connect(os.path.join(F["bk"], MAIN)); c.execute("CREATE TABLE z (a)"); c.commit(); c.close()
    cases.append(("stale backup (main)", go(F, "N_e1sd1"), "(BACKUP)"))
    refresh_backup(F)
    cases.append(("no backup dir", go(F, "N_e1sd1", backup=os.path.join(F["tmp"], "nope")), "(BACKUP)"))
    # a non-empty live -wal beside the corpus DB (a real tail: rows only in the -wal) without its backup copy
    make_tail(F, "INSERT INTO eval_results VALUES (2, 'b')")
    ok(tail(os.path.join(F["droot"], CORPUS), "-wal") is not None, "T5 fixture: the corpus DB carries a non-empty -wal")
    shutil.copyfile(os.path.join(F["droot"], CORPUS), os.path.join(F["bk"], CORPUS))     # the main file backed up, its -wal NOT
    shutil.copyfile(os.path.join(F["droot"], MAIN), os.path.join(F["bk"], MAIN))
    cases.append(("a live -wal with no backup copy", go(F, "N_e1sd1"), "(BACKUP)"))
    refresh_backup(F)
    rc_w, text_w = go(F, "N_e1sd1", dry=True)
    ok(rc_w == 0 and "checkpointed scratch copy" in text_w, "T4b a live corpus tail: the dry-run reads a checkpointed scratch copy")
    ok(not [x for x in os.listdir(os.path.join(F["droot"], WORK_REL))] if os.path.isdir(os.path.join(F["droot"], WORK_REL)) else True,
       "T4b no scratch dir left behind")
    shutil.rmtree(F["tmp"], ignore_errors=True)
    F = fixture()
    nc = sqlite3.connect(os.path.join(F["droot"], RL.DIR_REL, EA.cache_file(EA.ARMS["nomic_raw"])))
    nc.execute("DELETE FROM embeddings WHERE rowid = (SELECT MAX(rowid) FROM embeddings)")
    nc.commit(); nc.close()
    F["arms"]["nomic_raw"]["sha256"] = sha256_file(os.path.join(F["droot"], RL.DIR_REL, EA.cache_file(EA.ARMS["nomic_raw"])))
    with open(F["pf"], "w") as f:
        json.dump({"schema": EA.ARM_PINS_SCHEMA, "arms": F["arms"]}, f)
    cases.append(("a coverage miss (one nomic vector short)", go(F, "N_e1sd1"), "(5)"))
    shutil.rmtree(F["tmp"], ignore_errors=True)
    F = fixture()
    c = sqlite3.connect(os.path.join(F["droot"], CORPUS)); c.execute("INSERT INTO reserved_pool VALUES (?, 1, 'Math')", (F["sp"][1],)); c.commit(); c.close()
    refresh_backup(F)
    cases.append(("a pool CONFLICT", go(F, "N_e1sd1"), "CONFLICT"))
    shutil.rmtree(F["tmp"], ignore_errors=True)
    F = fixture()
    for k in (1, 2, 3):
        fake_rundir(F, "N", k)
    refresh_backup(F)
    cases.append(("a Q build with the pool FRESH", go(F, "Q_e1sd2"), "FRESH before a split's second build"))
    with open(os.path.join(F["droot"], CORPUS) + "-journal", "wb") as f:
        f.write(b"hot")
    cases.append(("a hot -journal beside the corpus DB", go(F, "N_e1sd1"), "never copied"))
    os.remove(os.path.join(F["droot"], CORPUS) + "-journal")
    for what, (rc, text), needle in cases:
        ok(rc == "REFUSED" and needle in text, "T5 %s: REFUSED %s" % (what, needle))
    ok(calls == [], "T5 no refusal launched anything")
    shutil.rmtree(F["tmp"], ignore_errors=True)

    # T6 verify
    F = fixture()
    for k in (1, 2, 3):
        engine_write(F, k)
    saved = dict(SPLIT_POOLS)
    SPLIT_POOLS.update(F["sp"])
    try:
        lines = []
        ok(verify(F["bk"], root=F["droot"], droot=F["droot"], out=lines.append) == 0, "T6 verify admits the three pools' rows")
        c = sqlite3.connect(os.path.join(F["droot"], CORPUS)); c.execute("UPDATE eval_results SET v = 'z'"); c.commit(); c.close()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                verify(F["bk"], root=F["droot"], droot=F["droot"], out=lines.append)
                r = "admitted"
            except Refusal:
                r = "REFUSED"
        ok(r == "REFUSED" and "eval_results" in buf.getvalue(), "T6 verify REFUSES a changed eval_results table")
        with open(os.path.join(F["droot"], MAIN) + "-wal", "wb") as f:
            f.write(b"x")
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                verify(F["bk"], root=F["droot"], droot=F["droot"], out=lines.append)
                r = "admitted"
            except Refusal:
                r = "REFUSED"
        ok(r == "REFUSED", "T6 verify REFUSES a live tail (CP-1 first)")
    finally:
        SPLIT_POOLS.clear(); SPLIT_POOLS.update(saved)
    shutil.rmtree(F["tmp"], ignore_errors=True)
    print("%s SELFTEST PASSED (%d checks)" % (TAG, n[0]))
    return 0


MUTANTS = (
    ("L01 backup check removed", "    check_backup(backup_dir, droot, out)                                                  # (4)", "    pass"),
    ("L02 backup ignores the -wal", "            if s and not tail(live, \"-wal\"):\n                continue", "            if s:\n                continue"),
    ("L03 declared blob unchecked", "        if got != want:\n            refuse(\"(DECLARED) the %s", "        if False:\n            refuse(\"(DECLARED) the %s"),
    ("L04 order check removed", "    check_order(arm, droot, out)                                                          # (3)", "    pass"),
    ("L05 order: N after Q admitted", "        if q:\n            refuse(\"(ORDER) an N build", "        if False:\n            refuse(\"(ORDER) an N build"),
    ("L06 coverage check removed", "    if miss:\n        refuse(\"(5)", "    if False:\n        refuse(\"(5)"),
    ("L07 Q admitted with a FRESH pool", "    if not first_build and st != \"RECORDED\":", "    if False:"),
    ("L08 view reads the main file despite a tail", "    if not tail(path, \"-wal\"):\n        return path, None, \"the file (no WAL tail)\"",
     "    if True:\n        return path, None, \"the file (no WAL tail)\""),
    ("L09 scratch copy not checkpointed", "        con.execute(\"PRAGMA wal_checkpoint(TRUNCATE)\")\n    finally:\n        con.close()\n    if tail(dst",
     "        pass\n    finally:\n        con.close()\n    if tail(dst"),
    ("L10 corpus comparison removed", "        bad = compare_views(\"corpus\", before_c, after_c, admitted, out)", "        bad = []"),
    ("L11 every change admitted", "        if b != a:\n            bad.append(\"%s %s %s -> %s\" % (label, key, b, a))", "        pass"),
    ("L12 admitted pool not compared with the file", "            if a != admitted[key]:", "            if False:"),
    ("L13 the e1sd pools' rows not split out of the pool tables", "            if t in POOL_TABLES and pools:", "            if False:"),
    ("L14 main comparison removed (Q)", "            bad += compare_views(\"main\", before_m, table_view(mview), {}, out)", "            pass"),
    ("L15 P' re-hash removed (Q)", "            breach = sorted(kk for kk in members if before_p[kk] != after_p[kk])", "            breach = []"),
    ("L16 run-dir check removed", "        got = SD.check_run_dir(SD.run_dir_of(arm, k, droot), arm, k, d, DECLARED[build],",
     "        got = dict(snapshot=\"SNAP_%s%d\" % (arm, k), pool_line=(\"\", \"\", \"\")) or SD.check_run_dir(SD.run_dir_of(arm, k, droot), arm, k, d, DECLARED[build],"),
    ("L17 hot journal admitted", "    if tail(path, \"-journal\"):\n        refuse(", "    if False:\n        refuse("),
    ("L18 thread cap dropped", "\"-PjvmThreads=%d\" % JVM_THREADS,", ""),
    ("L19 verify comparison removed", "        bad += compare_views(c, table_view(bk, pools), table_view(live, pools), admitted if c == CORPUS else {}, out)", "        pass"),
    ("L20 blobs not hashed", "                h.update(bytes(v))", "                pass"),
)


def run_mutants():
    import tempfile
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    head, sep, tail_ = src.partition("\nMUTANTS = (")
    killed = 0
    for name, a, b in MUTANTS:
        if head.count(a) != 1:
            print("%s MUTANT %s: anchor found %d times (must be 1)" % (TAG, name, head.count(a)))
            return 2
        p = os.path.join(HERE, "_mut_e1sd_launch.py")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(head.replace(a, b) + sep + tail_)
        try:
            r = subprocess.run([sys.executable, p, "--selftest", "--quiet"], capture_output=True, text=True)
        finally:
            os.remove(p)
        dead = r.returncode != 0
        killed += dead
        why = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["?"])[-1][:120] if dead else "SURVIVED"
        print("%s MUTANT %-52s %s  (%s)" % (TAG, name, "KILLED" if dead else "SURVIVED", why))
    print("%s MUTANTS %d of %d KILLED" % (TAG, killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--build")
    ap.add_argument("--backup-dir")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(quiet=a.quiet)
    if a.mutants:
        return run_mutants()
    if a.plan:
        s = __doc__
        print(s[s.index("THE LAUNCH PLAN (from"):s.index("SELFTEST / MUTANTS:")])
        return 0
    try:
        if a.verify:
            return verify(a.backup_dir)
        if not a.build:
            refuse("--build is required (one of %s)" % sorted(DECLARED))
        return run(a.build, a.backup_dir, dry_run=a.dry_run)
    except SystemExit as e:                                 # Refusal, SD.Refused, pool_guard's SystemExit(message): rc 2
        if not isinstance(e.code, int):
            print("%s REFUSED: %s" % (TAG, e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
