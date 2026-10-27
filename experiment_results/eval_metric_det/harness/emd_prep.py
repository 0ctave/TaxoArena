"""EVAL-METRIC-DETERMINISM operator helper: V1 (the diff scope), V2 (the input copies, five legs), the L6 pins and V9
(registration docs/judge_v2_program.md L20311-L20389, 55a6ce1; HYGIENE, INSTRUMENT, VALIDITY V1 / V2 / V9). Derived from
d9b_prep.py (sha256-lf16:8cc3eb84e92aa00a), which is untouched. Zero calls. Reads main's AG cache (+ -wal) and
embeddings_cache.db BY FILE COPY ONLY for the legs; checkpoints only the scratch COPY. The `pins` mode opens main's
embeddings_cache.db and snapshots.db read-only (mode=ro&immutable=1, then mode=ro: the two views of the L6 pins; the -shm
mtimes are EXPECTED to move under the mode=ro view, as ruled for D9b D1; content decides).

MODES
  python emd_prep.py pins <main checkout> <out json>
      main's L6 pins: size, mtime, sha256 of ag_news_smoke_cache_v1.db (+ -wal, -shm), embeddings_cache.db (+ -wal, -shm),
      snapshots.db (+ -wal, -shm); per-table row digests of embeddings_cache.db and snapshots.db in both views. Write-once.
  python emd_prep.py pre <main checkout> <P1 root> <R1 root> <R2 root> <P2 root> <R3 root> <$ST>
      V1: git diff --name-only BASE FIX -- src/main build.gradle.kts settings.gradle.kts gradle.properties gradle/ config/
      = exactly the three declared files, at the pinned FIX blobs; --name-status BASE FIX -- src/test = exactly
      "A <the new test>" at its pinned blob; --name-only BASE FIX -- experiment_configs tools = empty; the arm TOML = efd82bda
      at BASE, FIX and main; main's src/main / build files / config unchanged since BASE. Each leg root: HEAD = its assigned
      commit, a .git FILE, clean status, no DB, no build/, no outputDir. V2: main's AG files equal the D9b INPUT BASELINE;
      main's embeddings_cache.db equals its pin; one checkpointed AG copy and one embeddings copy are placed in all five
      legs, byte-identical (expected e3415684... / 52229e1e...); main unchanged by the copies. Creates $ST (must not exist)
      and $ST/classlists; writes $ST/emd_prep.txt and $ST/emd_prep.json (v1, v2, roots, copy shas). Exit 0 / 1 (refused).
  python emd_prep.py post <before pins json> <after pins json> <$ST>
      V9: embeddings_cache.db and snapshots.db equal in file sha256, size and both table-digest views; the AG DB and -wal
      unchanged in size, mtime and sha256; the -shm files printed (not deciding). Writes $ST/emd_post.json (v9). Exit 0 / 1.
"""
import hashlib, os, shutil, sqlite3, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emd_common as E  # noqa: E402

VERSION = "emd_prep-1"
LOG = []
PIN_FILES = ["ag_news_smoke_cache_v1.db", "ag_news_smoke_cache_v1.db-wal", "ag_news_smoke_cache_v1.db-shm",
             "embeddings_cache.db", "embeddings_cache.db-wal", "embeddings_cache.db-shm",
             "snapshots.db", "snapshots.db-wal", "snapshots.db-shm"]
PIN_DBS = ["embeddings_cache.db", "snapshots.db"]
V1_PATHS = ["src/main", "build.gradle.kts", "settings.gradle.kts", "gradle.properties", "gradle/", "config/"]


def say(s):
    LOG.append(s)
    print(s, flush=True)


class Die(Exception):
    pass


def die(s):
    say("[EMD-PREP] REFUSED: " + s)
    raise Die(s)


def git(root, *a):
    r = subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True)
    if r.returncode != 0:
        die("git -C %s %s failed: %s" % (root, " ".join(a), r.stderr.strip()[:200]))
    return r.stdout.strip()


def stat(p):
    s = os.stat(p)
    return s.st_size, s.st_mtime_ns


def views(p):
    out = {}
    u = os.path.abspath(p).replace("\\", "/")
    for view in ("mode=ro&immutable=1", "mode=ro"):
        con = sqlite3.connect("file:%s?%s" % (u, view), uri=True)
        try:
            d = {}
            for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall():
                h, n = hashlib.sha256(), 0
                for r in con.execute('SELECT * FROM "%s" ORDER BY rowid' % t):
                    h.update(repr(r).encode())
                    n += 1
                d[t] = [n, h.hexdigest()[:16]]
            out[view] = d
        finally:
            con.close()
    return out


def pins(main_root, out):
    if os.path.exists(out):
        die("%s exists (write-once)" % out)
    res = {"version": VERSION, "files": {}, "views": {}}
    for n in PIN_FILES:
        p = os.path.join(main_root, n)
        if os.path.exists(p):
            size, mt = stat(p)
            res["files"][n] = [size, mt, E.sha(p)]
            say("[PIN] %-34s size %d mtime_ns %d sha256 %s" % (n, size, mt, res["files"][n][2]))
        else:
            res["files"][n] = None
            say("[PIN] %-34s absent" % n)
    for n in PIN_DBS:
        p = os.path.join(main_root, n)
        res["views"][n] = views(p) if os.path.exists(p) else None
        for v, d in (res["views"][n] or {}).items():
            say("[PIN %s] %s %s" % (v, n, d))
    E.write_json_once(out, res)
    return 0


def pre(main_root, roots, stage):
    if os.path.exists(stage):
        die("stage dir %s exists (created here, never by hand)" % stage)
    # V1
    diff = sorted(git(main_root, "diff", "--name-only", E.BASE, E.FIX, "--", *V1_PATHS).splitlines())
    say("[V1] git diff --name-only BASE FIX -- %s: %s" % (" ".join(V1_PATHS), diff))
    if diff != sorted(E.FIX_SRC):
        die("the BASE..FIX src/main / build / config diff is not exactly the three declared files")
    for f, b in E.FIX_SRC.items():
        got = git(main_root, "rev-parse", "%s:%s" % (E.FIX, f))
        say("[V1] FIX:%s = %s" % (f, got))
        if got != b:
            die("FIX blob of %s is %s, not the pin %s" % (f, got, b))
    tst = git(main_root, "diff", "--name-status", E.BASE, E.FIX, "--", "src/test").splitlines()
    say("[V1] git diff --name-status BASE FIX -- src/test: %s" % tst)
    if [ln.split(None, 1) for ln in tst] != [["A", E.TEST_PATH]]:
        die("the src/test diff is not exactly the new test file (status A)")
    got = git(main_root, "rev-parse", "%s:%s" % (E.FIX, E.TEST_PATH))
    if got != E.TEST_BLOB:
        die("FIX blob of the test is %s, not the pin %s" % (got, E.TEST_BLOB))
    other = git(main_root, "diff", "--name-only", E.BASE, E.FIX, "--", "experiment_configs", "tools")
    say("[V1] git diff --name-only BASE FIX -- experiment_configs tools: %s" % (other.splitlines() or "none"))
    if other:
        die("experiment_configs / tools differ between BASE and FIX")
    for c in (E.BASE, E.FIX, "main"):
        b = git(main_root, "rev-parse", "%s:%s" % (c, E.TOML))
        say("[V1] %s:%s = %s" % (c[:7], E.TOML, b))
        if b != E.TOML_BLOB:
            die("the arm TOML blob differs at %s" % c)
    moved = git(main_root, "diff", "--name-only", E.BASE, "main", "--", *V1_PATHS)
    say("[V1] main moved since BASE on these paths: %s" % (moved.splitlines() or "none"))
    if moved:
        die("main's src/main / build files / config moved since BASE: a re-run against a new BASE (registration: merge rule)")
    say("[V1] PASS")
    for leg in E.LEGS:
        root = roots[leg]
        head = git(root, "rev-parse", "HEAD")
        st = git(root, "status", "--short")
        say("[LEG %s] %s HEAD %s; .git is a file: %s; status lines: %d" % (leg, root, head,
                                                                     os.path.isfile(os.path.join(root, ".git")), len(st.splitlines())))
        if head != E.COMMIT[leg] or not os.path.isfile(os.path.join(root, ".git")) or st:
            die("leg %s worktree is not a clean detached checkout of %s" % (leg, E.COMMIT[leg]))
        for n in ("embeddings_cache.db", "ag_news_smoke_cache_v1.db", "snapshots.db", "ratings_emd_%s.db" % leg, "build"):
            for s in ("", "-wal", "-shm", "-journal"):
                if os.path.exists(os.path.join(root, n + s)):
                    die("leg %s already holds %s (a fresh worktree has none)" % (leg, n + s))
        if os.path.exists(os.path.join(root, E.OUT)):
            die("leg %s already holds the arm's outputDir" % leg)
    if len(set(os.path.normcase(os.path.abspath(r)) for r in roots.values())) != 5:
        die("the five leg roots are not five distinct directories")
    # V2
    os.makedirs(stage)
    main_emb = os.path.join(main_root, "embeddings_cache.db")
    for s in ("-wal", "-journal"):
        p = main_emb + s
        if os.path.exists(p) and os.path.getsize(p) > 0:
            die("main %s is non-empty; a file copy would miss its tail" % p)
    before = {}
    for n, (size, want) in E.AG_BASE.items():
        p = os.path.join(main_root, n)
        got = E.sha(p)
        before[n] = (stat(p), got)
        eq = got == want and os.path.getsize(p) == size
        say("[V2] main %s size %d sha256 %s (INPUT BASELINE %s)" % (n, os.path.getsize(p), got, "EQUAL" if eq else "DIFFERS"))
        if not eq:
            die("main %s differs from the INPUT BASELINE" % n)
        shutil.copyfile(p, os.path.join(stage, n))
    emb_sha = E.sha(main_emb)
    before["embeddings_cache.db"] = (stat(main_emb), emb_sha)
    eq = emb_sha == E.EMB_BASE[1] and os.path.getsize(main_emb) == E.EMB_BASE[0]
    say("[V2] main embeddings_cache.db size %d sha256 %s (pin %s)" % (os.path.getsize(main_emb), emb_sha, "EQUAL" if eq else "DIFFERS"))
    if not eq:
        die("main embeddings_cache.db differs from its pin")
    shutil.copyfile(main_emb, os.path.join(stage, "embeddings_cache.db"))
    agc = os.path.join(stage, "ag_news_smoke_cache_v1.db")
    con = sqlite3.connect(agc)
    say("[V2] checkpoint of the COPY: %s" % (con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone(),))
    con.close()
    for s in ("-wal", "-journal"):
        if os.path.exists(agc + s) and os.path.getsize(agc + s) > 0:
            die("the AG copy still has a non-empty %s after the checkpoint" % s)
    for s in ("-wal", "-shm"):
        if os.path.exists(agc + s):
            os.remove(agc + s)          # the scratch COPY's empty sidecars only
    staged = {n: E.sha(os.path.join(stage, n)) for n in ("ag_news_smoke_cache_v1.db", "embeddings_cache.db")}
    say("[V2] staged copies: ag %s (expected %s), emb %s" % (staged["ag_news_smoke_cache_v1.db"], E.AG_COPY_SHA,
                                                               staged["embeddings_cache.db"]))
    if staged["ag_news_smoke_cache_v1.db"] != E.AG_COPY_SHA or staged["embeddings_cache.db"] != E.EMB_BASE[1]:
        die("a staged copy differs from its expected value")
    for leg in E.LEGS:
        for n, h in staged.items():
            dst = os.path.join(roots[leg], n)
            shutil.copyfile(os.path.join(stage, n), dst)
            got = E.sha(dst)
            say("[V2] leg %s %s sha256 %s" % (leg, n, got))
            if got != h:
                die("leg %s copy of %s differs from the staged file" % (leg, n))
    for n, (st0, h0) in before.items():
        p = os.path.join(main_root, n)
        if stat(p) != st0 or E.sha(p) != h0:
            die("main %s changed during the copy" % n)
    say("[V2] PASS: all five legs (%s) hold byte-identical copies (ag %s / emb %s); main inputs unchanged (size, mtime, sha256)"
        % (", ".join(E.LEGS), staged["ag_news_smoke_cache_v1.db"][:16], staged["embeddings_cache.db"][:16]))
    os.makedirs(os.path.join(stage, "classlists"))
    E.write_json_once(os.path.join(stage, "emd_prep.json"), {"version": VERSION, "v1": True, "v2": True, "roots": roots,
                                                             "copies": staged, "base": E.BASE, "fix": E.FIX})
    E.write_once(os.path.join(stage, "emd_prep.txt"), "\n".join(LOG) + "\n")
    return 0


def post(before_p, after_p, stage):
    out = os.path.join(stage, "emd_post.json")
    if os.path.exists(out):
        die("%s exists (write-once)" % out)
    b, a = E.load_json(before_p, "pins"), E.load_json(after_p, "pins")
    ok = True
    for n in PIN_DBS:
        fb, fa = b["files"].get(n), a["files"].get(n)
        eq = fb is not None and fa is not None and fb[0] == fa[0] and fb[2] == fa[2] and b["views"].get(n) == a["views"].get(n)
        say("[V9] %s: size+sha256 %s -> %s; both views %s -> %s" % (n, fb and (fb[0], fb[2][:16]), fa and (fa[0], fa[2][:16]),
                                                                  "equal" if b["views"].get(n) == a["views"].get(n) else "DIFFER",
                                                                  "EQUAL" if eq else "DIFFERS"))
        ok &= eq
    for n in ("ag_news_smoke_cache_v1.db", "ag_news_smoke_cache_v1.db-wal"):
        fb, fa = b["files"].get(n), a["files"].get(n)
        eq = fb is not None and fb == fa
        say("[V9] %s: (size, mtime_ns, sha256) %s -> %s %s" % (n, fb, fa, "EQUAL" if eq else "DIFFERS"))
        ok &= eq
    for n in PIN_FILES:
        if n.endswith("-shm") or (n.endswith("-wal") and not n.startswith("ag_")):
            say("[V9, PRINTED, not deciding] %s %s -> %s" % (n, b["files"].get(n), a["files"].get(n)))
    say("[V9] %s" % ("MET" if ok else "NOT MET"))
    E.write_json_once(out, {"version": VERSION, "v9": bool(ok)})
    return 0 if ok else 1


def main(argv):
    try:
        if len(argv) == 3 and argv[0] == "pins":
            return pins(argv[1], argv[2])
        if len(argv) == 8 and argv[0] == "pre":
            return pre(argv[1], dict(zip(E.LEGS, argv[2:7])), argv[7])
        if len(argv) == 4 and argv[0] == "post":
            return post(*argv[1:4])
        print(__doc__)
        return 2
    except (Die, E.Refuse) as e:
        if isinstance(e, E.Refuse):
            say("[EMD-PREP] REFUSED: %s" % e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
