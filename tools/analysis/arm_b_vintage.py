"""ARM-B-VINTAGE - the ARM-B reference re-mint: vintage v1 of the cached grok-4-1-fast-reasoning reference on 200 canary
questions under v0's legacy protocol; agreement with v0 against the 0.89 alarm (FRAMEWORK L141). Registered 2026-09-19 in
docs/judge_v2_program.md ("Registered 2026-09-19 (before any code or call) - ARM-B-VINTAGE", commit c8e0c3f; authorised by
plan Amendment 6, docs/plan_2026-09-15.md L190-L231, item 6). The registration names the script ref_remint.py; this file is
the instrument the orchestrator asked for (arm_b_vintage.py) and ref_remint.py is a one-line alias to it - the outcome
files keep the registered names (ref_remint_outcome.txt, ref_remint_PILOT.txt).

  python tools/analysis/arm_b_vintage.py --selftest              (draw arithmetic, parse classes, agreement / Wilson / McNemar, the gates; no DB; 0 calls)
  python tools/analysis/arm_b_vintage.py --dry-run               (pool id first; 279 -> N eligible -> 200 drawn + set hash; v0's protocol facts
                                                                  found on disk; the ten L37 stamps; the sidecar plan; the bill; 0 calls)
  python tools/analysis/arm_b_vintage.py --pilot 12 [--workers 8] (12 solves; REFUSED unless ARMB_GO == 6 AND docs/reviews/READY_arm_b_vintage.md is
                                                                  committed AND SET_HASH_OF_RECORD is registered and equals the recomputed draw)
  python tools/analysis/arm_b_vintage.py --run [--workers 8]     (the remaining solves; same gate; resume = relaunch; protocol pinned in meta)
  python tools/analysis/arm_b_vintage.py --analyze | --report    (agreement A / B, key-correct + McNemar, stamps, the cross-read, the alarm state;
                                                                  refuses a cache short of the 200 rows; writes the v0 sidecar once)

VINTAGE v0 (found on disk at --dry-run, never opened for writing): experiment_results/judge_solve/grok-reasoning.db, `answers`
(question_id, answer, gt, correct, raw, tokens, latency, ts); 3,432 rows = the 3,445 pool questions minus the 13 HTTP 400
content-filter questions, which are ABSENT (judge_solve_map.run does not cache an error; the ids are read from
grok-reasoning_allreserved.log and asserted equal to pool minus cache). No cap column, no finish_reason, no response id;
`tokens` = usage.completion_tokens as judge_solve_map.call stored it (so completion tokens ARE known per v0 row);
`ts` per row (so minted_at is known per row: 2026-09-09 .. 2026-09-10). The cap: judge_solve_map.run calls call() without
max_tokens, and call's default is 4,096 (asserted from the source at dry-run); the logs print no cap. The SYSTEM bytes:
judge_solve_map.SYSTEM (sha256 printed); protocol_id "solve_json_v1".

THE SET: canary_set.json (hash 50af669ac6997f9f, 300 matches, 279 distinct questions). A question's HALF is "contested" if
any of its canary matches is contested, else "cross" (10 questions sit in both halves: assigned to contested, printed).
Minus the content-filter questions (rule 10). 200 drawn with random.Random(42): the contested half first then cross, each
half's ids sorted then shuffled, n_half = round(200 x half / eligible) (the remainder to cross); the 200 sorted by id; the
set hash = sha256 of the newline-joined ids, its first 16 hex digits registered as SET_HASH_OF_RECORD by the pre-run bracket
BEFORE the first call (JUDGE-WIRING W1). Every posting mode refuses any other set.

INSTRUMENT: rejudge_reasoning.call_judge_full (rule 9) with rr.JUDGE_MODEL grok-4-1-fast-reasoning, rr.MAX_TOKENS = v0's cap
(4,096), rr.TEMPERATURE None (omitted), system = judge_solve_map.SYSTEM (bytes asserted), user = judge_solve_map.user_prompt
(qtext, opts) from judge_solve_map.questions() (the same rows v0 saw); the body asserted against rr.payload_body's source.
Parse: judge_solve_map.parse_answer. States: YIELD (a letter), NON_TERMINATED (finish_reason length), NO_YIELD (stop, no
letter), UNUSABLE (content_filter). Own cache experiment_results/judge_solve/grok-reasoning-v1.db: `answers` as v0's schema
+ state, response_id and the ten L37 stamps (reference_model, deployment_fingerprint, prompt_hash, protocol_id, max_tokens,
temperature, finish_reason, completion_tokens, minted_at, side_at_mint); `meta` pinned at first launch.
deployment_fingerprint = the model string the endpoint returns (call_judge_full's provider field "azure:<model>"); the
endpoint's system_fingerprint is not surfaced by call_judge_full (stated in the outcome).
GUARD: NON_TERMINATED + NO_YIELD + UNUSABLE > 5% of the cached rows -> the run refuses to post more (--override-guard
recorded); --analyze prints C3 on the 200.
THE READY RULE: --pilot / --run refuse unless ARMB_GO == "6" AND docs/reviews/READY_arm_b_vintage.md exists and is committed
AND SET_HASH_OF_RECORD equals the recomputed hash. --dry-run and --selftest post nothing and create no cache.
"""
import os, sys, re, json, math, time, random, sqlite3, argparse, hashlib, inspect, subprocess, threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

POOL_ID = "p2dca21ab5f4ef3ae"
SOLVER = "grok-4-1-fast-reasoning"
PROTOCOL_ID = "solve_json_v1"
N_SET = 200
SEED = 42
ALARM_P, ALARM_Z = 0.94, 3.0
ALARM_BAR = 0.89                                     # FRAMEWORK L141 as written (0.9396 - 0.0504 = 0.8896, rounded)
SET_HASH_OF_RECORD = "60b1ef3a859abceb"  # registered by the pre-run bracket, commit 1da84e7
JS = os.path.join(ROOT, "experiment_results", "judge_solve")
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
V0_DB = os.path.join(JS, "grok-reasoning.db")
V0_LOG = os.path.join(JS, "grok-reasoning_allreserved.log")
V1_DB = os.path.join(JS, "grok-reasoning-v1.db")
SIDECAR = os.path.join(JS, "grok-reasoning_v0_stamp.json")
CANARY_JSON = os.path.join(X12DIR, "canary_set.json")
CANARY_HASH = "50af669ac6997f9f"
CANARY_PASS1 = os.path.join(X12DIR, "canary_baseline_pass1.db")
OUT = os.path.join(JS, "ref_remint_outcome.txt")
OUT_PILOT = os.path.join(JS, "ref_remint_PILOT.txt")
READY = os.path.join(ROOT, "docs", "reviews", "READY_arm_b_vintage.md")
GO_ENV, GO_VALUE = "ARMB_GO", "6"
STAMPS = ("reference_model", "deployment_fingerprint", "prompt_hash", "protocol_id", "max_tokens", "temperature",
          "finish_reason", "completion_tokens", "minted_at", "side_at_mint")
SIDE = "EVAL (pool of record)"
SCRIPT_SHA = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
OVERRIDE_GUARD = False
MAXTOK = None                                        # set from judge_solve_map.call's default at load (v0's cap of record)


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


def ro(path):
    assert os.path.exists(path), "missing %s" % path
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# ---------------------------------------------------------------- pure helpers (the selftest covers these)

def wilson(k, n, z=1.959963984540054):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def mcnemar_exact(b, c):
    """Exact two-sided McNemar on the discordant counts, integer arithmetic (systematic_budget.mcnemar_edge's form)."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n))


def alarm_bar(n):
    return ALARM_P - ALARM_Z * math.sqrt(ALARM_P * (1 - ALARM_P) / n)


def prompt_hash(system, user):
    return hashlib.sha256(system.encode("utf-8") + b"\n\x00\n" + user.encode("utf-8")).hexdigest()[:16]


def classify(finish, letter):
    if finish == "content_filter": return "UNUSABLE"
    if finish == "length": return "NON_TERMINATED"
    return "YIELD" if letter else "NO_YIELD"


def halves_of(matches):
    """qid -> half: contested if any canary match on the question is contested, else cross; plus the overlap list."""
    st = defaultdict(set)
    for m in matches: st[m["qid"]].add(m["stratum"])
    half = {q: ("contested" if "contested" in s else "cross") for q, s in st.items()}
    both = sorted(q for q, s in st.items() if len(s) == 2)
    return half, both


def draw(half, excluded, n_set=N_SET, seed=SEED):
    """The 200 stratified by half, proportional to the eligible counts; sorted by id. Returns (ids, per-half counts)."""
    elig = {h: sorted(q for q, hh in half.items() if hh == h and q not in excluded) for h in ("contested", "cross")}
    n_el = sum(len(v) for v in elig.values())
    n_take = min(n_set, n_el)
    n_c = round(n_take * len(elig["contested"]) / n_el) if n_el else 0
    n_x = n_take - n_c
    rng = random.Random(seed); out = []
    for h, n in (("contested", n_c), ("cross", n_x)):
        lst = list(elig[h]); rng.shuffle(lst); out.extend(lst[:n])
    return sorted(out), dict(contested=(n_c, len(elig["contested"])), cross=(n_x, len(elig["cross"])), eligible=n_el, taken=n_take)


def set_hash(ids):
    return hashlib.sha256("\n".join(str(q) for q in ids).encode("utf-8")).hexdigest()


def agreement(v0, v1, ids):
    """v0/v1: qid -> letter ('' = none). Convention A: same letter / n; B: same / both-yielded."""
    n = len(ids); same = sum(1 for q in ids if v0.get(q, "") and v0[q] == v1.get(q, ""))
    both = [q for q in ids if v0.get(q, "") and v1.get(q, "")]
    sameB = sum(1 for q in both if v0[q] == v1[q])
    return dict(n=n, same=same, A=same / n if n else float("nan"), ciA=wilson(same, n), nB=len(both), sameB=sameB,
                B=sameB / len(both) if both else float("nan"), ciB=wilson(sameB, len(both)))


# ---------------------------------------------------------------- the READY gate

def git_state(path):
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return t, c, h
    except Exception as e:
        return False, False, "git unavailable: %s" % e


def gate_state(recomputed_hash16=None):
    have = os.environ.get(GO_ENV); exists = os.path.exists(READY)
    t, c, h = git_state(READY) if exists else (False, False, "")
    if not exists: st = "MISSING"
    elif t and c: st = "exists, committed %s" % h
    elif not t: st = "exists, NOT committed (untracked)"
    else: st = "exists, uncommitted change"
    hash_ok = SET_HASH_OF_RECORD is not None and (recomputed_hash16 is None or SET_HASH_OF_RECORD == recomputed_hash16)
    ok = have == GO_VALUE and exists and t and c and hash_ok
    return ok, "%s=%r (needs %r) | %s %s | SET_HASH_OF_RECORD %s%s" % (GO_ENV, have, GO_VALUE, rel(READY), st, SET_HASH_OF_RECORD or "NOT REGISTERED",
                                                                     "" if recomputed_hash16 is None or SET_HASH_OF_RECORD is None else (" = recomputed" if hash_ok else " != recomputed %s" % recomputed_hash16))


def go_gate(what, recomputed_hash16=None):
    ok, s = gate_state(recomputed_hash16)
    if not ok:
        raise SystemExit("[READY] %s refused (0 calls): %s. Nothing is posted, including the 12-solve pilot, until the reviewer's READY is committed and the set hash is registered." % (what, s))
    print("[READY] %s" % s)


# ---------------------------------------------------------------- v0 and the set, as found on disk

def v0_facts():
    """v0's protocol facts from files and source, never from a writable handle."""
    import judge_solve_map as jsm
    sys_bytes = jsm.SYSTEM.encode("utf-8")
    cap_default = inspect.signature(jsm.call).parameters["max_tokens"].default
    run_src = inspect.getsource(jsm.run)
    m = re.search(r"call\(model, SYSTEM_CONF if CONFIDENCE else SYSTEM, user_prompt\(qtext, opts\)\)", run_src)
    run_passes_cap = m is None or "max_tokens" in (m.group(0) if m else "")
    con = ro(V0_DB)
    cols = [r[1] for r in con.execute("PRAGMA table_info(answers)")]
    n_rows, n_blank, ts_min, ts_max = con.execute("SELECT COUNT(*), SUM(answer=''), MIN(ts), MAX(ts) FROM answers").fetchone()
    tok = [r[0] for r in con.execute("SELECT tokens FROM answers WHERE tokens IS NOT NULL")]
    n_cf_raw = con.execute("SELECT COUNT(*) FROM answers WHERE raw LIKE '%content_filter%'").fetchone()[0]
    con.close()
    log_cf = []
    if os.path.exists(V0_LOG):
        log_cf = sorted({int(x) for x in re.findall(r"ERROR q (\d+): HTTP Error 400", open(V0_LOG, encoding="utf-8", errors="replace").read())})
    log_cap = "max_tokens" in open(V0_LOG, encoding="utf-8", errors="replace").read() if os.path.exists(V0_LOG) else False
    return dict(system_sha256=hashlib.sha256(sys_bytes).hexdigest(), system_len=len(sys_bytes), cap_default=cap_default, run_passes_cap=run_passes_cap,
                columns=cols, n_rows=n_rows, n_blank=n_blank, ts_min=ts_min, ts_max=ts_max, tokens_median=(sorted(tok)[len(tok) // 2] if tok else None),
                n_content_filter_rows=n_cf_raw, log_content_filter_ids=log_cf, log_prints_cap=log_cap)


def load_set():
    """(ids, hash_hex, draw info, half map, overlap list, content-filter ids among the 279, canary matches)."""
    d = json.load(open(CANARY_JSON, encoding="utf-8")); ms = d["matches"]
    assert d["set_hash"] == CANARY_HASH and d["pool_id"] == POOL_ID and len(ms) == 300, "canary_set.json is not the set of record"
    half, both = halves_of(ms)
    con = ro(V0_DB); have = {q for (q,) in con.execute("SELECT question_id FROM answers")}; con.close()
    cf = sorted(q for q in half if q not in have)
    ids, info = draw(half, set(cf))
    return ids, set_hash(ids), info, half, both, cf, ms


def v0_answers(ids):
    con = ro(V0_DB)
    rows = {q: (a, gt, c, tok, ts) for q, a, gt, c, tok, ts in con.execute("SELECT question_id, answer, gt, correct, tokens, ts FROM answers")}
    con.close(); return {q: rows[q] for q in ids if q in rows}


def payloads(ids):
    """qid -> (system, user, gt) with the bytes v0 saw: judge_solve_map.questions() rows and user_prompt."""
    import judge_solve_map as jsm
    saved = jsm.ALL_RESERVED; jsm.ALL_RESERVED = True
    try: qs = jsm.questions()
    finally: jsm.ALL_RESERVED = saved
    out = {}
    for q in ids:
        assert q in qs, "question %d has no eval row" % q
        qtext, opts, gt = qs[q]
        out[q] = (jsm.SYSTEM, jsm.user_prompt(qtext, opts), gt)
    return out


def assert_body_fidelity():
    import rejudge_reasoning as rr
    src = inspect.getsource(rr.payload_body)
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full)
    assert '{"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and '"messages": [{"role": "system", "content": system},' in src \
        and 'payload_body["temperature"] = TEMPERATURE' in src, "rejudge_reasoning.payload_body changed"
    body = rr.payload_body("s", "u")
    assert tuple(body.keys()) == ("model", "max_tokens", "messages") and body["model"] == SOLVER and body["max_tokens"] == MAXTOK, body
    return body


def configure_rr():
    import rejudge_reasoning as rr
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = SOLVER; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = None


def load_cap():
    global MAXTOK
    import judge_solve_map as jsm
    MAXTOK = inspect.signature(jsm.call).parameters["max_tokens"].default
    assert MAXTOK == 4096, "judge_solve_map.call's default moved to %s; the registration's cap of record is 4,096 subject to the dry-run finding" % MAXTOK


# ---------------------------------------------------------------- cache

def open_cache():
    con = sqlite3.connect(V1_DB)
    con.execute("CREATE TABLE IF NOT EXISTS answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, tokens INTEGER, latency REAL, ts REAL, "
                "state TEXT, response_id TEXT, reference_model TEXT, deployment_fingerprint TEXT, prompt_hash TEXT, protocol_id TEXT, max_tokens INTEGER, "
                "temperature TEXT, finish_reason TEXT, completion_tokens INTEGER, minted_at TEXT, side_at_mint TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit(); return con


def pin_meta(con, hash16, system_sha):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    meta = {"test": "ARM-B-VINTAGE", "vintage": "v1", "pool_id": POOL_ID, "reference_model": SOLVER, "provider": "azure", "protocol_id": PROTOCOL_ID,
            "system_sha256": system_sha, "max_tokens": str(MAXTOK), "temperature": "omitted", "set_hash": hash16, "n_set": str(N_SET),
            "seed": str(SEED), "script_sha256_16": SCRIPT_SHA, "started": now}
    stored = dict(con.execute("SELECT key, value FROM meta"))
    if stored:
        con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((stored.get("resumed", "") + ";" + now).strip(";"),))
        for k in ("pool_id", "reference_model", "protocol_id", "system_sha256", "max_tokens", "temperature", "set_hash", "n_set", "seed"):
            if stored.get(k) != meta[k]:
                raise SystemExit("[META] REFUSED: %s was pinned with %s=%s; this launch has %s (a changed cap / protocol / set is a new session)" % (rel(V1_DB), k, stored.get(k), meta[k]))
    for k, v in meta.items(): con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", (k, v))
    con.commit()


def guard(con):
    rows = con.execute("SELECT state FROM answers").fetchall()
    n = len(rows); bad = sum(1 for (s,) in rows if s != "YIELD")
    return n, bad, (bad / n if n else 0.0), dict(Counter(s for (s,) in rows))


# ---------------------------------------------------------------- dry run

def dry_run():
    load_cap()
    F = v0_facts()
    ids, hh, info, half, both, cf, ms = load_set()
    print("VINTAGE v0 as found on disk (%s, mode=ro):" % rel(V0_DB))
    print("  rows %d (blank answers %d; rows whose raw carries content_filter %d) | columns %s" % (F["n_rows"], F["n_blank"], F["n_content_filter_rows"], F["columns"]))
    print("  no cap column, no finish_reason, no response id; `tokens` = usage.completion_tokens per row (median %s): completion tokens ARE known for v0; `ts` per row: minted %s .. %s (minted_at per row is known)"
          % (F["tokens_median"], time.strftime("%Y-%m-%d %H:%M", time.localtime(F["ts_min"])), time.strftime("%Y-%m-%d %H:%M", time.localtime(F["ts_max"]))))
    print("  CAP FINDING: judge_solve_map.call(..., max_tokens=%d) is the default; judge_solve_map.run calls call() %s; the --all-reserved log prints a cap: %s -> v0's cap of record = %d (by code default; no row carries it)"
          % (F["cap_default"], "WITHOUT max_tokens (default applies)" if not F["run_passes_cap"] else "WITH max_tokens (READ THE SOURCE)", F["log_prints_cap"], F["cap_default"]))
    print("  SYSTEM bytes: judge_solve_map.SYSTEM, %d bytes, sha256 %s | protocol_id %s | temperature omitted (judge_solve_map.call posts none) | posted by judge_solve_map's own urllib call (pre-rule-9)" % (F["system_len"], F["system_sha256"], PROTOCOL_ID))
    print("  content-filter questions: the log names %d ids %s; pool minus cache = %d; the 13 are ABSENT rows, not cached refusals" % (len(F["log_content_filter_ids"]), F["log_content_filter_ids"], 3445 - F["n_rows"]))
    print("THE SET: %s (hash %s = record): 300 matches, %d distinct questions; halves by question: contested %d, cross %d (%d questions in both halves -> contested: %s)"
          % (rel(CANARY_JSON), CANARY_HASH, len(half), sum(1 for h in half.values() if h == "contested"), sum(1 for h in half.values() if h == "cross"), len(both), both))
    print("  content-filter questions among the %d (no v0 row): %d %s -> eligible %d" % (len(half), len(cf), cf, info["eligible"]))
    print("  DRAW seed %d stratified by half: contested %d of %d, cross %d of %d -> %d questions, sorted by id" % (SEED, info["contested"][0], info["contested"][1], info["cross"][0], info["cross"][1], info["taken"]))
    print("  ids: %s" % " ".join(str(q) for q in ids))
    print("  SET HASH sha256 %s | SET_HASH_OF_RECORD (first 16) = %s -> register this in the script and by the pre-run bracket BEFORE the first call; currently %s"
          % (hh, hh[:16], SET_HASH_OF_RECORD or "NOT REGISTERED (every posting mode refuses)"))
    if info["taken"] < N_SET: print("  NOTE: eligible %d < %d: the draw is the eligible count and the alarm formula's n becomes %d (registration (e))" % (info["eligible"], N_SET, info["taken"]))
    v0 = v0_answers(ids)
    assert len(v0) == len(ids), "v0 rows missing for %d drawn questions" % (len(ids) - len(v0))
    P = payloads(ids)
    import judge_solve_map as jsm
    assert P[ids[0]][0].encode("utf-8") == jsm.SYSTEM.encode("utf-8")
    configure_rr(); body = assert_body_fidelity()
    import rejudge_reasoning as rr
    first = rr.payload_bytes(P[ids[0]][0], P[ids[0]][1])
    print("PAYLOAD: model %s | max_tokens %d | temperature omitted | body keys %s | first question %d payload sha256 %s (%d bytes) | prompt_hash %s | %d payloads assembled, 0 posted"
          % (body["model"], body["max_tokens"], tuple(body.keys()), ids[0], hashlib.sha256(first).hexdigest(), len(first), prompt_hash(P[ids[0]][0], P[ids[0]][1]), len(P)))
    print("THE TEN L37 STAMPS every v1 row carries: %s" % ", ".join(STAMPS))
    print("  values: reference_model %s | deployment_fingerprint = the endpoint's model string (call_judge_full provider 'azure:<model>'; system_fingerprint not surfaced) | prompt_hash sha256(system + user)[:16] per row | protocol_id %s | max_tokens %d | temperature 'omitted' | finish_reason per call | completion_tokens per call | minted_at per call (UTC ISO) | side_at_mint '%s'; plus response_id and state (YIELD / NON_TERMINATED / NO_YIELD / UNUSABLE)"
          % (SOLVER, PROTOCOL_ID, MAXTOK, SIDE))
    print("SIDECAR PLAN for v0 (%s, written once by --analyze; v0 never edited): vintage v0 | reference_model %s | protocol_id %s (reconstructed from the SYSTEM bytes, sha256 %s) | max_tokens %d (judge_solve_map.call default; no row carries it) | temperature 'omitted' | finish_reason 'unknown (pre-rule-9)' | completion_tokens per question from answers.tokens (the registration expected null: the column exists) | minted_at per question from answers.ts | side_at_mint '%s' | deployment_fingerprint 'unknown' | prompt_hash per question reconstructed and labelled | the %d drawn ids with their v0 letters | the agreement stamp after the outcome"
          % (rel(SIDECAR), SOLVER, PROTOCOL_ID, F["system_sha256"], MAXTOK, SIDE, len(ids)))
    print("BILL: %d reasoning solves x ~10 cce = ~%d cce (the 12-solve pilot inside); 0 judge calls; not an arena match; authorised by plan Amendment 6 item 6" % (len(ids), 10 * len(ids)))
    print("ALARM: agreement under A < %.2f (unrounded %.4f at n = %d) -> ALARM; falsifier < 0.85" % (ALARM_BAR, alarm_bar(len(ids)), len(ids)))
    print("cache: %s%s (the dry run creates nothing) | outcome %s | pilot %s" % (rel(V1_DB), " (EXISTS)" if os.path.exists(V1_DB) else " (new)", rel(OUT), rel(OUT_PILOT)))
    ok, s = gate_state(hh[:16])
    print("READY gate (not enforced by --dry-run): %s -> %s" % (s, "OPEN" if ok else "CLOSED (nothing may be posted)"))
    print("script sha256[:16] %s" % SCRIPT_SHA)
    print("dry run OK: 0 calls posted, no cache created")


# ---------------------------------------------------------------- live run

def run(pilot, workers):
    import rejudge_reasoning as rr
    import judge_solve_map as jsm
    load_cap()
    F = v0_facts()
    ids, hh, info, half, both, cf, ms = load_set()
    go_gate("--pilot %d" % pilot if pilot else "--run", hh[:16])
    assert len(ids) == N_SET or info["eligible"] < N_SET
    P = payloads(ids)
    configure_rr(); assert_body_fidelity(); rr.load_env()
    con = open_cache(); pin_meta(con, hh[:16], F["system_sha256"])
    if OVERRIDE_GUARD: con.execute("INSERT OR REPLACE INTO meta VALUES ('override_guard', ?)", (time.strftime("%Y-%m-%d %H:%M:%S"),)); con.commit()
    n, bad, rate, states = guard(con)
    if n and rate > 0.05 and not OVERRIDE_GUARD:
        raise SystemExit("  GUARD: %d of %d cached solves (%.1f%%) NON_TERMINATED / NO_YIELD / UNUSABLE %s; nothing more is posted (--override-guard posts anyway and is recorded)" % (bad, n, 100 * rate, states))
    have = {q for (q,) in con.execute("SELECT question_id FROM answers")}
    todo = [q for q in ids if q not in have]
    if pilot: todo = todo[:pilot]
    print("ARM-B-VINTAGE v1: model %s | max_tokens %d | temperature omitted | set %s (%d) | cached %d | to solve %d | workers %d | cache %s"
          % (SOLVER, MAXTOK, hh[:16], len(ids), len(have), len(todo), workers, rel(V1_DB)), flush=True)
    lock = threading.Lock()
    def one(q):
        system, user, gt = P[q]
        t0 = time.time()
        content, provider, ctok, lat, finish, msg = rr.call_judge_full(system, user)
        raw = content if finish != "content_filter" else "error: HTTP 400 content_filter " + str((msg or {}).get("_refusal", ""))[:300]
        letter = jsm.parse_answer(content) if finish not in ("length", "content_filter") else ""
        state = classify(finish, letter)
        return (q, letter, gt, int(letter != "" and letter == gt), raw, ctok, lat, time.time(), state, (msg or {}).get("_response_id"),
                SOLVER, provider, prompt_hash(system, user), PROTOCOL_ID, MAXTOK, "omitted", finish, ctok, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)), SIDE)
    ok = err = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s" % (futs[f], str(e)[:120]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO answers VALUES (%s)" % ",".join("?" * len(row)), row); con.commit()
            ok += 1
            if i % 25 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    n, bad, rate, states = guard(con)
    print("  GUARD LINE: %d of %d cached solves (%.1f%%) NON_TERMINATED + NO_YIELD + UNUSABLE; states %s -> %s" % (bad, n, 100 * rate, states, "OK (<= 5%)" if rate <= 0.05 else "ABOVE 5%: the run refuses to continue"), flush=True)
    print("done. --analyze for the readout (refuses a cache short of %d rows)." % len(ids), flush=True)


# ---------------------------------------------------------------- analysis

def analyze():
    load_cap()
    F = v0_facts()
    ids, hh, info, half, both, cf, ms = load_set()
    if not os.path.exists(V1_DB): raise SystemExit("no cache at %s: nothing minted, nothing written" % rel(V1_DB))
    con = ro(V1_DB); meta = dict(con.execute("SELECT key, value FROM meta"))
    rows = {r[0]: r for r in con.execute("SELECT question_id, answer, gt, correct, raw, tokens, latency, ts, state, response_id, reference_model, deployment_fingerprint, "
                                         "prompt_hash, protocol_id, max_tokens, temperature, finish_reason, completion_tokens, minted_at, side_at_mint FROM answers")}
    con.close()
    n = len(ids); have = [q for q in ids if q in rows]; extra = sorted(set(rows) - set(ids))
    complete = len(have) == n and not extra and meta.get("set_hash") == hh[:16]
    v0 = v0_answers(ids)
    v0l = {q: v0[q][0] for q in ids}; v1l = {q: (rows[q][1] if q in rows and rows[q][8] == "YIELD" else "") for q in ids}
    states = Counter(rows[q][8] for q in have)
    bad = sum(1 for q in have if rows[q][8] != "YIELD")
    ag = agreement(v0l, v1l, have)
    alarm = "UNDETERMINED"
    if complete:
        c3 = bad / n <= 0.05
        alarm = ("NO ALARM" if ag["A"] >= ALARM_BAR else "ALARM") if c3 else "UNDETERMINED"
    L = ["[POOL] %s" % POOL_ID,
         "ALARM STATE: %s%s" % (alarm, "" if complete else " (cache %d of %d rows%s: no verdict)" % (len(have), n, "; %d rows outside the set" % len(extra) if extra else "")),
         "=== ARM-B-VINTAGE: v1 vs v0 on %d canary questions (registration c8e0c3f; Amendment 6 item 6; FRAMEWORK L37 / L141) ===" % n,
         "  v1 cache %s (mode=ro): model %s | protocol %s | system sha256 %s | max_tokens %s | temperature %s | set %s | started %s | resumed %s | script %s (this %s) | override_guard %s"
         % (rel(V1_DB), meta.get("reference_model"), meta.get("protocol_id"), meta.get("system_sha256"), meta.get("max_tokens"), meta.get("temperature"), meta.get("set_hash"), meta.get("started"), meta.get("resumed", "-"), meta.get("script_sha256_16"), SCRIPT_SHA, meta.get("override_guard", "no")),
         "  v0 %s (mode=ro): %d rows, cap %d by judge_solve_map.call's default (no row carries it), SYSTEM sha256 %s, minted %s .. %s, 13 content-filter questions absent"
         % (rel(V0_DB), F["n_rows"], F["cap_default"], F["system_sha256"], time.strftime("%Y-%m-%d", time.localtime(F["ts_min"])), time.strftime("%Y-%m-%d", time.localtime(F["ts_max"]))),
         "  set: %d of the 279 canary questions (hash %s; contested %d, cross %d; %d content-filter questions excluded)" % (n, hh[:16], info["contested"][0], info["cross"][0], len(cf)),
         "  v1 states on %d rows: %s | guard NON_TERMINATED + NO_YIELD + UNUSABLE = %d (%.1f%%)" % (len(have), dict(states), bad, 100 * bad / max(1, len(have)))]
    L.append("(1) AGREEMENT v1 vs v0: convention A (same letter / %d; non-yielded v1 rows = disagreement) %.4f [%.4f, %.4f] (%d of %d) | convention B (same / both-yielded %d) %.4f [%.4f, %.4f]"
             % (ag["n"], ag["A"], *ag["ciA"], ag["same"], ag["n"], ag["nB"], ag["B"], *ag["ciB"]))
    L.append("    alarm bar 0.89 as written (unrounded %.4f at n = %d) | falsifier 0.85" % (alarm_bar(n), n))
    byh = {}
    for h in ("contested", "cross"):
        sub = [q for q in have if half[q] == h]; a = agreement(v0l, v1l, sub); byh[h] = a
        L.append("    by half %-9s n %3d: A %.4f [%.4f, %.4f] | B %.4f (n %d)" % (h, a["n"], a["A"], *a["ciA"], a["B"], a["nB"]))
    anchor_of = {m["qid"]: m["anchor"] for m in ms}
    for anc in sorted({anchor_of[q] for q in have}):
        sub = [q for q in have if anchor_of[q] == anc]; a = agreement(v0l, v1l, sub)
        L.append("    by anchor %-18s n %3d: A %.3f | B %.3f (n %d)  (descriptive)" % (anc, a["n"], a["A"], a["B"], a["nB"]))
    # (2) key-correct
    gt = {q: v0[q][1] for q in ids}
    k0 = {q: int(v0l[q] != "" and v0l[q] == gt[q]) for q in have}; k1 = {q: int(v1l[q] != "" and v1l[q] == gt[q]) for q in have}
    b = sum(1 for q in have if k0[q] and not k1[q]); c = sum(1 for q in have if k1[q] and not k0[q])
    bothy = [q for q in have if v0l[q] and v1l[q]]
    bB = sum(1 for q in bothy if k0[q] and not k1[q]); cB = sum(1 for q in bothy if k1[q] and not k0[q])
    acc0, acc1 = sum(k0.values()) / max(1, len(have)), sum(k1.values()) / max(1, len(have))
    L.append("(2) KEY-CORRECT on the %d: v0 %.3f, v1 %.3f (A: non-yielded = wrong) | discordant v0-only-right %d, v1-only-right %d, exact McNemar p %.4f | B (both-yielded %d): v0 %.3f, v1 %.3f, p %.4f"
             % (len(have), acc0, acc1, b, c, mcnemar_exact(b, c), len(bothy), sum(k0[q] for q in bothy) / max(1, len(bothy)), sum(k1[q] for q in bothy) / max(1, len(bothy)), mcnemar_exact(bB, cB)))
    # (3) stamps
    stamped = sum(1 for q in have if all(rows[q][10 + i] is not None for i in range(len(STAMPS))) and rows[q][16] is not None)
    ct = sorted(rows[q][17] for q in have if rows[q][17] is not None)
    fps = Counter(rows[q][11] for q in have)
    L.append("(3) STAMPS: %d of %d v1 rows carry all ten L37 fields with finish_reason | finish_reason %s | completion_tokens median %s p95 %s max %s | deployment fingerprint(s) %s | prompt_hash per row: %d distinct"
             % (stamped, len(have), dict(Counter(rows[q][16] for q in have)), ct[len(ct) // 2] if ct else None, ct[min(len(ct) - 1, int(0.95 * len(ct)))] if ct else None, ct[-1] if ct else None, dict(fps), len({rows[q][12] for q in have})))
    # (4) cross-read
    dis = [q for q in have if not (v0l[q] and v0l[q] == v1l[q])]
    tie_set = dec_set = 0; tie_dis = dec_dis = 0
    if os.path.exists(CANARY_PASS1):
        cp = ro(CANARY_PASS1)
        cv = {mid: (q, w, inv) for mid, q, w, inv in cp.execute("SELECT match_id, qid, winner, invalid FROM verdicts")}; cp.close()
        for mid, (q, w, inv) in cv.items():
            if inv: continue
            if w == "TIE": tie_set += 1
            else: dec_set += 1
            if q in dis:
                if w == "TIE": tie_dis += 1
                else: dec_dis += 1
    tr_set = tie_set / max(1, tie_set + dec_set); tr_dis = tie_dis / max(1, tie_dis + dec_dis)
    L.append("(4) DESCRIPTIVE cross-read (no criterion): %d disagreements -> their canary pass-1 matches: %d decided, %d TIE (tie rate %.3f vs the set's %.3f); ids %s" % (len(dis), dec_dis, tie_dis, tr_dis, tr_set, dis))
    L.append("=== criteria ===")
    c1 = complete and ag["A"] >= ALARM_BAR; c3 = complete and bad / n <= 0.05
    L.append("  C1 AGREEMENT >= 0.89 under A: %.4f -> %s" % (ag["A"], ("HELD" if c1 else "FAILED") if complete else "no verdict (partial)"))
    L.append("  C2 STAMPS: %d of %d rows complete; v0 sidecar %s -> %s" % (stamped, n, "written by this analysis" if complete else "not written (partial)", "DELIVERED" if complete and stamped == n else "NOT DELIVERED"))
    L.append("  C3 GUARD: %d of %d (%.1f%%) <= 5%% -> %s" % (bad, n, 100 * bad / max(1, n), ("HELD" if c3 else "FAILED") if complete else "no verdict (partial)"))
    L.append("  VERDICT: %s" % {"NO ALARM": "C1 HELD and C3 HELD -> \"no alarm; the legacy vintage is stamped; arm B is live\"",
                                 "ALARM": "C1 FAILED with C3 HELD -> ALARM: consequences (a)-(d) of the registration apply from the moment this file is written",
                                 "UNDETERMINED": "C3 FAILED or partial -> UNDETERMINED-by-instrument (the cap or the protocol, not the vintage); a re-post decision is the author's"}[alarm])
    L.append("=== predictions (blind, labelled) ===")
    L.append("  P1 (plan) A in [0.92, 0.95]: %.4f -> %s" % (ag["A"], "HELD" if 0.92 <= ag["A"] <= 0.95 else "FAILED"))
    L.append("  P2 B - A <= 0.02: %.4f -> %s" % (ag["B"] - ag["A"], "HELD" if ag["B"] - ag["A"] <= 0.02 else "FAILED"))
    L.append("  P3 v1 key-correct within +-3pp of v0: %.3f vs %.3f -> %s" % (acc1, acc0, "HELD" if abs(acc1 - acc0) <= 0.03 else "FAILED"))
    d = byh["cross"]["A"] - byh["contested"]["A"]
    L.append("  P4 contested-half agreement lower than cross-tier by 2-6pp: cross - contested = %+.4f -> %s" % (d, "HELD" if 0.02 <= d <= 0.06 else "FAILED"))
    L.append("  P5 NO_YIELD 0-2 of %d: %d -> %s" % (n, states.get("NO_YIELD", 0), "HELD" if states.get("NO_YIELD", 0) <= 2 else "FAILED"))
    med = ct[len(ct) // 2] if ct else None; p95 = ct[min(len(ct) - 1, int(0.95 * len(ct)))] if ct else None
    L.append("  P6 completion_tokens median in [400, 1200] and p95 < 4000: median %s, p95 %s -> %s" % (med, p95, "HELD" if med is not None and 400 <= med <= 1200 and p95 < 4000 else "FAILED"))
    L.append("  P7 disagreements' matches decided at a rate within 10pp of the set's: |%.3f - %.3f| = %.3f -> %s" % (tr_dis, tr_set, abs(tr_dis - tr_set), "HELD" if abs(tr_dis - tr_set) <= 0.10 else "FAILED"))
    L.append("  not shown by a HELD verdict: that v0 is right more often than the record says; anything per cell; a drift rate; anything about the deployed judge")
    txt = "\n".join(L); print(txt)
    if complete:
        open(OUT, "w", encoding="utf-8").write(txt + "\n")
        import judge_solve_map as jsm
        P = payloads(ids)
        side = dict(vintage="v0", cache=rel(V0_DB), reference_model=SOLVER, deployment_fingerprint="unknown", protocol_id=PROTOCOL_ID + " (reconstructed from the SYSTEM bytes)",
                    system_sha256=F["system_sha256"], max_tokens=F["cap_default"], max_tokens_source="judge_solve_map.call default; no v0 row carries a cap", temperature="omitted",
                    finish_reason="unknown (pre-rule-9)", completion_tokens="per question below from answers.tokens (usage.completion_tokens)", minted_at="per question below from answers.ts (UTC)",
                    side_at_mint=SIDE, prompt_hash="per question below, reconstructed from judge_solve_map.SYSTEM + user_prompt and labelled reconstructed",
                    stamped_by="ARM-B-VINTAGE", stamped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                    agreement="legacy, agreement with v1 = A %.4f [%.4f, %.4f] (B %.4f) on %d canary questions, alarm state %s, %s" % (ag["A"], *ag["ciA"], ag["B"], n, alarm, time.strftime("%Y-%m-%d")),
                    set_hash=hh[:16],
                    questions={str(q): dict(v0_answer=v0[q][0], gt=v0[q][1], correct=v0[q][2], completion_tokens=v0[q][3], minted_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(v0[q][4])),
                                            prompt_hash_reconstructed=prompt_hash(P[q][0], P[q][1])) for q in ids})
        if os.path.exists(SIDECAR):
            old = json.load(open(SIDECAR, encoding="utf-8"))
            print("NOTE: %s exists (stamped %s); not rewritten" % (rel(SIDECAR), old.get("stamped_at")))
        else:
            json.dump(side, open(SIDECAR, "w", encoding="utf-8"), indent=1)
            print("written: %s" % rel(SIDECAR))
        print("written: %s" % rel(OUT))
    else:
        open(OUT_PILOT, "w", encoding="utf-8").write(txt + "\n")
        print("PARTIAL / PILOT readout: written to %s; the outcome file of record is untouched" % rel(OUT_PILOT))


# ---------------------------------------------------------------- selftest (no DB, no env)

def selftest():
    # the draw: 146 contested / 133 cross (the record's halves after the overlap rule), 0 excluded -> 105 / 95
    ms = [dict(qid=q, stratum="contested") for q in range(1, 147)] + [dict(qid=q, stratum="cross") for q in range(137, 280)]
    half, both = halves_of(ms)
    assert len(half) == 279 and len(both) == 10 and sum(1 for h in half.values() if h == "contested") == 146, (len(half), len(both))
    ids, info = draw(half, set())
    assert len(ids) == 200 and ids == sorted(ids) and info["contested"] == (105, 146) and info["cross"] == (95, 133), info
    assert draw(half, set())[0] == ids                                        # deterministic
    ids2, info2 = draw(half, {5, 200, 250})
    assert info2["eligible"] == 276 and len(ids2) == 200 and not {5, 200, 250} & set(ids2)
    ids3, info3 = draw({q: "contested" for q in range(1, 151)}, set())        # eligible < 200 -> the eligible count
    assert len(ids3) == 150 and info3["taken"] == 150
    assert len(set_hash(ids)) == 64 and set_hash(ids) != set_hash(ids2)
    # parse classes
    assert classify("stop", "A") == "YIELD" and classify("stop", "") == "NO_YIELD" and classify("length", "A") == "NON_TERMINATED" and classify("content_filter", "") == "UNUSABLE"
    # agreement, both conventions; a non-yielded v1 row counts as disagreement under A only
    v0 = {q: "A" for q in range(10)}; v1 = dict(v0); v1[3] = "B"; v1[7] = ""
    a = agreement(v0, v1, list(range(10)))
    assert a["same"] == 8 and abs(a["A"] - 0.8) < 1e-12 and a["nB"] == 9 and a["sameB"] == 8, a
    lo, hi = wilson(178, 200); assert abs(lo - 0.8391) < 5e-4 and abs(hi - 0.9262) < 5e-4, (lo, hi)
    assert abs(mcnemar_exact(5, 5) - 1.0) < 1e-12 and mcnemar_exact(0, 0) == 1.0 and abs(mcnemar_exact(0, 6) - 2 / 64) < 1e-12
    assert abs(alarm_bar(200) - 0.8896) < 5e-4 and alarm_bar(150) < alarm_bar(200)
    assert prompt_hash("s", "u") == prompt_hash("s", "u") and prompt_hash("s", "u") != prompt_hash("s", "v")
    # the gate: refuses without the env, without the READY, without the registered hash
    saved = os.environ.pop(GO_ENV, None)
    try:
        try: go_gate("selftest", "deadbeefdeadbeef"); raise AssertionError("gate did not refuse")
        except SystemExit as e: assert "refused" in str(e)
        os.environ[GO_ENV] = GO_VALUE
        try: go_gate("selftest", "deadbeefdeadbeef"); raise AssertionError("gate did not refuse without the READY / the hash")
        except SystemExit as e: assert "NOT REGISTERED" in str(e) or "MISSING" in str(e), str(e)
    finally:
        if saved is None: os.environ.pop(GO_ENV, None)
        else: os.environ[GO_ENV] = saved
    assert SET_HASH_OF_RECORD is None or re.fullmatch(r"[0-9a-f]{16}", SET_HASH_OF_RECORD)
    print("selftest OK: draw (105/95, deterministic, exclusion, short set), parse classes, agreement A/B, Wilson, McNemar, alarm bar, prompt hash, the READY gate (no DB, 0 calls)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", "--report", action="store_true", dest="analyze")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--override-guard", action="store_true")
    a = ap.parse_args()
    OVERRIDE_GUARD = a.override_guard
    if a.selftest: selftest(); sys.exit(0)
    import pool_guard
    print("[POOL] %s" % pool_guard.assert_pool_of_record(POOL_ID))
    if a.dry_run: dry_run()
    elif a.pilot is not None or a.run: run(a.pilot, a.workers)
    elif a.analyze: analyze()
    else: ap.print_help()
