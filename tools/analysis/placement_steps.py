"""PLACEMENT-STEPS - one further bisection step per separable tier for the two recorded newcomers (judged; 400 matches
= 800 calls). Registered 2026-09-19 in docs/judge_v2_program.md ("Registered 2026-09-19 (before any code or call) -
PLACEMENT-STEPS", commit 20cb7b6; authorised by plan Amendment 6, docs/plan_2026-09-15.md L190-L231; plan
docs/agents/plans/2026-09-18_reframing_and_next.md S2 R5).

  python tools/analysis/placement_steps.py --selftest                 (synthetic verdicts through the readout; opens no DB; 0 calls)
  python tools/analysis/placement_steps.py --dry-run                  (pool id first; C0 replayed; the four step schedules; every payload
                                                                       assembled; the bill; 0 calls; no cache created)
  python tools/analysis/placement_steps.py --pilot 12 [--workers 8]   (the first 12 matches of the fixed schedule = 24 calls; REFUSED unless
                                                                       STEPS_GO == 6 AND docs/reviews/READY_placement_steps.md exists and is committed)
  python tools/analysis/placement_steps.py --run [--workers 8]        (the remaining matches; same gate; resume = relaunch; cap / protocol pinned)
  python tools/analysis/placement_steps.py --analyze [--draws 2000]   (refuses a partial cache; writes the outcome of record only when complete)

THE STEPS (fixed now; no bisection decides them: the registration L8404-L8410).
  claude-3-5-sonnet-20241022 vs deepseek-chat-v2_5 (t5), claude-3-5-haiku-20241022 (t6), Qwen1.5-110B (t7): 3 x 100 matches;
  gpt-4o-mini vs deepseek-chat-v2_5 (t5): 100 matches. 400 matches x 2 orders = 800 calls, the 12-match pilot inside the count.
QUESTIONS per step: pool p2dca21ab5f4ef3ae only; (a) both contestants carry an eval-side trace; (b) a CACHED grok-reasoning
reference exists; (c) the two eval_results.pred DISAGREE under the shipped MatchFilter.kt rule (trimmed, case-insensitive,
both non-blank); (d) the question was not used in the newcomer's four recorded anchors (newcomer_placement.db mode=ro);
the eligible list is shuffled with random.Random("42:<newcomer>:<opponent>") EXACTLY as newcomer_placement.candidates drew
the recorded anchors and the first 100 are taken (the registration's "stratified by the 14 anchors as the recorded protocol
drew them": the recorded protocol did NOT stratify - it drew by that seeded shuffle; the anchor distribution of the draw is
printed beside the eligible distribution so the reviewer can read the stratification, see the report). Counts are FIXED at
the dry-run; a step with fewer than 100 eligible questions takes the eligible number (printed, never topped up).
JUDGE: STACK-v2 on grok-4-1-fast-non-reasoning, the routed bareq512_s42 anchor rubric, the CACHED_SOLVE grok-reasoning
reference (D5), cap 8192, temperature OMITTED (D2), dual order, TIE on flip, no third call; every call through
rejudge_reasoning.call_judge_full via newcomer_placement.judge_jobs (finish_reason, completion tokens, cap per row; an HTTP 400
content_filter cached as an unusable row, never re-posted). The payload assembler is newcomer_placement.payload (imported,
never re-implemented); the body is asserted against rr.payload_body (rule 9).
READOUT (--analyze): the four recorded certificates per newcomer REPLAYED from newcomer_placement.db mode=ro through
placement_ceiling.certificates and asserted equal to PLACEMENT-CEILING's numbers (C0, the gate); the new anchors certified
(question-clustered bootstrap B = 2,000, seed 42, 0.975 with 0.95 beside, opposite-draw counts) under PRIMARY (ties 1/2,
unusable excluded) / A / B; the band re-read over all 7 (sonnet) / 5 (gpt-4o-mini) anchors under BOTH readings:
  INCLUSIVE = placement_ceiling.tier_interval over all anchors (the reading of record that reproduced 7 / 3);
  EXCLUSIVE = the band of record (PLACEMENT-CEILING's interval, 1..7 / 4..6) minus every (iii) tier BOUNDED by a certificate
  (a tier is bounded when the NEWCOMER IS CERTIFIED ABOVE a member of it: registration C1's definition); a (iii) tier whose
  member is certified ABOVE the newcomer joins the band as ii* ("joins the band as (ii) or (i) by its key relation", C1) and
  is NEVER dropped (review D1); tiers attributed (i) / (ii) are never dropped by a certificate.
  This operationalisation reproduces every number the registration writes (sonnet exclusive 4 = [t1..t4], inclusive 5;
  gpt-4o-mini exclusive 2 or 3); the literal "bounding tiers dropped" would give sonnet 3 (t1 dropped too) - see the report.
  Criterion (22) ("<= 2 ADJACENT tiers") is read on the INCLUSIVE interval: MET iff its width is 2 and the own key tier is
  contained (review D2); the exclusive width is printed beside.
Components per tier after the steps: (i) / (ii) as PLACEMENT-CEILING; a (iii) tier is ii* KEY-CONTRADICTED (a member certified
ABOVE the newcomer; counted with (i)+(ii)), else iii-c BOUNDED (the newcomer certified above a member), else iii-a (a member
judged and unseparated), else iii-b (never judged); per-member states printed (Meta-Llama-3_1-70B-
Instruct in t6 and the D5-excluded peer are printed as never judged). Power column for every unseparated new anchor.
SECONDARY (MIXED-FIT / EXTRAPOLATED, never the verdict): the merged fit's point theta with the new edges (P8).
CRITERIA C0-C3 and PREDICTIONS P1-P8 scored HELD / FAILED as registered (L8455-L8486); VERDICT RULE as registered.
HYGIENE: pool_guard first, own cache experiment_results/x12_crossdomain/newcomer_placement_steps.db (newcomer_placement.db
is opened mode=ro only); run_meta pinned at first launch (script sha, protocol, max_tokens, temperature "omitted", the step
table and the question-id hash) - a relaunch differing on any is REFUSED; the TRUNCATION GUARD refuses to post more once the
unusable rate on the cached matches exceeds 5% (--override-guard posts anyway and is recorded); --analyze refuses a cache
short of the fixed match count or above 5% unusable; pilot / partial readouts go to newcomer_placement_steps_PILOT.txt.
THE READY RULE: --pilot and --run refuse unless the environment variable STEPS_GO equals "6" (plan Amendment 6) AND
docs/reviews/READY_placement_steps.md exists, is tracked by git and carries no uncommitted change (the reviewer's READY of
record) AND experiment_results/judge_solve/ref_remint_outcome.txt exists with its "ALARM STATE:" line reading "ALARM STATE:
NO ALARM" (ARM-B-VINTAGE's registration (b): ARM-B runs BEFORE this pilot; review D6). --dry-run and --selftest never post
and never create the cache; a refused or partial cache prints "NO VERDICT (refused: ...)" in place of the verdict rule (D7).
"""
import os, sys, json, time, random, sqlite3, argparse, hashlib, subprocess, statistics
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

POOL_ID = "p2dca21ab5f4ef3ae"
NEWCOMERS = ["claude-3-5-sonnet-20241022", "gpt-4o-mini"]
EXCLUDED = "Meta-Llama-3-70B-Instruct"
# (newcomer, opponent, key tier of the opponent as recorded in placement_ceiling_bands.csv) - the step table of record
STEPS = [("claude-3-5-sonnet-20241022", "deepseek-chat-v2_5", 5),
         ("claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", 6),
         ("claude-3-5-sonnet-20241022", "Qwen1.5-110B", 7),
         ("gpt-4o-mini", "deepseek-chat-v2_5", 5)]
PER_STEP = 100
SEED = 42
CONF = 0.975
DRAWS = 2000
KEY_GAP = 0.017
MAXTOK = 8192
TEMPERATURE = None
JUDGE_MODEL = "grok-4-1-fast-non-reasoning"
REFERENCE = "grok-reasoning"
MID_BASE = 90_000_000                      # distinct from newcomer_placement's 80_000_000 range
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
RECORD_CACHE = os.path.join(X12DIR, "newcomer_placement.db")
CACHE = os.path.join(X12DIR, "newcomer_placement_steps.db")
OUT = os.path.join(X12DIR, "newcomer_placement_steps_outcome.txt")
OUT_BANDS = os.path.join(X12DIR, "newcomer_placement_steps_bands.csv")
OUT_PILOT = os.path.join(X12DIR, "newcomer_placement_steps_PILOT.txt")
BANDS_OF_RECORD = os.path.join(X12DIR, "placement_ceiling_bands.csv")
READY = os.path.join(ROOT, "docs", "reviews", "READY_placement_steps.md")
ARMB_OUT = os.path.join(ROOT, "experiment_results", "judge_solve", "ref_remint_outcome.txt")     # ARM-B-VINTAGE's outcome (registration (b))
ARMB_OK = "ALARM STATE: NO ALARM"
GO_ENV, GO_VALUE = "STEPS_GO", "6"
PROTOCOL = ("PLACEMENT-STEPS: one further step per separable tier, fixed anchors, %d answer-disagreement-filtered pool "
            "questions per step, CACHED_SOLVE grok-reasoning reference (D5), STACK-v2 (prompt v2 + anchor rubric + reference "
            "block), dual order, TIE on flip, no third call (NO-TIES)" % PER_STEP)
# C0: PLACEMENT-CEILING's replayed certificates (placement_ceiling_outcome.txt L29-32 / L118-121), PRIMARY, share rounded 3 dp
RECORDED_CERTS = {"claude-3-5-sonnet-20241022": [("Qwen1.5-72B-Chat", 0.910, "below"), ("gpt-4o-2024-08-06", 0.505, "unseparated"),
                                                 ("gemini-3.1-pro_5-shots", 0.225, "above"), ("arx_3", 0.510, "unseparated")],
                  "gpt-4o-mini": [("Qwen1.5-72B-Chat", 0.710, "below"), ("arx_0314", 0.170, "above"),
                                  ("claude-3-5-haiku-20241022", 0.595, "below"), ("gpt-4o-2024-08-06", 0.360, "above")]}
RECORDED_BANDS = {"claude-3-5-sonnet-20241022": (1, 7, 3), "gpt-4o-mini": (4, 6, 6)}       # lo, hi, own tier (1-based)
SCRIPT_SHA = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
OVERRIDE_GUARD = False


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


# ---------------------------------------------------------------- the READY gate

def git_tracked_clean(path):
    """(tracked, clean, head) for a file: tracked by git and without an uncommitted change."""
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception as e:
        return False, False, "git unavailable: %s" % e
    return t, c, h


def gate_state():
    have = os.environ.get(GO_ENV)
    exists = os.path.exists(READY)
    tracked, clean, head = git_tracked_clean(READY) if exists else (False, False, "")
    ok = have == GO_VALUE and exists and tracked and clean
    if not exists: state = "MISSING"
    elif tracked and clean: state = "exists, committed %s" % head
    elif not tracked: state = "exists, NOT committed (untracked)"
    else: state = "exists, uncommitted change"
    return ok, "%s=%r (needs %r) | %s %s" % (GO_ENV, have, GO_VALUE, rel(READY), state)


def armb_alarm_state():
    """The 'ALARM STATE:' line of ARM-B-VINTAGE's outcome file, or None when the file does not exist (ARM-B has not run)."""
    if not os.path.exists(ARMB_OUT): return None
    return next((l.strip() for l in open(ARMB_OUT, encoding="utf-8") if l.startswith("ALARM STATE:")), None)


def go_gate(what):
    ok, s = gate_state()
    if not ok:
        raise SystemExit("[READY] %s refused (0 calls): %s. The pilot follows a committed reviewer READY (Amendment 6; the registration's READY rule)." % (what, s))
    print("[READY] %s" % s)
    st = armb_alarm_state()
    if st != ARMB_OK:
        raise SystemExit("[ARM-B] %s refused (0 calls): %s reads %r; ARM-B-VINTAGE (b): no judged spend against v0 references before its outcome is NO ALARM" % (what, rel(ARMB_OUT), st))
    print("[ARM-B] %s: %s" % (rel(ARMB_OUT), st))


# ---------------------------------------------------------------- data of record

def load():
    """Everything the dry run and the analysis need: placement_ceiling.load_record (board, key tiers, the recorded placement
    cache mode=ro) + newcomer_placement.setup (pool, preds, key, routing, rubrics, references)."""
    import placement_ceiling as pc
    import newcomer_placement as npl
    assert npl.CACHE == RECORD_CACHE and pc.CACHE == RECORD_CACHE
    assert npl.MAXTOK == MAXTOK and npl.TEMPERATURE is None and npl.JUDGES["grok"] == JUDGE_MODEL and npl.REFERENCE == REFERENCE
    R = pc.load_record()
    pool, P, K, route, anchor_of, rubrics, refs = npl.setup()
    R.update(pool=pool, P=P, K=K, route=route, anchor_of=anchor_of, rubrics=rubrics, refs=refs)
    R["frontier"] = pc.frontier_band_of_record()
    assert len(R["kt"]) == 14, "key tiers: %d, the record says 14" % len(R["kt"])
    assert EXCLUDED not in R["models"]
    # the x20 board's names for the step opponents, asserted against placement_ceiling_bands.csv
    import csv
    recorded = {(r["newcomer"], r["incumbent"], int(r["tier"])) for r in csv.DictReader(open(BANDS_OF_RECORD, newline="", encoding="utf-8"))}
    for new, opp, t in STEPS:
        assert (new, opp, t) in recorded, "step %s vs %s (t%d) is not a band incumbent row of %s" % (new, opp, t, rel(BANDS_OF_RECORD))
        assert R["tier_of"][opp] + 1 == t and opp in R["models"], (opp, R["tier_of"].get(opp))
    return R


def used_questions(new):
    con = sqlite3.connect("file:%s?mode=ro" % RECORD_CACHE.replace("\\", "/"), uri=True)
    used = {q for (q,) in con.execute("SELECT qid FROM schedule WHERE newcomer=?", (new,))}
    con.close(); return used


def shipped_disagree(pa, pb):
    """MatchFilter.kt AnswerDisagreementFilter.verdict == DISAGREE: both non-blank after trim, different case-insensitively."""
    a = (pa or "").strip(); b = (pb or "").strip()
    return bool(a) and bool(b) and a.upper() != b.upper()


def eligible(new, opp, R, evals_pred):
    """(ordered candidate list after the recorded shuffle, n_eligible, n_used_excluded, n_record_rule) for one step."""
    pool, route, refs = R["pool"], R["route"], R["refs"]
    used = used_questions(new)
    Pn, Po = evals_pred[new], evals_pred[opp]
    cand = [q for q in sorted(pool) if q in Pn and q in Po and shipped_disagree(Pn[q], Po[q]) and q in route and q in refs]
    n_record = sum(1 for q in cand if (Pn[q] or "").strip().upper()[:1] != (Po[q] or "").strip().upper()[:1])
    kept = [q for q in cand if q not in used]
    random.Random("%d:%s:%s" % (SEED, new, opp)).shuffle(kept)          # newcomer_placement.candidates' RNG, verbatim
    return kept, len(cand), len(cand) - len(kept), n_record


def preds_and_traces(R, models):
    """qid -> pred per model over the pool, and the trace presence, from eval_results (mode=ro)."""
    import rejudge_grok as rj
    con = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    P = {m: {} for m in models}
    for q, m, pred, mo in con.execute("SELECT question_id, model_name, pred, model_output FROM eval_results"):
        if m in P and q in R["pool"] and mo:
            P[m][q] = pred
    con.close(); return P


def schedule_of_record(R):
    """The fixed step table: [(mid, newcomer, step_index, opponent, tier, qid, anchor)], counts, and the question-id hash."""
    models = {n for n, _, _ in STEPS} | {o for _, o, _ in STEPS}
    evals_pred = preds_and_traces(R, models)
    rows = []; info = []
    for si, (new, opp, t) in enumerate(STEPS):
        kept, n_el, n_used, n_record = eligible(new, opp, R, evals_pred)
        take = kept[:PER_STEP]
        for i, q in enumerate(take):
            rows.append((MID_BASE + si * 100_000 + i, new, si, opp, t, q, R["anchor_of"](R["route"][q])))
        info.append(dict(new=new, opp=opp, tier=t, n_eligible=n_el, n_used_excluded=n_used, n_record_rule=n_record, n_after=len(kept), n_take=len(take),
                         anchors_take=Counter(R["anchor_of"](R["route"][q]) for q in take), anchors_all=Counter(R["anchor_of"](R["route"][q]) for q in kept),
                         key_decidable=sum(1 for q in take if R["K"][q].get(new, 0) != R["K"][q].get(opp, 0))))
    canon = "\n".join("%s:%s:%d:%d" % (r[1], r[3], r[4], r[5]) for r in rows)
    return rows, info, hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def step_table_json():
    return json.dumps([[n, o, t] for n, o, t in STEPS])


# ---------------------------------------------------------------- the C0 gate (recorded certificates replayed)

def replay_c0(R):
    """placement_ceiling.certificates on the recorded cache under PRIMARY, asserted against RECORDED_CERTS and RECORDED_BANDS."""
    import placement_ceiling as pc
    out = {}
    for new in NEWCOMERS:
        P = R["place"][new]
        assert P["n_sched"] == 400, "%s: %d scheduled in the recorded cache" % (new, P["n_sched"])
        per = {}
        for conv in ("PRIMARY", "A", "B"):
            certs, statuses, lo_t, hi_t, width = pc.certificates(new, P["steps"], R["tier_of"], len(R["kt"]), conv)
            per[conv] = (certs, statuses, lo_t, hi_t, width)
        certs, statuses, lo_t, hi_t, width = per["PRIMARY"]
        got = [(c["anchor"], round(c["share"], 3), c["status"]) for c in certs]
        assert got == RECORDED_CERTS[new], "C0 GATE FAILED for %s: replayed %s, recorded %s" % (new, got, RECORDED_CERTS[new])
        pc.assert_recorded(new, lo_t, hi_t, R["tier_of"][new])
        out[new] = per
    return out


# ---------------------------------------------------------------- the re-read (pure; the selftest plants into it)

def certify_new(vals_by_step, conv, draws, rng):
    """vals_by_step: [(opp, {qid: value|None})] in step order -> [dict(anchor, n, share, n_up, n_dn, sd, status, status95)]."""
    import placement_ceiling as pc
    out = []
    for opp, vals in vals_by_step:
        items = pc.convention_items(vals, conv)
        if not items:
            out.append(dict(anchor=opp, n=0, share=None, n_up=0, n_dn=0, sd=None, status="unseparated", status95="unseparated")); continue
        share, n, n_up, n_dn, sd, st = pc.certify_replay(items, draws, rng)
        out.append(dict(anchor=opp, n=n, share=share, n_up=n_up, n_dn=n_dn, sd=sd, status=st, status95=pc.status_from_counts(n_up, n_dn, draws, 0.95)))
    return out


def re_read(new, kt, tier_of, acc, frontier, old_statuses, new_statuses, band_lo, band_hi, peer):
    """The band after the steps. Returns a dict: inclusive (lo, hi, width|None, own_contained), band-of-record tiers with their
    class, per-member state, bounded tiers, exclusive tiers / width, component counts, the C1 / C2 / C3 objects."""
    import placement_ceiling as pc
    statuses = dict(old_statuses); statuses.update(new_statuses)
    judged = set(statuses)
    n_tiers = len(kt)
    lo_t, hi_t, width = pc.tier_interval(statuses, tier_of, n_tiers)
    own = tier_of[new]
    inclusive = dict(lo=lo_t, hi=hi_t, width=width, own_contained=(width is not None and lo_t <= own <= hi_t))
    band, comp, sub, note, tier_comp = pc.decompose(new, kt, tier_of, acc, frontier, statuses, judged, band_lo, band_hi, peer)
    tiers = {}
    for t in range(band_lo, band_hi + 1):
        members = [m for m in kt[t] if m != new]
        c = tier_comp[t]
        cert = [(m, statuses[m]) for m in members if m in statuses and statuses[m] in ("above", "below")]
        uns = [m for m in members if m in statuses and statuses[m] == "unseparated"]
        newcomer_above = [m for m, s in cert if s == "below"]      # BOUNDED: the newcomer certified above a member (C1's definition)
        beat_newcomer = [m for m, s in cert if s == "above"]       # a member certified ABOVE the newcomer: joins the band (C1's "or" clause)
        if c == "iii":
            if beat_newcomer: cls, why = "ii*", "KEY-CONTRADICTED: %s certified ABOVE the newcomer; joins the band (registration C1), never dropped" % ", ".join(beat_newcomer)
            elif newcomer_above: cls, why = "iii-c", "BOUNDED by %s (newcomer certified above)" % ", ".join(newcomer_above)
            elif uns: cls, why = "iii-a", "judged, UNSEPARATED: %s" % ", ".join(uns)
            else: cls, why = "iii-b", "never judged"
        else:
            cls, why = c, ("bounded by %s" % ", ".join("%s (%s)" % (m, s) for m, s in cert)) if cert else "no certificate"
        tiers[t] = dict(comp=c, cls=cls, why=why, members=[(m, sub[m], statuses.get(m, "never judged")) for m in members],
                        bounded=bool(newcomer_above) and not beat_newcomer, key_contradicted_members=beat_newcomer if c == "iii" else [])
    exclusive = [t for t in range(band_lo, band_hi + 1) if not (tiers[t]["comp"] == "iii" and tiers[t]["bounded"])]
    counts = Counter(tiers[t]["cls"] for t in exclusive)
    comp_counts = Counter(tiers[t]["comp"] for t in exclusive)
    return dict(statuses=statuses, inclusive=inclusive, band=(band_lo, band_hi), tiers=tiers, exclusive=exclusive,
                exclusive_width=len(exclusive), counts=counts, comp_counts=comp_counts,
                iii_total=counts["iii-a"] + counts["iii-b"] + counts["iii-c"],
                i_ii_tiers=[t for t in exclusive if tiers[t]["comp"] in ("i", "ii") or tiers[t]["cls"] == "ii*"])


# ---------------------------------------------------------------- cache

def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, newcomer TEXT, step INTEGER, opponent TEXT, tier INTEGER, qid INTEGER, anchor TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, "
                "finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))")
    con.commit(); return con


def open_cache_ro():
    if not os.path.exists(CACHE): return None
    return sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)


def pin_meta(con, qid_hash, n_matches):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    meta = {"test": "PLACEMENT-STEPS", "pool_id": POOL_ID, "judge_model": JUDGE_MODEL, "provider": "azure", "protocol": PROTOCOL,
            "reference": REFERENCE, "max_tokens": str(MAXTOK), "temperature": "omitted" if TEMPERATURE is None else repr(TEMPERATURE),
            "seed": str(SEED), "per_step": str(PER_STEP), "conf": str(CONF), "steps": step_table_json(), "qid_hash": qid_hash,
            "n_matches": str(n_matches), "script_sha256_16": SCRIPT_SHA, "started": now}
    stored = dict(con.execute("SELECT key, value FROM meta"))
    if stored:
        con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((stored.get("resumed", "") + ";" + now).strip(";"),))
        for k in ("pool_id", "judge_model", "protocol", "reference", "max_tokens", "temperature", "seed", "per_step", "conf", "steps", "qid_hash", "n_matches"):
            if stored.get(k) != meta[k]:
                raise SystemExit("[META] REFUSED: cache %s was pinned with %s=%s; this launch has %s (a changed cap or protocol is a new session: move the cache aside)"
                                 % (rel(CACHE), k, stored.get(k), meta[k]))
        if stored.get("script_sha256_16") != SCRIPT_SHA:
            print("  NOTE: cache first produced by script sha %s; this script is %s (resume recorded)" % (stored.get("script_sha256_16"), SCRIPT_SHA))
    for k, v in meta.items(): con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", (k, v))
    con.commit()


def guard_line(con, mids):
    """(n_matches_both_orders, n_unusable, rate, finish counts) over the cached matches of the given schedule."""
    import newcomer_placement as npl
    V = defaultdict(dict)
    for i in range(0, len(mids), 500):
        chunk = mids[i:i + 500]
        for m, arm, inv, fin in con.execute("SELECT mid, arm, invalid, COALESCE(finish,'(none)') FROM verdicts WHERE mid IN (%s)" % ",".join("?" * len(chunk)), chunk):
            V[m][arm] = (inv, fin)
    both = [m for m in mids if "fwd" in V.get(m, {}) and "rev" in V.get(m, {})]
    unus = sum(1 for m in both if V[m]["fwd"][0] or V[m]["rev"][0])
    fins = Counter(f for m in V for (_, f) in V[m].values())
    return len(both), unus, (unus / len(both) if both else 0.0), dict(fins)


# ---------------------------------------------------------------- dry run

def dry_run():
    import newcomer_placement as npl
    import rejudge_reasoning as rr
    R = load()
    print("  %d pool questions | reference CACHED_SOLVE %s: %d covered | board of record x12 %d + x20 %d = %d verdicts, %d models, %s absent"
          % (len(R["pool"]), REFERENCE, sum(1 for q in R["pool"] if q in R["refs"]), R["n12"], R["n20"], len(R["rows"]), len(R["models"]), EXCLUDED))
    print("  recorded cache %s (mode=ro): schedule %d | verdicts %d | finish %s | meta cap %s temperature %s"
          % (rel(RECORD_CACHE), R["counts"]["schedule"], R["counts"]["verdicts"], R["counts"]["finish"], R["meta"].get("max_tokens"), R["meta"].get("temperature")))
    print("  key tiers at %.3f over the %d x20-judged questions: %d" % (KEY_GAP, len(R["qs_judged"]), len(R["kt"])))
    for i, t in enumerate(R["kt"]): print("    tier %2d: %s" % (i + 1, ", ".join("%s %.3f" % (m, R["acc"][m]) for m in t)))
    # C0
    c0 = replay_c0(R)
    print("C0 GATE: the recorded certificates replayed (PRIMARY) and asserted equal to PLACEMENT-CEILING's:")
    for new in NEWCOMERS:
        certs, statuses, lo_t, hi_t, width = c0[new]["PRIMARY"]
        for c in certs:
            print("    %-28s vs %-28s share %.3f (draws above %4d / below %4d) -> %s" % (new, c["anchor"], c["share"], c["n_up"], c["n_dn"], c["status"]))
        print("    %-28s band of record (inclusive) tiers %d..%d = %d, own tier %d: ASSERTED = recorded %s" % (new, lo_t + 1, hi_t + 1, width, R["tier_of"][new] + 1, RECORDED_BANDS[new]))
        peer = [n for n in NEWCOMERS if n != new][0]
        rr0 = re_read(new, R["kt"], R["tier_of"], R["acc"], R["frontier"], statuses, {}, lo_t, hi_t, peer)
        print("    %-28s before the steps: exclusive tiers %s (width %d) | classes %s" % (new, [t + 1 for t in rr0["exclusive"]], rr0["exclusive_width"], dict(rr0["counts"])))
    # the schedule
    rows, info, qh = schedule_of_record(R)
    print("STEP SCHEDULE (fixed at this dry-run; seed %d; the recorded shuffle; question-id hash %s):" % (SEED, qh))
    for si, inf in enumerate(info):
        flag = "" if inf["n_take"] == PER_STEP else "   <- SHORT: the count of record is %d" % inf["n_take"]
        print("  step %d %-28s vs %-28s (t%d): eligible %4d (shipped DISAGREE; record rule %4d) - used in the newcomer's recorded anchors %3d = %4d -> %3d matches | key-decidable %3d%s"
              % (si + 1, inf["new"], inf["opp"], inf["tier"], inf["n_eligible"], inf["n_record_rule"], inf["n_used_excluded"], inf["n_after"], inf["n_take"], inf["key_decidable"], flag))
        anchors = sorted(set(inf["anchors_all"]) | set(inf["anchors_take"]))
        print("         anchors (drawn / eligible): " + ", ".join("%s %d/%d" % (a, inf["anchors_take"][a], inf["anchors_all"][a]) for a in anchors))
    # payloads
    npl.assert_body_fidelity()
    import rejudge_grok as rj
    qids = sorted({r[5] for r in rows}); models = {n for n, _, _ in STEPS} | {o for _, o, _ in STEPS}
    evals = rj.load_eval_rows(qids, models)
    n_pay = 0; first = None
    for mid, new, si, opp, t, q, anc in rows:
        pl = npl.payload(new, opp, q, evals, R["route"], R["anchor_of"], R["rubrics"], R["refs"])
        assert pl is not None, "payload could not be built for mid %d (%s vs %s q %d)" % (mid, new, opp, q)
        n_pay += 2
        if first is None: first = (new, opp, q, pl)
    n_matches = len(rows)
    body = npl.request_body(first[3][0], first[3][1])
    print("BILL: %d matches x 2 orders = %d calls would be POSTED by --run (the 12-match pilot = 24 calls inside the count); %d payloads assembled; 0 reference solves; 0 posted"
          % (n_matches, 2 * n_matches, n_pay))
    print("protocol: %s" % PROTOCOL)
    print("judge: %s on azure | max_tokens %d | temperature %s (D2) | body keys %s | first payload body model=%s max_tokens=%d"
          % (JUDGE_MODEL, MAXTOK, "omitted" if TEMPERATURE is None else TEMPERATURE, tuple(body.keys()), body["model"], body["max_tokens"]))
    print("cache: %s%s (the dry run opens no cache) | outcome %s | pilot %s" % (rel(CACHE), " (EXISTS)" if os.path.exists(CACHE) else " (new)", rel(OUT), rel(OUT_PILOT)))
    ok, s = gate_state()
    st = armb_alarm_state()
    print("READY gate (not enforced by --dry-run): %s -> %s | ARM-B gate: %s reads %r -> %s" % (s, "OPEN" if ok else "CLOSED (nothing may be posted)", rel(ARMB_OUT), st, "OPEN" if st == ARMB_OK else "CLOSED (ARM-B-VINTAGE (b): ARM-B runs first)"))
    print("guard: --run refuses to post once > 5%% of the cached matches are unusable (either order unparsed / non-terminated / content_filter); --analyze refuses the same and any schedule short of %d" % n_matches)
    print("script sha256[:16] %s" % SCRIPT_SHA)
    new, opp, q, (system, ufwd, urev) = first
    print("\n===== FIRST PAYLOAD: %s vs %s, question %d, order fwd (newcomer = Model A) =====" % (new, opp, q))
    print("----- system -----"); print(system)
    print("----- user -----"); print(ufwd)
    print("===== END FIRST PAYLOAD =====")
    print("dry run OK: 0 calls posted, no cache created")


# ---------------------------------------------------------------- live run

def run(pilot, workers):
    import newcomer_placement as npl
    import rejudge_reasoning as rr
    import rejudge_grok as rj
    go_gate("--pilot %d" % pilot if pilot else "--run")
    R = load()
    replay_c0(R)
    rows, info, qh = schedule_of_record(R)
    npl.assert_body_fidelity()
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE_MODEL; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE; rr.load_env()
    npl.MAXTOK = MAXTOK; npl.TEMPERATURE = TEMPERATURE; npl.JUDGE = "grok"
    con = open_cache(); pin_meta(con, qh, len(rows))
    if OVERRIDE_GUARD: con.execute("INSERT OR REPLACE INTO meta VALUES ('override_guard', ?)", (time.strftime("%Y-%m-%d %H:%M:%S"),)); con.commit()
    have = con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
    if have == 0:
        con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?,?)", rows); con.commit()
    else:
        cached = con.execute("SELECT mid, newcomer, step, opponent, tier, qid, anchor FROM schedule ORDER BY mid").fetchall()
        assert [tuple(r) for r in cached] == [tuple(r) for r in rows], "[SCHEDULE] REFUSED: the cached schedule differs from the recomputed one"
    mids = [r[0] for r in rows]
    n_both, unus, rate, fins = guard_line(con, mids)
    print("PLACEMENT-STEPS: judge %s | max_tokens %d | temperature %s | reference %s | %d matches fixed (hash %s) | cached with both orders %d | workers %d | cache %s"
          % (JUDGE_MODEL, MAXTOK, "omitted" if TEMPERATURE is None else TEMPERATURE, REFERENCE, len(rows), qh, n_both, workers, rel(CACHE)), flush=True)
    if n_both and rate > 0.05 and not OVERRIDE_GUARD:
        raise SystemExit("  GUARD: %d of %d cached matches (%.1f%%) unusable; finish_reason %s; nothing more is posted (--override-guard posts anyway and is recorded)" % (unus, n_both, 100 * rate, fins))
    target = mids[:pilot] if pilot else mids
    have_rows = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    todo = [(m, a) for m in target for a in ("fwd", "rev") if (m, a) not in have_rows]
    by_mid = {r[0]: r for r in rows}
    qids = sorted({by_mid[m][5] for m, _ in todo}); models = {n for n, _, _ in STEPS} | {o for _, o, _ in STEPS}
    evals = rj.load_eval_rows(qids, models) if qids else {}
    jobs = []
    for m, a in todo:
        _, new, si, opp, t, q, anc = by_mid[m]
        system, ufwd, urev = npl.payload(new, opp, q, evals, R["route"], R["anchor_of"], R["rubrics"], R["refs"])
        if a == "fwd": jobs.append((m, "fwd", system, ufwd, {"Model A": new, "Model B": opp, "TIE": "TIE"}))
        else: jobs.append((m, "rev", system, urev, {"Model A": opp, "Model B": new, "TIE": "TIE"}))
    print("  %s: %d matches targeted, %d calls to post" % ("PILOT" if pilot else "RUN", len(target), len(jobs)), flush=True)
    if jobs: npl.judge_jobs(con, jobs, workers, "steps")
    n_both, unus, rate, fins = guard_line(con, target)
    print("  GUARD LINE: %d of %d matches (%.1f%%) unusable on the deciding subset (both orders cached %d); finish_reason %s -> %s"
          % (unus, n_both, 100 * rate, n_both, fins, "OK (<= 5%)" if rate <= 0.05 else "ABOVE 5%: the run refuses to continue; nothing is an outcome"), flush=True)
    import newcomer_placement as _n
    for si, (new, opp, t) in enumerate(STEPS):
        sm = [r[0] for r in rows if r[2] == si]
        dv = _n.dual_verdicts(con, sm, new, opp)
        w, l, ti, u, p = _n.tally(dv, new, opp)
        if w + l + ti + u: print("  step %d %s vs %s: %d : %d (ties %d, unusable %d, pending %d)" % (si + 1, new, opp, w, l, ti, u, p), flush=True)
    print("done. --analyze for the readout (refuses a partial cache).", flush=True)


# ---------------------------------------------------------------- analysis

def analyze(draws):
    import placement_ceiling as pc
    import newcomer_placement as npl
    import judge_free_tests as jf
    R = load()
    con = open_cache_ro()
    if con is None: raise SystemExit("no cache at %s: nothing judged, nothing written" % rel(CACHE))
    meta = dict(con.execute("SELECT key, value FROM meta"))
    rows, info, qh = schedule_of_record(R)
    cached = con.execute("SELECT mid, newcomer, step, opponent, tier, qid, anchor FROM schedule ORDER BY mid").fetchall()
    n_fixed = len(rows)
    L = ["=== PLACEMENT-STEPS: one further step per separable tier (400 matches = 800 calls; registration 20cb7b6; Amendment 6) ===",
         "  pool %s | judge %s | max_tokens %s | temperature %s | reference %s | protocol: %s" % (POOL_ID, meta.get("judge_model"), meta.get("max_tokens"), meta.get("temperature"), meta.get("reference"), meta.get("protocol")),
         "  cache %s (mode=ro) | producing script sha %s | this script %s%s | started %s | resumed %s | override_guard %s"
         % (rel(CACHE), meta.get("script_sha256_16"), SCRIPT_SHA, "" if meta.get("script_sha256_16") == SCRIPT_SHA else " (DIFFERS)", meta.get("started"), meta.get("resumed", "-"), meta.get("override_guard", "no")),
         "  board of record: x12 %d + x20 %d = %d verdicts, %d models, %s absent; key tiers %d at %.3f over the %d x20-judged questions; frontier band %s"
         % (R["n12"], R["n20"], len(R["rows"]), len(R["models"]), EXCLUDED, len(R["kt"]), KEY_GAP, len(R["qs_judged"]), ", ".join(R["frontier"]))]
    for i, t in enumerate(R["kt"]): L.append("    tier %2d: %s" % (i + 1, ", ".join("%s %.3f" % (m, R["acc"][m]) for m in t)))
    complete = True; problems = []
    if meta.get("qid_hash") != qh or [tuple(r) for r in cached] != [tuple(r) for r in rows]:
        problems.append("the cached schedule (%d rows, hash %s) is not the fixed schedule (%d rows, hash %s)" % (len(cached), meta.get("qid_hash"), n_fixed, qh))
    mids = [r[0] for r in rows]
    n_both, unus, rate, fins = guard_line(con, mids)
    n_rows = con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
    L.append("  cache rows: verdicts %d of %d | matches with both orders %d of %d | unusable %d (%.1f%%) | finish_reason %s" % (n_rows, 2 * n_fixed, n_both, n_fixed, unus, 100 * rate, fins))
    if n_both < n_fixed: problems.append("PARTIAL: %d of %d matches judged in both orders" % (n_both, n_fixed))
    if rate > 0.05: problems.append("VERDICT REFUSED: %.1f%% unusable on the deciding subset (> 5%%)" % (100 * rate))
    if problems:
        complete = False
        for p in problems: L.append("  " + p)
    c0 = replay_c0(R)
    L.append("C0 GATE: the four recorded certificates per newcomer replayed and asserted equal to PLACEMENT-CEILING's (sonnet 0.910 below / 0.505 / 0.510 unseparated / 0.225 above; gpt-4o-mini 0.710 below / 0.595 below / 0.170 above / 0.360 above); bands 7 / 3: HELD")
    verdict = {}; bands_csv = []
    tie_n = tie_d = 0; unus_total = 0
    for new in NEWCOMERS:
        peer = [n for n in NEWCOMERS if n != new][0]
        L.append(""); L.append("--- %s (own key tier %d, key %.3f) ---" % (new, R["tier_of"][new] + 1, R["acc"][new]))
        band_lo, band_hi = RECORDED_BANDS[new][0] - 1, RECORDED_BANDS[new][1] - 1
        my_steps = [(si, opp, t) for si, (n, opp, t) in enumerate(STEPS) if n == new]
        vals_by_step = []
        for si, opp, t in my_steps:
            sm = [r[0] for r in rows if r[2] == si]
            dv = npl.dual_verdicts(con, sm, new, opp)
            w, l, ti, u, p = npl.tally(dv, new, opp)
            vals = {}
            for r in rows:
                if r[2] != si: continue
                v = dv[r[0]]
                if v == "PENDING": continue
                vals[r[5]] = None if v is None else (1.0 if v == new else (0.5 if v == "TIE" else 0.0))
            tie_n += ti; tie_d += (w + l + ti); unus_total += u
            vals_by_step.append((opp, vals))
            L.append("  step vs %-28s (t%d): %3d : %3d (ties %2d, unusable %2d, pending %2d) on %d fixed matches" % (opp, t, w, l, ti, u, p, len(sm)))
        per = {}
        for conv in ("PRIMARY", "A", "B"):
            certs = certify_new(vals_by_step, conv, draws, random.Random(SEED))
            per[conv] = certs
            L.append("  [%s] new anchors, win share with %s, question-clustered bootstrap B=%d, seed %d:" % (conv, {"PRIMARY": "ties 1/2, unusable excluded", "A": "ties 1/2, unusable 1/2", "B": "committed verdicts only"}[conv], draws, SEED))
            for c in certs:
                if c["n"] == 0: L.append("    vs %-28s: no usable match" % c["anchor"]); continue
                opp_draws = (draws - c["n_up"] if c["n_up"] >= c["n_dn"] else draws - c["n_dn"]) if c["status"] != "unseparated" else "n/a"
                L.append("    vs %-28s (t%d, key %.3f): n %3d, share %.3f, sd %.3f | draws above 0.5: %4d, below: %4d, at: %d | %s at %.3f (opposite draws %s); %s at 0.95"
                         % (c["anchor"], R["tier_of"][c["anchor"]] + 1, R["acc"][c["anchor"]], c["n"], c["share"], c["sd"], c["n_up"], c["n_dn"], draws - c["n_up"] - c["n_dn"],
                            {"above": "anchor ABOVE newcomer", "below": "newcomer ABOVE anchor", "unseparated": "UNSEPARATED"}[c["status"]], CONF, opp_draws, c["status95"]))
        for conv in ("PRIMARY", "A", "B"):
            old = c0[new][conv][1]
            newst = {c["anchor"]: c["status"] for c in per[conv]}
            rr_ = re_read(new, R["kt"], R["tier_of"], R["acc"], R["frontier"], old, newst, band_lo, band_hi, peer)
            inc = rr_["inclusive"]
            L.append("  [%s] band re-read over %d anchors: INCLUSIVE (tier_interval over all certificates) %s | EXCLUSIVE (band of record %d..%d minus bounded (iii) tiers) tiers %s width %d | classes %s | (i)+(ii) tiers %s"
                     % (conv, len(rr_["statuses"]), "KEY-CONTRADICTED" if inc["width"] is None else "tiers %d..%d = %d (own tier %s)" % (inc["lo"] + 1, inc["hi"] + 1, inc["width"], "contained" if inc["own_contained"] else "NOT contained"),
                        band_lo + 1, band_hi + 1, [t + 1 for t in rr_["exclusive"]], rr_["exclusive_width"], dict(rr_["counts"]), [t + 1 for t in rr_["i_ii_tiers"]]))
            for t in range(band_lo, band_hi + 1):
                T = rr_["tiers"][t]
                L.append("    tier %2d -> (%s) %s%s" % (t + 1, T["cls"], T["why"], "" if not T["key_contradicted_members"] else "   <- a key-separable incumbent certified ABOVE the newcomer: %s (printed; joins the band as ii*, never dropped)" % T["key_contradicted_members"]))
                for m, s, st in T["members"]:
                    L.append("        %-30s key %.3f  (%s) %s%s" % (m, R["acc"][m], s, st, "  (peer newcomer, D5: never an anchor)" if m == peer else ""))
                    if conv == "PRIMARY":
                        bands_csv.append(dict(newcomer=new, tier=t + 1, incumbent=m, key=round(R["acc"][m], 4), member_sub=s, judged_status=st, tier_class=T["cls"],
                                              in_exclusive=int(t in rr_["exclusive"]), in_inclusive=int(inc["width"] is not None and inc["lo"] <= t <= inc["hi"])))
            if conv == "PRIMARY": verdict[new] = dict(rr=rr_, certs=per["PRIMARY"])
        # power column
        L.append("  power column (PRIMARY; unseparated new anchors; SE_n = sd x sqrt(n / n'); certify at %.3f if the share held):" % CONF)
        anyu = False
        for c in per["PRIMARY"]:
            if c["status"] == "unseparated" and c["n"]:
                anyu = True; npairs = pc.power_pairs(c["share"], c["sd"], c["n"])
                L.append("    vs %-28s share %.3f sd %.3f n %d -> %s question-pairs" % (c["anchor"], c["share"], c["sd"], c["n"], "never (share = 0.5)" if npairs is None else npairs))
        if not anyu: L.append("    none unseparated")
        # SECONDARY mixed fit (point theta only; the scale caveat)
        try:
            order, th_inc, inc_rows = npl.incumbent_order(R["rows"], R["models"], new)
            oldp = [(new, opp, q, (new if v == 1.0 else (opp if v == 0.0 else "TIE")), 0) for _, opp, vals in R["place"][new]["steps"] for q, v in vals.items() if v is not None]
            newp = [(new, opp, q, (new if v == 1.0 else (opp if v == 0.0 else "TIE")), 0) for opp, vals in vals_by_step for q, v in vals.items() if v is not None]
            th_old = jf.board_from(npl.votes(inc_rows + oldp), R["models"])[new]
            th_new = jf.board_from(npl.votes(inc_rows + oldp + newp), R["models"])[new]
            verdict[new]["theta"] = (th_old, th_new)
            L.append("  SECONDARY, MIXED-FIT / EXTRAPOLATED (never the verdict; ARENA-13 scale caveat): theta with the 4 recorded anchors %+.3f -> with the new edges %+.3f (delta %+.3f; %d + %d protocol edges)" % (th_old, th_new, th_new - th_old, len(oldp), len(newp)))
        except Exception as e:
            L.append("  SECONDARY MIXED-FIT not computed (%s: %s)" % (type(e).__name__, str(e)[:100]))
    # ---- criteria and predictions (PRIMARY)
    L.append(""); L.append("=== criteria (PRIMARY; A and B printed above) ===")
    S = verdict[NEWCOMERS[0]]["rr"]; G = verdict[NEWCOMERS[1]]["rr"]
    c1 = S["iii_total"] == 0
    L.append("  C1 SONNET (iii) -> 0: iii-a %d + iii-b %d + iii-c %d = %d on the exclusive reading (every tier-5/6/7 tier bounded: %s) -> %s"
             % (S["counts"]["iii-a"], S["counts"]["iii-b"], S["counts"]["iii-c"], S["iii_total"], [(t + 1, S["tiers"][t]["bounded"]) for t in range(4, 7)], "HELD" if c1 else "FAILED"))
    c2 = sorted(t + 1 for t in S["i_ii_tiers"]) == [1, 2, 3, 4] and S["exclusive_width"] == 4
    L.append("  C2 SONNET BAND = the structural floor: (i)+(ii) tiers %s (needs [1, 2, 3, 4]) and EXCLUSIVE width %d (needs 4); INCLUSIVE beside: %s -> %s"
             % ([t + 1 for t in S["i_ii_tiers"]], S["exclusive_width"], "KEY-CONTRADICTED" if S["inclusive"]["width"] is None else "%d..%d = %d" % (S["inclusive"]["lo"] + 1, S["inclusive"]["hi"] + 1, S["inclusive"]["width"]), "HELD" if c2 else "FAILED"))
    dsk = G["statuses"].get("deepseek-chat-v2_5")
    g_ok = G["counts"]["iii-b"] == 0 and G["exclusive_width"] in (2, 3) and (5 in G["exclusive"]) and (3 in G["exclusive"])
    met22 = G["inclusive"]["width"] == 2 and G["inclusive"]["own_contained"]          # (22) = "<= 2 ADJACENT tiers": read on the INCLUSIVE interval (D2)
    L.append("  C3 GPT-4O-MINI: deepseek %s; (iii-b) %d; exclusive tiers %s width %d (2 or 3; t4 and t6 present) -> %s | criterion (22) %s on the INCLUSIVE interval %s (MET iff inclusive width 2 and the own key tier 6 contained; the exclusive set {t4, t6} is not an interval; exclusive width %d beside)"
             % (dsk, G["counts"]["iii-b"], [t + 1 for t in G["exclusive"]], G["exclusive_width"], "HELD" if g_ok else "FAILED", "MET" if met22 else "NOT MET",
                "KEY-CONTRADICTED" if G["inclusive"]["width"] is None else "%d..%d = %d (own tier %s)" % (G["inclusive"]["lo"] + 1, G["inclusive"]["hi"] + 1, G["inclusive"]["width"], "contained" if G["inclusive"]["own_contained"] else "NOT contained"),
                G["exclusive_width"]))
    L.append("=== predictions (blind, labelled) ===")
    p1 = c1 and S["exclusive_width"] == 4 and S["inclusive"]["width"] == 5
    L.append("  P1 (plan) sonnet (iii) 3 -> 0; band 4 [4, 5] (exclusive 4, inclusive 5): (iii) %d, exclusive %d, inclusive %s -> %s" % (S["iii_total"], S["exclusive_width"], S["inclusive"]["width"], "HELD" if p1 else "FAILED"))
    L.append("  P2 (plan) gpt-4o-mini band 2 or 3: exclusive %d -> %s" % (G["exclusive_width"], "HELD" if G["exclusive_width"] in (2, 3) else "FAILED"))
    sc = {c["anchor"]: c for c in verdict[NEWCOMERS[0]]["certs"]}
    p3r = {"deepseek-chat-v2_5": (0.60, 0.75), "claude-3-5-haiku-20241022": (0.65, 0.80), "Qwen1.5-110B": (0.75, 0.90)}
    p3 = all(sc[a]["share"] is not None and lo <= sc[a]["share"] <= hi for a, (lo, hi) in p3r.items())
    L.append("  P3 sonnet shares vs deepseek [0.60, 0.75], haiku [0.65, 0.80], Qwen1.5-110B [0.75, 0.90]: %s -> %s" % (", ".join("%s %.3f" % (a, sc[a]["share"]) if sc[a]["share"] is not None else "%s n/a" % a for a in p3r), "HELD" if p3 else "FAILED"))
    p4 = all(sc[a]["status"] != "unseparated" and max(sc[a]["n_up"], sc[a]["n_dn"]) >= 1900 for a in p3r)
    L.append("  P4 each sonnet step certifies at 0.975 with >= 1,900 of %d draws on one side: %s -> %s" % (draws, ", ".join("%s %d/%d %s" % (a, sc[a]["n_up"], sc[a]["n_dn"], sc[a]["status"]) for a in p3r), "HELD" if p4 else "FAILED"))
    gc = verdict[NEWCOMERS[1]]["certs"][0]
    p5 = gc["share"] is not None and 0.45 <= gc["share"] <= 0.60
    L.append("  P5 gpt-4o-mini vs deepseek share in [0.45, 0.60]: %s; certificate %s (P(certified) recorded 0.5, no direction) -> %s" % ("%.3f" % gc["share"] if gc["share"] is not None else "n/a", gc["status"], "HELD" if p5 else "FAILED"))
    tr = tie_n / tie_d if tie_d else float("nan")
    L.append("  P6 tie rate under PRIMARY on the %d new matches in [0.20, 0.30]: %.3f (%d ties of %d usable) -> %s" % (n_fixed, tr, tie_n, tie_d, "HELD" if 0.20 <= tr <= 0.30 else "FAILED"))
    L.append("  P7 unusable rows <= 2 of %d: %d -> %s" % (n_fixed, unus_total, "HELD" if unus_total <= 2 else "FAILED"))
    th = verdict[NEWCOMERS[0]].get("theta")
    L.append("  P8 sonnet MIXED-FIT theta moves by < 0.10: %s -> %s" % ("%+.3f -> %+.3f (|delta| %.3f)" % (th[0], th[1], abs(th[1] - th[0])) if th else "not computed", ("HELD" if abs(th[1] - th[0]) < 0.10 else "FAILED") if th else "UNDETERMINED"))
    L.append("=== verdict rule ===")
    if problems:
        L.append("  NO VERDICT (refused: %s)" % "; ".join(problems))                     # D7: a refused / partial cache never prints the verdict-rule sentence
    elif c1 and c2:
        L.append("  C1 AND C2 HELD -> \"placement cost is 400 + 100 per separable tier per newcomer; the residual is the structural floor (i) + (ii); criterion (22) is reachable for mid-board newcomers only\"")
    elif not c1:
        L.append("  C1 FAILED -> FALSIFIER F1: at least one tier-5/6/7 incumbent remains UNSEPARATED (or unbounded) after 100 filtered matches: the unseparated separable tier is JUDGE-side; NEWCOMER-PLACEMENT-LIVE's \"not judge error\" and PLACEMENT-CEILING's steps reading take brackets; \"400 + 100 per separable tier does not bound the band for a frontier-adjacent newcomer\"")
    else:
        L.append("  C1 HELD, C2 FAILED -> the (iii) tiers are bounded but the residual is not [t1..t4] (or a key-contradicted ii* tier widened it): printed above; no verdict-rule sentence applies; registrar reads the components")
    L.append("  not overturned: the 4-tier structural floor, the two placements' directions, the contained key tiers, FILTER-BOARD, the frontier order (unread)")
    txt = "\n".join(L); print(txt)
    if complete:
        open(OUT, "w", encoding="utf-8").write(txt + "\n")
        import csv
        with open(OUT_BANDS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(bands_csv[0].keys())); w.writeheader(); w.writerows(bands_csv)
        print("written: %s, %s (%d rows)" % (rel(OUT), rel(OUT_BANDS), len(bands_csv)))
    else:
        open(OUT_PILOT, "w", encoding="utf-8").write(txt + "\n")
        print("PARTIAL / PILOT readout (%s): written to %s; the outcome file of record is untouched" % ("; ".join(problems), rel(OUT_PILOT)))


# ---------------------------------------------------------------- selftest (synthetic; no DB, no env)

def selftest():
    import placement_ceiling as pc
    acc = {"gemini-3.1-pro_5-shots": 0.912, "arx_0314": 0.8329, "iask_pro": 0.8165, "arx_3": 0.7844, "claude-3-5-sonnet-20241022": 0.782,
           "gpt-4o-2024-08-06": 0.750, "deepseek-chat-v2_5": 0.651, "gpt-4o-mini": 0.631, "claude-3-5-haiku-20241022": 0.629,
           "Meta-Llama-3_1-70B-Instruct": 0.628, "Qwen1.5-110B": 0.492, "Qwen1.5-72B-Chat": 0.476, "Mixtral-8x7B-Instruct-v0.1": 0.417,
           "c4ai-command-r-v01": 0.370, "Meta-Llama-3_1-8B": 0.369, "Qwen1.5-14B-Chat": 0.351, "gemma-7b": 0.313, "Yi-6b-Chat": 0.274,
           "Llama-2-13b-hf": 0.239, "Llama-2-7b-hf": 0.184}
    models = sorted(acc); kt = pc.key_tiers(acc, models); tier_of = {m: i for i, t in enumerate(kt) for m in t}
    assert len(kt) == 14 and tier_of["claude-3-5-sonnet-20241022"] == 2 and tier_of["gpt-4o-mini"] == 5, kt
    frontier = ("arx_0314", "iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06")
    S_old = {a: s for a, _, s in RECORDED_CERTS["claude-3-5-sonnet-20241022"]}
    G_old = {a: s for a, _, s in RECORDED_CERTS["gpt-4o-mini"]}
    # before the steps: the record (inclusive 1..7 / 4..6; exclusive 6 / 3)
    r0 = re_read("claude-3-5-sonnet-20241022", kt, tier_of, acc, frontier, S_old, {}, 0, 6, "gpt-4o-mini")
    assert (r0["inclusive"]["lo"], r0["inclusive"]["hi"], r0["inclusive"]["width"]) == (0, 6, 7) and r0["exclusive_width"] == 6, r0["inclusive"]
    assert r0["counts"] == {"ii": 3, "i": 1, "iii-b": 2}, r0["counts"]
    g0 = re_read("gpt-4o-mini", kt, tier_of, acc, frontier, G_old, {}, 3, 5, "claude-3-5-sonnet-20241022")
    assert (g0["inclusive"]["lo"], g0["inclusive"]["hi"]) == (3, 5) and g0["exclusive_width"] == 3 and g0["counts"] == {"ii": 1, "iii-b": 1, "i": 1}, g0["counts"]
    # planted verdicts through the certificate code: sonnet beats all three, gpt-4o-mini vs deepseek a coin flip
    rng = random.Random(7)
    def plant(p, n=100): return {q: (1.0 if rng.random() < p else 0.0) for q in range(1000, 1000 + n)}
    s_steps = [("deepseek-chat-v2_5", plant(0.70)), ("claude-3-5-haiku-20241022", plant(0.75)), ("Qwen1.5-110B", plant(0.85))]
    s_steps[0][1][1003] = None                              # one unusable row
    certs = certify_new(s_steps, "PRIMARY", 400, random.Random(SEED))
    assert [c["status"] for c in certs] == ["below"] * 3, certs
    r1 = re_read("claude-3-5-sonnet-20241022", kt, tier_of, acc, frontier, S_old, {c["anchor"]: c["status"] for c in certs}, 0, 6, "gpt-4o-mini")
    assert r1["iii_total"] == 0 and r1["exclusive_width"] == 4 and [t + 1 for t in r1["i_ii_tiers"]] == [1, 2, 3, 4], (r1["counts"], r1["exclusive"])
    assert (r1["inclusive"]["lo"] + 1, r1["inclusive"]["hi"] + 1, r1["inclusive"]["width"]) == (1, 5, 5), r1["inclusive"]
    assert r1["tiers"][5]["cls"] == "iii-c" and "Meta-Llama-3_1-70B-Instruct" in [m for m, _, st in r1["tiers"][5]["members"] if st == "never judged"]
    # the falsifier: haiku unseparated -> t6 iii-a, C1 fails, exclusive 5
    r2 = re_read("claude-3-5-sonnet-20241022", kt, tier_of, acc, frontier, S_old, {"deepseek-chat-v2_5": "below", "claude-3-5-haiku-20241022": "unseparated", "Qwen1.5-110B": "below"}, 0, 6, "gpt-4o-mini")
    assert r2["counts"]["iii-a"] == 1 and r2["iii_total"] == 1 and r2["exclusive_width"] == 5, r2["counts"]
    # a key-separable incumbent certified ABOVE sonnet: its tier joins the band as ii* (registration C1), is NEVER dropped (D1);
    # C1 holds (iii_total 0) but the exclusive width is 5 and the (i)+(ii) tiers are 1..5 -> C2 fails
    r3 = re_read("claude-3-5-sonnet-20241022", kt, tier_of, acc, frontier, S_old, {"deepseek-chat-v2_5": "above", "claude-3-5-haiku-20241022": "below", "Qwen1.5-110B": "below"}, 0, 6, "gpt-4o-mini")
    assert r3["tiers"][4]["key_contradicted_members"] == ["deepseek-chat-v2_5"] and r3["tiers"][4]["cls"] == "ii*" and not r3["tiers"][4]["bounded"], r3["tiers"][4]
    assert r3["iii_total"] == 0 and r3["exclusive_width"] == 5 and [t + 1 for t in r3["i_ii_tiers"]] == [1, 2, 3, 4, 5], (r3["counts"], r3["exclusive"])
    assert r3["inclusive"]["width"] is None or not r3["inclusive"]["own_contained"], r3["inclusive"]
    # gpt-4o-mini: unseparated -> width 3; newcomer certified above deepseek -> width 2 with t4 and t6 (not adjacent), inclusive 4..5 own tier NOT contained
    g1 = re_read("gpt-4o-mini", kt, tier_of, acc, frontier, G_old, {"deepseek-chat-v2_5": "unseparated"}, 3, 5, "claude-3-5-sonnet-20241022")
    assert g1["exclusive_width"] == 3 and g1["counts"]["iii-a"] == 1 and g1["inclusive"]["width"] == 3, g1["counts"]
    g2 = re_read("gpt-4o-mini", kt, tier_of, acc, frontier, G_old, {"deepseek-chat-v2_5": "below"}, 3, 5, "claude-3-5-sonnet-20241022")
    assert g2["exclusive_width"] == 2 and [t + 1 for t in g2["exclusive"]] == [4, 6] and g2["inclusive"]["width"] == 2 and not g2["inclusive"]["own_contained"], g2
    # deepseek certified ABOVE gpt-4o-mini: t5 joins as ii* and is never dropped (D1) -> exclusive [4, 5, 6] width 3; inclusive 5..6 own contained
    g3 = re_read("gpt-4o-mini", kt, tier_of, acc, frontier, G_old, {"deepseek-chat-v2_5": "above"}, 3, 5, "claude-3-5-sonnet-20241022")
    assert g3["exclusive_width"] == 3 and [t + 1 for t in g3["exclusive"]] == [4, 5, 6] and g3["tiers"][4]["cls"] == "ii*" and not g3["tiers"][4]["bounded"], g3["tiers"][4]
    assert (g3["inclusive"]["lo"] + 1, g3["inclusive"]["hi"] + 1) == (5, 6) and g3["inclusive"]["own_contained"], g3["inclusive"]
    # criterion (22) on the INCLUSIVE interval (D2): above -> 5..6 own in -> MET; below -> 4..5 own NOT in -> NOT MET; unseparated -> 4..6 -> NOT MET
    def met22(g): return g["inclusive"]["width"] == 2 and g["inclusive"]["own_contained"]
    assert met22(g3) and not met22(g2) and not met22(g1), (g3["inclusive"], g2["inclusive"], g1["inclusive"])
    # conventions on the planted steps: A adds the unusable row at 1/2, B drops ties (none planted) -> same statuses
    for conv in ("A", "B"):
        assert [c["status"] for c in certify_new(s_steps, conv, 400, random.Random(SEED))] == ["below"] * 3
    # the filter rule and the READY gate
    assert shipped_disagree("A", "b") and not shipped_disagree("a", " A ") and not shipped_disagree("", "B") and not shipped_disagree(None, "B")
    saved = os.environ.pop(GO_ENV, None)
    try:
        try: go_gate("selftest"); raise AssertionError("gate did not refuse without %s" % GO_ENV)
        except SystemExit as e: assert "refused" in str(e)
        os.environ[GO_ENV] = GO_VALUE
        if not os.path.exists(READY):
            try: go_gate("selftest"); raise AssertionError("gate did not refuse without the READY file")
            except SystemExit as e: assert "MISSING" in str(e)
        elif armb_alarm_state() != ARMB_OK:
            try: go_gate("selftest"); raise AssertionError("gate did not refuse on the ARM-B state %r" % armb_alarm_state())
            except SystemExit as e: assert "[ARM-B]" in str(e)
        assert (armb_alarm_state() is None) == (not os.path.exists(ARMB_OUT))
    finally:
        if saved is None: os.environ.pop(GO_ENV, None)
        else: os.environ[GO_ENV] = saved
    assert json.loads(step_table_json()) == [list(s) for s in STEPS]
    print("selftest OK: record reproduced (7/3 inclusive, 6/3 exclusive), planted steps -> sonnet (iii) 0 / exclusive 4 / inclusive 5, falsifier iii-a, "
          "key-contradicted tier ii* never dropped (exclusive 5, C2 fails), gpt-4o-mini exclusive widths 3 / 2 / 3 (unseparated / newcomer above / deepseek above as ii*) with (22) on the inclusive interval NOT MET / NOT MET / MET, "
          "conventions, the shipped filter, the READY + ARM-B gate (opens no DB, 0 calls)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="post the first N matches of the fixed schedule (2N calls); gated")
    ap.add_argument("--run", action="store_true", help="post every remaining match; gated")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--override-guard", action="store_true", help="post past the 5%% guard (recorded in meta)")
    a = ap.parse_args()
    OVERRIDE_GUARD = a.override_guard
    if a.selftest: selftest(); sys.exit(0)
    import pool_guard
    print("[POOL] %s" % pool_guard.assert_pool_of_record(POOL_ID))
    if a.dry_run: dry_run()
    elif a.pilot is not None or a.run: run(a.pilot, a.workers)
    elif a.analyze: analyze(a.draws)
    else: ap.print_help()
