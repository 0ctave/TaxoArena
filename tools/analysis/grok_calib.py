"""GROK-CALIB — the x12 schedule re-judged by grok-4-1-fast-non-reasoning under the STACK-v2 recipe
(FRAMEWORK.md "Tests to register before shipping", item 26; registered by reference at eaf1dbf; scheduled as
Block 2 item e in docs/plan_2026-09-15.md; above the 4,000-match rule, explicit GO recorded there).

  python tools/analysis/grok_calib.py --dry-run [--pilot 12]           (0 calls: payloads assembled, nothing posted)
  python tools/analysis/grok_calib.py --run --pilot 12 [--workers 8]   (the pilot the truncation guard reads)
  python tools/analysis/grok_calib.py --run [--workers 8] [--maxtok 8192]
  python tools/analysis/grok_calib.py --report [--pilot 12]           (guard + readout on that schedule slice, 0 calls; exit 2 on refusal)
  python tools/analysis/grok_calib.py --analyze                        (guard, then systematic_budget on THIS cache)

WHAT IS JUDGED. Every match in the Mistral x12 recipe cache (stack_v2_promptv2_x12all.db, 9,142 of the 9,144
MAIN matches: 4389 and 6528 were content-filter refusals under Mistral in ARENA-V2, ledger 2026-09-10 20:20;
both questions are routed and have traces, and they are left out here so every grok row pairs with a Mistral
row and the plan's "9,144" reads 9,142 x 2 = 18,284 calls) is re-judged
with the IDENTICAL recipe: prompt v2 + the ladder's anchor rubric for the question's routed leaf in the clean
bareq512_s42 tree + the grok-reasoning reference (J2-R) in the question block + dual order with flip -> TIE
and INVALID when either order fails to parse. The 19 matches Mistral judged without a reference are judged
without one here too. The schedule is drawn from the cache, not from ratings_x12.db, so every grok verdict
is paired with a Mistral verdict on the same match, and the cache asserts per match that the anchor and the
reference letter it derives equal the ones Mistral saw.

WHY. The widener of record (b0 -3.2326, b1 +3.3133, CI on b1 [1.72, 7.87]) is fitted on Mistral verdicts and
JUDGE-TRANSFER showed it does not carry to grok (tau -> 0 on established labels, utility 57.0%). Until a
calibration board exists for the shipped judge, grok-judged cells run the fallback certificate and no
ORDERED-JUDGED edge exists. This run is that board.

CRITERIA (FRAMEWORK item 26, scored in --analyze): b1 identified on established labels (b1 = 0 rejected at
delta-deviance 3.84); utility (2) = LOAO-called at 0.975 / ALL edges of the population >= 60%, the denominator
every registered use of the 60% bar has used (SYSTEMATIC-BUDGET frac = lo_called/filt 74.4%, BUDGET-TRANSFER,
JUDGE-TRANSFER 57.0% FAIL); called / raw-called is printed beside it as a NON-DECIDING second figure
(Amendment 1 D6, docs/plan_2026-09-15.md); LOAO wrong count reported with all(established); calibration status
by the power rule (nominal < 3 -> UNDETERMINED). Prediction: UNDETERMINED at the operating point, b1 inside
[1.72, 7.87].

GUARD (D6). --report/--analyze evaluate the 5% unparsed guard on the SCHEDULE, not on the cached rows: schedule
coverage is printed, and every scheduled match without a cached row (errors are never cached: an HTTP 400
content-filter refusal raises in rr.call_judge_full and is skipped) counts as unparsed in the overall rate and,
where the key decides the match, in the key-decidable rate. A pilot's guard is read with the same --pilot N
(`--report --pilot 12`), otherwise the 9,130 unjudged matches refuse the read, as they should.

TEMPERATURE (D2). Omitted from the payload (provider default), as every cache this run pairs with omitted it;
recorded in the cache's meta table and printed in every header. The request body is built by
rejudge_reasoning.call_judge_full (model, max_tokens, messages[, temperature]); the dry-run assembles the same
body locally, asserts its key tuple and prints the model field.

CACHE. experiment_results/x12_crossdomain/grok_calib.db (grok_calib_mt<N>.db at a non-default --maxtok), table
`verdicts` with the x12 cache's 18 columns in the same order and names, plus finish1/finish2, tok1/tok2,
provider1/provider2, lat1/lat2, protocol, maxtok; table `meta` (protocol, max_tokens, temperature, judge,
script sha pinned at first launch, started once, resumes appended; a resume whose protocol or max_tokens differ
is refused). systematic_budget.build() reads the verdicts through stack_judge.open_cache(); --analyze points
that at this file without editing systematic_budget. A --dry-run never creates the file; --analyze on an absent
cache writes nothing; a pilot-sized cache (< 1000 matches) writes grok_calib_outcome_pilot.txt, never the
outcome file of record.
"""
import os, sys, math, time, json, hashlib, sqlite3, argparse, threading, urllib.error
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj

def judge_full(system, user):
    """rr.call_judge_full, with a provider REFUSAL made visible: an HTTP 400 whose body carries finish_reason=content_filter
    is deterministic (re-posting it forever stalls the run; not caching it makes the match vanish from the guard
    denominator, the class that lost 4389 and 6528 in ARENA-V2). It returns an EMPTY content with finish_reason
    'content_filter', which parses as INVALID and counts against the 5% guard like a truncation. Every other HTTP error
    is still raised and re-posted on resume. Added 2026-09-16 after NEWCOMER-PLACEMENT-LIVE hit one on a History match."""
    try:
        return rr.call_judge_full(system, user)
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode("utf-8", "replace")
        except Exception: pass
        if e.code == 400 and "content_filter" in body:
            return ("", "azure:refusal", 0, 0.0, "content_filter", None)
        raise


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

JUDGE = "grok-4-1-fast-non-reasoning"
PROVIDER = "azure"
MAXTOK_DEFAULT = 8192      # rejudge_reasoning's cap, the one RECIPE-GROK posted with; Mistral's x12 run used 2048
MAXTOK = MAXTOK_DEFAULT
REFERENCE = "grok-reasoning"
TREE = "bareq512_s42"
POOL = pool_guard.FROZEN_POOL_ID
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
X12_CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x12all.db")
CACHE_BASE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "grok_calib")
GUARD = 0.05
X12_COLS = ["match_id", "model_a", "model_b", "node_id", "qid", "anchor", "ref_letter", "ref_correct", "vote1", "vote2_raw",
            "conf1", "conf2", "winner", "flip", "invalid", "raw1", "raw2", "ts"]
EXTRA_COLS = [("finish1", "TEXT"), ("finish2", "TEXT"), ("tok1", "INTEGER"), ("tok2", "INTEGER"), ("provider1", "TEXT"),
              ("provider2", "TEXT"), ("lat1", "REAL"), ("lat2", "REAL"), ("protocol", "TEXT"), ("maxtok", "INTEGER")]

sj.PROMPT = "v2"       # system_for() builds the v2 system prompt; never sj.JUDGE = "grok", that names a different cache


def protocol():
    return ("STACK-v2 on %s/%s: prompt_v2 system template + ladder anchor rubric (routed leaf in %s, depth-1 label) + "
            "schema instruction; question block carries the %s reference (J2-R) where one exists; dual order, "
            "flip -> TIE, INVALID if either order unparsed; temperature omitted; max_tokens %d; "
            "reasoning text stripped before parse" % (PROVIDER, JUDGE, TREE, REFERENCE, MAXTOK))


def cache_path():
    """Own cache, named for the run; a non-default cap gets its OWN file (ref_qualify's rule) so a re-run at a
    larger --maxtok never mixes with, or overwrites, the run at the cap of record."""
    return CACHE_BASE + ("" if MAXTOK == MAXTOK_DEFAULT else "_mt%d" % MAXTOK) + ".db"


def out_path(suffix):
    return cache_path()[:-3] + suffix


def x12_ro():
    return sqlite3.connect("file:%s?mode=ro" % X12_CACHE, uri=True)


TEMPERATURE_LABEL = "omitted (provider default; Amendment 1 D2)"
BODY_KEYS = ("model", "max_tokens", "messages")


def request_body(system, user):
    """Local copy of the body rejudge_reasoning.call_judge_full posts (rejudge_reasoning.py lines 92-96: model,
    max_tokens, messages, and temperature only when rr.TEMPERATURE is not None). Kept here so the dry-run can
    print the model field of what --run will post; the dry-run asserts the key tuple against BODY_KEYS."""
    pb = {"model": JUDGE, "max_tokens": MAXTOK,
          "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None:
        pb["temperature"] = rr.TEMPERATURE
    return pb


def script_sha():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]


def schedule():
    """The 9,142 x12 recipe matches, by match_id, with what Mistral saw on each (for the per-match identity assert)."""
    con = x12_ro()
    rows = con.execute("SELECT match_id, model_a, model_b, node_id, qid, anchor, ref_letter, ref_correct, winner, invalid "
                       "FROM verdicts ORDER BY match_id").fetchall()
    con.close()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    ev.close()
    outside = sorted({r[4] for r in rows} - pool)
    assert not outside, "[POOL] %d x12 questions are outside %s: %s" % (len(outside), POOL, outside[:10])
    bad = {r[1] for r in rows} | {r[2] for r in rows}
    assert not (bad & EXCLUDED), "excluded model in the schedule: %s" % (bad & EXCLUDED)
    return rows


def cached_ids():
    """Resume set at zero side effects: a dry run must not create the cache file."""
    if not os.path.exists(cache_path()): return set()
    con = sqlite3.connect("file:%s?mode=ro" % cache_path(), uri=True)
    ids = {r[0] for r in con.execute("SELECT match_id FROM verdicts")}; con.close(); return ids


def open_cache():
    con = sqlite3.connect(cache_path())
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, "
                "anchor TEXT, ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, "
                "flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    for col, decl in EXTRA_COLS:
        try: con.execute("ALTER TABLE verdicts ADD COLUMN %s %s" % (col, decl))
        except sqlite3.OperationalError: pass
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit()
    return con


def pin_meta(con):
    """First launch writes the protocol of record once; every later launch is a resume and must match it
    (Amendment 1: 'started' written once, resumes appended, script sha pinned at first launch, a resume with a
    different max_tokens or protocol is refused). Temperature is recorded as omitted (D2)."""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    meta = dict(con.execute("SELECT key, value FROM meta"))
    want = {"protocol": protocol(), "max_tokens": str(MAXTOK), "temperature": TEMPERATURE_LABEL}
    if not meta:
        rows = [("judge", JUDGE), ("provider", PROVIDER), ("reference", REFERENCE), ("tree", TREE), ("pool", POOL),
                ("schedule_source", os.path.basename(X12_CACHE)), ("script_sha256_16", script_sha()), ("started", now)]
        con.executemany("INSERT INTO meta VALUES (?, ?)", rows + list(want.items())); con.commit()
        return
    bad = [(k, meta.get(k), v) for k, v in want.items() if meta.get(k) != v]
    if bad:
        for k, have, w in bad:
            print("[META] %s differs from the cache of record:\n   cached: %r\n   now:    %r" % (k, have, w))
        raise SystemExit("resume refused: a different max_tokens/protocol is a new session and gets a new cache (--maxtok names one)")
    con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((meta.get("resumed") + ", " if meta.get("resumed") else "") + now,))
    if meta.get("script_sha256_16") != script_sha():
        print("[META] script edited since first launch: pinned sha %s, now %s (recorded as script_sha256_16_relaunch)"
              % (meta.get("script_sha256_16"), script_sha()))
        con.execute("INSERT OR REPLACE INTO meta VALUES ('script_sha256_16_relaunch', ?)", (script_sha(),))
    con.commit()


class Assembler:
    """Everything a match needs, loaded once; payload(m) returns (system, user_order1, user_order2, ref) at zero calls."""

    def __init__(self, sample):
        rref.set_reference(REFERENCE); self.refs = rref.references()
        self.rubrics = sj.anchor_rubrics(); self.anchors = sj.routed_anchor()
        missing = [a for a in set(self.anchors.values()) if a not in self.rubrics]
        assert not missing, "no anchor rubric for %s" % missing
        self.evals = rj.load_eval_rows([m[4] for m in sample], {m[1] for m in sample} | {m[2] for m in sample})

    def payload(self, m):
        mid, a, b, nid, qid, anc_x12, ref_x12, refc_x12 = m[:8]
        ra, rb = self.evals.get((qid, a)), self.evals.get((qid, b))
        if ra is None or rb is None:
            raise RuntimeError("match %d: trace missing for %s" % (mid, a if ra is None else b))
        anc = self.anchors.get(qid)
        if anc != anc_x12:
            raise RuntimeError("match %d: routed anchor %r differs from the one Mistral saw %r" % (mid, anc, anc_x12))
        ref = self.refs.get(qid)
        if (ref[0] if ref else "") != (ref_x12 or ""):
            raise RuntimeError("match %d: reference %r differs from the one Mistral saw %r" % (mid, ref[0] if ref else "", ref_x12))
        q = rref.with_reference(ra[0], ref) if ref is not None else ra[0]
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = sj.system_for(anc, self.rubrics)
        return system, rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta), ref


def header(sample, todo, calls_label, cache_exists=None):
    """cache_exists is captured by the caller BEFORE open_cache() creates the file, so --run's first launch
    reads 'new file' and not 'exists, resume'."""
    if cache_exists is None: cache_exists = os.path.exists(cache_path())
    print("[POOL] %s (pool of record; pool_guard: active pool matches)" % POOL, flush=True)
    print("[RUN]  GROK-CALIB | judge %s on %s | schedule %d matches from %s" % (JUDGE, PROVIDER, len(sample), os.path.basename(X12_CACHE)))
    print("[CALLS] %s" % calls_label)
    print("[PROTOCOL] %s" % protocol())
    print("[PARAMS] judge=%s | provider=%s | max_tokens=%d (default %d; --maxtok names a new cache; stored per row) | temperature=%s"
          % (JUDGE, PROVIDER, MAXTOK, MAXTOK_DEFAULT, TEMPERATURE_LABEL))
    print("[CACHE] %s (%s)" % (cache_path(), "exists, resume" if cache_exists else "new file, created on --run"))
    print("[EXCLUDED] %s not in the schedule (asserted)" % ", ".join(sorted(EXCLUDED)))


def dry_run(pilot):
    sample = schedule()
    if pilot: sample = sample[:pilot]
    done = cached_ids()
    todo = [m for m in sample if m[0] not in done]
    header(sample, todo, "%d matches x 2 orders = %d calls (%d already cached, %d to post)" % (len(sample), 2 * len(sample), len(done & {m[0] for m in sample}), 2 * len(todo)))
    assert rr.TEMPERATURE is None, "D2: temperature must be omitted from the payload; rr.TEMPERATURE is %r" % (rr.TEMPERATURE,)
    asm = Assembler(sample)
    n = 0; nref = 0; nbytes = 0; first = None; anchors = Counter()
    for m in sample:
        system, u1, u2, ref = asm.payload(m)
        n += 2; nref += ref is not None; anchors[m[5]] += 1
        nbytes += len(system.encode("utf-8")) * 2 + len(u1.encode("utf-8")) + len(u2.encode("utf-8"))
        if first is None: first = (m, system, u1, u2)
    print("[DRY-RUN] assembled %d payloads for %d matches | %d with a reference, %d without | %.1f MB of prompt text | nothing posted"
          % (n, len(sample), nref, len(sample) - nref, nbytes / 1e6))
    print("[DRY-RUN] anchors: %s" % ", ".join("%s %d" % kv for kv in sorted(anchors.items())))
    m, system, u1, u2 = first
    body = request_body(system, u1)
    assert tuple(body.keys()) == BODY_KEYS, "request body keys %r != %r (rejudge_reasoning.call_judge_full lines 92-96 changed?)" % (tuple(body.keys()), BODY_KEYS)
    assert body["messages"][0]["content"] == system and body["messages"][1]["content"] == u1
    print("[PAYLOAD] first request body: model=%s | max_tokens=%d | temperature=%s | keys=%s | %d bytes"
          % (body["model"], body["max_tokens"], "omitted" if "temperature" not in body else body["temperature"],
             ",".join(body.keys()), len(json.dumps(body).encode("utf-8"))))
    print("[DRY-RUN] first payload: match %d | %s vs %s | qid %d | anchor %s | ref %s (correct=%s)" % (m[0], m[1], m[2], m[4], m[5], m[6] or "-", m[7]))
    print("----- SYSTEM (verbatim, both orders) -----")
    print(system)
    print("----- USER, order 1 (verbatim) -----")
    print(u1)
    print("----- USER, order 2 = the same question block with the traces swapped (%d chars) -----" % len(u2))
    print("[DRY-RUN] OK: 0 calls made")


def run(pilot, workers):
    rr.PROVIDER = PROVIDER; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.load_env()
    sample = schedule()
    if pilot: sample = sample[:pilot]
    assert rr.TEMPERATURE is None, "D2: temperature must be omitted from the payload; rr.TEMPERATURE is %r" % (rr.TEMPERATURE,)
    cache_exists = os.path.exists(cache_path())      # before open_cache() creates the file (review LOW, [CACHE] header)
    cache = open_cache()
    pin_meta(cache)
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    header(sample, todo, "%d matches x 2 orders = %d calls | cached %d | to post %d" % (len(sample), 2 * len(sample), len(sample) - len(todo), 2 * len(todo)), cache_exists)
    if not todo:
        print("nothing to do"); L = []; guard_and_summary(L, pilot); print("\n".join(L), flush=True); return
    asm = Assembler(todo)
    print("[RUN] workers %d | resume: %d matches skipped as cached" % (workers, len(sample) - len(todo)), flush=True)
    lock = threading.Lock(); ok = err = 0; proto = protocol()

    def one(m):
        mid, a, b, nid, qid = m[:5]
        system, u1, u2, ref = asm.payload(m)
        c1, p1, k1, l1, f1, _ = judge_full(system, u1)
        c2, p2, k2, l2, f2, _ = judge_full(system, u2)
        raw1, raw2 = rr.strip_think(c1), rr.strip_think(c2)
        v1, cf1 = rj.parse_judge(raw1); v2, cf2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, m[5], ref[0] if ref else "", int(ref[2]) if ref else -1, v1, v2, cf1, cf2,
                {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time(),
                f1, f2, k1, k2, p1, p2, l1, l2, proto, MAXTOK)
    cols = X12_COLS + [c for c, _ in EXTRA_COLS]
    ins = "INSERT OR REPLACE INTO verdicts (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:140]), flush=True); continue
            with lock:
                cache.execute(ins, row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d (errors are not cached; re-run to resume; they count as unparsed in the guard below)" % (ok, err), flush=True)
    L = []; guard_and_summary(L, pilot); print("\n".join(L), flush=True)


def load_verdicts():
    if not os.path.exists(cache_path()): return []
    con = sqlite3.connect("file:%s?mode=ro" % cache_path(), uri=True)
    rows = con.execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, ref_correct, anchor, finish1, finish2, tok1, tok2, "
                       "vote1, vote2_raw FROM verdicts").fetchall()
    con.close(); return rows


def guard_and_summary(L, pilot=None):
    """The truncation guard and the pilot readout. Returns True when the verdict may be written.

    Deciding subset for a calibration board: every valid verdict enters the bootstrap fit and the key-decidable
    ones carry the labels, so the guard is evaluated on ALL scheduled matches and on the KEY-DECIDABLE ones, and
    refuses if either exceeds 5% unparsed. Unparsed = INVALID in either order OR no cached row for a scheduled
    match (errors are never cached, so a refusal rate would otherwise be invisible; Amendment 1 D6). The
    schedule is the x12 schedule sliced by --pilot, exactly as --run slices it."""
    sched = schedule()
    if pilot: sched = sched[:pilot]
    sid = {m[0]: m for m in sched}
    all_rows = load_verdicts()
    rows = [r for r in all_rows if r[0] in sid]
    missing = sorted(set(sid) - {r[0] for r in rows})
    L.append("  schedule coverage: %d of %d scheduled matches cached (%d cached rows outside this schedule ignored) | %d missing (errors are never cached; counted as unparsed below)%s"
             % (len(rows), len(sched), len(all_rows) - len(rows), len(missing), (": " + ", ".join(map(str, missing[:20])) + (" ..." if len(missing) > 20 else "")) if missing else ""))
    if not rows:
        L.insert(0, "no verdicts cached yet"); return False
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    ev.close()
    def decidable(qid, a, b):
        return G.get((qid, a)) is not None and G.get((qid, b)) is not None and G[(qid, a)] != G[(qid, b)]
    dec = [r for r in rows if decidable(r[3], r[1], r[2])]
    missing_dec = [mid for mid in missing if decidable(sid[mid][4], sid[mid][1], sid[mid][2])]
    inv_all = [r for r in rows if r[6]]; inv_dec = [r for r in dec if r[6]]
    n_all = len(sched); n_dec = len(dec) + len(missing_dec)
    unp_all = len(inv_all) + len(missing); unp_dec = len(inv_dec) + len(missing_dec)
    rate_all = unp_all / max(1, n_all); rate_dec = unp_dec / max(1, n_dec)
    fin = Counter(); length = 0
    for r in rows:
        fin[r[9] or "(none)"] += 1; fin[r[10] or "(none)"] += 1
        length += (r[9] == "length") + (r[10] == "length")
    toks = [t for r in rows for t in (r[11], r[12]) if t]
    L.insert(0, "=== GROK-CALIB readout: %d of %d scheduled matches judged (%d key-decidable of %d) | judge %s | cap %s | temperature %s ==="
             % (len(rows), n_all, len(dec), n_dec, JUDGE, MAXTOK, TEMPERATURE_LABEL))
    L.append("  unparsed (INVALID in either order + missing): %d of %d overall (%.1f%%; %d INVALID + %d missing) | %d of %d key-decidable (%.1f%%; %d INVALID + %d missing) | guard %.0f%%"
             % (unp_all, n_all, 100 * rate_all, len(inv_all), len(missing), unp_dec, n_dec, 100 * rate_dec, len(inv_dec), len(missing_dec), 100 * GUARD))
    L.append("  finish_reason over %d calls: %s | finish=length: %d" % (2 * len(rows), dict(fin), length))
    L.append("  completion tokens: mean %.0f | p95 %d" % (sum(toks) / max(1, len(toks)), sorted(toks)[int(0.95 * (len(toks) - 1))] if toks else 0))
    valid = [r for r in rows if not r[6]]
    if valid:
        L.append("  flip rate %.3f | tie rate %.3f (all valid) | key-decidable accuracy %.3f (n=%d, ties count as wrong)"
                 % (sum(r[5] for r in valid) / len(valid), sum(r[4] == "TIE" for r in valid) / len(valid),
                    sum(1 for r in dec if not r[6] and r[4] == (r[1] if G[(r[3], r[1])] else r[2])) / max(1, sum(1 for r in dec if not r[6])),
                    sum(1 for r in dec if not r[6])))
        x = {r[0]: r for r in x12_ro().execute("SELECT match_id, winner, invalid FROM verdicts")}
        both = [r for r in valid if r[0] in x and not x[r[0]][2]]
        L.append("  paired with Mistral x12 on %d matches: 3-way agreement %.3f | both decisive agree %.3f (n=%d)"
                 % (len(both), sum(r[4] == x[r[0]][1] for r in both) / max(1, len(both)),
                    sum(r[4] == x[r[0]][1] for r in both if r[4] != "TIE" and x[r[0]][1] != "TIE") / max(1, sum(1 for r in both if r[4] != "TIE" and x[r[0]][1] != "TIE")),
                    sum(1 for r in both if r[4] != "TIE" and x[r[0]][1] != "TIE")))
    if rate_all > GUARD or rate_dec > GUARD:
        L.append("  VERDICT REFUSED: more than %.0f%% of the schedule (overall or key-decidable) is unparsed or missing. An unparsed"
                 " verdict is dropped from the fit, so a calibration read here would be on a selected schedule. Missing matches:"
                 " re-run --run to resume (errors are re-posted). INVALID: inspect finish_reason; re-run with a larger --maxtok"
                 " (new cache) or record non-termination as a property of the judge." % (100 * GUARD))
        return False
    L.append("  guard: PASS")
    return True


def analyze(pilot=None):
    """systematic_budget's pipeline pointed at THIS cache, then the item-26 criteria from the same helpers.
    Writes nothing on an absent cache; a pilot-sized cache writes the _outcome_pilot.txt file, never the outcome
    file of record."""
    if not os.path.exists(cache_path()):
        print("[ANALYZE] no cache at %s: nothing judged yet, nothing written (run --run first)" % cache_path()); return
    L = []
    ok = guard_and_summary(L, pilot)
    print("\n".join(L))
    n = len(load_verdicts())
    outcome = out_path("_outcome.txt") if (pilot is None and n >= 1000) else out_path("_outcome_pilot.txt")
    if not ok:
        open(outcome, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("[ANALYZE] refusal written to %s" % outcome); sys.exit(2)
    if n < 1000:
        L.append("  %d matches is a pilot: the calibration fit needs the full schedule (>= 200 verdicts per anchor). Readout only." % n)
        print(L[-1]); open(outcome, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("[ANALYZE] pilot readout written to %s" % outcome); return
    item26_criteria(L, cache_path(), out_path("_systematic_budget.txt"))
    txt = "\n".join(L); print(txt); open(outcome, "w", encoding="utf-8").write(txt + "\n"); print("[ANALYZE] written to %s" % outcome)


def item26_criteria(L, cache_db, sb_out):
    """The item-26 readout (widener fit, established-label refit, LOAO utility, calibration status) on ANY cache whose
    `verdicts` table carries stack_judge's columns: systematic_budget's pipeline pointed at `cache_db`, its full table
    written to `sb_out`, the criteria lines appended to L. Extracted from analyze() on 2026-09-16 with zero numeric
    change (analyze() calls it on this cache; grok_calib_outcome.txt reproduces byte for byte) so that
    judge_wiring.py --analyze-board reads the Kotlin board with the SAME helpers instead of a copy."""
    import systematic_budget as sb
    from scipy.optimize import minimize_scalar
    # point the existing pipeline at this cache: build() reads verdicts through stack_judge.open_cache()
    sj.open_cache = lambda: sqlite3.connect("file:%s?mode=ro" % cache_db, uri=True)
    sb.OUT = sb_out
    built = {}
    _build = sb.build
    def build_once():
        if "v" not in built: built["v"] = _build()
        return built["v"]
    sb.build = build_once
    print("\n[ANALYZE] systematic_budget.main() on %s -> %s" % (os.path.basename(cache_db), sb.OUT), flush=True)
    # [2026-09-23] sb.main now takes the edge set explicitly (--edges is REQUIRED on the CLI because
    # the record does not establish a default); "filtered" is the population this call has always run
    # on (sb.main fitted `filt`), so item-26 and grok_calib_outcome.txt are unchanged.
    sb.main("filtered")
    models, K, P, by, edges, anchor_qs = build_once()
    L.append(""); L.append("=== FRAMEWORK item 26 criteria (helpers from systematic_budget; full table in %s) ===" % os.path.basename(sb.OUT))
    for tag, es in (("key gap >= %.2f (the derivation's population)" % sb.GAP, [e for e in edges if e["gap"] >= sb.GAP]), ("unfiltered (the adopted denominator)", edges)):
        if len(es) < 50:
            L.append("  %s: only %d edges, no fit" % (tag, len(es))); continue
        b0, b1 = sb.fit(es)
        est = sb.established(es, K, anchor_qs)
        e0, e1 = sb.fit(est, x0=(b0, b1)) if len(est) >= 50 else (float("nan"), float("nan"))
        if len(est) >= 50:
            null = minimize_scalar(lambda x: sb.nll((x, 0.0), est), bounds=(-12, 4), method="bounded")
            ddev = 2 * (null.fun - sb.nll((e0, e1), est))
        else:
            ddev = float("nan")
        raw_called = [e for e in es if sb.craw(e) >= sb.THRESH]
        ancs = sorted({e["anchor"] for e in es}); oof = {}
        for A_ in ancs:
            f0, f1 = sb.fit([e for e in es if e["anchor"] != A_], x0=(b0, b1))
            for e in es:
                if e["anchor"] == A_: oof[id(e)] = sb.cbud(e, f0, f1)
        lo = [e for e in es if oof[id(e)] >= sb.THRESH]
        est_ids = {id(e) for e in est}
        lo_wrong = sum(1 for e in lo if not e["right"]); lo_wrong_est = sum(1 for e in lo if not e["right"] and id(e) in est_ids)
        lo_nom = sum(1 - oof[id(e)] for e in lo)
        # Criterion (2), Amendment 1 D6: LOAO-called over ALL edges of the population, systematic_budget.main's
        # frac = len(lo_called) / len(filt) (the 74.4% of record; JUDGE-TRANSFER's 57.0% FAIL). Called over
        # raw-called is printed beside it and decides nothing.
        util = len(lo) / max(1, len(es))
        util_raw = len(lo) / max(1, len(raw_called))
        L.append("  [%s] edges %d (established %d) | b0 %+.4f b1 %+.4f | established-label refit b1 %+.4f, delta-dev vs b1=0: %.2f -> %s"
                 % (tag, len(es), len(est), b0, b1, e1, ddev, "IDENTIFIED" if ddev >= 3.84 else "NOT identified"))
        L.append("      LOAO at %.3f: called %d of %d edges (utility %.1f%% -> %s; criterion (2), denominator = all edges of the population)"
                 " | called/raw-called %d/%d = %.1f%% (non-deciding) | wrong %d (established %d) | nominal %.2f -> %s"
                 % (sb.THRESH, len(lo), len(es), 100 * util, "PASS" if util >= 0.60 else "FAIL", len(lo), len(raw_called), 100 * util_raw,
                    lo_wrong, lo_wrong_est, lo_nom,
                    "UNDETERMINED (power rule: nominal < 3)" if lo_nom < 3 else "%.1fx all / %.1fx established" % (lo_wrong / lo_nom, lo_wrong_est / lo_nom)))
        L.append("      prediction b1 in [1.72, 7.87]: %s (established-label b1 %+.3f)" % ("HELD" if 1.72 <= e1 <= 7.87 else "FAILED", e1))
    L.append("  Consequence if b1 is identified and utility passes: ORDERED-JUDGED becomes available for the shipped judge; otherwise fallback stays.")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first payload, post nothing")
    ap.add_argument("--run", action="store_true", help="post the judge calls (resumes from the cache)")
    ap.add_argument("--report", action="store_true", help="guard + readout on the cache, 0 calls (give the pilot's --pilot N to read its guard)")
    ap.add_argument("--analyze", action="store_true", help="guard, then systematic_budget on this cache (writes nothing on an absent cache)")
    ap.add_argument("--pilot", type=int, default=None, help="limit to the first N matches of the schedule (by match_id); --report/--analyze evaluate the guard on the same slice")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=MAXTOK_DEFAULT, help="completion cap posted per call (default %d)" % MAXTOK_DEFAULT)
    a = ap.parse_args()
    MAXTOK = a.maxtok
    if a.dry_run: dry_run(a.pilot)
    elif a.run: run(a.pilot, a.workers)
    elif a.report:
        L = []; ok = guard_and_summary(L, a.pilot); print("\n".join(L)); sys.exit(0 if ok else 2)
    elif a.analyze: analyze(a.pilot)
    else: ap.print_help()
