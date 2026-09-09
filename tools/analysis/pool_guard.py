"""Reserved-pool guard for the Python analyses.

The construction/arena split is the method's contamination guarantee: the tree and the
rubrics are built on the construction side, the arena judges only the reserved side.
`eval_results.is_reserved` mirrors whichever pool is ACTIVE in the dataset DB, and every
construction run (sweep builds included) activates its OWN split — so an analysis that
reads `is_reserved = 1` while a sweep pool is active silently uses a different 30%, ~70%
of which is on the frozen tree's train side.

    from pool_guard import assert_frozen_pool
    assert_frozen_pool(conn)          # raises unless the frozen pool is active

    python tools/analysis/pool_guard.py            # print the active pool and the frozen one
    python tools/analysis/pool_guard.py --activate # re-activate the frozen pool + restore
                                                   # reserved_test_queries.json from the snapshot

FROZEN_POOL_ID is the content hash (ReservedPool.computePoolId) of the 3,445 judgeable
reserved questions of snapshot 20260727_042523; it hash-matches reserved_leaf_assignments.csv.
"""
import os, sys, json, sqlite3, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATASET_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
SNAPSHOT_DB = os.path.join(ROOT, "snapshots_frozen.db")
FROZEN_SNAPSHOT_ID = "20260727_042523_Headless_Run_Auto_ge"
FROZEN_POOL_ID = "p2dca21ab5f4ef3ae"


def compute_pool_id(ids_by_domain):
    """Mirror of ReservedPool.computePoolId: 'p' + sha256(sorted 'domain:id' lines)[:16]."""
    canon = "\n".join(sorted("%s:%d" % (d, q) for d, ids in ids_by_domain.items() for q in ids))
    return "p" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def active_pool_id(conn):
    try:
        row = conn.execute("SELECT pool_id FROM active_reserved_pool WHERE only_row = 1").fetchone()
    except sqlite3.OperationalError:
        return None
    return row[0] if row else None


def assert_frozen_pool(conn, expected=FROZEN_POOL_ID):
    active = active_pool_id(conn)
    if active != expected:
        raise SystemExit(
            "[POOL-GUARD] active reserved pool is %s, expected %s. A construction run has "
            "switched the pool; run `python tools/analysis/pool_guard.py --activate` first."
            % (active, expected))
    return active


def frozen_reserved_from_snapshot():
    c = sqlite3.connect("file:%s?mode=ro" % SNAPSHOT_DB, uri=True)
    raw = c.execute("SELECT reserved_queries FROM snapshots WHERE id = ?", (FROZEN_SNAPSHOT_ID,)).fetchone()[0]
    return json.loads(raw)  # domain -> [ids], sentinel ids <= 0 included (routing-only)


def activate(pool_id=FROZEN_POOL_ID):
    reserved = frozen_reserved_from_snapshot()
    judgeable = {d: [q for q in ids if q > 0] for d, ids in reserved.items()}
    judgeable = {d: ids for d, ids in judgeable.items() if ids}
    assert compute_pool_id(judgeable) == pool_id, "snapshot reserved set does not hash to %s" % pool_id
    conn = sqlite3.connect(DATASET_DB)
    known = conn.execute("SELECT COUNT(*) FROM reserved_pool WHERE pool_id = ?", (pool_id,)).fetchone()[0]
    assert known > 0, "pool %s is not recorded in reserved_pool" % pool_id
    with conn:
        conn.execute("UPDATE eval_results SET is_reserved = 0 WHERE is_reserved = 1")
        n = conn.execute(
            "UPDATE eval_results SET is_reserved = 1 WHERE question_id IN "
            "(SELECT question_id FROM reserved_pool WHERE pool_id = ?)", (pool_id,)).rowcount
        conn.execute("INSERT OR REPLACE INTO active_reserved_pool (only_row, pool_id, active_at) VALUES (1, ?, ?)",
                     (pool_id, int(time.time() * 1000)))
    # Restore the root JSON the Kotlin side reads (identical to what loadSnapshot writes).
    with open(os.path.join(ROOT, "reserved_test_queries.json"), "w", encoding="utf-8") as f:
        json.dump(reserved, f, indent=4)
    print("[POOL-GUARD] activated %s: %d eval_results rows flagged; reserved_test_queries.json restored" % (pool_id, n))


def activate_id(pool_id):
    """Activate an already-recorded pool by id WITHOUT touching reserved_test_queries.json
    (used transiently, e.g. T3 routing of p8a29; always follow with --activate to re-pin)."""
    conn = sqlite3.connect(DATASET_DB)
    known = conn.execute("SELECT COUNT(*) FROM reserved_pool WHERE pool_id = ?", (pool_id,)).fetchone()[0]
    assert known > 0, "pool %s is not recorded" % pool_id
    with conn:
        conn.execute("UPDATE eval_results SET is_reserved = 0 WHERE is_reserved = 1")
        n = conn.execute("UPDATE eval_results SET is_reserved = 1 WHERE question_id IN "
                         "(SELECT question_id FROM reserved_pool WHERE pool_id = ?)", (pool_id,)).rowcount
        conn.execute("INSERT OR REPLACE INTO active_reserved_pool (only_row, pool_id, active_at) VALUES (1, ?, ?)",
                     (pool_id, int(time.time() * 1000)))
    print("[POOL-GUARD] TRANSIENT activation of %s: %d rows flagged (JSON untouched; re-pin with --activate)" % (pool_id, n))


def main():
    if "--activate-id" in sys.argv:
        activate_id(sys.argv[sys.argv.index("--activate-id") + 1])
    elif "--activate" in sys.argv:
        activate()
    conn = sqlite3.connect("file:%s?mode=ro" % DATASET_DB, uri=True)
    active = active_pool_id(conn)
    n = conn.execute("SELECT COUNT(DISTINCT question_id) FROM eval_results WHERE is_reserved = 1").fetchone()[0]
    print("active pool: %s (%d questions) | frozen pool: %s -> %s"
          % (active, n, FROZEN_POOL_ID, "OK" if active == FROZEN_POOL_ID else "MISMATCH"))


if __name__ == "__main__":
    main()
