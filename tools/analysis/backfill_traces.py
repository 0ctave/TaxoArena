"""One-off repair: backfill eval_results.model_output from the upstream archives.

WHY NOT RE-INGEST: ModelEvalStore.saveBatch uses INSERT OR IGNORE on PK
(question_id, model_name), so existing rows are skipped and the empty column stays.
Deleting first would re-derive `is_reserved` from reserved_test_queries.json, which
risks shifting the held-out set and invalidating the frozen artifact 20260727_042523.

So: UPDATE model_output ONLY, matched on the primary key. Every other column is
left untouched, and that is asserted before and after.

Mirrors taxonomy.dataset.unwrapTraceEnvelope (allow-list: keep `response`, drop all
other envelope keys).
"""
import sqlite3, zipfile, json, glob, os, sys, hashlib

DB = 'mmlu_pro_dataset_cache_v2.db'
DRY = '--apply' not in sys.argv


def unwrap(s):
    t = s.lstrip()
    if not t.startswith('{'):
        return s
    try:
        o = json.loads(t)
    except Exception:
        return s
    if not isinstance(o, dict):
        return s
    r = o.get('response')
    return r if isinstance(r, str) and r.strip() else s


def archive_model(path):
    n = os.path.basename(path)
    n = n.replace('model_outputs_', '')
    for suf in ('.json.zip', '.zip', '.json'):
        if n.endswith(suf):
            n = n[: -len(suf)]
    if n.endswith('_5shots'):
        n = n[: -len('_5shots')]
    return n


con = sqlite3.connect(DB)
cur = con.cursor()

# ---- pre-flight fingerprint of everything we must NOT change ----
def fingerprint():
    h = hashlib.sha256()
    for row in cur.execute(
        "SELECT question_id, model_name, category, question_text, options_json, "
        "gt_answer, pred, is_correct, is_reserved FROM eval_results "
        "ORDER BY model_name, question_id"
    ):
        h.update(repr(row).encode())
    return h.hexdigest()

before_fp = fingerprint()
before_counts = dict(cur.execute(
    "SELECT model_name, SUM(CASE WHEN TRIM(model_output)='' THEN 1 ELSE 0 END) "
    "FROM eval_results GROUP BY model_name"))
print(f"pre-flight fingerprint (all non-trace columns): {before_fp[:16]}")
print(f"models with any blank trace: {sum(1 for v in before_counts.values() if v)}")

db_models = {m for (m,) in cur.execute("SELECT DISTINCT model_name FROM eval_results")}

total_upd = 0
report = []
for path in sorted(glob.glob('eval_results/*.zip') + glob.glob('eval_results/*.json')):
    model = archive_model(path)
    if model not in db_models:
        continue
    try:
        if path.endswith('.zip'):
            Z = zipfile.ZipFile(path)
            raw = Z.read(Z.namelist()[0])
        else:
            raw = open(path, 'rb').read()
        d = json.loads(raw)
        if isinstance(d, dict):
            d = list(d.values())[0]
    except Exception as e:
        report.append((model, 'ARCHIVE-ERROR', str(e)[:40], 0, 0))
        continue

    pending = []
    for it in d:
        if not isinstance(it, dict):
            continue
        qid = it.get('question_id')
        if qid is None:
            continue
        trace = (it.get('model_outputs') or '') or (it.get('cot_content') or '') \
            or (it.get('generated_text') or '')
        if not trace.strip():
            continue
        pending.append((unwrap(trace), qid, model))

    if not pending:
        report.append((model, 'no-trace-in-archive', '', 0, 0))
        continue

    # Only fill rows that are currently blank OR still hold a raw envelope.
    cur.executemany(
        "UPDATE eval_results SET model_output=? WHERE question_id=? AND model_name=? "
        "AND (TRIM(model_output)='' OR (TRIM(model_output) LIKE '{%' AND model_output LIKE '%\"response\"%'))",
        pending,
    ) if not DRY else None
    n = cur.rowcount if not DRY else -1
    if DRY:
        qs = [(p[1], p[2]) for p in pending]
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS _probe(qid INT, m TEXT)")
        cur.execute("DELETE FROM _probe")
        cur.executemany("INSERT INTO _probe VALUES (?,?)", qs)
        n = cur.execute(
            "SELECT COUNT(*) FROM eval_results e JOIN _probe p "
            "ON e.question_id=p.qid AND e.model_name=p.m "
            "WHERE TRIM(e.model_output)='' OR (TRIM(e.model_output) LIKE '{%' "
            "AND e.model_output LIKE '%\"response\"%')").fetchone()[0]
    total_upd += max(n, 0)
    report.append((model, 'ok', f'{len(pending)} in archive', n, len(pending)))

print()
print(f"{'model':<34}{'status':<22}{'would-update' if DRY else 'updated':>13}")
for m, st, note, n, tot in sorted(report, key=lambda r: -r[3]):
    print(f"{m:<34}{st:<22}{n:>13}")

print()
print(f"TOTAL rows {'that would be' if DRY else ''} updated: {total_upd:,}")

if DRY:
    con.rollback()
    print("\nDRY RUN — nothing written. Re-run with --apply")
else:
    after_fp = fingerprint()
    assert after_fp == before_fp, "NON-TRACE COLUMN CHANGED — rolling back"
    con.commit()
    print(f"\npost-flight fingerprint: {after_fp[:16]}  MATCHES — only model_output changed")
con.close()
