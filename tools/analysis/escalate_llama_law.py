"""ESCALATE-LLAMA-LAW — item 24 of docs/design/FRAMEWORK.md "Tests to register before shipping", registered by
reference at commit eaf1dbf; fixed parameters in docs/plan_2026-09-15.md (control model Qwen1.5-72B-Chat) and
Amendment 1 of the same plan (D2 temperature omitted, D4 deciding threshold / comparator label / stratified readout /
coverage rule), applied here before the first judged call.

THE QUESTION. KEY-TIE-DECLINE's composed rule leaves four residue errors on the merged per-anchor board, all
four the same model (Meta-Llama-3.1-70B-Instruct) over-rated against cheaper-tier opponents in Law (3) and
Philosophy (1). Does escalating exactly those cells to the reasoning judge WITH the reference (J1-R) buy
committed accuracy there, or is JUDGE-2x2 right that judge competence is irrelevant once the reference is fixed?

DESIGN (registered text, FRAMEWORK.md item 24):
  population  every x12 MAIN match whose question sits in a Law or Philosophy cell and involves
                treatment  Meta-Llama-3_1-70B-Instruct   (the model the residue is anchored on)
                control    Qwen1.5-72B-Chat              (same key tier on x20, no residue error; a match that
                                                          involves BOTH is a treatment match, never a control)
              cell = depth-1 anchor of the question's routed leaf on bareq512_s42 (the definition
              systematic_budget.build() used to find the residue; --cell-by category = MMLU-Pro category instead)
  judge       J1-R = grok-4-1-fast-reasoning, v1 cell-rubric prompt + the grok-reasoning reference block, dual
              order, flip -> TIE (byte-identical to rejudge_reasoning.py --reference grok-reasoning, the J1-R of
              the ledger), every call through call_judge_full so finish_reason and completion tokens are stored.
              Temperature is OMITTED from the payload (provider default; Amendment 1 D2), recorded in meta.
  comparator  Mistral STACK-v2, proxy for the shipped grok recipe judge (JUDGE-SWAP p = 1.0): the cached
              Mistral-Large-3 STACK-v2 verdicts on the IDENTICAL matches (ARENA-V2, stack_v2_promptv2_x12all.db).
              No grok-recipe cache covers the population; the 53-match overlap with stack_v2_promptv2_grok.db is
              printed as a secondary, underpowered readout. The 10-cce consequence is a claim about the proxy.
  readouts    committed accuracy on the key-decidable matches of each arm under BOTH tie conventions
                A  ties count as wrong   (denominator: all key-decidable matches)
                B  ties excluded         (denominator: committed = non-tie verdicts of both judges)
              paired exact McNemar b:c against the comparator; paired MDE at n, two-sided alpha 0.05 / power 0.80,
              MDE = (1.96 + 0.84) * sqrt(d / n).
  threshold   THE DECIDING MDE IS THE A PRIORI ONE at d = 0.20 and the known key-decidable n, fixed before launch
              (Amendment 1 D4): n = 85 treatment -> 0.136, n = 80 control -> 0.140. The MDE at the observed
              discordance d = (b + c) / n is reported beside it and does not decide (it is data-dependent: delta >
              2.80 * sqrt(d / n) is algebraically z > 2.80 on the discordant pairs). The registered n counts the two
              key-decidable matches without a reference; the judgeable key-decidable n is 84/79 and the NOTE on the
              readout is expected; the D4 thresholds (0.136/0.140) stay.
  criterion   PASS iff, under both conventions, the TREATMENT arm's paired gain exceeds 0.136 AND the CONTROL arm
              shows no significant fall (exact McNemar p < 0.05 with c > b). Prediction: FAIL.
  confound    the J1-R system prompt is the leaf judgePrompt/judgeRubric of the FROZEN tree (20260727_042523),
              whose reserved split was p8a29d8f3ff75aa55 (the INCIDENT split): 168 of the run's 250 questions are
              on that tree's train side, i.e. the rubric the treatment judge sees was induced with the question in
              view; the comparator (bareq512 anchor rubric, p2dca reserved) is clean. Directional in favour of J1-R,
              bounded by LEAF-POWERED (+-2pp) and RUBRIC-512-R (24:24), below the deciding MDE; recorded in meta and
              the report, and the paired delta is read stratified: clean (82 questions, in p8a29 AND p2dca, by
              explicit id) vs train-side (168). The default prompt stays byte-identical to the ledger's J1-R.
  guard       VERDICT REFUSED when more than 5% of the deciding subset (key-decidable matches, per arm or pooled)
              is unparsed or non-terminated (finish_reason == length is NON_TERMINATED: never a verdict, never a tie).
              A judgeable match missing from the cache (errored after the retries) COUNTS AS UNPARSED in the guard.
  coverage    the REGISTERED PASS/FAIL line is written only when the cache covers 100% of the judgeable population
              (population minus the matches with no grok-reasoning reference, listed by id); otherwise the report
              says INCOMPLETE: no registered verdict. A --pilot N run writes <cache>_pilot<N>.txt, never the report
              of record; 'started' is written once, resumes are appended; the producing script's sha256 is pinned
              at first launch and a resume under a different judge/protocol/cap is refused.

    python tools/analysis/escalate_llama_law.py --dry-run [--pilot 12]      # zero calls: payloads, counts, prompts
    python tools/analysis/escalate_llama_law.py --pilot 12 --workers 8      # 24 calls, report to _pilot12.txt, read the guard
    python tools/analysis/escalate_llama_law.py --workers 8 --maxtok 8192   # the run (resumes from its own cache)
    python tools/analysis/escalate_llama_law.py --analyze                   # report only
"""
import os, sys, json, math, time, sqlite3, argparse, threading, hashlib, inspect
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"):   # the prompts carry an em dash; a cp1252 console must not abort the verbatim print
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_512 as r512

POOL = pool_guard.FROZEN_POOL_ID                       # p2dca21ab5f4ef3ae, the pool of record
CLEAN_POOL = "p8a29d8f3ff75aa55"                        # the frozen tree's reserved split: a question in BOTH pools is clean
TREATMENT = "Meta-Llama-3_1-70B-Instruct"
CONTROL = "Qwen1.5-72B-Chat"
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}                # never judged, never compared (eval id-space repair)
CELLS = ("Law", "Philosophy")
JUDGE = "grok-4-1-fast-reasoning"
PROTOCOL = "J1-R: v1 cell rubric + grok-reasoning reference, reasoning judge, dual order, flip->TIE"
RUBRIC_SOURCE = ("frozen tree %s (reserved split %s): 168 of the run's 250 questions are on its train side, the "
                 "comparator's bareq512 anchor rubric is clean; confound directional for J1-R, bounded +-2pp" % (rj.SNAP_ID, CLEAN_POOL))
DEFAULT_MAXTOK = 8192                                   # rejudge_reasoning's constant, the cap J1-R of record ran at
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "escalate_llama_law.db")   # set by cache_path()
COMPARATOR = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x12all.db")
COMPARATOR_LABEL = "Mistral STACK-v2, proxy for the shipped grok recipe judge (JUDGE-SWAP p=1.0)"
GROK_RECIPE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_grok.db")   # 53-match overlap, secondary
J1R_LEDGER = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok_4_1_fast_reasoning_refgrok.db")
REPORT = CACHE[:-3] + ".txt"
CELL_BY = "anchor"
MAXTOK = DEFAULT_MAXTOK
TEMPERATURE = None      # None = field omitted (Amendment 1 D2), byte-identical to the J1-R of record; --temperature writes a literal
Z_MDE = 1.959964 + 0.841621
# Amendment 1 D4: the deciding threshold, fixed before launch at d = 0.20 and the known key-decidable n per arm.
N_REGISTERED = {"treatment": 85, "control": 80}
MDE_DECIDING = {"treatment": 0.136, "control": 0.140}


def script_sha256():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def cache_path():
    """Own cache per configuration (ref_qualify's rule): a raised cap, a set temperature or the category cell
    definition never overwrites the run of record, so a voided run stays on disk as evidence."""
    tag = ""
    if MAXTOK != DEFAULT_MAXTOK: tag += "_mt%d" % MAXTOK
    if TEMPERATURE is not None: tag += "_t%s" % str(TEMPERATURE).replace(".", "p")
    if CELL_BY != "anchor": tag += "_" + CELL_BY
    return os.path.join(ROOT, "experiment_results", "x12_crossdomain", "escalate_llama_law%s.db" % tag)


def report_path(pilot):
    """The report of record is written only by the complete run; a pilot writes its own file."""
    return CACHE[:-3] + ("_pilot%d.txt" % pilot if pilot else ".txt")


def clean_questions():
    """Questions of the frozen tree's reserved side, read by explicit id (the clean stratum is POOL intersect CLEAN_POOL)."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    s = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (CLEAN_POOL,))}
    ev.close()
    assert s, "pool %s is not recorded in reserved_pool" % CLEAN_POOL
    return s


def population():
    """Ordered list of (match, arm, cell) for the treatment and control arms, pool membership by explicit id."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    assert pool, "pool %s is not recorded in reserved_pool" % POOL
    if CELL_BY == "anchor":
        route = r512.primary_routing("bareq512_s42")
        anchor_of = r512.anchor_fn(r512.load_graph(r512.snapshot_id("bareq512_s42")))
        cell = {q: anchor_of(leaf) for q, leaf in route.items()}
    else:
        cell = {q: (c or "").strip().title() for q, c in ev.execute("SELECT DISTINCT question_id, category FROM eval_results")}
    ev.close()
    con = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    rows = con.execute("SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie FROM match_history "
                       "WHERE condition='MAIN' AND snapshot_id=? ORDER BY id", (rj.SNAP_MAIN,)).fetchall()
    con.close()
    out = []
    for m in rows:
        q = int(m[1])
        if q not in pool:
            continue
        if m[2] in EXCLUDED or m[3] in EXCLUDED:
            continue
        c = cell.get(q)
        if c not in CELLS:
            continue
        if TREATMENT in (m[2], m[3]):
            out.append((m, "treatment", c))
        elif CONTROL in (m[2], m[3]):
            out.append((m, "control", c))
    assert all(int(m[1]) in pool for m, _, _ in out)
    return out


def judgeable(pop, nodes, evals, refs):
    """(jobs, skipped): jobs = [(entry, prompts)] for every match with a trace and a reference; skipped = the entries
    without one, listed by id. Zero cost: prompts are assembled locally."""
    jobs, skipped = [], []
    for e in pop:
        pr = prompts_for(e[0], nodes, evals, refs)
        if pr is None: skipped.append(e)
        else: jobs.append((e, pr))
    return jobs, skipped


def open_cache():
    con = sqlite3.connect(CACHE)
    # rejudge_reasoning's verdicts schema (so rejudge_reasoning-style readers work), extended with the arm, the
    # cell, the reference and the per-call finish_reason; r1_* columns hold the J1-R verdict as in that cache.
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER,
        mistral_winner TEXT,
        vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL,
        r1_winner TEXT, r1_flip INTEGER, r1_invalid INTEGER,
        raw1 TEXT, raw2 TEXT, provider1 TEXT, provider2 TEXT,
        tok1 INTEGER, tok2 INTEGER, lat1 REAL, lat2 REAL, ts REAL,
        arm TEXT, cell TEXT, ref_letter TEXT, ref_correct INTEGER,
        finish1 TEXT, finish2 TEXT, nonterm INTEGER)""")
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit()
    return con


def read_meta(con):
    return {k: json.loads(v) for k, v in con.execute("SELECT key, value FROM meta")}


def record_meta(con, **kv):
    for k, v in kv.items():
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (k, json.dumps(v)))
    con.commit()


def stamp_cache(con):
    """First launch pins the protocol and the script; a resume must match it ('started' once, resumes appended)."""
    meta = read_meta(con)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    fixed = dict(judge=JUDGE, provider="azure", protocol=PROTOCOL, max_tokens=MAXTOK, temperature=TEMPERATURE,
                 pool=POOL, cell_by=CELL_BY, treatment=TREATMENT, control=CONTROL)
    if "started" in meta:
        diff = {k: (meta.get(k), v) for k, v in fixed.items() if meta.get(k) != v}
        if diff:
            sys.exit("REFUSED: resume into %s under a different protocol: %s" % (CACHE, diff))
        record_meta(con, resumed_at=list(meta.get("resumed_at", [])) + [now])
        if meta.get("script_sha256") != script_sha256():
            record_meta(con, script_sha256_resumes=list(meta.get("script_sha256_resumes", [])) + [script_sha256()])
        return
    record_meta(con, started=now, resumed_at=[], script_sha256=script_sha256(), **fixed)
    record_meta(con, comparator=os.path.basename(COMPARATOR), comparator_label=COMPARATOR_LABEL,
                grok_recipe_secondary=os.path.basename(GROK_RECIPE), rubric_source=RUBRIC_SOURCE, clean_pool=CLEAN_POOL,
                mde_deciding=MDE_DECIDING, n_registered=N_REGISTERED, temperature_policy="omitted from the payload (Amendment 1 D2)")


def configure_judge():
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE


# The posted body is assembled in rejudge_reasoning.call_judge_full, lines 92-96 (payload_body = {"model", "max_tokens",
# "messages"[, "temperature" when not None]}). This is a local copy for the dry-run only; check_payload_copy() asserts
# at dry-run time that the source still builds the same key tuple, so a later change there cannot go unnoticed here.
PAYLOAD_KEYS = ("model", "max_tokens", "messages")


def payload(system, user):
    """The body rejudge_reasoning.call_judge_full posts, assembled without posting (dry-run only)."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None:
        body["temperature"] = rr.TEMPERATURE
    return body


def check_payload_copy(body):
    """Dry-run assertion: the local copy's key tuple equals what call_judge_full's source builds."""
    expect = PAYLOAD_KEYS + (("temperature",) if rr.TEMPERATURE is not None else ())
    assert tuple(body.keys()) == expect, (tuple(body.keys()), expect)
    src = inspect.getsource(rr.payload_body)   # 2026-09-16: the body builder was factored out of call_judge_full (JUDGE-WIRING), bytes unchanged
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    for frag in ('payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,',
                 '"messages": [{"role": "system", "content": system},',
                 '{"role": "user", "content": user}]}',
                 'if TEMPERATURE is not None:', 'payload_body["temperature"] = TEMPERATURE'):
        assert frag in src, "rejudge_reasoning.call_judge_full no longer builds the body this copy prints: %r" % frag
    assert body["messages"][0]["role"] == "system" and body["messages"][1]["role"] == "user"
    assert "temperature" not in body or body["temperature"] == rr.TEMPERATURE


def prompts_for(m, nodes, evals, refs):
    """(system, user order 1, user order 2) or None when a trace or the reference is missing (skipped, counted)."""
    mid, qid, a, b, nid, *_ = m; qid = int(qid)
    ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
    if ra is None or rb is None or ref is None:
        return None
    q = rref.with_reference(ra[0], ref)
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    system = rj.build_system_prompt(nodes[nid])
    return system, rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)


def judge_one(entry, nodes, evals, refs):
    m, arm, cell = entry
    mid, qid, a, b, nid, winner, is_tie = m; qid = int(qid)
    pr = prompts_for(m, nodes, evals, refs)
    if pr is None:
        return None
    system, u1, u2 = pr
    c1_, p1, k1, l1, f1, _ = rr.call_judge_full(system, u1)
    c2_, p2, k2, l2, f2, _ = rr.call_judge_full(system, u2)
    v1, c1 = rj.parse_judge(rr.strip_think(c1_)); v2, c2 = rj.parse_judge(rr.strip_think(c2_))
    nonterm = int(f1 == "length" or f2 == "length")
    if nonterm:
        v1 = "NON_TERMINATED" if f1 == "length" else v1
        v2 = "NON_TERMINATED" if f2 == "length" else v2
        w, flip, inv = "NON_TERMINATED", False, True
    else:
        w, flip, inv = rj.combine_orders(v1, v2)
    ref = refs[qid]
    return (mid, a, b, nid, qid, "TIE" if is_tie else winner, v1, v2, c1, c2,
            {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), c1_, c2_, p1, p2, k1, k2, l1, l2, time.time(),
            arm, cell, ref[0], int(ref[2]), f1, f2, nonterm)


def header(pop, todo, skipped, workers, dry, pilot):
    print("[POOL] %s (pool of record, asserted active; every question addressed by explicit id)" % POOL, flush=True)
    arms = defaultdict(int); cells = defaultdict(int)
    for _, arm, cell in pop:
        arms[arm] += 1; cells[(arm, cell)] += 1
    print("ESCALATE-LLAMA-LAW%s%s | cell-by=%s | population %d matches: treatment(%s) %d, control(%s) %d | %s"
          % (" DRY-RUN" if dry else "", " PILOT %d" % pilot if pilot else "", CELL_BY, len(pop), TREATMENT, arms["treatment"],
             CONTROL, arms["control"], ", ".join("%s/%s %d" % (a, c, n) for (a, c), n in sorted(cells.items()))), flush=True)
    print("  judge=%s provider=azure | protocol: %s" % (JUDGE, PROTOCOL), flush=True)
    print("  cap: max_tokens=%d | temperature=%s | workers=%d | script sha256 %s"
          % (MAXTOK, "omitted" if TEMPERATURE is None else TEMPERATURE, workers, script_sha256()[:16]), flush=True)
    print("  cache: %s" % CACHE, flush=True)
    print("  report: %s%s" % (REPORT, " (pilot: never the report of record)" if pilot else ""), flush=True)
    print("  comparator: %s (%s)" % (COMPARATOR, COMPARATOR_LABEL), flush=True)
    print("  rubric source: %s" % RUBRIC_SOURCE, flush=True)
    print("  deciding threshold (Amendment 1 D4, a priori d=0.20 at registered n): treatment %.3f (n=%d), control %.3f (n=%d); observed-d MDE reported, non-deciding"
          % (MDE_DECIDING["treatment"], N_REGISTERED["treatment"], MDE_DECIDING["control"], N_REGISTERED["control"]), flush=True)
    print("  to judge: %d matches -> %d calls (dual order) | skipped for missing trace/reference: %d%s"
          % (len(todo), 2 * len(todo), len(skipped),
             " [match ids %s; questions %s]" % (", ".join(str(e[0][0]) for e in skipped), ", ".join(str(int(e[0][1])) for e in skipped)) if skipped else ""), flush=True)


def run(pilot, workers, dry):
    configure_judge()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    nodes = rj.load_nodes()
    pop = population()
    if pilot:
        pop = pop[:pilot]
    if not dry:
        rr.load_env()
        cache = open_cache()
        stamp_cache(cache)
        done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    else:
        done = set()
    pop_todo = [e for e in pop if e[0][0] not in done]
    evals = rj.load_eval_rows([int(e[0][1]) for e in pop_todo], {e[0][2] for e in pop_todo} | {e[0][3] for e in pop_todo})
    jobs, skipped = judgeable(pop_todo, nodes, evals, refs)
    header(pop, jobs, skipped, workers, dry, pilot)
    if dry:
        payloads = []
        for e, (system, u1, u2) in jobs:
            payloads.append(payload(system, u1)); payloads.append(payload(system, u2))
        assert all("max_tokens" in p and p["model"] == JUDGE and p["max_tokens"] == MAXTOK for p in payloads)
        assert all(("temperature" in p) == (TEMPERATURE is not None) for p in payloads)
        for p in payloads: check_payload_copy(p)
        print("  DRY-RUN: %d payloads assembled, %d bytes total, nothing posted | payload keys %s verified against rejudge_reasoning.call_judge_full source"
              % (len(payloads), sum(len(json.dumps(p)) for p in payloads), tuple(payloads[0].keys()) if payloads else ()), flush=True)
        if payloads:
            e0 = jobs[0][0]
            print("  first payload: match %d arm=%s cell=%s %s vs %s qid=%d | model=%s max_tokens=%d temperature=%s"
                  % (e0[0][0], e0[1], e0[2], e0[0][2], e0[0][3], int(e0[0][1]), payloads[0]["model"], payloads[0]["max_tokens"],
                     payloads[0].get("temperature", "omitted")))
            print("----- SYSTEM (verbatim) -----"); print(payloads[0]["messages"][0]["content"])
            print("----- USER, order 1 (verbatim) -----"); print(payloads[0]["messages"][1]["content"])
            print("----- END -----")
        return
    if not jobs:
        print("nothing to judge (all cached)"); return
    lock = threading.Lock(); ok = err = 0; nonterm = 0; errored = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(judge_one, e, nodes, evals, refs): e for e, _ in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as ex_:
                err += 1; errored.append(futs[f][0][0])
                print("  ERROR match %s: %s" % (futs[f][0][0], str(ex_)[:140]), flush=True); continue
            if row is None: continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 29), row); cache.commit()
            ok += 1; nonterm += row[28]
            if i % 20 == 0 or i == len(jobs):
                print("  %d/%d (ok %d, err %d, non-terminated %d)" % (i, len(jobs), ok, err, nonterm), flush=True)
    record_meta(cache, finished=time.strftime("%Y-%m-%d %H:%M:%S"), last_pass_errors=sorted(errored))
    print("done: ok %d, errors %d (match ids %s; a resume re-posts them), non-terminated %d" % (ok, err, sorted(errored), nonterm), flush=True)


# ── Analysis ───────────────────────────────────────────────────────────────────

def mde(n, d):
    return Z_MDE * math.sqrt(d / n) if n and d > 0 else float("nan")


def paired(rows, conv):
    """rows: list of dicts with 'r1' (J1-R correct/None), 'cmp' (comparator correct/None), tie flags.
    conv A: ties are wrong, every key-decidable match counts. conv B: a match counts only if NEITHER judge tied."""
    if conv == "A":
        use = rows
    else:
        use = [r for r in rows if not r["r1_tie"] and not r["cmp_tie"]]
    n = len(use)
    if not n:
        return dict(n=0)
    x = sum(r["r1"] for r in use) / n; y = sum(r["cmp"] for r in use) / n
    b = sum(1 for r in use if r["r1"] and not r["cmp"]); c = sum(1 for r in use if r["cmp"] and not r["r1"])
    d = (b + c) / n
    return dict(n=n, r1=x, cmp=y, delta=x - y, b=b, c=c, p=rr.mcnemar_p(b, c), mde_obs=mde(n, d), mde_20=mde(n, 0.20), d=d)


def paired_rows(entries, G, cmp_, key="cmp"):
    """Paired (J1-R, comparator) correctness rows over cached, parsed, key-decidable matches with a parsed comparator."""
    rows = []
    for r in entries:
        mid, a, b, q, w, fl, inv, *_ = r
        if inv: continue
        c = cmp_.get(mid)
        if c is None or c[2]: continue
        d = a if G[(q, a)] else b
        rows.append(dict(r1=w == d, cmp=c[1] == d, r1_tie=w == "TIE", cmp_tie=c[1] == "TIE"))
    return rows


def fmt_paired(L, indent, s, conv, lab, deciding=None):
    if not s["n"]:
        L.append("%s%s (%s): n=0" % (indent, conv, lab)); return
    L.append("%s%s (%-13s) n=%3d | J1-R %.3f vs STACK-v2 %.3f (%+.3f) | %d:%d McNemar p=%.4f | MDE: %sa priori d=0.20 at this n %.3f | observed d=%.2f -> %.3f (non-deciding)"
             % (indent, conv, lab, s["n"], s["r1"], s["cmp"], s["delta"], s["b"], s["c"], s["p"],
                ("DECIDING %.3f (registered) | " % deciding) if deciding is not None else "", s["mde_20"], s["d"], s["mde_obs"]))


def analyze(pilot=None):
    """Report. A complete cache (100% of the judgeable population) writes the REGISTERED line into the report of
    record; a pilot or an incomplete cache writes INCOMPLETE and, for a pilot, only into <cache>_pilot<N>.txt."""
    con = sqlite3.connect("file:%s?mode=ro" % CACHE, uri=True)
    meta = read_meta(con)
    st = con.execute("SELECT match_id, model_a, model_b, qid, r1_winner, r1_flip, r1_invalid, arm, cell, finish1, finish2, nonterm, tok1, tok2 FROM verdicts").fetchall()
    if not st:
        print("no verdicts cached"); return
    cmp_ = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % COMPARATOR, uri=True).execute("SELECT match_id, winner, invalid FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    ev.close()
    clean = clean_questions()
    # coverage: the judgeable population (population minus the reference-less skips), recomputed at zero cost
    rref.set_reference("grok-reasoning"); refs = rref.references(); nodes = rj.load_nodes()
    pop = population()
    scope = pop[:pilot] if pilot else pop
    evals = rj.load_eval_rows([int(e[0][1]) for e in scope], {e[0][2] for e in scope} | {e[0][3] for e in scope})
    jobs, skipped = judgeable(scope, nodes, evals, refs)
    cached = {r[0] for r in st}
    missing = [e for e, _ in jobs if e[0][0] not in cached]
    extra = sorted(cached - {e[0][0] for e, _ in jobs})
    # the readout is about the judgeable scope only, in both modes: a pilot's matches, or the judgeable population
    # (cached rows outside the scope are counted in the coverage line above and never enter the readouts)
    keep = {e[0][0] for e, _ in jobs}; st = [r for r in st if r[0] in keep]
    complete = not pilot and not missing
    stale = meta.get("script_sha256") not in (None, script_sha256())
    L = ["=== ESCALATE-LLAMA-LAW%s: J1-R (%s, cap %s, temperature %s) vs %s on identical matches ===" % (
        " PILOT %d" % pilot if pilot else "", meta.get("judge", JUDGE), meta.get("max_tokens", "?"),
        "omitted" if meta.get("temperature", None) is None else meta.get("temperature"), meta.get("comparator_label", COMPARATOR_LABEL)),
         "  pool %s | cell-by %s | judged %d matches | comparator %s (%s)" % (meta.get("pool", POOL), meta.get("cell_by", "?"), len(st), os.path.basename(COMPARATOR), COMPARATOR_LABEL),
         "  rubric source: %s" % meta.get("rubric_source", RUBRIC_SOURCE),
         "  producing script sha256 %s%s | started %s | resumes %s | report written %s" % (
             meta.get("script_sha256"), " <- STALE: cache judged by a different version; current %s" % script_sha256()[:16] if stale else "",
             meta.get("started"), len(meta.get("resumed_at", [])), time.strftime("%Y-%m-%d %H:%M:%S")),
         "  coverage: %d cached of %d judgeable%s (population %d, no reference for %d: match ids %s) | missing %d%s%s" % (
             len(jobs) - len(missing), len(jobs), " in the pilot scope" if pilot else "", len(scope), len(skipped),
             ", ".join(str(e[0][0]) for e in skipped) or "-", len(missing),
             ": match ids %s" % ", ".join(str(e[0][0]) for e in missing) if missing else "",
             " | %d cached rows outside the scope%s" % (len(extra), ": %s" % extra if len(extra) <= 20 else " (ignored)") if extra else "")]
    # deciding subset = key-decidable matches; the guard reads unparsed + non-terminated there, per arm and pooled,
    # and a judgeable match missing from the cache counts as unparsed (Amendment 1 D4)
    dec = defaultdict(list); miss_dec = defaultdict(int)
    for r in st:
        mid, a, b, q, w, fl, inv, arm, cell, f1, f2, nt, t1, t2 = r
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        dec[arm].append(r); dec["pooled"].append(r)
    for (m, arm, cell) in missing:
        q = int(m[1]); ca, cb = G.get((q, m[2])), G.get((q, m[3]))
        if ca is None or cb is None or ca == cb: continue
        miss_dec[arm] += 1; miss_dec["pooled"] += 1
    fin = defaultdict(int)
    for r in st: fin[str(r[9])] += 1; fin[str(r[10])] += 1
    L.append("  finish_reason over %d calls: %s | mean completion tokens %.0f" % (
        2 * len(st), dict(fin), sum((r[12] or 0) + (r[13] or 0) for r in st) / max(1, 2 * len(st))))
    refused = False
    for arm in ("treatment", "control", "pooled"):
        rows = dec[arm]; bad = sum(1 for r in rows if r[6]); n_dec = len(rows) + miss_dec[arm]
        rate = (bad + miss_dec[arm]) / max(1, n_dec)
        L.append("  guard [%s]: key-decidable %d | unparsed or non-terminated %d + missing from cache %d (%.1f%%) -> %s" % (
            arm, n_dec, bad, miss_dec[arm], 100 * rate, "OK" if rate <= 0.05 else "ABOVE 5%"))
        refused |= rate > 0.05 and n_dec > 0
    if refused:
        L.append("  VERDICT REFUSED: more than 5% of a deciding subset is unparsed, non-terminated or missing. Re-run (a resume")
        L.append("  re-posts errored matches), raise --maxtok (own cache by design) or record non-termination as a property of the judge; no accuracy is read.")
        if not complete:
            L.append("  INCOMPLETE: no registered verdict (%s)." % ("pilot of %d" % pilot if pilot else "%d judgeable matches missing" % len(missing)))
        txt = "\n".join(L); print(txt); open(REPORT, "w", encoding="utf-8").write(txt + "\n"); return
    res = {}
    for arm in ("treatment", "control", "pooled"):
        rows = paired_rows(dec[arm], G, cmp_)
        res[arm] = {conv: paired(rows, conv) for conv in ("A", "B")}
        L.append("  %s: %d paired key-decidable matches | J1-R ties %.3f | STACK-v2 ties %.3f%s" % (
            arm.upper(), len(rows), sum(r["r1_tie"] for r in rows) / max(1, len(rows)), sum(r["cmp_tie"] for r in rows) / max(1, len(rows)),
            "" if arm == "pooled" or len(dec[arm]) + miss_dec[arm] == N_REGISTERED[arm] else
            " | NOTE key-decidable n=%d differs from the registered n=%d; the registered threshold still decides" % (len(dec[arm]) + miss_dec[arm], N_REGISTERED[arm])))
        for conv, lab in (("A", "ties wrong"), ("B", "ties excluded")):
            fmt_paired(L, "      ", res[arm][conv], conv, lab, MDE_DECIDING.get(arm))
        # stratified readout: clean questions (reserved on the frozen tree, in CLEAN_POOL) vs train-side (rubric induced with the question in view)
        for lab, sel in (("clean (in %s)" % CLEAN_POOL, lambda r: r[3] in clean), ("train-side of the frozen tree", lambda r: r[3] not in clean)):
            sub = [r for r in dec[arm] if sel(r)]
            srows = paired_rows(sub, G, cmp_)
            L.append("      stratum %-32s %d key-decidable, %d paired" % (lab + ":", len(sub), len(srows)))
            for conv, lab2 in (("A", "ties wrong"), ("B", "ties excluded")):
                fmt_paired(L, "          ", paired(srows, conv), conv, lab2)
    # registered criterion: the a priori threshold fixed before launch decides (Amendment 1 D4), same figure under both conventions
    checks = []
    for conv in ("A", "B"):
        t, c = res["treatment"][conv], res["control"][conv]
        rise = bool(t.get("n")) and t["delta"] > MDE_DECIDING["treatment"]
        fall = bool(c.get("n")) and c["delta"] < 0 and c["p"] < 0.05
        checks.append(("conv %s: treatment gain %+.3f > deciding MDE %.3f (observed-d MDE %.3f, non-deciding)" % (
            conv, t.get("delta", float("nan")), MDE_DECIDING["treatment"], t.get("mde_obs", float("nan"))), rise))
        checks.append(("conv %s: control shows no significant fall (%+.3f, p=%.3f; deciding MDE %.3f)" % (
            conv, c.get("delta", float("nan")), c.get("p", float("nan")), MDE_DECIDING["control"]), not fall))
    for lab, ok in checks: L.append("  %-92s %s" % (lab, "OK" if ok else "FAIL"))
    verdict = "PASS" if all(ok for _, ok in checks) else "FAIL"
    if complete:
        L.append("  ESCALATE-LLAMA-LAW REGISTERED (prediction FAIL): %s" % verdict)
        if verdict == "PASS":
            L.append("  consequence: a model-anchored escalation rule for %s in %s, priced at 10 cce per match (read against the Mistral proxy, not the shipped grok recipe judge)" % (TREATMENT, "/".join(CELLS)))
    else:
        L.append("  INCOMPLETE: no registered verdict (%s; the criterion would currently read %s, not of record)."
                 % ("pilot of %d matches" % pilot if pilot else "%d of %d judgeable matches missing from the cache" % (len(missing), len(jobs)), verdict))
    # secondary readout, underpowered: J1-R vs the shipped grok recipe judge on the matches its cache covers (53 of 337)
    if os.path.exists(GROK_RECIPE):
        gk = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % GROK_RECIPE, uri=True).execute("SELECT match_id, winner, invalid FROM verdicts")}
        for arm in ("treatment", "control", "pooled"):
            grows = paired_rows([r for r in dec[arm] if r[0] in gk], G, gk)
            L.append("  secondary [%s] J1-R vs grok recipe (%s), %d paired matches, UNDERPOWERED (non-deciding):" % (arm, os.path.basename(GROK_RECIPE), len(grows)))
            for conv, lab in (("A", "ties wrong"), ("B", "ties excluded")):
                s = paired(grows, conv)
                if not s["n"]: L.append("      %s (%s): n=0" % (conv, lab)); continue
                L.append("      %s (%-13s) n=%3d | J1-R %.3f vs grok recipe %.3f (%+.3f) | %d:%d McNemar p=%.4f | MDE a priori d=0.20 at this n %.3f"
                         % (conv, lab, s["n"], s["r1"], s["cmp"], s["delta"], s["b"], s["c"], s["p"], s["mde_20"]))
    # side readout, zero cost: J1-R of the ledger already judged some of these matches (the R3 sample) -> test-retest
    if os.path.exists(J1R_LEDGER):
        led = {r[0]: r[1] for r in sqlite3.connect("file:%s?mode=ro" % J1R_LEDGER, uri=True).execute("SELECT match_id, r1_winner FROM verdicts WHERE r1_invalid=0")}
        both = [(r[4], led[r[0]]) for r in st if r[0] in led and not r[6]]
        if both:
            L.append("  side readout: %d matches also in the ledger's J1-R cache | verdict agreement %.3f (J1-R test-retest, same prompts)"
                     % (len(both), sum(a == b for a, b in both) / len(both)))
    txt = "\n".join(L); print(txt); open(REPORT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first prompts, post nothing")
    ap.add_argument("--pilot", type=int, default=None, help="limit to the first N matches of the population; report to <cache>_pilot<N>.txt")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=DEFAULT_MAXTOK, help="completion cap written into every payload (default %d)" % DEFAULT_MAXTOK)
    ap.add_argument("--temperature", type=float, default=None, help="explicit literal; omitted from the payload when not given (Amendment 1 D2)")
    ap.add_argument("--cell-by", choices=["anchor", "category"], default="anchor")
    ap.add_argument("--analyze", action="store_true", help="report only; with --pilot N the report goes to the pilot file")
    a = ap.parse_args()
    MAXTOK = a.maxtok; TEMPERATURE = a.temperature; CELL_BY = a.cell_by
    CACHE = cache_path(); REPORT = report_path(a.pilot)
    assert os.path.basename(CACHE).startswith("escalate_llama_law"), CACHE   # never an existing cache of another run
    assert (a.pilot is None) == (REPORT == CACHE[:-3] + ".txt")               # the report of record only without --pilot
    if a.analyze:
        analyze(a.pilot)
    else:
        run(a.pilot, a.workers, a.dry_run)
        if not a.dry_run:
            analyze(a.pilot)
