"""JUDGE-FINISH-AUDIT (FRAMEWORK.md "Tests to register before shipping" item 19; process rule 10). ZERO API CALLS.

Opens every judge verdict cache under experiment_results READ-ONLY and tabulates, per cache, whether the rows can
distinguish a NON_TERMINATED verdict (finish_reason == length, or a content-filter refusal) from a merely wrong one:
does the table carry finish_reason, completion_tokens, provider, max_tokens and a provider response id, and where
finish_reason exists, what its counts are. A cache WITHOUT finish_reason cannot tell an empty or unparsed verdict from
a wrong one; its invalid rate is an upper bound on truncation only if the raw text is stored.

Skipped by name: snapshots_frozen.db, embeddings_cache.db, ratings*.db (engine state), multicorpus_cache*.db and
checker_answers*.db (construction / checker state, not judge calls), engine state DBs (any DB carrying an
agent_ratings_v2 / node_pair_stats table, e.g. h9_sweep/db_*.db), and any DB with no verdicts-like table (a table
with a raw / vote / grade / answer / invalid / winner column). empty_content is counted PER raw column because some
designs store an empty raw2 on purpose (leaf_powered judges one order only).

    python tools/analysis/judge_finish_audit.py            # prints the table and writes
                                                            # experiment_results/x12_crossdomain/judge_finish_audit.txt

2026-09-16: written alongside the rejudge_reasoning.call_judge_full change that returns content-filter refusals as
finish_reason 'content_filter' and attaches the provider response id to the raw message dict.
"""
import os, sys, glob, sqlite3, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RES = os.path.join(ROOT, "experiment_results")
OUT = os.path.join(RES, "x12_crossdomain", "judge_finish_audit.txt")

SKIP_NAMES = ("snapshots_frozen.db", "embeddings_cache.db")
SKIP_PREFIX = ("ratings", "multicorpus_cache", "checker_answers")
ENGINE_TABLES = {"agent_ratings_v2", "node_pair_stats"}

FINISH_COLS = ("finish", "finish1", "finish2", "finish_reason", "finish_reason1", "finish_reason2")
CTOK_COLS = ("ctokens", "ctok1", "ctok2", "completion_tokens", "tokens", "tok1", "tok2")
PROV_COLS = ("provider", "provider1", "provider2")
MAXTOK_COLS = ("max_tokens", "maxtok", "max_tok")
RID_COLS = ("response_id", "provider_response_id", "_response_id", "response_id1", "response_id2")
INVALID_COLS = ("invalid", "r1_invalid", "grok_invalid", "ref_invalid")
RAW_COLS = ("raw", "raw1", "raw2")
VERDICT_LIKE = set(RAW_COLS) | {"vote1", "grade", "answer", "invalid", "winner"}
RAW_TO_FINISH = {"raw": ("finish", "finish_reason"), "raw1": ("finish1", "finish_reason1"),
                 "raw2": ("finish2", "finish_reason2")}


def skip(path):
    b = os.path.basename(path).lower()
    return b in SKIP_NAMES or any(b.startswith(p) for p in SKIP_PREFIX)


def q(con, sql):
    return con.execute(sql).fetchone()[0]


def audit_table(con, table, cols):
    """One audit row for (db, table). Every count is a plain SELECT over the stored columns."""
    cs = set(cols)
    n = q(con, "SELECT COUNT(*) FROM %s" % table)
    fin = [c for c in FINISH_COLS if c in cs]
    ctok = [c for c in CTOK_COLS if c in cs]
    prov = [c for c in PROV_COLS if c in cs]
    maxtok = [c for c in MAXTOK_COLS if c in cs]
    rid = [c for c in RID_COLS if c in cs]
    inv = [c for c in INVALID_COLS if c in cs]
    raw = [c for c in RAW_COLS if c in cs]
    finish_counts = Counter()
    for c in fin:
        for v, k in con.execute("SELECT COALESCE(%s,'NULL'), COUNT(*) FROM %s GROUP BY 1" % (c, table)):
            finish_counts[str(v) if str(v).strip() else "(blank)"] += k
    invalid = sum(q(con, "SELECT COUNT(*) FROM %s WHERE %s=1" % (table, c)) for c in inv) if inv else None
    empty = None
    empty_not_length = None
    if raw:
        empty = {c: q(con, "SELECT COUNT(*) FROM %s WHERE %s IS NULL OR TRIM(%s)=''" % (table, c, c)) for c in raw}
        if fin:
            parts = []
            for rc in raw:
                fc = [f for f in RAW_TO_FINISH[rc] if f in cs]
                if fc:
                    parts.append("((%s IS NULL OR TRIM(%s)='') AND COALESCE(%s,'') <> 'length')" % (rc, rc, fc[0]))
            if parts:
                empty_not_length = q(con, "SELECT COUNT(*) FROM %s WHERE %s" % (table, " OR ".join(parts)))
    return dict(table=table, rows=n, finish_cols=fin, finish_counts=dict(finish_counts), ctok=ctok, prov=prov,
                maxtok=maxtok, rid=rid, invalid=invalid, invalid_cols=inv, raw=raw, empty=empty,
                empty_not_length=empty_not_length)


def meta_maxtok(con, tables):
    """max_tokens recorded in a two-column key/value meta table (run_meta / meta) rather than per row."""
    for t in tables:
        cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
        if t in ("meta", "run_meta") and len(cols) == 2:
            k, v = cols
            for key, val in con.execute("SELECT %s, %s FROM %s" % (k, v, t)):
                kl = str(key).lower()
                if "tok" in kl and "max" in kl:
                    return "meta:%s=%s" % (key, str(val)[:12])
    return None


def audit():
    rows = []
    dbs = sorted(glob.glob(os.path.join(RES, "**", "*.db"), recursive=True))
    for p in dbs:
        if skip(p):
            continue
        try:
            if os.path.basename(p).startswith("db_") and "h9_sweep" in p.replace("\\", "/"):
                continue  # WAL-mode engine DBs: never opened (a ro open still touches their -shm) [checker 2026-09-16]
            con = sqlite3.connect("file:%s?mode=ro&immutable=1" % p.replace("\\", "/"), uri=True)
            tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        except sqlite3.Error as e:
            rows.append(dict(db=os.path.relpath(p, RES).replace("\\", "/"), table="?", error=str(e)))
            continue
        if ENGINE_TABLES & set(tables):
            con.close(); continue
        mm = meta_maxtok(con, tables)
        for t in tables:
            cols = [r[1] for r in con.execute("PRAGMA table_info(%s)" % t)]
            if not (set(cols) & VERDICT_LIKE):
                continue
            r = audit_table(con, t, cols)
            r["db"] = os.path.relpath(p, RES).replace("\\", "/")
            r["meta_maxtok"] = mm
            rows.append(r)
        con.close()
    return rows


def fmt_counts(d):
    if not d:
        return "-"
    return ",".join("%s=%d" % (k, v) for k, v in sorted(d.items(), key=lambda kv: -kv[1]))


def render(rows):
    hdr = ("cache", "table", "rows", "has_finish", "finish_counts", "invalid", "empty_content",
           "empty&finish!=length", "ctok", "provider", "max_tokens", "response_id")
    body = []
    for r in rows:
        if "error" in r:
            body.append((r["db"], "?", "ERR", r["error"][:40], "", "", "", "", "", "", "", ""))
            continue
        body.append((r["db"], r["table"], str(r["rows"]),
                     ("Y:" + "/".join(r["finish_cols"])) if r["finish_cols"] else "N",
                     fmt_counts(r["finish_counts"]),
                     "-" if r["invalid"] is None else str(r["invalid"]),
                     "-" if r["empty"] is None else ",".join("%s=%d" % kv for kv in r["empty"].items()),
                     "-" if r["empty_not_length"] is None else str(r["empty_not_length"]),
                     "/".join(r["ctok"]) or "N", "/".join(r["prov"]) or "N",
                     "/".join(r["maxtok"]) or (r["meta_maxtok"] or "N"), "/".join(r["rid"]) or "N"))
    w = [max([len(h)] + [len(b[i]) for b in body]) for i, h in enumerate(hdr)]
    fmt = "  ".join("%%-%ds" % x for x in w)
    lines = [fmt % hdr, fmt % tuple("-" * x for x in w)]
    for b in body:
        lines.append(fmt % b)
    return "\n".join(lines)


def headline(rows):
    ok = [r for r in rows if "error" not in r]
    dbs = sorted({r["db"] for r in ok})
    with_fin = sorted({r["db"] for r in ok if r["finish_cols"]})
    with_rid = sorted({r["db"] for r in ok if r["rid"]})
    with_maxtok = sorted({r["db"] for r in ok if r["maxtok"] or r["meta_maxtok"]})
    with_raw = sorted({r["db"] for r in ok if r["raw"]})
    n_rows = sum(r["rows"] for r in ok)
    n_rows_fin = sum(r["rows"] for r in ok if r["finish_cols"])
    fin_all = Counter()
    for r in ok:
        fin_all.update(r["finish_counts"])
    out = ["JUDGE-FINISH-AUDIT %s | zero API calls | %d caches (%d verdict-like tables, %d rows) under experiment_results"
           % (time.strftime("%Y-%m-%d %H:%M"), len(dbs), len(ok), n_rows),
           "  caches WITH finish_reason: %d of %d (%d rows, %.1f%% of rows) -> %s"
           % (len(with_fin), len(dbs), n_rows_fin, 100.0 * n_rows_fin / max(1, n_rows), ", ".join(with_fin)),
           "  caches WITHOUT finish_reason: %d of %d (cannot distinguish NON_TERMINATED from wrong; invalid and empty raw text are the only proxies)"
           % (len(dbs) - len(with_fin), len(dbs)),
           "  finish counts pooled over the caches that have it: %s" % fmt_counts(fin_all),
           "  caches with a per-row max_tokens column or a meta max_tokens key: %d of %d -> %s"
           % (len(with_maxtok), len(dbs), ", ".join(with_maxtok) or "-"),
           "  caches with a provider response id: %d of %d -> %s" % (len(with_rid), len(dbs), ", ".join(with_rid) or "-"),
           "  caches storing raw judge text (empty-content proxy available): %d of %d; without raw text: %s"
           % (len(with_raw), len(dbs), ", ".join(sorted(set(dbs) - set(with_raw))) or "-")]
    return "\n".join(out)


def main():
    rows = audit()
    text = headline(rows) + "\n\n" + render(rows) + "\n"
    print(text)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print("written %s" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
