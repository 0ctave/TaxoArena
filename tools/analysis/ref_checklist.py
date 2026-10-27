"""REF-CHECKLIST, judging half (docs/judge_v2_program.md, "Registered 2026-09-17 ... REF-CHECKLIST"; registered before
any code or call). Three FRESH arms of the STACK-v2 recipe on grok-4-1-fast-non-reasoning, interleaved in one session
on the 944 key-decidable R3 matches, differing ONLY in the question block:
  REF        the recipe's answer-reference block, byte-identical to RECIPE-GROK (stack_v2_promptv2_grok.db): the
             session control. Asserted against a line-for-line replica of stack_judge.run's assembly on every job.
  CHECKLIST  the reference block replaced by the verification checklist (checklist_gen.py) rendered as a bullet list
             under the SAME wrapper sentence with "solution" -> "verification checklist":
                 [Reference verification checklist — produced independently, may be wrong]
                 Required (a correct answer must contain or rely on):
                 - ...
                 Pitfalls (a wrong answer typically shows):
                 - ...
             The wrapper is derived from rejudge_reference.with_reference at import time, never retyped.
  BOTH       the answer reference block, then the checklist block.
The system prompt (v2 verify-first mechanics + anchor rubric + confidence + SCHEMA_INSTRUCTION) is the same bytes in
all three arms; dual order, TIE on flip, cap 8192, temperature omitted (D2). Matches whose checklist the audit
dropped, or whose checklist did not parse, are EXCLUDED from all three arms and counted.

  python tools/analysis/ref_checklist.py --dry-run [--pilot N]     (0 calls: assemble every payload, print the first)
  python tools/analysis/ref_checklist.py --run [--pilot N] [--workers 8]
  python tools/analysis/ref_checklist.py --analyze

Budget: 3 arms x 944 matches x 2 orders = 5,664 calls at most (fewer by the excluded matches), under the 4,000-match rule.
Comparators from cache: RECIPE-GROK (REF, other session -> the session floor against the fresh REF arm) and PAIR-NOREF
(neither reference nor checklist).

SCORING (stack_norubric conventions): A = decisive-and-correct (TIE and NON_TERMINATED wrong); B = correct-given-
committed (TIE and NON_TERMINATED out of the denominator). An unparsed verdict or finish_reason=length in either order
is NON_TERMINATED: never a verdict, never a tie. Paired McNemar on convention A; question-clustered bootstrap
(B=2000, seed 42, clusters = questions) for the CIs of both conventions' deltas.

REGISTERED CRITERIA (quoted from the registration):
 (1) PRIMARY: BOTH vs REF on key-decidable, p < 0.05 either direction, reported with the session floor (REF-fresh vs
     RECIPE-GROK) beside it.
 (2) CHECKLIST vs REF: the falsifier line - CHECKLIST alone at or above REF on key-decidable falsifies the reference
     line as the record states it (the value of a reference is verification structure, not the answer).
 (3) reference-WRONG stratum: CHECKLIST and BOTH vs REF, paired.
 (4) leakage: gemini-agreement delta of CHECKLIST vs REF; expected NEGATIVE.
PREDICTIONS: CHECKLIST below REF by 3-6pp; BOTH within the session floor of REF; on the reference-wrong stratum
CHECKLIST and BOTH above REF by >= 5pp; gemini agreement lower under CHECKLIST by >= 2pp.
LEAKAGE READOUTS (criterion 4), three of them, each named after the module whose formula it is:
  - the CONSENSUS-FIT coefficient proper: format_ref.fit (= consensus_fit.logistic on the rows format_ref.rows_pairwise
    builds: KEY = cf.sign_contrast(key favours A, key favours B), REF = cf.sign_contrast(reference letter == A's answer,
    == B's answer), winner A/B/TIE with ties half-weighted, NON_TERMINATED rows skipped as rows_pairwise skips invalid
    ones) fitted per arm on the common matches; the REF coefficient is the leakage predictor, its delta CHECKLIST - REF
    and BOTH - REF are printed. The functions are REUSED, not replicated.
  - ref_qualify (3)'s per-contestant answer-agreement, REPLICATED with the arm's verdict in place of the reference
    letter: for each contestant m, over the matches m plays with a committed verdict, the share of verdicts that side
    with m (ref_qualify: over the pool questions m answered, the share where the reference letter equals m's answer).
    The registered "gemini delta" is this share's CHECKLIST - REF difference.
  - the reference-mirroring rate: share of committed verdicts siding with the model whose answer equals the reference
    letter, where exactly one side does (consensus_fit's readout (2) cell "reference agrees with ...", collapsed).
Reference correctness is the cached grok-reasoning letter against the key.

INVARIANTS: pool_guard.assert_pool_of_record first; every question inside p2dca21ab5f4ef3ae; Meta-Llama-3-70B-Instruct
absent; reference vintage equal to the cached session's letter; own cache experiment_results/x12_crossdomain/
ref_checklist.db with per-order raw, finish_reason, completion tokens, provider, response id, max_tokens, arm and prompt
sha; meta pinned at first launch (judge, cap, temperature, protocol, checklist cache sha = content + audit decisions,
arm set, script sha); a resumed cache under different parameters is refused; the first PILOT_BLOCK=12 matches of a
--run (all three arms) are posted first and read by the truncation guard (5%, refuse) before the rest; the guard is
re-read before analysis and refuses the verdict; --analyze on fewer than the eligible matches writes a PILOT/INCOMPLETE
file and prints no REGISTERED line.
"""
import os, sys, json, time, random, hashlib, sqlite3, argparse, threading, inspect
import numpy as np
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
import pair_noref as pn
import checklist_gen as cg
import consensus_fit as cf
import format_ref as fr

POOL = pool_guard.MMLU_PRO_POOL
JUDGE = "grok-4-1-fast-non-reasoning"
MAXTOK = 8192                  # rejudge_reasoning.MAX_TOKENS, the value stack_v2_promptv2_grok.db was judged under (stack_judge never sets it)
PILOT_BLOCK = 12
SEED = 42
NBOOT = 2000
N_TARGETS = 944
EXCLUDED = "Meta-Llama-3-70B-Instruct"
ARMS = ("REF", "CHECKLIST", "BOTH")
NT = "NON_TERMINATED"
GEMINI = "gemini-3.1-pro_5-shots"
X = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
PW_REF = os.path.join(X, "stack_v2_promptv2_grok.db")     # RECIPE-GROK, the STACK-v2 grok session of record
PW_NOREF = os.path.join(X, "pairnoref.db")                # PAIR-NOREF
CACHE = os.path.join(X, "ref_checklist.db")
OUT = os.path.join(X, "ref_checklist_outcome.txt")
OUT_PILOT = os.path.join(X, "ref_checklist_outcome_PILOT.txt")
PROTOCOL = ("STACK-v2 pairwise: v2 verify-first mechanics + anchor rubric + confidence; dual order, TIE on flip; question block per arm: "
            "REF = grok-reasoning reference block; CHECKLIST = verification checklist under the same wrapper; BOTH = reference then checklist")
TEMPERATURE_DECISION = "omitted from the payload (provider default), as the cached session: docs/plan_2026-09-15.md Amendment 1, D2"

# The wrapper, derived from the module of record: with_reference(query, (letter, text, _)) appends
# "\n\n[Reference solution — produced independently, may be wrong]\n(letter) text".
_probe = rref.with_reference("", ("\x01", "\x02", False))
REF_HEADER = _probe.split("\n\n", 1)[1].split("\n(\x01) \x02")[0]
assert REF_HEADER.startswith("[Reference solution") and REF_HEADER.endswith("may be wrong]"), REF_HEADER
CHECKLIST_HEADER = REF_HEADER.replace("solution", "verification checklist", 1)
REQUIRED_LINE = "Required (a correct answer must contain or rely on):"
PITFALLS_LINE = "Pitfalls (a wrong answer typically shows):"


def script_sha():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


def checklist_block(parsed):
    one = lambda s: " ".join(s.split())
    return "\n".join([CHECKLIST_HEADER, REQUIRED_LINE] + ["- " + one(x) for x in parsed["required"]] + [PITFALLS_LINE] + ["- " + one(x) for x in parsed["pitfalls"]])


def question_block(arm, stem, ref, parsed):
    if arm == "REF": return rref.with_reference(stem, ref)
    if arm == "CHECKLIST": return stem + "\n\n" + checklist_block(parsed)
    if arm == "BOTH": return rref.with_reference(stem, ref) + "\n\n" + checklist_block(parsed)
    raise ValueError(arm)


def temperature_label():
    return "omitted (provider default, as the cached session)" if rr.TEMPERATURE is None else "%g (explicit literal; deviation from D2, recorded)" % rr.TEMPERATURE


# ── targets: the 944 key-decidable R3 matches exactly as pair_noref derives them; seeded order so a pilot spans the strata ──
def targets():
    sched, K = pn.targets()                       # [(mid, qid, a, b, anchor)] sorted by mid
    assert len(sched) == N_TARGETS, "expected the %d key-decidable R3 pairs, found %d" % (N_TARGETS, len(sched))
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    bad = [t for t in sched if t[1] not in pool]
    assert not bad, "%d matches outside the pool of record %s" % (len(bad), POOL)
    assert not any(EXCLUDED in (t[2], t[3]) for t in sched), "%s must be excluded" % EXCLUDED
    cached = {mid: (w, rl) for mid, w, rl in sqlite3.connect("file:%s?mode=ro" % PW_REF, uri=True).execute("SELECT match_id, winner, ref_letter FROM verdicts")}
    order = list(sched); random.Random(SEED).shuffle(order)
    return order, K, cached


def jobs_for(sched, use, pilot):
    """Match-major, arm order rotated by match index; matches without a usable checklist are excluded from ALL arms.
    --pilot N takes the first N ELIGIBLE matches of the seeded order (so --pilot 12 is exactly the pilot block)."""
    jobs = []; excluded = []; n_el = 0
    for i, t in enumerate(sched):
        if t[1] not in use: excluded.append(t); continue
        if pilot and n_el >= pilot: break
        n_el += 1
        rot = i % len(ARMS)
        for arm in ARMS[rot:] + ARMS[:rot]: jobs.append((t, arm))
    return jobs, excluded


def build(job, rubrics, refs, evals, use, cached):
    (mid, qid, a, b, anc), arm = job
    ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
    if ra is None or rb is None: return None, "no eval row"
    if ref is None: return None, "no reference"
    rl = (cached.get(mid) or ("", ""))[1]
    if rl and ref[0] != rl: return None, "reference vintage differs from the cached session (%s vs %s)" % (ref[0], rl)
    if anc not in rubrics: return None, "no anchor rubric"
    parsed = use.get(qid)
    if parsed is None: return None, "no usable checklist"
    system = sj.system_for(anc, rubrics)
    q = question_block(arm, ra[0], ref, parsed)
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    u1, u2 = rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)
    if arm == "REF": assert_ref_identity(job[0], rubrics, refs, evals, system, u1, u2)
    return (system, u1, u2, ref), None


def stack_judge_replica(t, rubrics, refs, evals):
    """Line-for-line replica of stack_judge.run's one() for --judge grok --prompt v2 (RECIPE-GROK), returning the two request bodies."""
    mid, qid, a, b, anc = t
    ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
    q = rref.with_reference(ra[0], ref)
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    system = sj.system_for(anc, rubrics)
    return rr.payload_bytes(system, rj.build_user_prompt(q, ta, tb)), rr.payload_bytes(system, rj.build_user_prompt(q, tb, ta))


def assert_ref_identity(t, rubrics, refs, evals, system, u1, u2):
    """The REF arm posts the bytes RECIPE-GROK posted: same body builder, same assembly lines, same model and cap."""
    src = inspect.getsource(sj.run)
    for line in ('rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"', 'q = rref.with_reference(ra[0], ref)',
                 'system = system_for(anc, rubrics)', 'rj.build_user_prompt(q, ta, tb)', 'rj.build_user_prompt(q, tb, ta)'):
        assert line in src, "stack_judge.run no longer assembles RECIPE-GROK the way the replica does: %r" % line
    assert "rr.call_judge(system, user)" in inspect.getsource(sj.judge_call), "stack_judge.judge_call no longer posts through rejudge_reasoning"
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    assert sj.PROMPT == "v2" and rr.JUDGE_MODEL == JUDGE and rr.MAX_TOKENS == MAXTOK and rr.TEMPERATURE is None
    r1, r2 = stack_judge_replica(t, rubrics, refs, evals)
    assert rr.payload_bytes(system, u1) == r1 and rr.payload_bytes(system, u2) == r2, "REF arm payload is not byte-identical to stack_judge's assembly (match %d)" % t[0]


def prepare(pilot, placeholder=False):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK
    sj.PROMPT = "v2"; sj.JUDGE = "grok"
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics()
    sched, K, cached = targets()
    qids = sorted({t[1] for t in sched})
    use, counts = cg.usable(qids)
    if placeholder and not use:
        use = {q: {"required": ["DRY-RUN PLACEHOLDER: the checklist cache does not exist yet"], "pitfalls": ["DRY-RUN PLACEHOLDER"]} for q in qids}
    jobs, excluded = jobs_for(sched, use, pilot)
    evals = rj.load_eval_rows([j[0][1] for j in jobs], {j[0][2] for j in jobs} | {j[0][3] for j in jobs})
    return sched, jobs, excluded, rubrics, refs, evals, K, cached, use, counts, qids


def meta_of(qids):
    return {"pool": POOL, "judge": JUDGE, "provider": "azure", "protocol": PROTOCOL, "max_tokens": str(MAXTOK), "temperature": temperature_label(),
            "temperature_decision": TEMPERATURE_DECISION, "arms": ",".join(ARMS), "reference": "grok-reasoning", "control_of_record": os.path.basename(PW_REF),
            "checklist_cache": rel(cg.CACHE), "checklist_sha256": cg.checklist_sha(qids), "checklist_header": CHECKLIST_HEADER}


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                "finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, provider1 TEXT, provider2 TEXT, rid1 TEXT, rid2 TEXT, max_tokens INTEGER, "
                "sys_sha TEXT, prompt_sha1 TEXT, prompt_sha2 TEXT, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
    con.commit(); return con


def pin_meta(con, qids):
    want = meta_of(qids); have = dict(con.execute("SELECT k, v FROM meta"))
    if have:
        diff = {k: (have.get(k), v) for k, v in want.items() if k in have and have[k] != v}
        if diff:
            raise SystemExit("[CACHE] %s was judged under different parameters; refusing to resume into it: %s\n"
                             "        A new cap, temperature, arm set or checklist set is a NEW SESSION and gets a new cache: move %s aside and relaunch."
                             % (os.path.basename(CACHE), "; ".join("%s cached=%r now=%r" % (k, a, b) for k, (a, b) in diff.items()), CACHE))
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    for k, v in want.items(): con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (k, v))
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("script_sha256", script_sha()))
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("started", ts))
    if have:
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("script_sha256_relaunch_" + ts, script_sha()))
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("resumed", (have.get("resumed", "") + "; " if have.get("resumed") else "") + ts))
    con.commit()


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# ── dry run ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def dry_run(pilot):
    sched, jobs, excluded, rubrics, refs, evals, K, cached, use, counts, qids = prepare(pilot, placeholder=True)
    placeholder = not os.path.exists(cg.CACHE)
    built = []; skipped = defaultdict(int); sys_sha = set(); n_ref_checked = 0
    for j in jobs:
        pr, why = build(j, rubrics, refs, evals, use, cached)
        if pr is None: skipped[why] += 1; continue
        if j[1] == "REF": n_ref_checked += 1
        built.append((j, pr)); sys_sha.add(sha16(pr[0]))
    by_arm = defaultdict(int)
    for j, _ in built: by_arm[j[1]] += 1
    cols = [r[1] for r in sqlite3.connect("file:%s?mode=ro" % PW_REF, uri=True).execute("PRAGMA table_info(verdicts)")]
    stores_prompts = any(c in cols for c in ("system", "user1", "prompt", "system_prompt"))
    print("REF-CHECKLIST DRY RUN: nothing posted")
    print("  matches      %d of %d key-decidable R3 matches (%s) | eligible %d | EXCLUDED (no usable checklist) %d of the %d in the set"
          % (len({j[0][0] for j in jobs}), N_TARGETS, "pilot %d (the first %d eligible)" % (pilot, pilot) if pilot else "full", len({j[0][0] for j in jobs}),
             len(excluded), len(sched)))
    print("  jobs         %d = %s (match-major, arm order rotated by match index)" % (len(built), " + ".join("%s %d" % (a, by_arm[a]) for a in ARMS)))
    print("  CALL COUNT   %d (2 orders per job)" % (2 * len(built)))
    if skipped: print("  skipped      %s" % dict(skipped))
    print("  POOL         %s (every question asserted inside it; %s asserted absent)" % (POOL, EXCLUDED))
    print("  JUDGE        %s (provider azure) | CAP max_tokens %d | TEMPERATURE %s   [%s]" % (JUDGE, MAXTOK, temperature_label(), TEMPERATURE_DECISION))
    print("  PROTOCOL     %s" % PROTOCOL)
    print("  REF ARM      byte identity vs stack_judge's assembly asserted on %d REF jobs (request bodies via rejudge_reasoning.payload_bytes); "
          "%s stores %s, so the assertion is against the assembly, not stored prompts" % (n_ref_checked, os.path.basename(PW_REF), "prompts" if stores_prompts else "NO prompts (raw verdicts only)"))
    print("  WRAPPER      REF        %s" % REF_HEADER)
    print("               CHECKLIST  %s  +  \"%s\" / \"%s\" bullet lists" % (CHECKLIST_HEADER, REQUIRED_LINE, PITFALLS_LINE))
    print("               BOTH       reference block, blank line, checklist block")
    print("  SYSTEM       %d distinct system prompts (one per anchor), identical across the three arms" % len(sys_sha))
    print("  CHECKLISTS   %s: questions %d | parsed %d | unparsed %d (%.1f%%) | %s | usable %d | guard %s%s"
          % (rel(cg.CACHE), counts["questions"], counts["parsed"], counts["unparsed"], 100 * counts["unparsed_rate"], cg.dropped_label(counts),
             counts["usable"], "OK" if counts["guard_ok"] else "FAIL",
             "   <- CACHE MISSING: placeholders render the CHECKLIST/BOTH payloads; a --run refuses" if placeholder else ""))
    print("  CACHE        %s%s" % (CACHE, "   <- EXISTS" if os.path.exists(CACHE) else "   (new)"))
    print("  OUTCOME      %s (file of record, complete runs only) | %s (pilot / incomplete)" % (OUT, OUT_PILOT))
    print("  SCORING      unparsed / non-terminated verdicts stay in the paired set as %s: wrong under A, not committed under B, never a tie" % NT)
    print("  PILOT BLOCK  the first %d matches of a --run (all three arms) are judged first and read by the truncation guard before the rest" % PILOT_BLOCK)
    print("  META PIN     judge, cap, temperature, protocol, arm set, checklist sha (content + audit decisions), script sha; a mismatch refuses to resume")
    print("  SCRIPT SHA   %s | checklist_gen sha %s" % (script_sha(), cg.script_sha()))
    if not built: print("  nothing assembled"); return 0
    (j0, (s0, u0, u0b, ref0)) = built[0]
    b0 = rr.payload_body(s0, u0); assert tuple(b0) == ("model", "max_tokens", "messages")
    print("\n=== FIRST PAYLOAD: match %d, arm %s, order 1 (request body keys %s; model %s, max_tokens %d) ===" % (j0[0][0], j0[1], tuple(b0), b0["model"], b0["max_tokens"]))
    print("--- system ---"); print(s0); print("--- user ---"); print(u0); print("--- end of first payload ---")
    for (j, (s, u, ub, ref)) in built[1:3]:
        if j[0][0] == j0[0][0]:
            qb = question_block(j[1], evals[(j[0][1], j[0][2])][0], ref, use[j[0][1]])
            print("\n=== SAME MATCH, arm %s: question block only (system and traces identical) ===" % j[1]); print(qb)
    return 0


# ── run ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _judge_block(todo, rubrics, refs, evals, use, cached, con, workers, tag):
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        pr, why = build(job, rubrics, refs, evals, use, cached)
        if pr is None: return None
        system, u1, u2, ref = pr
        (mid, qid, a, b, anc), arm = job
        c1, p1, k1, _, f1, m1 = rr.call_judge_full(system, u1); c2, p2, k2, _, f2, m2 = rr.call_judge_full(system, u2)
        raw1, raw2 = rr.strip_think(c1 or ""), rr.strip_think(c2 or "")
        v1, cf1 = rj.parse_judge(raw1); v2, cf2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        rid = lambda m: (m or {}).get("_response_id") if isinstance(m, dict) else None
        return (mid, arm, a, b, qid, anc, ref[0], int(ref[2]), v1, v2, cf1, cf2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv),
                f1, f2, k1, k2, p1, p2, rid(m1), rid(m2), rr.MAX_TOKENS, sha16(system), sha16(system + "\x00" + u1), sha16(system + "\x00" + u2), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 30), row); con.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo): print("  [%s] %d/%d (ok %d, skip %d, err %d)" % (tag, i, len(todo), ok, skip, err), flush=True)
    print("[%s] done: ok %d, skipped %d, errors %d" % (tag, ok, skip, err), flush=True)


def run(pilot, workers):
    rr.load_env()
    sched, jobs, excluded, rubrics, refs, evals, K, cached, use, counts, qids = prepare(pilot)
    if not counts["guard_ok"] or not use:
        print("[CHECKLIST GUARD] %s: unparsed %d of %d (%.1f%%) > 5%% or no usable checklist: a verdict-bearing run is REFUSED. Run checklist_gen.py first."
              % (rel(cg.CACHE), counts["unparsed"], counts["questions"], 100 * counts["unparsed_rate"]), flush=True)
        return False
    con = open_cache(); pin_meta(con, qids)
    done = {(m, a) for m, a in con.execute("SELECT match_id, arm FROM verdicts")}
    todo = [j for j in jobs if (j[0][0], j[1]) not in done]
    print("REF-CHECKLIST RUN: pool %s | judge %s | arms %s | eligible matches %d (excluded %d) | jobs %d | cached %d | to do %d (%d calls) | max_tokens %d | temperature %s | workers %d | script %s"
          % (POOL, JUDGE, "/".join(ARMS), len({j[0][0] for j in jobs}), len(excluded), len(jobs), len(jobs) - len(todo), len(todo), 2 * len(todo), MAXTOK, temperature_label(), workers, script_sha()[:16]), flush=True)
    pilot_ids = [t[0] for t in sched if t[1] in use][:PILOT_BLOCK]
    first = [j for j in todo if j[0][0] in set(pilot_ids)]; rest = [j for j in todo if j[0][0] not in set(pilot_ids)]
    if first:
        print("  PILOT BLOCK: %d jobs (%d calls) on the first %d eligible matches, all three arms, then the truncation guard" % (len(first), 2 * len(first), PILOT_BLOCK), flush=True)
        _judge_block(first, rubrics, refs, evals, use, cached, con, workers, "pilot")
    have = {(m, a) for m, a in con.execute("SELECT match_id, arm FROM verdicts")}
    missing = [(m, a) for m in pilot_ids for a in ARMS if (m, a) not in have]
    if missing:
        print("  PILOT GUARD: the pilot block is INCOMPLETE (%d of %d (match, arm) rows missing: errors are not cached) -> not posting the remaining %d jobs.\n"
              "  Relaunch the same command: the missing pilot rows are re-posted and the guard re-read. Missing: %s%s"
              % (len(missing), len(pilot_ids) * len(ARMS), len(rest), ", ".join("%d/%s" % x for x in missing[:6]), " ..." if len(missing) > 6 else ""), flush=True)
        return False
    bad = truncation_readout(con, only_ids=set(pilot_ids))
    if bad:
        print("  PILOT GUARD FAILED on %s: not posting the remaining %d jobs.\n"
              "  Read the pilot rows above: finish_reason=length means the cap is too small; finish_reason=stop with an unparsed answer is a parse\n"
              "  failure; finish_reason=content_filter is a deterministic refusal. EITHER WAY this cache keeps the failed pilot rows (cached rows are\n"
              "  never re-posted) and a relaunch re-reads them and fails again: move %s aside (rename it; a new cap is a new session and\n"
              "  gets a new cache) and relaunch." % (", ".join(bad), len(rest), CACHE), flush=True)
        return False
    if rest: _judge_block(rest, rubrics, refs, evals, use, cached, con, workers, "main")
    truncation_readout(con)
    return True


def unparsed(r):
    return bool(r["invalid"]) or r["finish1"] == "length" or r["finish2"] == "length"


def load_rows(con):
    cols = ["match_id", "arm", "model_a", "model_b", "qid", "winner", "flip", "invalid", "finish1", "finish2", "ctok1", "ctok2", "ref_letter", "ref_correct"]
    return [dict(zip(cols, r)) for r in con.execute("SELECT %s FROM verdicts" % ",".join(cols))]


def truncation_readout(con, only_ids=None):
    rows = load_rows(con); bad = []
    if only_ids is not None: rows = [r for r in rows if r["match_id"] in only_ids]
    for arm in ARMS:
        s = [r for r in rows if r["arm"] == arm]
        if not s: continue
        u = sum(1 for r in s if unparsed(r)); fr = defaultdict(int)
        for r in s: fr[r["finish1"] or "(none)"] += 1; fr[r["finish2"] or "(none)"] += 1
        ct = [c for r in s for c in (r["ctok1"], r["ctok2"]) if c is not None]
        over = u > 0.05 * len(s)
        if over: bad.append(arm)
        print("  TRUNCATION GUARD %-9s n=%4d | unparsed or non-terminated %d (%.1f%%) | finish_reason %s | completion tokens max %s | %s"
              % (arm, len(s), u, 100 * u / len(s), dict(fr), max(ct) if ct else "?", "OK" if not over else "ABOVE 5%: the verdict will be REFUSED"))
        if only_ids is not None:
            for r in sorted(s, key=lambda r: r["match_id"]):
                if unparsed(r): print("      pilot row %-9s match %6d | winner %-28s | invalid %d | finish %s/%s | completion tokens %s/%s"
                                      % (arm, r["match_id"], r["winner"], r["invalid"], r["finish1"], r["finish2"], r["ctok1"], r["ctok2"]))
    return bad


# ── analysis ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def acc(win, keys, dw):
    """(A: correct / n with TIE and NT wrong; B: correct / committed; tie rate; n committed; n NT)"""
    n = len(keys); c = sum(1 for k in keys if win[k] == dw[k]); t = sum(1 for k in keys if win[k] == "TIE"); u = sum(1 for k in keys if win[k] == NT)
    return c / max(1, n), c / max(1, n - t - u), t / max(1, n), n - t - u, u


def cluster_boot(x, y, keys, dw, qid_of, B=NBOOT, seed=SEED):
    """Question-clustered bootstrap of delta A and delta B (x minus y). Per-question sums are resampled with replacement."""
    by = defaultdict(list)
    for k in keys: by[qid_of[k]].append(k)
    qs = sorted(by); M = np.zeros((len(qs), 5))     # n, xc, yc, xcommitted, ycommitted
    for i, q in enumerate(qs):
        ks = by[q]
        M[i] = [len(ks), sum(x[k] == dw[k] for k in ks), sum(y[k] == dw[k] for k in ks),
                sum(x[k] not in ("TIE", NT) for k in ks), sum(y[k] not in ("TIE", NT) for k in ks)]
    rng = np.random.default_rng(seed); dA = np.empty(B); dB = np.empty(B)
    for b in range(B):
        S = M[rng.integers(0, len(qs), len(qs))].sum(axis=0)
        dA[b] = (S[1] - S[2]) / max(1, S[0]); dB[b] = S[1] / max(1, S[3]) - S[2] / max(1, S[4])
    return (float(np.percentile(dA, 2.5)), float(np.percentile(dA, 97.5))), (float(np.percentile(dB, 2.5)), float(np.percentile(dB, 97.5)))


def compare(L, label, x, y, keys, dw, qid_of, xname, yname):
    """Paired x vs y on keys; returns (deltaA, pA, deltaB, ciA, ciB)."""
    if not keys:
        L.append("  %s: no paired matches" % label); return None
    aX, bX, tX, cX, uX = acc(x, keys, dw); aY, bY, tY, cY, uY = acc(y, keys, dw)
    b_ = sum(1 for k in keys if x[k] == dw[k] and y[k] != dw[k]); c_ = sum(1 for k in keys if y[k] == dw[k] and x[k] != dw[k])
    p = p8.mcn(b_, c_); ciA, ciB = cluster_boot(x, y, keys, dw, qid_of)
    L.append("  %s (paired n=%d, %d questions)" % (label, len(keys), len({qid_of[k] for k in keys})))
    L.append("      conv A  %-9s %.3f (NT %d) | %-11s %.3f (NT %d) | delta %+.3f  95%% CI [%+.3f, %+.3f] (question-clustered, B=%d) | %d:%d McNemar p=%.4g"
             % (xname, aX, uX, yname, aY, uY, aX - aY, ciA[0], ciA[1], NBOOT, b_, c_, p))
    L.append("      conv B  %-9s %.3f (committed %d) | %-11s %.3f (committed %d) | delta %+.3f  95%% CI [%+.3f, %+.3f]"
             % (xname, bX, cX, yname, bY, cY, bX - bY, ciB[0], ciB[1]))
    L.append("      ties    %s %.3f | %s %.3f" % (xname, tX, yname, tY))
    return aX - aY, p, bX - bY, ciA, ciB


def agreement(V, keys, models, mids):
    """Per contestant: share of the arm's committed verdicts that side with it, over the matches it plays."""
    out = {}
    for m in models:
        ks = [k for k in keys if m in (mids[k][0], mids[k][1]) and V[k] not in ("TIE", NT)]
        out[m] = (sum(1 for k in ks if V[k] == m) / len(ks) if ks else float("nan"), len(ks))
    return out


def analyze():
    if not os.path.exists(CACHE):
        print("[CACHE] %s does not exist: nothing judged, nothing written" % CACHE); return
    con = sqlite3.connect("file:%s?mode=ro" % CACHE, uri=True)
    rows = load_rows(con); meta = dict(con.execute("SELECT k, v FROM meta"))
    sched, K, cached = targets(); qids = sorted({t[1] for t in sched})
    use, counts = cg.usable(qids)
    eligible = [t for t in sched if t[1] in use]; excluded = [t for t in sched if t[1] not in use]
    dw = {t[0]: (t[2] if K[t[1]][t[2]] else t[3]) for t in sched}; qid_of = {t[0]: t[1] for t in sched}; mids = {t[0]: (t[2], t[3]) for t in sched}
    rref.set_reference("grok-reasoning"); refs = rref.references()
    qrows = cg.question_rows(qids)
    refc = {q: (refs[q][0] == qrows[q][2]) for q in qids if q in refs and q in qrows}     # the cached letter against the key
    for q in refc: assert refc[q] == bool(refs[q][2]), "reference correctness disagrees with the solve cache for q %d" % q
    P = defaultdict(dict)
    for q, m, pr in sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True).execute("SELECT question_id, model_name, pred FROM eval_results"):
        if m in p8.ARENA12: P[q][m] = (pr or "").strip().upper()[:1]
    arms = defaultdict(dict)
    for r in rows: arms[r["arm"]][r["match_id"]] = r
    verdicts = lambda d: {m: (r["winner"] if not unparsed(r) else NT) for m, r in d.items()}
    V = {a: verdicts(arms.get(a, {})) for a in ARMS}
    recipe = {t[0]: cached[t[0]][0] for t in sched if t[0] in cached}
    noref = {}
    if os.path.exists(PW_NOREF):
        for mid, w, inv in sqlite3.connect("file:%s?mode=ro" % PW_NOREF, uri=True).execute("SELECT match_id, winner, invalid FROM verdicts"):
            if mid in dw: noref[mid] = NT if inv else w
    pinned = meta.get("script_sha256"); stale = pinned not in (None, script_sha())
    cl_sha = cg.checklist_sha(qids); cl_stale = meta.get("checklist_sha256") not in (None, cl_sha)
    common = sorted(set(V["REF"]) & set(V["CHECKLIST"]) & set(V["BOTH"]))
    complete = len(common) == len(eligible) and len(eligible) > 0
    partial = not complete
    out = OUT_PILOT if partial else OUT
    L = ["=== REF-CHECKLIST: a verification checklist as a reference in rubric form, three fresh arms on the %d key-decidable R3 matches (pool %s) ===" % (N_TARGETS, POOL)]
    if partial:
        L.append("  %s: %d of %d eligible matches carry all three arms. NOT the outcome of record; written to %s; no registered verdict line."
                 % ("PILOT n=%d" % len(common) if len(common) <= PILOT_BLOCK else "INCOMPLETE n=%d" % len(common), len(common), len(eligible), os.path.basename(out)))
    L += ["  judge %s | %s" % (meta.get("judge", JUDGE), meta.get("protocol", PROTOCOL)),
          "  max_tokens %s | temperature %s | temperature decision: %s" % (meta.get("max_tokens", "?"), meta.get("temperature", "?"), meta.get("temperature_decision", TEMPERATURE_DECISION)),
          "  wrapper: REF %s | CHECKLIST %s" % (REF_HEADER, meta.get("checklist_header", CHECKLIST_HEADER)),
          "  provenance: finish_reason, completion tokens, provider, response id, max_tokens, system and prompt shas stored per order",
          "  scoring: unparsed / non-terminated verdicts kept in the paired set as %s (wrong under A, not committed under B, never a tie)" % NT,
          "  producing script sha256 (pinned at first launch) %s | current %s%s | checklist sha %s%s | started %s%s"
          % ((pinned or "?")[:16], script_sha()[:16], "   <- STALE" if stale else "", cl_sha[:16], "   <- CHECKLIST SET CHANGED since the pin" if cl_stale else "",
             meta.get("started", "?"), " | resumed " + meta["resumed"] if meta.get("resumed") else "")]
    # audit counts
    L.append("")
    L.append("  CHECKLIST AUDIT: questions %d | parsed %d | unparsed %d (%.1f%%) | %s | usable %d"
             % (counts["questions"], counts["parsed"], counts["unparsed"], 100 * counts["unparsed_rate"], cg.dropped_label(counts), counts["usable"]))
    L.append("  matches EXCLUDED from all three arms: %d of %d (eligible %d)" % (len(excluded), N_TARGETS, len(eligible)))
    # guards
    refused = []
    if not counts["guard_ok"]: refused.append(("checklist set", counts["unparsed"], counts["questions"]))
    for arm in ARMS:
        d = arms.get(arm, {}); u = sum(1 for r in d.values() if unparsed(r))
        L.append("  guard %-9s n=%4d | unparsed or non-terminated %d (%.1f%%)" % (arm, len(d), u, 100 * u / max(1, len(d))))
        if len(d) and u > 0.05 * len(d): refused.append((arm, u, len(d)))
    if refused or not common:
        L.append("  VERDICT REFUSED: %s" % ("; ".join("%s %d of %d unparsed" % x for x in refused) if refused else "no match carries all three arms"))
        txt = "\n".join(L); print(txt); open(out, "w", encoding="utf-8").write(txt + "\n"); return
    # per-arm summary
    L.append("")
    L.append("  PER ARM on the %d common matches (conventions A / B, ties, flips):" % len(common))
    for arm in ARMS:
        a_, b_, t_, c_, u_ = acc(V[arm], common, dw)
        parsed_ = [arms[arm][k] for k in common if not unparsed(arms[arm][k])]
        fl = sum(1 for r in parsed_ if r["flip"]) / max(1, len(parsed_))
        L.append("      %-9s conv A %.3f | conv B %.3f (committed %d) | ties %.3f | flips %.3f of %d parsed | NT %d" % (arm, a_, b_, c_, t_, fl, len(parsed_), u_))
    ck = [k for k in common if k in recipe]; nk = [k for k in common if k in noref]
    for nm, d in (("RECIPE-GROK", recipe), ("PAIR-NOREF", noref)):
        ks = ck if nm == "RECIPE-GROK" else nk
        if ks:
            a_, b_, t_, c_, u_ = acc(d, ks, dw)
            L.append("      %-11s conv A %.3f | conv B %.3f (committed %d) | ties %.3f | NT %d   (cache, n=%d)" % (nm, a_, b_, c_, t_, u_, len(ks)))
    # (1) primary and the session floor
    L.append("")
    L.append("  (1) PRIMARY: BOTH vs REF on key-decidable, p < 0.05 either direction, with the session floor beside it")
    r1 = compare(L, "BOTH vs REF", V["BOTH"], V["REF"], common, dw, qid_of, "BOTH", "REF")
    rf = compare(L, "SESSION FLOOR: REF-fresh vs RECIPE-GROK (byte-identical prompts, other session)", V["REF"], recipe, ck, dw, qid_of, "REF-fresh", "RECIPE-GROK")
    dis = sum(1 for k in ck if V["REF"][k] != recipe[k]) / max(1, len(ck))
    L.append("      verdict disagreement REF-fresh / RECIPE-GROK %.3f | DECOMP floor 0.057" % dis)
    # (2) checklist vs ref, the falsifier
    L.append("")
    L.append("  (2) CHECKLIST vs REF: the falsifier line (prediction: CHECKLIST below REF by 3-6pp)")
    r2 = compare(L, "CHECKLIST vs REF", V["CHECKLIST"], V["REF"], common, dw, qid_of, "CHECKLIST", "REF")
    # secondary: each fresh arm vs the caches
    L.append("")
    L.append("  SECONDARY: each fresh arm against the cached comparators")
    for arm in ARMS:
        if arm != "REF": compare(L, "%s vs RECIPE-GROK" % arm, V[arm], recipe, ck, dw, qid_of, arm, "RECIPE-GROK")
    for arm in ARMS:
        if nk: compare(L, "%s vs PAIR-NOREF" % arm, V[arm], noref, nk, dw, qid_of, arm, "PAIR-NOREF")
    # (3) strata
    L.append("")
    L.append("  (3) STRATA by the answer reference's correctness (cached grok-reasoning letter vs the key)")
    r3 = {}
    for lab, want in (("reference CORRECT", True), ("reference WRONG", False)):
        ks = [k for k in common if refc.get(qid_of[k]) is want]
        L.append("    %s (n=%d):" % (lab, len(ks)))
        r3[(lab, "CHECKLIST")] = compare(L, "CHECKLIST vs REF", V["CHECKLIST"], V["REF"], ks, dw, qid_of, "CHECKLIST", "REF")
        r3[(lab, "BOTH")] = compare(L, "BOTH vs REF", V["BOTH"], V["REF"], ks, dw, qid_of, "BOTH", "REF")
    # (4) answer agreement, gemini first
    L.append("")
    L.append("  (4) ANSWER-AGREEMENT of each arm's committed verdicts with every contestant: ref_qualify (3)'s per-contestant share with the verdict in place of the reference letter")
    ag = {arm: agreement(V[arm], common, sorted(p8.ARENA12), mids) for arm in ARMS}
    agr = agreement(recipe, ck, sorted(p8.ARENA12), mids)
    g_ck = ag["CHECKLIST"][GEMINI][0] - ag["REF"][GEMINI][0]; g_bo = ag["BOTH"][GEMINI][0] - ag["REF"][GEMINI][0]
    L.append("      GEMINI delta  CHECKLIST - REF %+.3f | BOTH - REF %+.3f   (REF %.3f on n=%d; prediction: CHECKLIST lower by >= 2pp)"
             % (g_ck, g_bo, ag["REF"][GEMINI][0], ag["REF"][GEMINI][1]))
    L.append("      %-30s %9s %9s %9s %9s | %9s %9s" % ("contestant", "REF", "CHECKLIST", "BOTH", "RECIPE", "CK-REF", "BOTH-REF"))
    f3 = lambda v, sign=False: ("%+9.3f" if sign else "%9.3f") % v if v == v else "%9s" % "-"
    for m in sorted(p8.ARENA12, key=lambda m: -ag["REF"][m][0] if ag["REF"][m][0] == ag["REF"][m][0] else 0):
        L.append("      %-30s %s %s %s %s | %s %s%s" % (m[:30], f3(ag["REF"][m][0]), f3(ag["CHECKLIST"][m][0]), f3(ag["BOTH"][m][0]), f3(agr[m][0]),
                 f3(ag["CHECKLIST"][m][0] - ag["REF"][m][0], True), f3(ag["BOTH"][m][0] - ag["REF"][m][0], True), "   <- frontier" if m in sj.TOP4 else ""))
    # reference-mirroring: verdicts siding with the model whose answer equals the reference letter
    def mirror(Vd, keys):
        ks = []
        for k in keys:
            a, b = mids[k]; q = qid_of[k]; rl = refs[q][0]
            sa, sb = P[q].get(a) == rl, P[q].get(b) == rl
            if sa != sb and Vd[k] not in ("TIE", NT): ks.append((k, a if sa else b))
        return (sum(1 for k, s in ks if Vd[k] == s) / len(ks) if ks else float("nan")), len(ks)
    L.append("      reference-mirroring rate (committed verdicts siding with the model whose answer equals the reference letter, where exactly one side does):")
    L.append("      " + " | ".join("%s %.3f (n=%d)" % ((arm,) + mirror(V[arm], common)) for arm in ARMS) + " | RECIPE-GROK %.3f (n=%d)" % mirror(recipe, ck))
    # the CONSENSUS-FIT coefficient proper: format_ref.fit on rows built as format_ref.rows_pairwise builds them (REUSED, not replicated)
    def contrast_rows(Vd, keys):
        out = []
        for k in keys:
            a, b = mids[k]; q = qid_of[k]; rl = refs[q][0]; pa, pb = P[q].get(a), P[q].get(b)
            if Vd[k] == NT or pa is None or pb is None: continue                      # rows_pairwise skips invalid rows
            out.append((cf.sign_contrast(K[q].get(a, 0) == 1, K[q].get(b, 0) == 1), cf.sign_contrast(rl == pa, rl == pb),
                        "A" if Vd[k] == a else ("B" if Vd[k] == b else "TIE")))
        return out
    L.append("      CONSENSUS-FIT coefficients (format_ref.fit = consensus_fit.logistic of the verdict on the signed contrasts KEY and REF; ties half-weighted; NT skipped):")
    coef = {}
    for nm, Vd, ks in [(arm, V[arm], common) for arm in ARMS] + [("RECIPE-GROK", recipe, ck)]:
        rws = contrast_rows(Vd, ks)
        try:
            bta, se = fr.fit(rws); coef[nm] = (bta[1], se[1], bta[2], se[2], len(rws))
            L.append("      %-11s n=%4d | KEY %+.3f +- %.3f | REF %+.3f +- %.3f | REF-KEY %+.3f" % (nm, len(rws), bta[1], se[1], bta[2], se[2], bta[2] - bta[1]))
        except Exception as e:
            L.append("      %-11s fit failed on n=%d rows (%s)" % (nm, len(rws), str(e)[:60]))
    if all(a in coef for a in ARMS):
        L.append("      REF coefficient delta  CHECKLIST - REF %+.3f | BOTH - REF %+.3f   (the leakage predictor; expected negative under CHECKLIST)"
                 % (coef["CHECKLIST"][2] - coef["REF"][2], coef["BOTH"][2] - coef["REF"][2]))
    # criteria
    L.append("")
    L.append("  criteria readout (PILOT / INCOMPLETE: informational only, not the outcome of record, nothing scored):" if partial else "  REGISTERED CRITERIA:")
    dA1, p1, _, ci1, _ = r1; floorA = abs(rf[0]) if rf else None
    L.append("      (1) BOTH vs REF: delta A %+.3f, McNemar p=%.4g -> %s%s" % (dA1, p1, "PASS (p < 0.05, %s)" % ("upward" if dA1 > 0 else "downward") if p1 < 0.05 else "not significant",
             "; session floor |REF-fresh - RECIPE-GROK| = %.3f%s" % (floorA, " (delta inside the floor)" if abs(dA1) <= floorA else "") if floorA is not None else "; floor not measured"))
    dA2 = r2[0]
    L.append("      (2) CHECKLIST vs REF: delta A %+.3f (p=%.4g) -> %s" % (dA2, r2[1],
             "FALSIFIER FIRES: CHECKLIST alone at or above REF; the value of a reference is verification structure, not the answer, and the leakage is avoidable"
             if dA2 >= 0 else ("as predicted (3-6pp below)" if -0.06 <= dA2 <= -0.03 else "below REF, outside the predicted 3-6pp band")))
    for arm in ("CHECKLIST", "BOTH"):
        r = r3.get(("reference WRONG", arm))
        if r: L.append("      (3) reference-WRONG stratum, %s vs REF: delta A %+.3f, p=%.4g, CI [%+.3f, %+.3f] -> %s" % (arm, r[0], r[1], r[3][0], r[3][1], "as predicted (>= +5pp)" if r[0] >= 0.05 else "NOT as predicted"))
    L.append("      (4) leakage, gemini-agreement delta CHECKLIST - REF %+.3f -> %s" % (g_ck, "NEGATIVE as expected" + (" (>= 2pp, as predicted)" if g_ck <= -0.02 else " (under the predicted 2pp)") if g_ck < 0 else "NOT negative"))
    L.append("      falsifier line: CHECKLIST alone at or above REF on key-decidable (conv A) -> %s" % ("FIRED" if dA2 >= 0 else "not fired"))
    if not partial:
        ok1 = p1 < 0.05
        L.append("      REGISTERED (1) PRIMARY: %s | consequence: %s" % ("PASS" if ok1 else "FAIL",
                 "BOTH enters the recipe as a registered arm at +1 reasoning call per question" if (ok1 and dA1 > 0) else
                 ("a reference-quality-gated switch is the next registration, not adopted here" if any(r3.get(("reference WRONG", a)) and r3[("reference WRONG", a)][0] >= 0.05 for a in ("CHECKLIST", "BOTH")) else "no recipe change")))
    if stale: L.append("      STALE: producing code hash differs from the cache's pinned first-launch sha; re-run --analyze from the recorded version or re-register")
    if cl_stale: L.append("      CHECKLIST SET CHANGED since the pin: the judged checklists are not the ones the audit now certifies; re-audit or re-register")
    txt = "\n".join(L); print(txt); open(out, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    print("[POOL] %s (pool of record; active pool verified by pool_guard)" % POOL, flush=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first payload, post nothing")
    ap.add_argument("--run", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="only the first N matches (all three arms)")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.dry_run: sys.exit(dry_run(a.pilot))
    elif a.run:
        if run(a.pilot, a.workers): analyze()
        else: sys.exit(2)
    elif a.analyze: analyze()
    else: ap.print_help()
