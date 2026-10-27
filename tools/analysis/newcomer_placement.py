"""NEWCOMER-PLACEMENT-LIVE - place two real newcomers by the ARENA-13 protocol at the registered budget
(FRAMEWORK.md "Tests to register before shipping" item 22, registered by reference at commit eaf1dbf;
parameters fixed in docs/plan_2026-09-15.md; Amendment 1 D5 and D2 bind the reference, the readout and the
temperature; the dry-run review of 2026-09-15 is applied in full).

  python tools/analysis/newcomer_placement.py --dry-run [--pilot N] [--newcomer M]   (assembles every payload, posts nothing)
  python tools/analysis/newcomer_placement.py --run [--pilot N] [--newcomer M] [--workers 8] [--maxtok 8192]
  python tools/analysis/newcomer_placement.py --run --retry-unusable [--maxtok 16384]   (re-posts ONLY invalid rows of the UNDECIDED step)
  python tools/analysis/newcomer_placement.py --analyze [--draws 2000]

WHAT IS PLACED. claude-3-5-sonnet-20241022 (frontier-adjacent) and gpt-4o-mini (mid-board): both have eval-side
traces (eval_results.model_output) and both are absent from x12. Each is placed ONE AT A TIME onto the 20-model
BOARD OF RECORD (x12 cache + x20 cache, the rows x20_merged.merged_rows reads) with ITS OWN x20 edges WITHHELD, so
the board it enters is the 19 incumbents and the only evidence about it is what the protocol buys. Its withheld
x20 edges (19 x 100 unfiltered matches) and its key tier remain as comparators the protocol never sees.
The PEER newcomer is an incumbent on the board (with its full x20 edges) but is EXCLUDED FROM THE ANCHOR SET
(D5): no protocol edge is judged against a model whose own placement is the other half of this test.

THE PROTOCOL (arena13.py / placebo_entry.py, at the budget FRAMEWORK L189 registers): 400 answer-disagreement-
filtered matches per newcomer = 4 anchors x 100 questions, anchors chosen SEQUENTIALLY BY BISECTION of the
incumbent board (M3's rule: anchor = the middle of the open interval, move up or down on the dual-order outcome
of the 100 matches; synthetic_arena_scaling.insert), questions drawn ONLY from the pool of record, the
CACHED_SOLVE grok-reasoning REFERENCE of the board of record (rejudge_reference.set_reference('grok-reasoning'),
the reference STACK-v2, the x12 and the x20 caches all carry; D5 - NOT ARENA-13's in-roster ensemble, which
ENSEMBLE-REF upheld against and which contained each newcomer's sibling), STACK-v2 prompt (v2 mechanics + anchor
rubric + reference block + JSON schema), grok-4-1-fast-non-reasoning (the newcomer-placement judge of record,
FRAMEWORK L73), DUAL ORDER with TIE on flip and no third call (NO-TIES). 4 x 100 x 2 = 800 calls per newcomer,
1,600 in all; 0 reference solves.

READOUTS, per newcomer (D5). PRIMARY, single-source (only the protocol's own grok-judged edges): for each of the
four anchors, the dual-order win share (ties 1/2) with a QUESTION-CLUSTERED bootstrap at B = 2,000 -> the anchor
is certified below the newcomer, certified above it, or unseparated at 0.975 (and 0.95), with the opposite-draw
count printed behind every certificate; the certificates are mapped onto the incumbents' order (a position BAND
on the 20-model board) and onto the x20 KEY TIERS (x20_replications.key_tiers at the 0.017 gap over the
x20-judged questions, exactly as x20_merged.py); the class is BANDED / PROVISIONAL - never a rank.
SECONDARY, labelled MIXED-FIT / EXTRAPOLATED and never the verdict (FRAMEWORK L85, L238): the merged
Bradley-Terry fit of the incumbents' Mistral-judged unfiltered edges plus the newcomer's grok-judged filtered
edges, with its bootstrap band, printed with the scale caveat (ARENA-13: filtering widens the theta scale ~13%).
CRITERION (item 22): the certificate's key-tier interval spans <= 2 adjacent key tiers and contains the newcomer's
key tier, for both; the frontier newcomer is BANDED with no top-tier rank. FALSIFIER: an interval wider than 2
tiers (then 400 matches is not a placement budget).

INVARIANTS: pool_guard first; questions only from p2dca21ab5f4ef3ae (printed first); own cache; finish_reason,
completion tokens and the max_tokens cap per verdict row (call_judge_full); explicit --maxtok; temperature
OMITTED (D2, recorded in meta and printed in every header); resume from cache; a guard that REFUSES a verdict
(and refuses to take a bisection step) when more than 5% of the deciding matches are unparsed or non-terminated,
with --retry-unusable as the exit (re-posts only the invalid rows of the refused, undecided step at a raised cap,
logged in meta max_tokens_history; fresh rows are never posted in a retry and the cap of record stays, so a later
--run at the original cap resumes); a DECIDED step is frozen: its steps row is never rewritten and its direction is
read from that row, so a retry can never flip a taken bisection step; Meta-Llama-3-70B-Instruct excluded and asserted absent; --pilot N (refused once the full
schedule exists); the x12all cache of record is read through a read-only URI; the dry run creates no cache;
pilot or partial caches never write the outcome file of record; the producing script's sha is pinned at first
launch and resumes are appended to meta.
"""
import os, sys, json, time, random, sqlite3, argparse, threading, hashlib, inspect, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import x20_replications as xr
import prompt_v2

for _s in (sys.stdout, sys.stderr):   # the prompts carry an em dash and box characters; a cp1252 console must not abort the verbatim print
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

POOL_ID = pool_guard.FROZEN_POOL_ID                      # p2dca21ab5f4ef3ae
NEWCOMERS = ["claude-3-5-sonnet-20241022", "gpt-4o-mini"]
FRONTIER_NEWCOMER = "claude-3-5-sonnet-20241022"
FRONTIER = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "arx_3", "gpt-4o-2024-08-06"]   # x20 TOP6 minus the newcomer
EXCLUDED = "Meta-Llama-3-70B-Instruct"
REFERENCE = "grok-reasoning"   # D5: the CACHED_SOLVE reference of the board of record (stack_judge.run, arena_v2_x20)
N_ANCHORS = 4
PER_ANCHOR = 100
SEED = 42
CONF = 0.975
DRAWS = 2000           # FRAMEWORK L85: B >= 2,000 when a tail is published at 0.975
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "newcomer_placement.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "newcomer_placement_outcome.txt")
JUDGES = {"grok": "grok-4-1-fast-non-reasoning", "mistral": "Mistral-Large-3"}
JUDGE = "grok"
MAXTOK = 8192          # rejudge_reasoning's default, the constant ARENA-13 / PLACEBO-ENTRY posted; explicit here
TEMPERATURE = None     # D2: None = field omitted (byte-identical to ARENA-13 and every cache compared with); --temperature writes a literal
PROTOCOL = ("ARENA-13 newcomer protocol at the registered budget: 4 anchors by sequential bisection of the "
            "19-incumbent board of record (peer newcomer excluded from the anchor set) x %d pool questions, "
            "answer-disagreement filter, CACHED_SOLVE grok-reasoning reference (the board of record's reference), "
            "STACK-v2 (prompt v2 + anchor rubric + reference block), dual order, TIE on flip, "
            "no third call (NO-TIES)" % PER_ANCHOR)
MID_BASE = 80_000_000
RETRY_UNUSABLE = False
SCRIPT_SHA = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]


# ---------------------------------------------------------------- data

def setup():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL_ID,))}
    assert pool, "pool of record %s not recorded in reserved_pool" % POOL_ID
    P = defaultdict(dict); K = defaultdict(dict)
    for q, m, p, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if q in pool: P[q][m] = (p or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    ev.close()
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    rubrics = sj.anchor_rubrics()
    rref.set_reference(REFERENCE); refs = rref.references()      # D5: exactly stack_judge.run's reference (stack_judge.py:99)
    assert rref.SOLVE_DB.endswith(os.path.join("judge_solve", REFERENCE + ".db")), rref.SOLVE_DB
    return pool, P, K, route, anchor_of, rubrics, refs


def x12all_path():
    """The x12 half of the board of record, the path stack_judge.cache_path() builds for PROMPT='v2', JUDGE='mistral',
    ALL_X12=True (stack_judge.py:35-40, as x20_merged.merged_rows sets it at x20_merged.py:29-30). Local copy so this
    script can open it READ-ONLY instead of through sj.open_cache() (which opens read-write with CREATE TABLE)."""
    p = sj.CACHE.replace("stack_v2.db", "stack_v2_promptv2.db").replace(".db", "_x12all.db")
    saved = (sj.PROMPT, sj.JUDGE, sj.ALL_X12, sj.DATACARD)
    try:
        sj.PROMPT, sj.JUDGE, sj.ALL_X12, sj.DATACARD = "v2", "mistral", True, False
        assert p == sj.cache_path(), "x12all path drifted from stack_judge.cache_path(): %s vs %s" % (p, sj.cache_path())
    finally:
        sj.PROMPT, sj.JUDGE, sj.ALL_X12, sj.DATACARD = saved
    return p


def board_of_record():
    """The merged 20-model board (x12 cache + x20 cache), rows (a, b, qid, winner, invalid) with invalid dropped.
    Same rows as x20_merged.merged_rows (x20_merged.py:27-31), both halves opened read-only."""
    c20 = sqlite3.connect("file:%s?mode=ro" % xr.X20, uri=True)
    r20 = [r for r in c20.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]; c20.close()
    c12 = sqlite3.connect("file:%s?mode=ro" % x12all_path(), uri=True)
    r12 = [r for r in c12.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]; c12.close()
    rows = r12 + r20
    models = sorted({r[0] for r in rows} | {r[1] for r in rows})
    assert EXCLUDED not in models, "%s must not be on the board" % EXCLUDED
    assert all(n in models for n in NEWCOMERS), "newcomers must be on the x20 board of record (their edges are withheld)"
    return rows, models, len(r12), len(r20)


def votes(rows, drop_ties=False):
    out = []
    for a, b, q, w, *_ in rows:
        if w == "TIE":
            if drop_ties: continue
            out.append((a, b, 0.5, 1.0))
        else: out.append((a, b, 1.0 if w == a else 0.0, 1.0))
    return out


def incumbent_order(rows, models, new):
    """The 19 incumbents in descending theta with the newcomer's edges withheld (bisection reads this board)."""
    inc = [r for r in rows if new not in (r[0], r[1])]
    ms = [m for m in models if m != new]
    th = jf.board_from(votes(inc), ms)
    return sorted(ms, key=lambda m: -th[m]), th, inc


def peer_exclusions(new):
    """D5: the peer newcomer is never an anchor."""
    return [n for n in NEWCOMERS if n != new]


def candidates(new, opp, pool, P, route, refs):
    """Pool questions where the two disagree, routed, and carrying the reference of record; deterministic per pair."""
    cand = [q for q in sorted(pool)
            if P[q].get(new) and P[q].get(opp) and P[q][new] != P[q][opp]
            and q in route and q in refs]
    random.Random("%d:%s:%s" % (SEED, new, opp)).shuffle(cand)
    return cand


def payload(new, opp, qid, evals, route, anchor_of, rubrics, refs):
    """(system, user_fwd, user_rev): fwd = newcomer as Model A, rev = opponent as Model A. Byte-identical
    construction to stack_judge.run (v2 system on the routed anchor, with_reference on the grok-reasoning reference)."""
    rn, ro = evals.get((qid, new)), evals.get((qid, opp))
    if rn is None or ro is None: return None
    ref = refs.get(qid)
    if ref is None: return None
    sp, rub = rubrics[anchor_of(route[qid])]
    system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
    q = rref.with_reference(rn[0], ref)
    tn = rj.robust_trace(rn[2], rn[3], rn[1]); to = rj.robust_trace(ro[2], ro[3], ro[1])
    return system, rj.build_user_prompt(q, tn, to), rj.build_user_prompt(q, to, tn)


def request_body(system, user):
    """Local copy of the body rejudge_reasoning.call_judge_full posts (rejudge_reasoning.py:96-101), so the dry run can
    print the model field of what --run would post. assert_body_fidelity() checks the copy against the source."""
    body = {"model": JUDGES[JUDGE], "max_tokens": MAXTOK,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if TEMPERATURE is not None: body["temperature"] = TEMPERATURE
    return body


def assert_body_fidelity():
    src = inspect.getsource(rr.payload_body)   # 2026-09-16: the body builder was factored out of call_judge_full (JUDGE-WIRING), bytes unchanged
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    assert '{"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and '"messages": [{"role": "system", "content": system},' in src \
        and 'payload_body["temperature"] = TEMPERATURE' in src, "rejudge_reasoning.call_judge_full's body changed; update request_body()"
    keys = tuple(request_body("s", "u").keys())
    assert keys == (("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ())), keys


# ---------------------------------------------------------------- cache

def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, newcomer TEXT, step INTEGER, opponent TEXT, "
                "qid INTEGER, anchor TEXT, lo INTEGER, hi INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, "
                "finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))")
    if "max_tokens" not in {r[1] for r in con.execute("PRAGMA table_info(verdicts)")}:
        con.execute("ALTER TABLE verdicts ADD COLUMN max_tokens INTEGER")
    con.execute("CREATE TABLE IF NOT EXISTS steps (newcomer TEXT, step INTEGER, opponent TEXT, lo INTEGER, hi INTEGER, "
                "wins INTEGER, losses INTEGER, ties INTEGER, unusable INTEGER, direction TEXT, ts REAL, PRIMARY KEY (newcomer, step))")
    con.commit(); return con


def open_cache_ro():
    if not os.path.exists(CACHE): return None
    return sqlite3.connect("file:%s?mode=ro" % CACHE, uri=True)


def record_meta(con):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    meta = {"pool_id": POOL_ID, "judge": JUDGE, "judge_model": JUDGES[JUDGE], "provider": "azure", "protocol": PROTOCOL,
            "reference": REFERENCE, "max_tokens": str(MAXTOK), "temperature": "omitted" if TEMPERATURE is None else repr(TEMPERATURE),
            "seed": str(SEED), "per_anchor": str(PER_ANCHOR), "n_anchors": str(N_ANCHORS), "conf": str(CONF),
            "newcomers": ",".join(NEWCOMERS), "script_sha256_16": SCRIPT_SHA, "created": now, "started": now}
    stored = dict(con.execute("SELECT key, value FROM meta"))
    if stored:                                                   # a resume: appended, never overwritten
        con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((stored.get("resumed", "") + ";" + now).strip(";"),))
        if stored.get("script_sha256_16") not in (None, SCRIPT_SHA):
            print("  NOTE: cache was first produced by script sha %s; this script is %s (resume recorded)" % (stored.get("script_sha256_16"), SCRIPT_SHA))
    if RETRY_UNUSABLE and stored and stored.get("max_tokens") != meta["max_tokens"]:
        assert int(meta["max_tokens"]) > int(stored["max_tokens"]), "--retry-unusable only RAISES the cap (cache %s, asked %s)" % (stored["max_tokens"], meta["max_tokens"])
        hist = (stored.get("max_tokens_history", stored["max_tokens"]) + ";%s@%s" % (meta["max_tokens"], now))
        con.execute("INSERT OR REPLACE INTO meta VALUES ('max_tokens_history', ?)", (hist,))
        # meta max_tokens (the cap of record for fresh rows) is NOT overwritten: a retry posts only invalid rows, each
        # re-posted row carries the raised cap in its own max_tokens column, and a later --run at the original cap resumes
        print("  cap raised for --retry-unusable: invalid rows re-posted at max_tokens %s (cap of record stays %s; meta max_tokens_history: %s)" % (meta["max_tokens"], stored["max_tokens"], hist))
    for k, v in meta.items():
        con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", (k, v))
    con.commit()
    stored = dict(con.execute("SELECT key, value FROM meta"))
    for k in ("judge_model", "max_tokens", "temperature", "per_anchor", "n_anchors", "seed", "protocol", "reference"):
        if k == "max_tokens" and RETRY_UNUSABLE: continue           # a raised retry cap is checked and logged above
        assert stored[k] == meta[k], ("cache %s was written with %s=%s; this run has %s (a different cap needs --retry-unusable "
                                      "to raise it on the invalid rows, or a new --cache)" % (CACHE, k, stored[k], meta[k]))


def mid_for(ni, step, i): return MID_BASE + ni * 1_000_000 + step * 10_000 + i


# ---------------------------------------------------------------- bisection

def next_anchor(order, lo, hi, used):
    mid = (lo + hi) // 2
    if not (0 <= mid < len(order)) or order[mid] in used:
        cands = [i for i in range(len(order)) if order[i] not in used]
        mid = min(cands, key=lambda i: abs(i - mid))
    return mid, order[mid]


def move(lo, hi, mid, newcomer_above):
    return (lo, mid - 1) if newcomer_above else (mid + 1, hi)


def dual_verdicts(con, mids, new, opp):
    """mid -> dual-order verdict in {new, opp, TIE, None, PENDING}; None = unusable (either order unparsed / non-terminated)."""
    V = defaultdict(dict)
    mids = list(mids)
    for i in range(0, len(mids), 500):
        chunk = mids[i:i + 500]; marks = ",".join("?" * len(chunk))
        for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts WHERE mid IN (%s)" % marks, chunk):
            V[m][arm] = None if inv else w
    out = {}
    for m in mids:
        d = V.get(m, {})
        if "fwd" not in d or "rev" not in d: out[m] = "PENDING"; continue
        if d["fwd"] is None or d["rev"] is None: out[m] = None; continue
        out[m] = d["fwd"] if d["fwd"] == d["rev"] else "TIE"      # rj.combine_orders in the model-name frame
    return out


def tally(dv, new, opp):
    wins = sum(1 for v in dv.values() if v == new); losses = sum(1 for v in dv.values() if v == opp)
    ties = sum(1 for v in dv.values() if v == "TIE"); unusable = sum(1 for v in dv.values() if v is None)
    pending = sum(1 for v in dv.values() if v == "PENDING")
    return wins, losses, ties, unusable, pending


def reachable_tree(order, used0):
    """Every (step, lo, hi, idx, anchor) the bisection can visit: the dry run assembles all of them."""
    nodes = []
    def rec(step, lo, hi, used):
        if step > N_ANCHORS: return
        idx, anc = next_anchor(order, lo, hi, used)
        nodes.append((step, lo, hi, idx, anc))
        for up in (True, False):
            l2, h2 = move(lo, hi, idx, up)
            rec(step + 1, l2, h2, used + [anc])
    rec(1, 0, len(order) - 1, list(used0))
    return nodes


# ---------------------------------------------------------------- dry run

def dry_run(pilot, newcomers):
    print("pool of record %s" % POOL_ID)
    pool, P, K, route, anchor_of, rubrics, refs = setup()
    print("  %d questions in the pool; questions are drawn from this set only" % len(pool))
    print("reference: CACHED_SOLVE %s (%s), the board of record's reference (D5): %d of %d pool questions covered"
          % (REFERENCE, os.path.relpath(rref.SOLVE_DB, ROOT), sum(1 for q in pool if q in refs), len(pool)))
    rows, models, n12, n20 = board_of_record()
    print("board of record: x12 %d + x20 %d = %d verdicts | %d models | %s absent: OK | both caches opened read-only" % (n12, n20, len(rows), len(models), EXCLUDED))
    assert_body_fidelity()
    per = pilot if pilot else PER_ANCHOR
    steps = 1 if pilot else N_ANCHORS
    posted = 0; assembled = 0; first = None; short = []
    for new in newcomers:
        order, th, inc = incumbent_order(rows, models, new)
        used0 = peer_exclusions(new)
        print("\n[%s] incumbent board (19, newcomer's %d x20 edges withheld; peer newcomer %s is an incumbent but never an anchor):"
              % (new, sum(1 for r in rows if new in (r[0], r[1])), ", ".join(used0)))
        for i, m in enumerate(order): print("    %2d. %-30s %+.3f%s" % (i + 1, m, th[m], "   (peer newcomer: excluded from anchors)" if m in used0 else ""))
        tree = [n for n in reachable_tree(order, used0) if n[0] <= steps]
        opps = {n[4] for n in tree}
        assert EXCLUDED not in opps and not (opps & set(used0)), "excluded models reachable as anchors: %s" % (opps & (set(used0) | {EXCLUDED}))
        cand = {opp: candidates(new, opp, pool, P, route, refs) for opp in opps}
        qids = {q for opp in opps for q in cand[opp][:per]}
        evals = rj.load_eval_rows(qids, {new} | opps)
        print("  reachable bisection tree (%d nodes; the run visits %d of them, one per step):" % (len(tree), steps))
        for step, lo, hi, idx, anc in tree:
            take = cand[anc][:per]
            built = [payload(new, anc, q, evals, route, anchor_of, rubrics, refs) for q in take]
            built = [b for b in built if b is not None]
            assembled += 2 * len(built)
            if first is None and built: first = (new, anc, take[0], built[0])
            dec = sum(1 for q in take if K[q][new] != K[q].get(anc, 0))
            flag = "" if len(cand[anc]) >= per and len(built) == per else "   <- SHORT"
            if flag: short.append((new, anc))
            print("    step %d [%2d,%2d] anchor #%2d %-30s candidates %4d -> %3d matches (%d payloads) | key-decidable %3d (%.0f%%)%s"
                  % (step, lo, hi, idx + 1, anc, len(cand[anc]), len(take), 2 * len(built), dec, 100 * dec / max(1, len(take)), flag))
        posted += steps * per * 2
    print("\ncall count: %d calls would be POSTED by --run (%d newcomers x %d anchors x %d matches x 2 orders); %d payloads assembled over the reachable tree; 0 reference solves"
          % (posted, len(newcomers), steps, per, assembled))
    print("protocol: %s" % PROTOCOL)
    print("judge: %s on azure | cap: max_tokens=%d | temperature: %s (D2) | finish_reason, completion_tokens and max_tokens stored per call (call_judge_full)"
          % (JUDGES[JUDGE], MAXTOK, "omitted" if TEMPERATURE is None else TEMPERATURE))
    print("cache: %s%s (the dry run opens no cache)" % (CACHE, " (exists)" if os.path.exists(CACHE) else " (new)"))
    print("guard: verdict refused, and no bisection step taken, above 5% unparsed/non-terminated on the deciding matches; exit = --run --retry-unusable [--maxtok N]")
    print("script sha256[:16] %s" % SCRIPT_SHA)
    new, anc, q, (system, ufwd, urev) = first
    body = request_body(system, ufwd)
    print("first payload body: model=%s | max_tokens=%d | keys=%s | temperature=%s" % (body["model"], body["max_tokens"], tuple(body.keys()), body.get("temperature", "omitted")))
    print("\n===== FIRST PAYLOAD: %s vs %s, question %d, order fwd (newcomer = Model A) =====" % (new, anc, q))
    print("----- system -----"); print(system)
    print("----- user -----"); print(ufwd)
    print("===== END FIRST PAYLOAD =====")
    if short:
        print("DRY-RUN FAILED: short candidate lists for %s" % short); sys.exit(1)
    print("dry run OK: 0 calls posted, no cache created")


# ---------------------------------------------------------------- live run

def judge_call(system, user):
    content, provider, ctok, _, finish, msg = rr.call_judge_full(system, user)
    if finish == "content_filter" and isinstance(msg, dict):   # keep the refusal body and response id as the raw text (provenance)
        return "error: HTTP 400 content_filter " + str(msg.get("_refusal", ""))[:300] + " id=" + str(msg.get("_response_id", "")), finish, ctok, provider
    return rr.strip_think(content), finish, ctok, provider


def judge_jobs(con, jobs, workers, label):
    """jobs: (mid, arm, system, user, mapping). Stores one verdict row per call (with the cap it was posted at); resumable."""
    lock = threading.Lock(); ok = err = 0
    def one(job):
        mid, arm, system, user, mp = job
        try:
            raw, finish, ctok, provider = judge_call(system, user)
        except urllib.error.HTTPError as e:
            # A provider REFUSAL (HTTP 400 whose body carries finish_reason=content_filter) is deterministic: re-posting
            # it forever stalls the step, and not caching it makes the match vanish from the guard denominator (the
            # failure class that lost 4389 and 6528 in ARENA-V2). Cache it as an UNUSABLE row with that finish_reason,
            # so it counts against the 5% guard like a truncation. Any other HTTP error is still raised (retried on resume).
            body = ""
            try: body = e.read().decode("utf-8", "replace")
            except Exception: pass
            if e.code == 400 and "content_filter" in body:
                return (mid, arm, "INVALID", 1, "error: HTTP 400 content_filter " + body[:300], time.time(), "content_filter", 0, "azure", MAXTOK)
            raise
        if finish == "length":
            return (mid, arm, "NON_TERMINATED", 1, raw, time.time(), finish, ctok, provider, MAXTOK)
        v, _ = rj.parse_judge(raw)
        w = mp.get(v, "INVALID")
        return (mid, arm, w, int(w == "INVALID"), raw, time.time(), finish, ctok, provider, MAXTOK)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0], futs[f][1], str(e)[:100]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 50 == 0 or i == len(jobs): print("  %s %d/%d (ok %d, err %d)" % (label, i, len(jobs), ok, err), flush=True)
    return ok, err


def run(pilot, workers, newcomers):
    print("pool of record %s" % POOL_ID)
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGES[JUDGE]; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE; rr.load_env()
    if JUDGE == "mistral":
        p8.load_env(); rr.AZURE_KEY = p8.KEY        # the Mistral deployment is keyed by AZURE_AI_API_KEY (rubric_p8), not the grok key
    pool, P, K, route, anchor_of, rubrics, refs = setup()
    rows, models, n12, n20 = board_of_record()
    con = open_cache(); record_meta(con)
    per = pilot if pilot else PER_ANCHOR
    steps = 1 if pilot else N_ANCHORS
    print("NEWCOMER-PLACEMENT-LIVE: judge %s | max_tokens %d | temperature %s | reference %s | %d newcomers x %d anchors x %d matches x 2 | workers %d | cache %s%s"
          % (JUDGES[JUDGE], MAXTOK, "omitted" if TEMPERATURE is None else TEMPERATURE, REFERENCE, len(newcomers), steps, per, workers, CACHE,
             " | RETRY-UNUSABLE: only invalid rows are re-posted" if RETRY_UNUSABLE else ""), flush=True)
    for new in newcomers:
        ni = NEWCOMERS.index(new)
        order, th, inc = incumbent_order(rows, models, new)
        lo, hi, used = 0, len(order) - 1, peer_exclusions(new)
        for step in range(1, steps + 1):
            sched = con.execute("SELECT mid, opponent, qid, lo, hi FROM schedule WHERE newcomer=? AND step=? ORDER BY mid", (new, step)).fetchall()
            if sched:
                opp = sched[0][1]
                assert (sched[0][3], sched[0][4]) == (lo, hi), "cached step %d of %s was scheduled on interval %s, recomputed %s" % (step, new, sched[0][3:5], (lo, hi))
                idx = order.index(opp)
                if len(sched) > per:
                    if pilot:
                        print("  REFUSED: --pilot %d but the cached schedule for %s step %d already holds %d rows (> %d); rerun with --pilot >= %d or without --pilot"
                              % (pilot, new, step, len(sched), pilot, len(sched))); sys.exit(4)
                    sched = sched[:per]
                elif len(sched) < per:                              # a full run extends a pilot's short schedule: same
                    take = candidates(new, opp, pool, P, route, refs)[:per]   # deterministic list, same index-based mids
                    assert len(take) == per, "only %d candidates for %s vs %s" % (len(take), new, opp)
                    assert [q for _, _, q, _, _ in sched] == take[:len(sched)], "cached schedule for %s step %d is not a prefix of the deterministic candidate list" % (new, step)
                    ext = [(mid_for(ni, step, i), opp, take[i], lo, hi) for i in range(len(sched), per)]
                    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?)",
                                    [(m, new, step, opp, q, anchor_of(route[q]), lo, hi) for m, _, q, _, _ in ext]); con.commit()
                    sched = sched + ext
            elif RETRY_UNUSABLE:                                    # a retry re-posts invalid rows only: it schedules nothing new
                print("[%s] step %d: not scheduled yet; --retry-unusable posts only invalid rows of an already scheduled step. Rerun --run to continue" % (new, step), flush=True)
                break
            else:
                idx, opp = next_anchor(order, lo, hi, used)
                assert opp != EXCLUDED and opp not in peer_exclusions(new)
                take = candidates(new, opp, pool, P, route, refs)[:per]
                assert len(take) == per, "only %d candidates for %s vs %s" % (len(take), new, opp)
                sched = [(mid_for(ni, step, i), opp, q, lo, hi) for i, q in enumerate(take)]
                con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?)",
                                [(m, new, step, opp, q, anchor_of(route[q]), lo, hi) for m, _, q, _, _ in sched]); con.commit()
            used.append(opp)
            mids = [s[0] for s in sched]
            have = {(m, a): inv for m, a, inv in con.execute("SELECT mid, arm, invalid FROM verdicts WHERE mid IN (%s)" % ",".join("?" * len(mids)), mids)}
            # a DECIDED step is frozen: a steps row decided on this very schedule (its tally covers every scheduled match)
            # fixes the direction of record; it is never rewritten, and a retry never touches its rows (even the invalid ones)
            srow = con.execute("SELECT opponent, lo, hi, wins, losses, ties, unusable, direction FROM steps WHERE newcomer=? AND step=?", (new, step)).fetchone()
            frozen = srow is not None and sum(srow[3:7]) == len(mids)
            if srow is not None and not frozen:                     # a pilot's short row being extended to the full schedule
                print("  steps row of %s step %d was decided on %d rows; the schedule now holds %d: the step is re-decided on the full schedule and the short row superseded"
                      % (new, step, sum(srow[3:7]), len(mids)))
            if RETRY_UNUSABLE:
                todo = set() if frozen else {k for k, inv in have.items() if inv}      # invalid rows of the undecided step only; fresh rows wait for --run
            else:
                todo = {(m, a) for m in mids for a in ("fwd", "rev")} - set(have)
            evals = rj.load_eval_rows([s[2] for s in sched], {new, opp})
            jobs = []
            for m, _, q, _, _ in sched:
                pl = payload(new, opp, q, evals, route, anchor_of, rubrics, refs)
                assert pl is not None, "payload could not be built for mid %d" % m
                system, ufwd, urev = pl
                if (m, "fwd") in todo: jobs.append((m, "fwd", system, ufwd, {"Model A": new, "Model B": opp, "TIE": "TIE"}))
                if (m, "rev") in todo: jobs.append((m, "rev", system, urev, {"Model A": opp, "Model B": new, "TIE": "TIE"}))
            print("[%s] step %d: interval [%d,%d] -> anchor #%d %s | %d matches | %d calls to post%s"
                  % (new, step, lo, hi, idx + 1, opp, len(mids), len(jobs), " | DECIDED (%s): frozen, direction read from the steps row" % srow[7] if frozen else ""), flush=True)
            if jobs: judge_jobs(con, jobs, workers, "%s/step%d" % (new[:12], step))
            dv = dual_verdicts(con, mids, new, opp)
            wins, losses, ties, unusable, pending = tally(dv, new, opp)
            if pending:
                print("  %d matches still pending after the pass (%s); rerun --run to resume before the step can be decided"
                      % (pending, "fresh rows are not posted by --retry-unusable" if RETRY_UNUSABLE else "errors")); sys.exit(3)
            if unusable / max(1, len(mids)) > 0.05:
                fr = dict(con.execute("SELECT COALESCE(finish,'(none)'), COUNT(*) FROM verdicts WHERE invalid=1 AND mid IN (%s) GROUP BY 1" % ",".join("?" * len(mids)), mids))
                print("  GUARD: %d of %d matches (%.1f%%) unparsed or non-terminated on this step; the bisection step is NOT taken."
                      " finish_reason among the invalid rows: %s. Exit: rerun `--run --retry-unusable` (re-posts ONLY the invalid rows of this step;"
                      " add --maxtok N above %d if finish_reason is 'length'; the raised cap is logged in meta max_tokens_history and per row)."
                      % (unusable, len(mids), 100 * unusable / len(mids), fr, MAXTOK))
                sys.exit(2)
            if frozen:
                assert srow[0] == opp, "steps row of %s step %d names %s, schedule names %s" % (new, step, srow[0], opp)
                above = srow[7] == "up"
                if tuple(srow[3:7]) != (wins, losses, ties, unusable):
                    print("  NOTE: steps row of record holds %d : %d (ties %d, unusable %d); the verdict rows now tally %d : %d (ties %d, unusable %d)"
                          " (delta %+d : %+d, ties %+d, unusable %+d); the recorded direction '%s' stands, a decided step is never re-decided"
                          % (srow[3], srow[4], srow[5], srow[6], wins, losses, ties, unusable,
                             wins - srow[3], losses - srow[4], ties - srow[5], unusable - srow[6], srow[7]), flush=True)
            else:
                above = wins > losses
                con.execute("INSERT OR REPLACE INTO steps VALUES (?,?,?,?,?,?,?,?,?,?,?)",      # a new row, or a pilot's short row superseded (see above)
                            (new, step, opp, lo, hi, wins, losses, ties, unusable, "up" if above else "down", time.time())); con.commit()
            print("  newcomer %d : %d (ties %d, unusable %d) vs %s -> %s%s" % (wins, losses, ties, unusable, opp, "ABOVE, search up" if above else "not above, search down",
                                                                          " (of record)" if frozen else ""), flush=True)
            lo, hi = move(lo, hi, idx, above)
    print("done. Run --analyze for the placement readouts.", flush=True)


# ---------------------------------------------------------------- analysis

def q_bootstrap(items, draws, stat, rng):
    """Question-clustered bootstrap: items = {qid: [values]}; stat(list of values) -> float. Returns the sorted draws."""
    qs = sorted(items); out = []
    for _ in range(draws):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        out.append(stat([v for q in pick for v in items[q]]))
    return sorted(out)


def analyze(draws, newcomers):
    print("pool of record %s" % POOL_ID)
    pool, P, K, route, anchor_of, rubrics, refs = setup()
    rows, models, n12, n20 = board_of_record()
    con = open_cache_ro()
    if con is None:
        print("no cache at %s: nothing judged, nothing written" % CACHE); return
    meta = dict(con.execute("SELECT key, value FROM meta"))
    L = ["=== NEWCOMER-PLACEMENT-LIVE (FRAMEWORK item 22) ===",
         "  pool %s | judge %s | max_tokens %s%s | temperature %s (D2: omitted = provider default) | reference %s | protocol: %s"
         % (POOL_ID, meta.get("judge_model"), meta.get("max_tokens"),
            " (history %s)" % meta["max_tokens_history"] if meta.get("max_tokens_history") else "",
            meta.get("temperature"), meta.get("reference", "(not recorded)"), meta.get("protocol")),
         "  board of record: x12 %d + x20 %d = %d verdicts, %d models; %s absent; incumbents' edges Mistral-judged and UNFILTERED, protocol edges grok-judged and answer-disagreement FILTERED (never one fit: FRAMEWORK L85/L238)"
         % (n12, n20, len(rows), len(models), EXCLUDED),
         "  producing script sha %s | this script %s%s | started %s | resumed %s" % (meta.get("script_sha256_16"), SCRIPT_SHA,
             "" if meta.get("script_sha256_16") in (None, SCRIPT_SHA) else " (DIFFERS)", meta.get("started"), meta.get("resumed", "-"))]
    # key tiers of record: x20_merged's object (accuracy over the x20-judged questions, 0.017 gap)
    qs_judged = sorted({r[2] for r in rows})
    Kall = defaultdict(dict)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models: Kall[q][m] = int(c or 0)
    ev.close()
    acc = {m: sum(Kall[q][m] for q in qs_judged if m in Kall.get(q, {})) / max(1, sum(1 for q in qs_judged if m in Kall.get(q, {}))) for m in models}
    kt = xr.key_tiers(acc, models); tier_of = {m: i for i, t in enumerate(kt) for m in t}
    L.append("  key tiers at %.3f gap over the %d x20-judged questions: %d (x20_merged.txt says 14 -> %s)"
             % (xr.KEY_GAP, len(qs_judged), len(kt), "OK" if len(kt) == 14 else "MISMATCH"))
    for i, t in enumerate(kt): L.append("    tier %2d: %s" % (i + 1, ", ".join("%s %.3f" % (m, acc[m]) for m in t)))
    results = {}; complete = True
    for new in newcomers:
        L.append(""); L.append("--- %s ---" % new)
        order, th_inc, inc = incumbent_order(rows, models, new)
        sched = con.execute("SELECT mid, step, opponent, qid FROM schedule WHERE newcomer=? ORDER BY mid", (new,)).fetchall()
        if not sched: L.append("  nothing scheduled"); complete = False; continue
        by_step = defaultdict(list)
        for m, step, opp, q in sched: by_step[step].append((m, opp, q))
        dv_all = {}
        for step, lst in by_step.items():
            opp = lst[0][1]
            dv = dual_verdicts(con, [m for m, _, _ in lst], new, opp)
            for m, _, q in lst: dv_all[m] = (opp, q, dv[m], step)
        steps_rows = con.execute("SELECT step, opponent, lo, hi, wins, losses, ties, unusable, direction FROM steps WHERE newcomer=? ORDER BY step", (new,)).fetchall()
        for step, opp, lo, hi, w, l, t, u, d in steps_rows:
            L.append("  step %d [%2d,%2d] vs %-30s %3d : %3d (ties %2d, unusable %2d) -> %s" % (step, lo, hi, opp, w, l, t, u, d))
        n_sched = len(sched); pending = sum(1 for v in dv_all.values() if v[2] == "PENDING"); unusable = sum(1 for v in dv_all.values() if v[2] is None)
        full = n_sched == N_ANCHORS * PER_ANCHOR and len(by_step) == N_ANCHORS
        if not full: complete = False
        L.append("  scheduled %d matches (%s) | judged %d | unusable (unparsed/non-terminated in either order) %d (%.1f%%)"
                 % (n_sched, "full schedule" if full else "PARTIAL / PILOT: %d of %d" % (n_sched, N_ANCHORS * PER_ANCHOR), n_sched - pending, unusable, 100 * unusable / max(1, n_sched)))
        if pending: L.append("  %d matches pending: the run is incomplete; no verdict" % pending); complete = False; continue
        if unusable / max(1, n_sched) > 0.05:
            fr = dict(con.execute("SELECT COALESCE(finish,'(none)'), COUNT(*) FROM verdicts WHERE invalid=1 AND mid IN (SELECT mid FROM schedule WHERE newcomer=?) GROUP BY 1", (new,)))
            L.append("  VERDICT REFUSED: %.1f%% of the deciding matches are unusable (> 5%%). finish_reason among them: %s. Exit: --run --retry-unusable [--maxtok N]" % (100 * unusable / n_sched, fr)); complete = False; continue
        usable = {m: v for m, v in dv_all.items() if v[2] is not None}
        dec = [m for m, (opp, q, v, _) in usable.items() if K[q][new] != K[q].get(opp, 0)]
        kacc = sum(1 for m in dec if usable[m][2] == (new if K[usable[m][1]][new] else usable[m][0])) / max(1, len(dec))
        L.append("  key-decidable %d of %d | judge accuracy there %.3f | ties %.3f" % (len(dec), len(usable), kacc, sum(1 for v in usable.values() if v[2] == "TIE") / len(usable)))

        # ---------- PRIMARY (D5): single-source, per anchor, question-clustered bootstrap ----------
        L.append("  PRIMARY (single-source: the protocol's own grok-judged edges only), per anchor, win share with ties 1/2, question-clustered bootstrap B=%d:" % draws)
        rng = random.Random(SEED)
        A_above, B_below, U_uns = {CONF: [], 0.95: []}, {CONF: [], 0.95: []}, {CONF: [], 0.95: []}
        anchors_met = []
        for step in sorted(by_step):
            opp = by_step[step][0][1]; idx = order.index(opp)
            items = defaultdict(list)
            for m, _, q in by_step[step]:
                v = usable.get(m)
                if v is None: continue
                items[q].append(1.0 if v[2] == new else (0.5 if v[2] == "TIE" else 0.0))
            n = sum(len(x) for x in items.values())
            if n == 0: L.append("    step %d vs %s: no usable match" % (step, opp)); continue
            share = sum(sum(x) for x in items.values()) / n
            bs = q_bootstrap(items, draws, lambda vs: sum(vs) / len(vs), rng)
            lo_i, hi_i = int(0.025 * draws), min(draws - 1, int(0.975 * draws))
            n_up = sum(1 for b in bs if b > 0.5); n_dn = sum(1 for b in bs if b < 0.5)
            status = {}
            for conf in (CONF, 0.95):
                if n_up / draws >= conf: status[conf] = "newcomer ABOVE anchor"; B_below[conf].append(opp)
                elif n_dn / draws >= conf: status[conf] = "anchor above newcomer"; A_above[conf].append(opp)
                else: status[conf] = "unseparated"; U_uns[conf].append(opp)
            anchors_met.append((opp, idx, status[CONF]))
            L.append("    step %d vs %-30s (incumbent #%2d, key tier %2d): n %3d, win share %.3f, 95%% CI [%.3f, %.3f] | draws above 0.5: %d, below: %d, at: %d | %s at %.3f (opposite draws %s); %s at 0.95"
                     % (step, opp, idx + 1, tier_of[opp] + 1, n, share, bs[lo_i], bs[hi_i], n_up, n_dn, draws - n_up - n_dn, status[CONF], CONF,
                        (draws - n_up if n_up >= n_dn else draws - n_dn) if status[CONF] != "unseparated" else "n/a", status[0.95]))
        A, Bl, U = A_above[CONF], B_below[CONF], U_uns[CONF]
        # position band on the 20-model board from the certificates (position = 1 + incumbents above the newcomer)
        lo_pos = max([order.index(m) + 2 for m in A], default=1); hi_pos = min([order.index(m) + 1 for m in Bl], default=len(order) + 1)
        for conf in (CONF, 0.95):
            L.append("  certificate at %.3f: anchors certified above the newcomer %s | certified below it %s | unseparated %s"
                     % (conf, A_above[conf] or "-", B_below[conf] or "-", U_uns[conf] or "-"))
        if lo_pos > hi_pos:
            L.append("  position band on the 20-model board: NON-TRANSITIVE certificate (an anchor ranked below a certified-above anchor was beaten) - no band")
        else:
            L.append("  position band on the 20-model board: [%d, %d] (incumbents' Mistral-board order; PROVISIONAL, printed as a band, never as a rank)" % (lo_pos, hi_pos))
        lo_t = max((tier_of[m] for m in A), default=0); hi_t = min((tier_of[m] for m in Bl), default=len(kt) - 1)
        kt_new = tier_of[new]
        if lo_t > hi_t:
            width = None
            L.append("  key-tier interval from the certificate: KEY-CONTRADICTED (lowest anchor certified above it is tier %d, highest certified below it is tier %d)" % (lo_t + 1, hi_t + 1))
        else:
            width = hi_t - lo_t + 1
            L.append("  key-tier interval from the certificate at %.3f: tiers %d..%d (%d tier%s) | newcomer's own key tier %d (key %.3f)"
                     % (CONF, lo_t + 1, hi_t + 1, width, "" if width == 1 else "s", kt_new + 1, acc[new]))
        ut = sorted({tier_of[m] for m in U})
        if ut: L.append("  tiers of the unseparated anchors: %d..%d" % (ut[0] + 1, ut[-1] + 1))
        ok = width is not None and width <= 2 and lo_t <= kt_new <= hi_t
        if new == FRONTIER_NEWCOMER:
            fr_met = [(m, s) for m, _, s in anchors_met if m in FRONTIER]
            L.append("  frontier anchors met: %s" % ("; ".join("%s -> %s" % (m, s) for m, s in fr_met) or "none"))
            top_rank = hi_pos == 1     # certified above the #1 incumbent = a top-tier rank, refused by rule
            L.append("  class: BANDED, PROVISIONAL; top-tier rank %s" % ("WOULD BE CLAIMED by the certificate - REFUSED by rule, published as band only" if top_rank else "not claimed: OK"))
            ok = ok and not top_rank
        results[new] = (ok, width, lo_t, hi_t, kt_new, full)
        L.append("  (22) certificate interval <= 2 adjacent key tiers and contains the key tier: %s%s" % ("PASS" if ok else "FAIL", "" if full else " (PARTIAL schedule: not a verdict)"))

        # ---------- SECONDARY: MIXED-FIT / EXTRAPOLATED (FRAMEWORK L85, L238) - never the verdict ----------
        try:
            prot = [(new, opp, q, v, 0) for m, (opp, q, v, _) in usable.items()]
            allrows = inc + prot
            th = jf.board_from(votes(allrows), models)
            th_nt = jf.board_from(votes(allrows, drop_ties=True), models)
            byq = defaultdict(list)
            for r in allrows: byq[r[2]].append(r)
            rng2 = random.Random(SEED)
            boards = []
            qs = sorted(byq)
            for _ in range(draws):
                pick = [qs[rng2.randrange(len(qs))] for _ in qs]
                boards.append(jf.board_from(votes([r for q in pick for r in byq[q]]), models))
            others = [m for m in models if m != new]
            ths = sorted(b[new] for b in boards)
            lo_i, hi_i = int(0.025 * draws), min(draws - 1, int(0.975 * draws))
            pos_pt = 1 + sum(1 for m in others if th[m] > th[new])
            poss = sorted(1 + sum(1 for m in others if b[m] > b[new]) for b in boards)
            mA = [m for m in others if sum(1 for b in boards if b[new] > b[m]) / draws <= 1 - CONF]
            mB = [m for m in others if sum(1 for b in boards if b[new] > b[m]) / draws >= CONF]
            mU = [m for m in others if m not in mA and m not in mB]
            L.append("  SECONDARY, MIXED-FIT / EXTRAPOLATED (not the verdict; FRAMEWORK L85/L238: %d Mistral-judged unfiltered incumbent edges + %d grok-judged filtered protocol edges in ONE fit without a scale term; ARENA-13: filtering widens the theta scale ~13%%):"
                     % (len(inc), len(prot)))
            L.append("    theta %+.3f (ties dropped %+.3f) | 95%% question-clustered bootstrap [%+.3f, %+.3f] over %d draws | position %d, interval [%d, %d] | at %.3f: above %d, below %d, unseparated %d%s"
                     % (th[new], th_nt[new], ths[lo_i], ths[hi_i], draws, pos_pt, poss[lo_i], poss[hi_i], CONF, len(mA), len(mB), len(mU),
                        (" (%s)" % ", ".join("%s(t%d)" % (m, tier_of[m] + 1) for m in sorted(mU, key=lambda m: -th[m]))) if mU else ""))
        except Exception as e:
            L.append("  SECONDARY MIXED-FIT line not computed (%s: %s); the primary readout above stands" % (type(e).__name__, str(e)[:120]))
        # comparators the protocol never saw: the withheld x20 edges and the 13-model ARENA-13 configuration
        try:
            th_full = jf.board_from(votes(rows), models)
            prot13 = [r for r in prot if r[1] in p8.ARENA12]
            m13 = sorted(set(p8.ARENA12) | {new})
            if prot13:
                r13 = [r for r in rows if r[0] in p8.ARENA12 and r[1] in p8.ARENA12] + prot13
                th13 = jf.board_from(votes(r13), m13)
                c13 = "13-model ARENA-13 configuration (x12 + the %d protocol edges against ARENA12 opponents) %+.3f, position %d of 13" % (
                    len(prot13), th13[new], 1 + sum(1 for m in m13 if m != new and th13[m] > th13[new]))
            else:
                c13 = "13-model ARENA-13 configuration not computed (no protocol edge against an ARENA12 opponent)"
            L.append("  comparators (free, never seen by the protocol): theta from its own %d withheld x20 edges on the full board %+.3f | %s"
                     % (sum(1 for r in rows if new in (r[0], r[1])), th_full[new], c13))
        except Exception as e:
            L.append("  comparators not computed (%s: %s); the primary readout above stands" % (type(e).__name__, str(e)[:120]))
    L.append("")
    if len(results) == len(NEWCOMERS) and all(v[5] for v in results.values()):
        allok = all(v[0] for v in results.values())
        wide = [n for n, v in results.items() if v[1] is None or v[1] > 2]
        L.append("NEWCOMER-PLACEMENT-LIVE: %s" % ("PASS - 400 filtered dual-order matches place a real newcomer within <= 2 key tiers" if allok else
                 "FAIL - " + ("interval wider than 2 tiers for %s: 400 matches is not a placement budget (falsifier)" % ", ".join(wide)
                              if wide else "interval does not contain the key tier / top-tier rank")))
    else:
        L.append("NEWCOMER-PLACEMENT-LIVE: no verdict (%d of %d newcomers readable on a full schedule)" % (sum(1 for v in results.values() if v[5]), len(NEWCOMERS)))
        complete = False
    txt = "\n".join(L); print(txt)
    out = OUT if (complete and len(newcomers) == len(NEWCOMERS)) else CACHE[:-3] + "_partial.txt"
    if out != OUT: print("PARTIAL / PILOT / RESTRICTED readout: written to %s, the outcome file of record is untouched" % out)
    open(out, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts, post nothing, open no cache")
    ap.add_argument("--run", action="store_true", help="the live run (posts to the deployment)")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="first N matches of the first anchor per newcomer (refused once the full schedule exists)")
    ap.add_argument("--newcomer", choices=NEWCOMERS, default=None, help="restrict to one newcomer (default: both, one at a time)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=MAXTOK, help="completion cap written into every payload and stored per verdict row (default %d)" % MAXTOK)
    ap.add_argument("--temperature", type=float, default=None, help="omitted unless given (D2: every run of record omits it)")
    ap.add_argument("--judge-model", choices=sorted(JUDGES), default="grok", help="grok = newcomer-placement judge of record")
    ap.add_argument("--retry-unusable", action="store_true", help="with --run: re-post ONLY rows with invalid=1 (unparsed / finish_reason=length) of the undecided step at the current --maxtok, which may be RAISED (logged in meta max_tokens_history; the cap of record stays); decided steps are frozen; fresh rows wait for --run")
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--cache", default=None, help="override the cache file (must not be an existing run's cache)")
    a = ap.parse_args()
    MAXTOK = a.maxtok; TEMPERATURE = a.temperature; JUDGE = a.judge_model; RETRY_UNUSABLE = a.retry_unusable
    newcomers = [a.newcomer] if a.newcomer else list(NEWCOMERS)
    if a.cache:
        assert os.path.basename(a.cache).startswith("newcomer_placement") and a.cache.endswith(".db"), \
            "--cache must be this run's own file (newcomer_placement*.db), never another run's cache"
        CACHE = a.cache; OUT = CACHE[:-3] + "_outcome.txt"
    if a.dry_run: dry_run(a.pilot, newcomers)
    elif a.run: run(a.pilot, a.workers, newcomers)
    elif a.analyze: analyze(a.draws, newcomers)
    else: ap.print_help()
