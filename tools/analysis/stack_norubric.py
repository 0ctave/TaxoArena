"""STACK-NORUBRIC - the STACK-v2 recipe WITHOUT the anchor rubric, on the 944 R3 key-decidable pairs
(docs/design/FRAMEWORK.md, "Tests to register before shipping", item 20; registered by reference at eaf1dbf;
queue position Block 2 (d) in docs/plan_2026-09-15.md; decisions D2 and D3 of that plan's Amendment 1 bind this script).

  python tools/analysis/stack_norubric.py --dry-run [--pilot N]        (0 calls: assemble every payload, print counts)
  python tools/analysis/stack_norubric.py --run [--pilot N] [--workers 8] [--maxtok 8192] [--ctrl 53]
  python tools/analysis/stack_norubric.py --analyze

WHAT IS JUDGED. The 944 key-decidable R3 matches exactly as stack_v2_promptv2_grok.db holds them (the STACK-v2
grok session of record: 0.865 all-decidable, ties 5.6%), every question in the pool of record p2dca21ab5f4ef3ae.
Three arms, one session, jobs interleaved per match so every arm sees the same deployment hour:
  norubric  the recipe FULLY DE-INDUCED (plan Amendment 1, D3): v2 verify-first mechanics, the reference block,
            dual order, confidence kept - but $systemPrompt = GENERIC_SYSTEM and $rubric = GENERIC_RUBRIC, both
            IMPORTED from rubric_value_contrast (the production GENERIC_JUDGE branch, the comparator the
            rubric-value line was measured against). Neither the anchor's induced rubric nor its induced persona
            (itself ~150 words of domain guidance) reaches the judge, so the run answers "recipe without the
            anchor rubric". The slot is not deleted: the user template says "referencing your rubric" and the
            mechanics say "against the rubric", text the item did not name.
            --sp anchor is the PERSONA-KEPT variant (anchor's induced $systemPrompt kept, only the $rubric slot
            swapped): an opt-in arm under its own cache (stack_norubric_spanchor.db), labelled
            "norubric-persona-kept" in its outcome, NOT the registered verdict.
  ctrl1     the recipe WITH the anchor rubric, BYTE-IDENTICAL to the cached session's prompts (asserted against
  ctrl2     stack_judge.system_for every time a payload is built), judged twice on a seeded subset of --ctrl
            matches. With the cached session that gives the >= 3 byte-identical control sessions the deployment
            rule asks for (FRAMEWORK.md, "Judge" rule) and measures the SESSION FLOOR the criterion is read against.
Budget at the defaults: 944 x 2 + 53 x 2 x 2 = 2,100 calls, the figure registered in the plan.

CRITERION (registered, quoted): non-inferior within 2pp under both tie conventions against the session floor.
  Convention A, decisive-and-correct: TIE scores as wrong (NO-TIES, the campaign's headline convention).
  Convention B, correct-given-committed: accuracy among non-TIE verdicts (PAIR-NOREF's decomposition).
  Unparsed or non-terminated verdicts (INVALID, or finish_reason=length in either order) are NON_TERMINATED:
  never a verdict and never a tie. They stay in the paired set and score WRONG under A; under B they are
  excluded from the committed denominator (plan Amendment 1, D3). The same rule applies to the control sessions.
  Read: delta = norubric - cached session on the 944, per convention; PASS iff delta >= -0.02 under both.
  The session floor (the three byte-identical sessions' spread on the control subset, and their verdict
  disagreement against DECOMP's 0.057) is printed beside it: a |delta| inside the floor is reported as
  indistinguishable from a byte-identical re-run rather than as a difference; an unmeasured floor is None and
  is printed as "floor not measured", never as 0.
PREDICTION (registered): non-inferior (the record's rubric value is 0 to +1pp n.s.).

INVARIANTS. pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL) before anything; the pool id is the first line printed; every
question asserted inside p2dca21ab5f4ef3ae; Meta-Llama-3-70B-Instruct asserted absent; own cache
(stack_norubric.db, never an existing one; a resumed cache must carry the same judge, cap, temperature, protocol,
arm and control size in its meta table or the run refuses - a new cap is a NEW SESSION and gets a new cache: move
the old one aside); every call through rejudge_reasoning.call_judge_full with finish_reason, completion tokens
and provider stored per order (provider_response_id is not returned by call_judge_full and is not stored; the gap
is printed in the outcome header); --maxtok explicit (default 8192 = the constant the cached session posted, so
the controls stay byte-identical in the request body too); temperature OMITTED from the payload (provider default,
as the cached session; plan Amendment 1, D2 - recorded in meta and printed in every outcome header; --temperature
T is a recorded deviation under the same refusal rule); resume from cache by (match_id, arm); the first 12
matches of a --run are a PILOT block read by the truncation guard before the rest is posted; a verdict is REFUSED
when more than 5% of the deciding subset of any arm is unparsed or non-terminated; the script's sha256 is printed
and pinned ONCE at first launch (relaunches recorded under their own keys) so the outcome can be marked STALE;
an outcome from fewer than the 944 norubric matches (a pilot, an incomplete run) is stamped PILOT/INCOMPLETE and
written to a separate file, never over the file of record.
"""
import os, sys, json, time, random, hashlib, sqlite3, argparse, threading, inspect, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import stack_judge as sj
import prompt_v2
import rubric_value_contrast as rvc

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


POOL = pool_guard.FROZEN_POOL_ID
JUDGE = "grok-4-1-fast-non-reasoning"
PROTOCOL = "STACK-v2 pairwise: v2 verify-first mechanics + grok-reasoning reference block + confidence; dual order, TIE on flip"
MAXTOK_DEFAULT = 8192          # rejudge_reasoning.MAX_TOKENS, the value stack_v2_promptv2_grok.db was judged under
CTRL_DEFAULT = 53              # 53 x 2 arms x 2 orders = 212 calls -> 2,100 with the 944 x 2
PILOT_BLOCK = 12               # the plan's pilot: the first 12 matches of every run are read by the truncation guard first
SEED = 42
N_TARGETS = 944
EXCLUDED = "Meta-Llama-3-70B-Instruct"
X = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
PW_REF = os.path.join(X, "stack_v2_promptv2_grok.db")        # the STACK-v2 grok session of record
GENERIC_SYSTEM = rvc.GENERIC_SYSTEM   # imported, never retyped (plan Amendment 1, D3): the production GENERIC_JUDGE branch
GENERIC_RUBRIC = rvc.GENERIC_RUBRIC   # (rubric_value_contrast.py lines 67-69); also rejudge_grok.build_system_prompt's rubric default
SP_MODE = "generic"   # registered arm; --sp anchor = persona-kept variant (separate cache stack_norubric_spanchor.db; not the verdict)
NT = "NON_TERMINATED"  # the scored value of an unparsed or non-terminated verdict: wrong under A, not committed under B, never a tie
ARMS = ("norubric", "ctrl1", "ctrl2")
TEMPERATURE_DECISION = "omitted from the payload (provider default) by decision: docs/plan_2026-09-15.md Amendment 1, D2"


def script_sha():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def cache_path():
    return os.path.join(X, "stack_norubric%s.db" % ("" if SP_MODE == "generic" else "_sp" + SP_MODE))


def out_path():
    """The outcome file of record; only a complete (944 norubric matches) analysis writes it."""
    return cache_path()[:-3] + "_outcome.txt"


def out_path_partial():
    """PILOT / INCOMPLETE outcomes go here and never overwrite the file of record."""
    return cache_path()[:-3] + "_outcome_PILOT.txt"


def arm_label():
    return "norubric" if SP_MODE == "generic" else "norubric-persona-kept"


def norubric_description():
    if SP_MODE == "generic":
        return "$systemPrompt = GENERIC_SYSTEM, $rubric = GENERIC_RUBRIC (imported from rubric_value_contrast; fully de-induced; plan Amendment 1 D3)"
    return "$systemPrompt = the anchor's INDUCED persona (kept), $rubric = GENERIC_RUBRIC; opt-in persona-kept variant, NOT the registered verdict"


def temperature_label():
    return "omitted (provider default, as the cached session)" if rr.TEMPERATURE is None else "%g (explicit literal; deviation from D2, recorded)" % rr.TEMPERATURE


def targets():
    """The 944 key-decidable R3 matches of the cached STACK-v2 grok session, in a seeded order so a --pilot prefix
    and the control subset both span the strata. Returns [(mid, qid, a, b, anchor, cached_winner, cached_ref_letter)]."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0)
    out = []
    for mid, a, b, qid, anc, w, inv, rl in sqlite3.connect("file:%s?mode=ro" % PW_REF, uri=True).execute(
            "SELECT match_id, model_a, model_b, qid, anchor, winner, invalid, ref_letter FROM verdicts"):
        if inv or qid is None: continue
        if K[qid].get(a) is None or K[qid].get(b) is None or K[qid][a] == K[qid][b]: continue
        out.append((mid, qid, a, b, anc, w, rl))
    out.sort(); random.Random(SEED).shuffle(out)
    bad = [t for t in out if t[1] not in pool]
    assert not bad, "%d matches outside the pool of record %s" % (len(bad), POOL)
    assert not any(EXCLUDED in (t[2], t[3]) for t in out), "%s must be excluded" % EXCLUDED
    assert len(out) == N_TARGETS, "expected the %d key-decidable R3 pairs, found %d" % (N_TARGETS, len(out))
    return out, K


def systems_for(anc, rubrics):
    """(control system, norubric system). The control is built by stack_judge's own code path."""
    sp, rb = rubrics[anc]
    ctrl = sj.system_for(anc, rubrics)
    tmpl = prompt_v2.v2_system_template()
    assert ctrl == tmpl.replace("$systemPrompt", sp).replace("$rubric", rb) + "\n\n" + rj.SCHEMA_INSTRUCTION, "control prompt is not byte-identical to stack_judge's"
    persona = GENERIC_SYSTEM if SP_MODE == "generic" else sp
    nor = tmpl.replace("$systemPrompt", persona).replace("$rubric", GENERIC_RUBRIC) + "\n\n" + rj.SCHEMA_INSTRUCTION
    assert rb not in nor, "anchor rubric still present in the norubric prompt"
    if SP_MODE == "generic": assert sp not in nor, "anchor's induced persona still present in the de-induced prompt"
    return ctrl, nor


def jobs_for(sched, ctrl_n, pilot):
    """Interleaved per match: norubric, then (on the control subset) ctrl1 and ctrl2."""
    ctrl_ids = {t[0] for t in sched[:ctrl_n]}
    if pilot: sched = sched[:pilot]
    jobs = []
    for t in sched:
        jobs.append((t, "norubric"))
        if t[0] in ctrl_ids: jobs += [(t, "ctrl1"), (t, "ctrl2")]
    return jobs


def build(job, rubrics, refs, evals):
    """Both orders' (system, user) for one job, or None with a reason."""
    (mid, qid, a, b, anc, _, rl), arm = job
    ra, rb = evals.get((qid, a)), evals.get((qid, b)); ref = refs.get(qid)
    if ra is None or rb is None: return None, "no eval row"
    if ref is None: return None, "no reference"
    if rl and ref[0] != rl: return None, "reference vintage differs from the cached session (%s vs %s)" % (ref[0], rl)
    if anc not in rubrics: return None, "no anchor rubric"
    ctrl, nor = systems_for(anc, rubrics)
    system = nor if arm == "norubric" else ctrl
    q = rref.with_reference(ra[0], ref)
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    return (system, rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta), ref), None


def payload(system, user):
    """LOCAL COPY of the request body rejudge_reasoning.call_judge_full posts (rejudge_reasoning.py lines 92-96:
    model, max_tokens, messages[system, user], temperature only when set), assembled here for the dry run only.
    assert_payload_copy() checks the copy against that source on every dry run."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None: body["temperature"] = rr.TEMPERATURE
    return body


def assert_payload_copy(body):
    """The dry-run body must carry the key tuple call_judge_full builds, and the source must still build it that way."""
    want = ("model", "max_tokens", "messages") + (("temperature",) if rr.TEMPERATURE is not None else ())
    assert tuple(body) == want, "payload key tuple %r != %r" % (tuple(body), want)
    src = inspect.getsource(rr.payload_body)   # 2026-09-16: the body builder was factored out of call_judge_full (JUDGE-WIRING), bytes unchanged
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    assert 'payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src, \
        "rejudge_reasoning.call_judge_full no longer builds the body payload() copies; update payload()"
    assert body["model"] == JUDGE and body["max_tokens"] == rr.MAX_TOKENS


def meta_of(maxtok, ctrl_n):
    return {"pool": POOL, "judge": JUDGE, "provider": "azure", "protocol": PROTOCOL, "max_tokens": str(maxtok), "temperature": temperature_label(),
            "temperature_decision": TEMPERATURE_DECISION, "ctrl": str(ctrl_n), "sp_mode": SP_MODE, "arm": arm_label(),
            "norubric_prompt": norubric_description(), "reference": "grok-reasoning", "control_of_record": os.path.basename(PW_REF)}


def open_cache():
    con = sqlite3.connect(cache_path())
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                "finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, provider1 TEXT, provider2 TEXT, raw1 TEXT, raw2 TEXT, sys_sha TEXT, ts REAL, "
                "PRIMARY KEY (match_id, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
    con.commit(); return con


def pin_meta(con, maxtok, ctrl_n):
    """A resumed cache must have been judged under the same parameters; otherwise the arms would mix sessions.
    The producing script's sha and 'started' are pinned ONCE; relaunches are recorded under their own keys."""
    want = meta_of(maxtok, ctrl_n); have = dict(con.execute("SELECT k, v FROM meta"))
    if have:
        diff = {k: (have.get(k), v) for k, v in want.items() if k in have and have[k] != v}
        if diff:
            raise SystemExit("[CACHE] %s was judged under different parameters; refusing to resume into it: %s\n"
                             "        A new cap, temperature or arm is a NEW SESSION and gets a new cache: move %s aside (rename it) and relaunch."
                             % (os.path.basename(cache_path()), "; ".join("%s cached=%r now=%r" % (k, a, b) for k, (a, b) in diff.items()), cache_path()))
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    for k, v in want.items(): con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (k, v))
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("script_sha256", script_sha()))     # pinned once, at first launch
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("started", ts))                     # written once
    if have:
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("script_sha256_relaunch_" + ts, script_sha()))
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("resumed", (have.get("resumed", "") + "; " if have.get("resumed") else "") + ts))
    con.commit()


def prepare(pilot, ctrl_n, maxtok):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = maxtok
    sj.PROMPT = "v2"
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics()
    sched, K = targets()
    jobs = jobs_for(sched, ctrl_n, pilot)
    evals = rj.load_eval_rows([j[0][1] for j in jobs], {j[0][2] for j in jobs} | {j[0][3] for j in jobs})
    return sched, jobs, rubrics, refs, evals, K


def dry_run(pilot, ctrl_n, maxtok):
    sched, jobs, rubrics, refs, evals, K = prepare(pilot, ctrl_n, maxtok)
    built = []; skipped = defaultdict(int); sys_hashes = defaultdict(set)
    for j in jobs:
        pr, why = build(j, rubrics, refs, evals)
        if pr is None: skipped[why] += 1; continue
        built.append((j, pr)); sys_hashes[j[1]].add(hashlib.sha256(pr[0].encode("utf-8")).hexdigest()[:16])
    assert sys_hashes.get("ctrl1", set()) == sys_hashes.get("ctrl2", set()), "the two control sessions do not share their system prompts"
    n_calls = 2 * len(built)
    by_arm = defaultdict(int)
    for j, _ in built: by_arm[j[1]] += 1
    print("STACK-NORUBRIC DRY RUN: nothing posted")
    print("  matches      %d of %d (%s)" % (len({j[0][0] for j in jobs}), N_TARGETS, "pilot %d" % pilot if pilot else "full"))
    print("  jobs         %d = %s" % (len(built), " + ".join("%s %d" % (a, by_arm[a]) for a in ARMS)))
    print("  CALL COUNT   %d (2 orders per job)" % n_calls)
    if skipped: print("  skipped      %s" % dict(skipped))
    print("  POOL         %s" % POOL)
    print("  JUDGE        %s (provider azure)" % JUDGE)
    print("  PROTOCOL     %s" % PROTOCOL)
    print("  TEMPERATURE  %s   [%s]" % (temperature_label(), TEMPERATURE_DECISION))
    print("  CAP          max_tokens %d (stated default %d)" % (rr.MAX_TOKENS, MAXTOK_DEFAULT))
    print("  CACHE        %s%s" % (cache_path(), "   <- EXISTS" if os.path.exists(cache_path()) else "   (new)"))
    print("  OUTCOME      %s (file of record, complete runs only) | %s (pilot / incomplete)" % (out_path(), out_path_partial()))
    print("  CONTROL      %d matches x 2 byte-identical sessions; with %s that is 3 sessions" % (min(ctrl_n, len(sched)), os.path.basename(PW_REF)))
    print("  ARM          %s" % arm_label())
    print("  NORUBRIC     %s" % norubric_description())
    print("  SCORING      unparsed / non-terminated verdicts stay in the paired set as %s: wrong under A, not committed under B, never a tie" % NT)
    print("  PILOT BLOCK  the first %d matches of a --run are judged first and read by the truncation guard before the rest is posted" % PILOT_BLOCK)
    print("  EXCLUDED     %s asserted absent; every question asserted in %s" % (EXCLUDED, POOL))
    print("  SYSTEM SHAS  distinct system prompts per arm: %s" % ", ".join("%s %d" % (a, len(sys_hashes[a])) for a in ARMS if a in sys_hashes))
    print("  SCRIPT SHA   %s" % script_sha())
    (j0, (s0, u0, u0b, ref0)) = built[0]
    b0 = payload(s0, u0); assert_payload_copy(b0)
    print("  MODEL FIELD  %s (first assembled payload; key tuple %s verified against rejudge_reasoning.call_judge_full)" % (b0["model"], tuple(b0)))
    print("\n=== FIRST PAYLOAD: match %d, arm %s, order 1 (request body keys %s) ===" % (j0[0][0], j0[1], sorted(b0)))
    print("--- system ---"); print(s0); print("--- user ---"); print(u0); print("--- end of first payload ---")
    return 0


def _judge_block(todo, rubrics, refs, evals, con, workers, tag):
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        pr, why = build(job, rubrics, refs, evals)
        if pr is None: return None
        system, u1, u2, ref = pr
        (mid, qid, a, b, anc, _, _), arm = job
        c1, p1, k1, _, f1, _ = judge_full(system, u1); c2, p2, k2, _, f2, _ = judge_full(system, u2)
        raw1, raw2 = rr.strip_think(c1), rr.strip_think(c2)
        v1, cf1 = rj.parse_judge(raw1); v2, cf2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, arm, a, b, qid, anc, ref[0], int(ref[2]), v1, v2, cf1, cf2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv),
                f1, f2, k1, k2, p1, p2, raw1, raw2, hashlib.sha256(system.encode("utf-8")).hexdigest()[:16], time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 25), row); con.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo): print("  [%s] %d/%d (ok %d, skip %d, err %d)" % (tag, i, len(todo), ok, skip, err), flush=True)
    print("[%s] done: ok %d, skipped %d, errors %d" % (tag, ok, skip, err), flush=True)


def run(pilot, ctrl_n, maxtok, workers):
    """Returns True when the run may be analysed; False when the pilot guard stopped it."""
    rr.load_env()
    sched, jobs, rubrics, refs, evals, K = prepare(pilot, ctrl_n, maxtok)
    con = open_cache(); pin_meta(con, maxtok, ctrl_n)
    done = {(m, a) for m, a in con.execute("SELECT match_id, arm FROM verdicts")}
    todo = [j for j in jobs if (j[0][0], j[1]) not in done]
    print("STACK-NORUBRIC RUN: pool %s | judge %s | arm %s | jobs %d | cached %d | to do %d (%d calls) | max_tokens %d | temperature %s | workers %d | script %s"
          % (POOL, JUDGE, arm_label(), len(jobs), len(jobs) - len(todo), len(todo), 2 * len(todo), maxtok, temperature_label(), workers, script_sha()[:16]), flush=True)
    pilot_ids = {t[0] for t in sched[:PILOT_BLOCK]}
    first = [j for j in todo if j[0][0] in pilot_ids]; rest = [j for j in todo if j[0][0] not in pilot_ids]
    if first:
        print("  PILOT BLOCK: %d jobs (%d calls) on the first %d matches, then the truncation guard" % (len(first), 2 * len(first), PILOT_BLOCK), flush=True)
        _judge_block(first, rubrics, refs, evals, con, workers, "pilot")
    bad = truncation_readout(con, only_ids=pilot_ids)
    if bad:
        print("  PILOT GUARD FAILED on %s: not posting the remaining %d jobs.\n"
              "  Read the pilot rows above: finish_reason=length means the cap is too small -> relaunch with a larger --maxtok;\n"
              "  finish_reason=stop with an unparsed answer is a transient parse failure -> relaunch with the same command.\n"
              "  EITHER WAY this cache holds the failed pilot rows and a relaunch would re-read them and fail again, and a new cap is\n"
              "  refused by the resume guard: move %s aside (rename it; a new cap is a new session and gets a new cache) and relaunch."
              % (", ".join(bad), len(rest), cache_path()), flush=True)
        return False
    if rest:
        _judge_block(rest, rubrics, refs, evals, con, workers, "main")
    truncation_readout(con)
    return True


def unparsed(r):
    """invalid, or either order non-terminated: NON_TERMINATED is never a verdict and never a tie."""
    return bool(r["invalid"]) or r["finish1"] == "length" or r["finish2"] == "length"


def load_rows(con):
    cols = ["match_id", "arm", "model_a", "model_b", "qid", "winner", "flip", "invalid", "finish1", "finish2", "ctok1", "ctok2"]
    return [dict(zip(cols, r)) for r in con.execute("SELECT %s FROM verdicts" % ",".join(cols))]


def truncation_readout(con, only_ids=None):
    """Per-arm unparsed-or-non-terminated rate; returns the arms above 5%. On a pilot read (only_ids given) every
    unparsed row is printed with its finish_reason and completion tokens so a transient parse failure can be told
    from a cap problem."""
    rows = load_rows(con); bad = []
    if only_ids is not None: rows = [r for r in rows if r["match_id"] in only_ids]
    for arm in ARMS:
        s = [r for r in rows if r["arm"] == arm]
        if not s: continue
        u = sum(1 for r in s if unparsed(r))
        fr = defaultdict(int)
        for r in s: fr[r["finish1"] or "(none)"] += 1; fr[r["finish2"] or "(none)"] += 1
        ct = [c for r in s for c in (r["ctok1"], r["ctok2"]) if c is not None]
        over = u > 0.05 * len(s)
        if over: bad.append(arm)
        print("  TRUNCATION GUARD %-8s n=%4d | unparsed or non-terminated %d (%.1f%%) | finish_reason %s | completion tokens max %s | %s"
              % (arm, len(s), u, 100 * u / len(s), dict(fr), max(ct) if ct else "?", "OK" if not over else "ABOVE 5%: the verdict will be REFUSED"))
        if only_ids is not None:
            for r in sorted(s, key=lambda r: r["match_id"]):
                if unparsed(r):
                    print("      pilot row %-8s match %6d | winner %-28s | invalid %d | finish %s/%s | completion tokens %s/%s"
                          % (arm, r["match_id"], r["winner"], r["invalid"], r["finish1"], r["finish2"], r["ctok1"], r["ctok2"]))
    return bad


def analyze():
    if not os.path.exists(cache_path()):
        print("[CACHE] %s does not exist: nothing judged, nothing written" % cache_path()); return
    con = sqlite3.connect("file:%s?mode=ro" % cache_path(), uri=True)
    rows = load_rows(con)
    sched, K = targets()
    cached = {t[0]: t[5] for t in sched}
    dw = {t[0]: (t[2] if K[t[1]][t[2]] else t[3]) for t in sched}     # the key-correct side
    meta = dict(con.execute("SELECT k, v FROM meta"))
    pinned = meta.get("script_sha256")
    stale = pinned not in (None, script_sha())
    arms = defaultdict(dict)
    for r in rows: arms[r["arm"]][r["match_id"]] = r
    n_nor = len(arms.get("norubric", {}))
    partial = n_nor < len(sched)
    out = out_path_partial() if partial else out_path()
    L = ["=== STACK-NORUBRIC: the recipe without the anchor rubric, on the %d key-decidable R3 pairs (pool %s) ===" % (N_TARGETS, POOL)]
    if partial:
        L.append("  %s: %d of %d norubric matches cached. NOT the outcome of record; written to %s"
                 % ("PILOT n=%d" % n_nor if n_nor <= PILOT_BLOCK else "INCOMPLETE n=%d" % n_nor, n_nor, len(sched), os.path.basename(out)))
    L += ["  arm %s | judge %s | %s | max_tokens %s | temperature %s | cache %s"
          % (arm_label(), JUDGE, PROTOCOL, meta.get("max_tokens", "?"), meta.get("temperature", "?"), os.path.basename(cache_path())),
          "  temperature decision: %s" % meta.get("temperature_decision", TEMPERATURE_DECISION),
          "  norubric prompt: %s" % meta.get("norubric_prompt", norubric_description()),
          "  provenance: finish_reason, completion tokens, provider and system-prompt sha stored per order; provider_response_id / batch_id NOT stored "
          "(rejudge_reasoning.call_judge_full does not return the response id; JUDGE-FINISH-AUDIT, Block 4)",
          "  scoring: unparsed / non-terminated verdicts kept in the paired set as %s (wrong under A, not committed under B, never a tie); same for the controls" % NT,
          "  producing script sha256 (pinned at first launch) %s | current %s%s | started %s%s"
          % ((pinned or "?")[:16], script_sha()[:16], "   <- STALE: the cache was judged by a different version" if stale else "",
             meta.get("started", "?"), " | resumed " + meta["resumed"] if meta.get("resumed") else "")]
    if SP_MODE != "generic":
        L.append("  NOTE: persona-kept variant (--sp anchor): the anchor's induced persona reaches the judge; this is an opt-in arm, NOT the registered verdict")
    # GUARD, evaluated on the DECIDING subset of every arm (every judged match here is key-decidable by construction)
    refused = []
    for arm, d in arms.items():
        u = sum(1 for r in d.values() if unparsed(r))
        L.append("  guard %-8s n=%4d | unparsed or non-terminated %d (%.1f%%)" % (arm, len(d), u, 100 * u / max(1, len(d))))
        if len(d) and u > 0.05 * len(d): refused.append((arm, u, len(d)))
    if refused or not arms.get("norubric"):
        L.append("  VERDICT REFUSED: %s" % ("; ".join("%s %d of %d unparsed" % x for x in refused) if refused else "no norubric verdicts cached"))
        L.append("  An unparsed verdict scores as wrong, so any accuracy would be a floor, not an estimate. Re-run with a larger --maxtok (a new cache) or record non-termination as a property of the arm.")
        txt = "\n".join(L); print(txt); open(out, "w", encoding="utf-8").write(txt + "\n"); return

    def acc(win, keys):
        """(convention A: correct / n, TIE and NON_TERMINATED wrong; convention B: correct / committed, committed = n - ties - non-terminated;
        tie rate over n; n committed; n non-terminated)"""
        n = len(keys); c = sum(1 for k in keys if win[k] == dw[k]); t = sum(1 for k in keys if win[k] == "TIE"); u = sum(1 for k in keys if win[k] == NT)
        return c / max(1, n), c / max(1, n - t - u), t / max(1, n), n - t - u, u
    verdicts = lambda d: {m: (r["winner"] if not unparsed(r) else NT) for m, r in d.items()}   # unparsed rows stay in the set as NT
    nor = verdicts(arms["norubric"])
    common = sorted(set(nor) & set(cached))
    aN, bN, tN, cN, uN = acc(nor, common); aC, bC, tC, cC, uC = acc(cached, common)
    rng = random.Random(SEED); dA = []; dB = []
    for _ in range(2000):
        bs = [common[rng.randrange(len(common))] for _ in common]
        a1, b1, _, _, _ = acc(nor, bs); a2, b2, _, _, _ = acc(cached, bs); dA.append(a1 - a2); dB.append(b1 - b2)
    dA.sort(); dB.sort()
    b_ = sum(1 for k in common if nor[k] == dw[k] and cached[k] != dw[k]); c_ = sum(1 for k in common if cached[k] == dw[k] and nor[k] != dw[k])
    L.append("")
    L.append("  (1) PRIMARY, paired on %d matches: %s vs the cached STACK-v2 session (anchor rubric present)" % (len(common), arm_label()))
    L.append("      convention A  decisive-and-correct (ties and non-terminated wrong)   norubric %.3f (non-terminated %d) | cached %.3f (non-terminated %d) | delta %+.3f  95%% CI [%+.3f, %+.3f] | %d:%d McNemar p=%.4g"
             % (aN, uN, aC, uC, aN - aC, dA[50], dA[1949], b_, c_, p8.mcn(b_, c_)))
    L.append("      convention B  correct-given-committed (non-terminated excluded)      norubric %.3f (committed n=%d, non-terminated %d) | cached %.3f (committed n=%d, non-terminated %d) | delta %+.3f  95%% CI [%+.3f, %+.3f]"
             % (bN, cN, uN, bC, cC, uC, bN - bC, dB[50], dB[1949]))
    L.append("      tie rate      norubric %.3f | cached %.3f (%+.3f)" % (tN, tC, tN - tC))
    n_parsed = sum(1 for r in arms["norubric"].values() if not unparsed(r))
    flipN = sum(1 for r in arms["norubric"].values() if not unparsed(r) and r["flip"]) / max(1, n_parsed)
    L.append("      flip rate     norubric %.3f of %d parsed (reported, not gated)" % (flipN, n_parsed))
    # (2) the session floor: three byte-identical sessions on the control subset
    c1 = verdicts(arms.get("ctrl1", {})); c2 = verdicts(arms.get("ctrl2", {}))
    sub = sorted(set(c1) & set(c2) & set(cached) & set(nor))
    L.append("")
    L.append("  (2) SESSION FLOOR on the control subset (n=%d): the recipe WITH the rubric, three byte-identical sessions" % len(sub))
    floorA = floorB = None; dis = None
    if sub:
        sess = {"cached": cached, "ctrl1": c1, "ctrl2": c2}
        st = {k: acc(v, sub) for k, v in sess.items()}
        for k in ("cached", "ctrl1", "ctrl2"):
            L.append("      %-7s conv A %.3f | conv B %.3f | ties %.3f | non-terminated %d" % (k, st[k][0], st[k][1], st[k][2], st[k][4]))
        pairs = [("cached", "ctrl1"), ("cached", "ctrl2"), ("ctrl1", "ctrl2")]
        floorA = max(abs(st[x][0] - st[y][0]) for x, y in pairs); floorB = max(abs(st[x][1] - st[y][1]) for x, y in pairs)
        dis = {(x, y): sum(1 for k in sub if sess[x][k] != sess[y][k]) / len(sub) for x, y in pairs}
        L.append("      verdict disagreement between sessions: %s | DECOMP floor 0.057" % ", ".join("%s/%s %.3f" % (x, y, v) for (x, y), v in dis.items()))
        L.append("      floor = largest between-session accuracy gap: conv A %.3f | conv B %.3f  (n=%d: an SE of about %.3f on each gap)"
                 % (floorA, floorB, len(sub), (0.25 / len(sub)) ** 0.5 * 2 ** 0.5))
        an, bn, _, _, _ = acc(nor, sub)
        mA = sum(st[k][0] for k in st) / 3; mB = sum(st[k][1] for k in st) / 3
        L.append("      norubric on the same subset: conv A %.3f (mean of the 3 sessions %.3f, %+.3f) | conv B %.3f (mean %.3f, %+.3f)" % (an, mA, an - mA, bn, mB, bn - mB))
    else:
        L.append("      no control verdicts cached: the floor is NOT MEASURED in this session (DECOMP's 0.057 stands as the reference)")
    # (3) the registered criterion
    okA = (aN - aC) >= -0.02; okB = (bN - bC) >= -0.02
    vs_floor = lambda d, fl: "floor not measured" if fl is None else "%s floor %.3f" % (">" if abs(d) > fl else "<=", fl)
    inside = floorA is not None and floorB is not None and abs(aN - aC) <= floorA and abs(bN - bC) <= floorB
    L.append("")
    L.append("  (3) REGISTERED CRITERION: non-inferior within 2pp under both tie conventions against the session floor")
    L.append("      convention A delta %+.3f >= -0.020: %s | convention B delta %+.3f >= -0.020: %s" % (aN - aC, "OK" if okA else "FAIL", bN - bC, "OK" if okB else "FAIL"))
    L.append("      read against the floor: |delta A| %.3f %s; |delta B| %.3f %s" % (abs(aN - aC), vs_floor(aN - aC, floorA), abs(bN - bC), vs_floor(bN - bC, floorB)))
    prefix = ("PILOT n=%d, NOT the verdict of record: " % n_nor if partial else "") + ("persona-kept variant, NOT the registered verdict: " if SP_MODE != "generic" else "")
    L.append("      -> %s%s%s" % (prefix, "PASS: NON-INFERIOR" if okA and okB else "FAIL: the anchor rubric is worth more than 2pp under at least one convention",
                                  "; the delta sits inside the session floor, indistinguishable from a byte-identical re-run" if inside else ""))
    L.append("      prediction was non-inferior (rubric value 0 to +1pp n.s.): %s" % ("as predicted" if okA and okB else "NOT as predicted"))
    if stale: L.append("      STALE: producing code hash differs from the cache's pinned first-launch sha; re-run --analyze from the recorded version or re-register")
    txt = "\n".join(L); print(txt); open(out, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    print("[POOL] %s (pool of record; active pool verified by pool_guard)" % POOL, flush=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first payload, post nothing")
    ap.add_argument("--run", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="only the first N matches (all their arms)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=MAXTOK_DEFAULT, help="completion cap; default %d = the cached session's" % MAXTOK_DEFAULT)
    ap.add_argument("--temperature", type=float, default=None, help="DEVIATION from plan Amendment 1 D2 (omitted); written as a literal and recorded; the controls then stop being byte-identical to the cached session's request body")
    ap.add_argument("--ctrl", type=int, default=CTRL_DEFAULT, help="matches per byte-identical control session (default %d -> 2,100 calls)" % CTRL_DEFAULT)
    ap.add_argument("--sp", choices=["generic", "anchor"], default="generic",
                    help="norubric $systemPrompt: generic = GENERIC_SYSTEM, fully de-induced (registered, D3); anchor = the anchor's induced persona kept (opt-in, own cache, not the verdict)")
    a = ap.parse_args(); SP_MODE = a.sp; rr.TEMPERATURE = a.temperature
    if a.temperature is not None:
        print("[TEMPERATURE] --temperature %g DEVIATES from plan Amendment 1 D2 (omitted); it is recorded in meta and the controls are no longer byte-identical to the cached session's request body" % a.temperature, flush=True)
    if a.dry_run: sys.exit(dry_run(a.pilot, a.ctrl, a.maxtok))
    elif a.run:
        if run(a.pilot, a.ctrl, a.maxtok, a.workers): analyze()
        else: sys.exit(2)
    elif a.analyze: analyze()
    else: ap.print_help()
