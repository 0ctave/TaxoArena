"""LCB-D9-BYTE-INERTNESS operator helper 1/3: precondition V1 and the input copies V2 (programme L18662-L18872, leg B
re-pinned L19241-L19271). Reads the MAIN checkout's ag_news_smoke_cache_v1.db (+ -wal) and embeddings_cache.db BY FILE
COPY ONLY (never opened by SQLite in place); checkpoints only the scratch COPY; copies one byte-identical file of each into
both leg worktrees; refuses on any mismatch. Zero calls. Writes <stage>/d9_prep.txt.

usage: python d9_prep.py <main checkout> <legA root> <legB root> <stage dir>
"""
import hashlib, os, shutil, sqlite3, subprocess, sys

A_SHA, B_SHA = "a62c7e0ddb7a47f6ba691450c0cdd643cbdbe76d", "6b9fc7c278121868cb79477a9e12803b36830a3a"
TOML = "experiment_configs/topic_partition/ag_news_smoke_s42.toml"
TOML_BLOB = "efd82bdacc06144439280d3b76923d38527bd7ae"
FOUR = sorted(["src/main/kotlin/taxonomy/config/TaxonomyConfig.kt", "src/main/kotlin/taxonomy/dataset/CorpusRegistry.kt",
               "src/main/kotlin/taxonomy/dataset/CorpusSource.kt", "src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt"])
B_BLOBS = {"src/main/kotlin/taxonomy/config/TaxonomyConfig.kt": "2825b12d", "src/main/kotlin/taxonomy/dataset/CorpusRegistry.kt": "5b1bbb3a",
           "src/main/kotlin/taxonomy/dataset/CorpusSource.kt": "817b1417", "src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.kt": "a2a85c03"}
AG_BASE = {"ag_news_smoke_cache_v1.db": (1622016, "7cf2082f92e20c5580520c1ca63c5655e2582c173ed9605cb0179a9ad3b8fd54"),
           "ag_news_smoke_cache_v1.db-wal": (206032, "7eea2abd89feb7aeffc7c90be37987f87d6f81803f0f8919673527c711d8c306")}
LOG = []


def say(s):
    LOG.append(s)
    print(s, flush=True)


def die(s):
    say("[D9-PREP] REFUSED: " + s)
    raise SystemExit(1)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 22), b""):
            h.update(ch)
    return h.hexdigest()


def git(root, *a):
    r = subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True)
    if r.returncode != 0:
        die("git -C %s %s failed: %s" % (root, " ".join(a), r.stderr.strip()[:200]))
    return r.stdout.strip()


def stat(p):
    s = os.stat(p)
    return s.st_size, s.st_mtime_ns


def main(main_root, la, lb, stage):
    # V1: the precondition
    diff = sorted(git(main_root, "diff", "--name-only", A_SHA, B_SHA, "--", "src/main", "build.gradle.kts", "settings.gradle.kts",
                      "gradle.properties", "gradle/", "config/").splitlines())
    say("[V1] git diff --name-only A B -- src/main build files config: %s" % diff)
    if diff != FOUR:
        die("the A..B diff is not exactly the four files")
    for c in (A_SHA, B_SHA, "main"):
        b = git(main_root, "rev-parse", "%s:%s" % (c, TOML))
        say("[V1] %s:%s = %s" % (c[:7], TOML, b))
        if b != TOML_BLOB:
            die("the arm TOML blob differs at %s" % c)
    moved = git(main_root, "diff", "--name-only", A_SHA, "main", "--", "src/main", "build.gradle.kts", "settings.gradle.kts",
                "gradle.properties", "gradle/", "config/")
    say("[V1] main moved since A on these paths: %s" % (moved.splitlines() or "none"))
    if moved:
        die("main's src/main moved since A: re-base A = main HEAD per V1 and re-review")
    for f, b in B_BLOBS.items():
        got = git(main_root, "rev-parse", "%s:%s" % (B_SHA, f))
        if not got.startswith(b):
            die("B blob of %s is %s, not %s" % (f, got, b))
    # the leg worktrees: HEAD, a .git FILE, no pre-existing caches or outputs
    for leg, root, want in (("A", la, A_SHA), ("B", lb, B_SHA)):
        head = git(root, "rev-parse", "HEAD")
        st = git(root, "status", "--short")
        say("[LEG %s] %s HEAD %s; .git is a file: %s; status lines: %d" % (leg, root, head, os.path.isfile(os.path.join(root, ".git")),
                                                                     len(st.splitlines())))
        if head != want or not os.path.isfile(os.path.join(root, ".git")) or st:
            die("leg %s worktree is not a clean detached checkout of %s" % (leg, want))
        for n in ("embeddings_cache.db", "ag_news_smoke_cache_v1.db", "snapshots.db", "ratings_d9_%s.db" % leg, "build"):
            for s in ("", "-wal", "-shm", "-journal"):
                if os.path.exists(os.path.join(root, n + s)):
                    die("leg %s already holds %s (a fresh worktree has none; R5 of the LCB rerun: run nothing inside it)" % (leg, n + s))
        if os.path.exists(os.path.join(root, "experiment_results", "topic_partition", "ag_news_smoke_s42")):
            die("leg %s already holds the arm's outputDir" % leg)
    copies(main_root, la, lb, stage)


def copies(main_root, la, lb, stage):
    # main inputs: baseline, file copy only
    os.makedirs(stage, exist_ok=False)
    main_emb = os.path.join(main_root, "embeddings_cache.db")
    for s in ("-wal", "-journal"):
        p = main_emb + s
        if os.path.exists(p) and os.path.getsize(p) > 0:
            die("main %s is non-empty; a file copy would miss its tail" % p)
    before = {}
    for n, (size, want) in AG_BASE.items():
        p = os.path.join(main_root, n)
        got = sha(p)
        before[n] = (stat(p), got)
        say("[V2] main %s size %d sha256 %s (INPUT BASELINE %s)" % (n, os.path.getsize(p), got, "EQUAL" if (got == want and os.path.getsize(p) == size) else "DIFFERS"))
        if got != want or os.path.getsize(p) != size:
            die("main %s differs from the registered INPUT BASELINE" % n)
        shutil.copyfile(p, os.path.join(stage, n))
    emb_sha = sha(main_emb)
    before["embeddings_cache.db"] = (stat(main_emb), emb_sha)
    say("[V2] main embeddings_cache.db size %d sha256 %s" % (os.path.getsize(main_emb), emb_sha))
    shutil.copyfile(main_emb, os.path.join(stage, "embeddings_cache.db"))
    # checkpoint the AG COPY only (the -wal folded into the DB file); then no sidecar may remain non-empty
    agc = os.path.join(stage, "ag_news_smoke_cache_v1.db")
    con = sqlite3.connect(agc)
    say("[V2] checkpoint of the COPY: %s" % (con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone(),))
    con.close()
    for s in ("-wal", "-journal"):
        if os.path.exists(agc + s) and os.path.getsize(agc + s) > 0:
            die("the AG copy still has a non-empty %s after the checkpoint" % s)
    for s in ("-wal", "-shm"):
        if os.path.exists(agc + s):
            os.remove(agc + s)          # the COPY's empty sidecars only
    # declared before the run: the reserved_pool* schema and the dropped timestamp column
    con = sqlite3.connect("file:%s?mode=ro" % agc.replace("\\", "/"), uri=True)
    for t in ("reserved_pool", "reserved_pool_meta"):
        say("[C1-SCHEMA] %s columns %s" % (t, [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]))
    con.close()
    say("[C1-SCHEMA] DECLARED DROP (clock-bearing): reserved_pool_meta.created_at; nothing else is dropped")
    for s in ("-wal", "-shm"):
        p = agc + s
        if os.path.exists(p):
            if s == "-wal" and os.path.getsize(p) > 0:
                die("the AG copy's -wal became non-empty after a read-only open")
            os.remove(p)                # the scratch COPY's empty sidecars only, never main's
    staged = {n: sha(os.path.join(stage, n)) for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db")}
    if staged["embeddings_cache.db"] != emb_sha:
        die("the embeddings copy differs from main's file")
    for leg, root in (("A", la), ("B", lb)):
        for n, h in staged.items():
            dst = os.path.join(root, n)
            shutil.copyfile(os.path.join(stage, n), dst)
            got = sha(dst)
            say("[V2] leg %s %s sha256 %s" % (leg, n, got))
            if got != h:
                die("leg %s copy of %s differs from the staged file" % (leg, n))
    # main unchanged by the copies
    for n, (st0, h0) in before.items():
        p = os.path.join(main_root, n)
        if stat(p) != st0 or sha(p) != h0:
            die("main %s changed during the copy" % n)
    say("[V2] PASS: both legs hold byte-identical copies (ag %s / emb %s); main inputs unchanged (size, mtime, sha256)"
        % (staged["ag_news_smoke_cache_v1.db"][:16], staged["embeddings_cache.db"][:16]))
    with open(os.path.join(stage, "d9_prep.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:5])
