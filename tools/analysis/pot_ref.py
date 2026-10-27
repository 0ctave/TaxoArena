"""POT-REF - REF-FORM-BY-CELL, the SOLVE stage (docs/judge_v2_program.md L7027-L7354, registered 2026-09-18 at d2f5393,
engineering note item 2). A program-of-thought (PoT) reference on the PoT-eligible quantitative questions: the solver
(grok-4-1-fast-reasoning, the incumbent's model and cap) writes ONE Python program, pot_runner executes it in the
container of record, the printed value is mapped to the option letter, scored against the key, cached in the
incumbent's `answers` schema so rejudge_reference.references() reads it unchanged.

  python tools/analysis/pot_ref.py --dry-run             # pool id first; eligible set, regex, counts vs the registration, bill; 0 calls
  python tools/analysis/pot_ref.py --pilot 12            # 12 solves (REFUSED unless REFFORM_GO == the plan amendment number)
  python tools/analysis/pot_ref.py --run [--workers 4]   # every eligible question not yet cached (same gate)
  python tools/analysis/pot_ref.py --report              # R1 / R2 / C1; writes pot_ref_outcome.txt ONLY from a complete cache
  python tools/analysis/pot_ref.py --selftest            # eligibility, extractor, truncation detector (the 27 of record, cache mode=ro); 0 calls
  python tools/analysis/pot_ref.py --repost-truncated    # re-posts the stop-truncated rows ONCE (same gate; 2026-09-19 follow-up, below)

POPULATION (read from grok_calib.db and mmlu_pro_dataset_cache_v2.db, mode=ro). Questions of pool p2dca21ab5f4ef3ae with
>= 1 key-decidable x12 MAIN match (GROK-CALIB's schedule) whose routed bareq512_s42 anchor is Math / Physics /
Chemistry / Engineering and whose options are numeric: >= 80% of the options START with a number under
pot_runner.first_number (sign, thousands, decimal, x10^n / e-n / 10^n, a simple a/b fraction; LaTeX and unicode
normalised) - the regex printed by --dry-run. The registration's design-time counts (461 q / 1,064 kd matches /
61 reference-wrong matches on 36 q; Math 431 / 7, Physics 319 / 13, Chemistry 220 / 17, Engineering 94 / 24) bind as
PREDICTIONS; --dry-run prints this script's counts beside them and the outcome scores against what it prints.

PROTOCOL OF RECORD (stored in meta at first launch; a resume that differs is refused): rr.PROVIDER azure,
rr.JUDGE_MODEL grok-4-1-fast-reasoning, rr.MAX_TOKENS 4,096 (asserted equal to judge_solve_map.call's default),
temperature OMITTED (Amendment 1 D2), system = SYSTEM_POT below, user = judge_solve_map.user_prompt(qtext, opts) byte
for byte; body built by rr.payload_body and asserted against rejudge_reasoning's source. finish_reason
content_filter -> cached as unusable (answer ''), never re-posted; finish_reason length -> cached as no yield
(answer ''); HTTP errors are NOT cached (re-posted on resume). Execution statuses: picked / no_pick / blocked /
timeout / error / degenerate (pot_runner.execute).

CACHE experiment_results/judge_solve/grok-reasoning-pot.db: `answers` (question_id, answer, gt, correct, raw, tokens,
latency, ts - the incumbent's exact schema; answer '' on no yield so references() drops the row and the judge stage
falls to the no-reference form), `pot_detail` (question_id, code, stdout, stderr, exit_code, wall, status, reason,
finish_reason, response_id), `meta`. Written once per question; --dry-run never creates the file.

GO GATE. --pilot / --run refuse unless the environment variable REFFORM_GO equals the number of the plan amendment
(docs/plan_2026-09-15.md, `## Amendment N ...`) whose heading names REF-FORM-BY-CELL; while no such amendment exists
the gate prints "author's go not given" and exits. Nothing in --dry-run / --report posts.

GUARD (--report): content_filter + length above 5% of the eligible population refuses the readout. The outcome file
of record is written only when every eligible question has a cached row; a pilot-sized cache writes
pot_ref_PILOT.txt, a larger incomplete one pot_ref_partial.txt.

STOP-TRUNCATIONS (added 2026-09-19 after the solve stage; the run's unregistered failure class, docs/judge_v2_program.md
L7106 bracket and the REF-FORM-BY-CELL outcome section, checker D1; re-post authorised by the author "you can repost
them"). A raw response is TRUNCATED, status `truncated`, iff truncated(raw) - a pure function: (a) it opens a code
fence it never closes and the unclosed body is code (a stray empty trailing ``` after a closed program, 15 rows of the
run, and a closed picked program followed by ```\\nYes. (q 9188) are NOT truncations), or (b) it has no open fence, no
ANSWER line, and its last line is an incomplete statement (does not compile, carries = ( or [, does not end in
sentence punctuation). The run's 27 (TRUNCATED_OF_RECORD; 13-171 completion tokens, finish_reason stop; Engineering
14 / Physics 6 / Chemistry 4 / Math 3) are asserted by --selftest against the cache (mode=ro): exactly those 27 of the
597 and no other. The guard counts them: content_filter + length + truncated over the eligible population. The runner
path caches a fresh truncation as status `truncated`, answer '' (no yield). --repost-truncated re-posts ONLY the
flagged rows ONCE (rows with pot_detail.repost_of set are never re-posted again; a second truncation stays
`truncated`), under the same protocol pin and body assertion, replacing the row's response / program / status in place
and keeping the original under pot_detail.raw_v1 / status_v1 / reason_v1 with repost_of = the original response id
and reposted_ts; no other row is touched (UPDATE ... WHERE question_id = ? AND repost_of IS NULL). pot_ref_outcome.txt
(9322e44) is WRITE-ONCE and is never rewritten; once re-posted rows exist --report writes pot_ref_outcome_repost.txt
with the same sections on the re-posted cache and a DIFF block (yield / deployable / among-yielded / fix-break / C1 /
guard, before and after, per cell and pooled; the 27 rows one by one). The before-state is reconstructed from the v1
columns (answer '', status truncated) and must equal the pre-re-post --report printout.
"""
import os, sys, re, json, time, math, hashlib, sqlite3, argparse, threading, inspect
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import judge_solve_map as jsm
import rubric_p8 as p8
import pot_runner

POOL = pool_guard.MMLU_PRO_POOL
QUANT4 = ("Math", "Physics", "Chemistry", "Engineering")
CELLS_READ = ("Math", "Physics", "Chemistry")          # Engineering is a descriptive row (UNDETERMINED-by-support)
SOLVER = "grok-4-1-fast-reasoning"; PROVIDER = "azure"; MAXTOK = 4096
ELIG_SHARE = 0.80
CALIB_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "grok_calib.db")
INCUMBENT_DB = os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning.db")
COT_DB = os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning-cot.db")
CACHE = os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning-pot.db")
OUT = os.path.join(ROOT, "experiment_results", "judge_solve", "pot_ref_outcome.txt")
OUT_REPOST = os.path.join(ROOT, "experiment_results", "judge_solve", "pot_ref_outcome_repost.txt")
# The run's 27 stop-truncations (checker D1; docs/judge_v2_program.md L7106 bracket): asserted by --selftest against the cache.
TRUNCATED_OF_RECORD = (4471, 4499, 4554, 7883, 8295, 9091, 9569, 9760, 9953, 10182, 10278, 11340, 11350, 11401, 11407, 11411,
                       11461, 11487, 11490, 11497, 11677, 11846, 11907, 11913, 12053, 12073, 12162)
UNUSABLE = ("content_filter", "length", "truncated")    # the guard's numerator classes
PLAN = os.path.join(ROOT, "docs", "plan_2026-09-15.md")
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
FRONTIER = ("gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06")
REG = dict(q=461, m=1064, w=61, wq=36, cells={"Math": (431, 7), "Physics": (319, 13), "Chemistry": (220, 17), "Engineering": (94, 24)})
SYSTEM_POT = (
    "Solve the multiple-choice problem by writing ONE self-contained Python 3 program. The program runs in a sandbox "
    "where the list OPTIONS (the option strings, in order) and two functions are already defined: pick(value) maps a "
    "numeric value to the option whose leading number is nearest (relative tolerance 2%%) and prints the letter; "
    "pick_text(s) maps a non-numeric answer string to the option it equals. Compute the answer NUMERICALLY in the units "
    "of the options, then call pick(value) (or pick_text(s) for a non-numeric answer) as the LAST statement of the "
    "program. Do not print a letter yourself; do not read input; do not hard-code the option's number - derive it. "
    "Allowed imports: %s. No file, network or system access. Output the program in a single ```python fenced block "
    "and nothing else after it." % ", ".join(pot_runner.ALLOWED_IMPORTS))


def script_sha(): return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
def runner_sha(): return hashlib.sha256(open(pot_runner.__file__, "rb").read()).hexdigest()[:16]
def ro(p): return sqlite3.connect("file:%s?mode=ro" % p, uri=True)


def protocol():
    return ("PoT solve on %s/%s: system SYSTEM_POT sha %s; user judge_solve_map.user_prompt(qtext, opts); max_tokens %d; temperature omitted; "
            "code = last ```python block; executed by pot_runner in %s (%s); letter = last ANSWER line; eligibility >= %.0f%% options start with a number"
            % (PROVIDER, SOLVER, hashlib.sha256(SYSTEM_POT.encode()).hexdigest()[:16], MAXTOK, pot_runner.IMAGE_TAG, pot_runner.PINNED_IMAGE_ID, 100 * ELIG_SHARE))


def eligible(opts):
    return bool(opts) and sum(1 for o in opts if pot_runner.first_number(o) is not None) >= ELIG_SHARE * len(opts)


def amendment_number():
    """The plan amendment that carries the author's go, by its heading; None while it does not exist."""
    if not os.path.exists(PLAN): return None
    for m in re.finditer(r"^## Amendment (\d+)\b(.*)$", open(PLAN, encoding="utf-8").read(), re.M):
        if "REF-FORM-BY-CELL" in m.group(2): return m.group(1)
    return None


def go_gate(what):
    n = amendment_number(); have = os.environ.get("REFFORM_GO")
    if n is None:
        raise SystemExit("[GO] author's go not given: no `## Amendment N` heading in %s names REF-FORM-BY-CELL; %s refused (0 calls)" % (os.path.relpath(PLAN, ROOT), what))
    if have != n:
        raise SystemExit("[GO] author's go not given: REFFORM_GO=%r, the plan amendment naming REF-FORM-BY-CELL is %s; %s refused (0 calls)" % (have, n, what))
    print("[GO] REFFORM_GO=%s matches plan Amendment %s (REF-FORM-BY-CELL)" % (have, n))


def population():
    """kd: key-decidable QUANT4 matches from grok_calib.db as dicts; META: qid -> (qtext, opts, gt); K/P per (q, model)."""
    ev = ro(rj.EVAL_DB)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m not in EXCLUDED: K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    gc = ro(CALIB_DB)
    rows = gc.execute("SELECT match_id, model_a, model_b, qid, anchor, ref_letter, ref_correct, winner, invalid, finish1, finish2 FROM verdicts "
                      "WHERE anchor IN (?,?,?,?) ORDER BY match_id", QUANT4).fetchall()
    gc.close()
    kd = []
    for mid, a, b, q, anc, rl, rc, w, inv, f1, f2 in rows:
        assert q in pool, "[POOL] match %d question %d outside %s" % (mid, q, POOL)
        ka, kb = K[q].get(a), K[q].get(b)
        if ka is None or kb is None or ka == kb: continue
        kd.append(dict(mid=mid, a=a, b=b, q=q, anchor=anc, ref_letter=rl or "", ref_correct=rc, winner=w, invalid=inv, finish1=f1, finish2=f2, key=a if ka else b))
    META = {}
    for q in sorted({r["q"] for r in kd}):
        r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        if r is None:
            r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name!='Meta-Llama-3-70B-Instruct'", (q,)).fetchone()
        opts = json.loads(r[1]) if r and r[1] else []
        META[q] = (r[0], opts, (r[2] or "").strip().upper()[:1])
    ev.close()
    elig = sorted(q for q in META if eligible(META[q][1]))
    return kd, META, K, P, elig


def set_hash(qids): return hashlib.sha256(",".join(str(q) for q in sorted(qids)).encode()).hexdigest()[:16]


def counts(kd, elig, L):
    """The registration's population table beside this script's, per anchor and pooled."""
    e = set(elig); anc_q = defaultdict(set)
    for r in kd: anc_q[r["anchor"]].add(r["q"])
    L.append("  %-12s %-28s %-30s %s" % ("anchor", "kd matches / q (all)", "eligible matches / q / ref-wrong m / q", "registration (m / ref-wrong m)"))
    for anc in QUANT4 + ("QUANT4",):
        rs = [r for r in kd if anc == "QUANT4" or r["anchor"] == anc]
        es = [r for r in rs if r["q"] in e]; ws = [r for r in es if r["ref_correct"] == 0]
        reg = REG["cells"].get(anc, (REG["m"], REG["w"]))
        L.append("  %-12s %5d / %4d %19s %5d / %4d / %3d / %3d %14s %5d / %3d %s" % (
            anc, len(rs), len({r["q"] for r in rs}), "", len(es), len({r["q"] for r in es}), len(ws), len({r["q"] for r in ws}), "",
            reg[0], reg[1], "" if anc == "QUANT4" else ""))
    es = [r for r in kd if r["q"] in e]; ws = [r for r in es if r["ref_correct"] == 0]
    acc = lambda rs: (sum(1 for r in rs if r["winner"] == r["key"]) / len(rs)) if rs else float("nan")
    L.append("  pooled QUANT4: %d kd matches on %d q (registration 1,836 / 784) | eligible %d / %d q (registration %d / %d) | reference-wrong %d m / %d q (registration %d / %d)"
             % (len(kd), len({r["q"] for r in kd}), len(es), len(e), REG["m"], REG["q"], len(ws), len({r["q"] for r in ws}), REG["w"], REG["wq"]))
    L.append("  GROK-CALIB control on the eligible kd matches: A %.3f | reference-right %.3f | reference-wrong %.3f (registration 0.865 / 0.905 / 0.309 on all 1,836)"
             % (acc(es), acc([r for r in es if r["ref_correct"] == 1]), acc(ws)))
    ceiling = len(ws) / max(1, len(es)) * (acc([r for r in es if r["ref_correct"] == 1]) - acc(ws)) if es else float("nan")
    L.append("  CEILING fixed before the run: %d / %d x (%.3f - %.3f) = %+.1fpp pooled (registration +3.4pp)" % (len(ws), len(es), acc([r for r in es if r["ref_correct"] == 1]), acc(ws), 100 * ceiling))
    return es


def header(kd, META, elig, L):
    L.append("[POOL] %s (pool of record; pool_guard.assert_pool_of_record passed)" % POOL)
    L.append("[RUN]  REF-FORM-BY-CELL solve stage | solver %s on %s | max_tokens %d (judge_solve_map.call default %d) | temperature omitted (Amendment 1 D2)"
             % (SOLVER, PROVIDER, MAXTOK, inspect.signature(jsm.call).parameters["max_tokens"].default))
    L.append("[ELIGIBILITY] >= %.0f%% of a question's options START with a number under pot_runner.first_number; regex of record:" % (100 * ELIG_SHARE))
    L.append("   " + pot_runner.NUM_PATTERN)
    L.append("[RUNNER] %s id %s | pinned %s | base %s | args %s | wall %.0fs" % (pot_runner.IMAGE_TAG, pot_runner.docker_image_id(), pot_runner.PINNED_IMAGE_ID,
             pot_runner.BASE_IMAGE, " ".join(pot_runner.DOCKER_ARGS), pot_runner.WALL_TIMEOUT_S))
    L.append("[CACHE] %s (%s) | set hash %s over %d eligible questions" % (CACHE, "exists" if os.path.exists(CACHE) else "absent, created on --run", set_hash(elig), len(elig)))
    L.append("[GO] plan amendment naming REF-FORM-BY-CELL: %s | REFFORM_GO=%r" % (amendment_number() or "NONE (author's go not given)", os.environ.get("REFFORM_GO")))


def assert_body(system, user):
    src = open(rr.__file__, encoding="utf-8").read()
    assert "body = payload_bytes(system, user)" in src and 'return json.dumps(payload_body(system, user)).encode("utf-8")' in src, "rejudge_reasoning no longer posts payload_body()"
    assert '"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src
    assert rr.TEMPERATURE is None, "D2: temperature must be omitted; rr.TEMPERATURE is %r" % (rr.TEMPERATURE,)
    assert MAXTOK == inspect.signature(jsm.call).parameters["max_tokens"].default, "the incumbent's cap changed"
    rr.PROVIDER = PROVIDER; rr.JUDGE_MODEL = SOLVER; rr.MAX_TOKENS = MAXTOK
    body = rr.payload_body(system, user)
    assert tuple(body) == ("model", "max_tokens", "messages") and body["model"] == SOLVER and body["max_tokens"] == MAXTOK
    assert body["messages"][0]["content"] == system and body["messages"][1]["content"] == user
    return body


CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def extract_code(content):
    blocks = CODE_RE.findall(content or "")
    if blocks: return blocks[-1].strip("\n")
    t = (content or "").strip()
    return t if ("pick" in t and "\n" in t) else ""


# ── stop-truncation detector (pure; 2026-09-19) ──
FENCE_RE = re.compile(r"```")
ANSWER_LINE_RE = re.compile(r"^ANSWER: ([A-J]|NONE)\s*$", re.M)
CODE_HINT_RE = re.compile(r"[=\[(]")


def _compiles(line):
    try: compile(line.strip(), "<line>", "exec"); return True
    except SyntaxError: return False      # IndentationError included


def _code_like(body):
    """A fence body is code when any line is a comment, compiles on its own, or carries = ( [ (prose such as 'Yes.' is not)."""
    return any(s and (s.startswith("#") or _compiles(s) or CODE_HINT_RE.search(s)) for s in (ln.strip() for ln in body.splitlines()))


def _incomplete_statement(line):
    s = line.strip()
    return bool(s) and not s.startswith("#") and s[-1] not in ".!?)" and not _compiles(s) and bool(CODE_HINT_RE.search(s))


def truncated(raw):
    """(is_truncated, why). Pure: no DB, no call. A response is truncated iff (a) it opens a ``` fence it never closes
    and the unclosed body is code, or (b) it has no open fence, no ANSWER line, and its last non-blank line (after the
    last closing fence, or of the whole text when there is no fence) is an incomplete statement."""
    text = (raw or "").rstrip()
    if not text: return False, ""
    ends = [m.end() for m in FENCE_RE.finditer(text)]
    if len(ends) % 2 == 1:
        body = text[ends[-1]:]
        body = body.split("\n", 1)[1] if "\n" in body else ""       # drop the language tag line
        if body.strip() and _code_like(body):
            return True, "unclosed code fence; last line %r" % body.rstrip().splitlines()[-1].strip()[-60:]
        return False, ""
    if ANSWER_LINE_RE.search(text): return False, ""
    tail = text[ends[-1]:] if ends else text
    lines = [l for l in tail.splitlines() if l.strip()]
    if lines and _incomplete_statement(lines[-1]):
        return True, "no open fence, no ANSWER line, last line an incomplete statement %r" % lines[-1].strip()[-60:]
    return False, ""


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, tokens INTEGER, latency REAL, ts REAL)")
    con.execute("CREATE TABLE IF NOT EXISTS pot_detail (question_id INTEGER PRIMARY KEY, code TEXT, stdout TEXT, stderr TEXT, exit_code INTEGER, wall REAL, "
                "status TEXT, reason TEXT, finish_reason TEXT, response_id TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    have = {r[1] for r in con.execute("PRAGMA table_info(pot_detail)")}
    for col, typ in (("raw_v1", "TEXT"), ("status_v1", "TEXT"), ("reason_v1", "TEXT"), ("repost_of", "TEXT"), ("reposted_ts", "REAL")):
        if col not in have: con.execute("ALTER TABLE pot_detail ADD COLUMN %s %s" % (col, typ))
    con.commit()
    return con


def repost_columns(con):
    """{q: (raw_v1, status_v1, reason_v1, repost_of, reposted_ts)} for the re-posted rows; {} on a cache without the columns."""
    have = {r[1] for r in con.execute("PRAGMA table_info(pot_detail)")}
    if "repost_of" not in have: return {}
    return {q: (rv, sv, rs, ro_, ts) for q, rv, sv, rs, ro_, ts in con.execute(
        "SELECT question_id, raw_v1, status_v1, reason_v1, repost_of, reposted_ts FROM pot_detail WHERE repost_of IS NOT NULL")}


def pin_meta(con, elig):
    want = {"protocol": protocol(), "judge": SOLVER, "provider": PROVIDER, "max_tokens": str(MAXTOK), "temperature": "omitted (provider default; Amendment 1 D2)",
            "eligibility_regex": pot_runner.NUM_PATTERN, "set_hash": set_hash(elig), "image_id": pot_runner.PINNED_IMAGE_ID, "pool": POOL}
    meta = dict(con.execute("SELECT key, value FROM meta")); now = time.strftime("%Y-%m-%d %H:%M:%S")
    if not meta:
        con.executemany("INSERT INTO meta VALUES (?, ?)", list(want.items()) + [("system_prompt", SYSTEM_POT), ("script_sha256_16", script_sha()),
                                                                                  ("runner_sha256_16", runner_sha()), ("started", now)]); con.commit(); return
    bad = [(k, meta.get(k), v) for k, v in want.items() if meta.get(k) != v]
    for k, h, w in bad: print("[META] %s differs from the cache of record:\n   cached: %r\n   now:    %r" % (k, h, w))
    if bad: raise SystemExit("resume refused: a different protocol / cap / set / image is a new vintage and gets a new cache")
    if meta.get("script_sha256_16") != script_sha() or meta.get("runner_sha256_16") != runner_sha():
        print("[META] script or runner edited since first launch (pinned %s / %s, now %s / %s); recorded as *_relaunch" % (meta.get("script_sha256_16"), meta.get("runner_sha256_16"), script_sha(), runner_sha()))
        con.execute("INSERT OR REPLACE INTO meta VALUES ('script_sha256_16_relaunch', ?)", (script_sha() + "/" + runner_sha(),))
    con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((meta.get("resumed") + ", " if meta.get("resumed") else "") + now,)); con.commit()


def cached_qids():
    if not os.path.exists(CACHE): return set()
    c = ro(CACHE); s = {q for (q,) in c.execute("SELECT question_id FROM answers")}; c.close(); return s


def dry_run():
    kd, META, K, P, elig = population()
    L = []; header(kd, META, elig, L); counts(kd, elig, L)
    done = cached_qids() & set(elig)
    L.append("[BILL] %d eligible questions x 1 reasoning solve = %d calls (%d cached, %d to post) | registration <= 600 solves x 10 cce = <= 6,000 cce | judged stage CONDITIONAL on C1"
             % (len(elig), len(elig), len(done), len(elig) - len(done)))
    assert len(elig) <= 600, "eligible set %d exceeds the registered <= 600 solves" % len(elig)
    q = elig[0]; qtext, opts, gt = META[q]
    user = jsm.user_prompt(qtext, opts); body = assert_body(SYSTEM_POT, user)
    L.append("[PAYLOAD] first body: model=%s | max_tokens=%d | temperature=%s | keys=%s | %d bytes" % (body["model"], body["max_tokens"], "omitted" if "temperature" not in body else body["temperature"], ",".join(body), len(json.dumps(body).encode())))
    L.append("----- SYSTEM (verbatim) -----"); L.append(SYSTEM_POT)
    L.append("----- USER, question %d (verbatim; judge_solve_map.user_prompt) -----" % q); L.append(user)
    L.append("----- PRELUDE head the container prepends (pot_runner.prelude) -----"); L.append("\n".join(pot_runner.prelude(opts).splitlines()[-22:]))
    st = Counter(); ex = Counter()
    for q in elig:
        st[len(META[q][1])] += 1; ex[sum(1 for o in META[q][1] if pot_runner.first_number(o) is not None) == len(META[q][1])] += 1
    L.append("[DRY-RUN] eligible options per question: %s | all options numeric: %d, >= 80%% only: %d" % (dict(sorted(st.items())), ex[True], ex[False]))
    L.append("[DRY-RUN] OK: 0 calls made, no file created")
    print("\n".join(L))


def solve(q, META):
    """ONE solve: the call (body asserted), the truncation / refusal / cap classes, the container; returns the
    `answers` row and the `pot_detail` row (the first ten columns) for question q. Shared by --run and --repost-truncated."""
    qtext, opts, gt = META[q]
    user = jsm.user_prompt(qtext, opts); assert_body(SYSTEM_POT, user)
    content, prov, tok, lat, finish, msg = rr.call_judge_full(SYSTEM_POT, user)
    rid = (msg or {}).get("_response_id")
    raw = rr.strip_think(content)
    if finish == "content_filter":
        return (q, "", gt, 0, raw, tok, lat, time.time()), (q, "", "", "", None, 0.0, "content_filter", "provider refusal (deterministic; cached as unusable)", finish, rid)
    if finish == "length":
        return (q, "", gt, 0, raw, tok, lat, time.time()), (q, extract_code(raw), "", "", None, 0.0, "length", "finish_reason length at cap %d" % MAXTOK, finish, rid)
    tr, why = truncated(raw)
    if tr:
        return (q, "", gt, 0, raw, tok, lat, time.time()), (q, extract_code(raw), "", "", None, 0.0, "truncated", "provider stop-truncation: %s" % why, finish, rid)
    code = extract_code(raw)
    if not code:
        return (q, "", gt, 0, raw, tok, lat, time.time()), (q, "", "", "", None, 0.0, "no_pick", "no python block in the response", finish, rid)
    r = pot_runner.execute(code, opts)
    letter = r["letter"] if r["status"] == "picked" else ""
    return (q, letter, gt, int(letter != "" and letter == gt), raw, tok, lat, time.time()), (q, code, r["stdout"], r["stderr"], r["exit_code"], r["wall"], r["status"], r["reason"], finish, rid)


def repost_truncated(workers):
    """Re-posts the stop-truncated rows ONCE (2026-09-19 follow-up, the author's 'you can repost them'): flagged =
    truncated(raw) AND repost_of IS NULL; the original response / status / reason move to raw_v1 / status_v1 /
    reason_v1 with repost_of = the original response id; the row's answer / correct / raw / tokens / latency / ts
    and code / stdout / stderr / exit_code / wall / status / reason / finish_reason / response_id are replaced by the
    new solve. HTTP errors are not cached (the row stays flagged; re-run to resume). No other row is touched."""
    print("[POOL] %s" % POOL)
    go_gate("--repost-truncated")
    assert amendment_number() == "5", "the re-post is authorised under plan Amendment 5 (REF-FORM-BY-CELL); the plan now names Amendment %r" % amendment_number()
    kd, META, K, P, elig = population()
    pot_runner.assert_image()
    rr.load_env()
    con = open_cache(); pin_meta(con, elig)
    rows = con.execute("SELECT a.question_id, a.raw, d.status, d.reason, d.response_id, d.repost_of FROM answers a JOIN pot_detail d USING(question_id) ORDER BY a.question_id").fetchall()
    already = sorted(q for q, raw, st, rs, rid, rof in rows if rof is not None)
    flagged = [(q, raw, st, rs, rid) for q, raw, st, rs, rid, rof in rows if rof is None and truncated(raw)[0]]
    assert all(q in elig for q, *_ in flagged), "a flagged row is outside the eligible set"
    fresh = sorted(q for q, *_ in flagged if q not in TRUNCATED_OF_RECORD)
    print("[REPOST] cached %d | already re-posted %d %s | flagged now %d (of record %d) %s%s" % (
        len(rows), len(already), already, len(flagged), len(TRUNCATED_OF_RECORD), [q for q, *_ in flagged],
        "" if not fresh else " | NOT of record (a truncation cached after the run): %s" % fresh))
    if not flagged: print("[REPOST] nothing to do (0 calls)"); return
    print("[REPOST] posting %d solves (%s, cap %d, temperature omitted) | workers %d | runner %s" % (len(flagged), SOLVER, MAXTOK, workers, pot_runner.PINNED_IMAGE_ID))
    lock = threading.Lock(); ok = err = 0; st = Counter(); second = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(solve, q, META): (q, raw, st0, rs0, rid0) for q, raw, st0, rs0, rid0 in flagged}
        for i, f in enumerate(as_completed(futs), 1):
            q, raw0, st0, rs0, rid0 = futs[f]
            try: arow, drow = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s (not cached; re-run to resume)" % (q, str(e)[:140]), flush=True); continue
            assert arow[0] == q and drow[0] == q
            with lock:      # both UPDATEs sit in one implicit transaction; committed together
                n1 = con.execute("UPDATE pot_detail SET raw_v1=?, status_v1=?, reason_v1=?, repost_of=?, reposted_ts=?, code=?, stdout=?, stderr=?, exit_code=?, wall=?, "
                                 "status=?, reason=?, finish_reason=?, response_id=? WHERE question_id=? AND repost_of IS NULL",
                                 (raw0, st0, rs0, rid0 or "(no response id cached)", time.time()) + drow[1:] + (q,)).rowcount
                n2 = con.execute("UPDATE answers SET answer=?, correct=?, raw=?, tokens=?, latency=?, ts=? WHERE question_id=?",
                                 (arow[1], arow[3], arow[4], arow[5], arow[6], arow[7], q)).rowcount if n1 == 1 else 0
                assert n1 == 1 and n2 == 1, "row %d: %d / %d rows updated (expected 1 / 1)" % (q, n1, n2)
                con.commit()
            ok += 1; st[drow[6]] += 1
            if drow[6] == "truncated": second.append(q)
            print("  %2d/%d q %-6d %-10s -> %-10s letter %-2s correct %d tokens %-5s | %s" % (i, len(flagged), q, st0, drow[6], arow[1] or "-", arow[3], arow[5], (drow[7] or "")[:70]), flush=True)
    n_rep = con.execute("SELECT count(*) FROM pot_detail WHERE repost_of IS NOT NULL").fetchone()[0]
    con.execute("INSERT OR REPLACE INTO meta VALUES ('reposted_truncated', ?)", ("%s: %d rows re-posted once (statuses %s); second truncations %s; script %s" % (
        time.strftime("%Y-%m-%d %H:%M:%S"), n_rep, dict(st), second, script_sha()),)); con.commit(); con.close()
    print("done: ok %d, errors %d | statuses %s | second truncation %s | rows carrying repost_of: %d" % (ok, err, dict(st), second, n_rep), flush=True)
    report()


def run(pilot, workers):
    print("[POOL] %s" % POOL)
    go_gate("--pilot" if pilot else "--run")
    kd, META, K, P, elig = population()
    assert len(elig) <= 600
    pot_runner.assert_image()
    rr.load_env()
    con = open_cache(); pin_meta(con, elig)
    done = {q for (q,) in con.execute("SELECT question_id FROM answers")}
    todo = [q for q in elig if q not in done]
    if pilot: todo = todo[:pilot]
    print("[RUN] eligible %d | cached %d | posting %d solves (%s) | workers %d | runner %s" % (len(elig), len(elig) - len([q for q in elig if q not in done]), len(todo), "pilot" if pilot else "run", workers, pot_runner.PINNED_IMAGE_ID))
    lock = threading.Lock(); ok = err = 0; st = Counter()
    one = lambda q: solve(q, META)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: arow, drow = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s (not cached; re-run to resume)" % (futs[f], str(e)[:140]), flush=True); continue
            with lock:
                con.execute("INSERT OR IGNORE INTO answers VALUES (?,?,?,?,?,?,?,?)", arow)
                con.execute("INSERT OR IGNORE INTO pot_detail VALUES (?,?,?,?,?,?,?,?,?,?)", drow); con.commit()
            ok += 1; st[drow[6]] += 1
            if i % 25 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d) | statuses %s" % (i, len(todo), ok, err, dict(st)), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)
    report(pilot=bool(pilot))


def mcn(b, c): return p8.mcn(b, c)


def readout(A, D, T, have, elig, anc_of, I, C, L, tag=""):
    """R1 per cell + C1 + predictions on one cache STATE (A: q -> (answer, correct); D: q -> (status, reason, finish);
    T: q -> truncated flag). Appends lines to L; returns the pooled dict (per anchor + QUANT4) with the guard numbers."""
    disp = lambda q: "truncated" if T.get(q) else D.get(q, ("(no detail)",))[0]
    unus = [q for q in have if disp(q) in UNUSABLE]
    rate = len(unus) / max(1, len(elig))
    L.append("  GUARD%s: content_filter + length + truncated = %d of %d eligible (%.1f%%) [%s] | %s | finish_reason: %s" % (
        tag, len(unus), len(elig), 100 * rate, "OK" if rate <= 0.05 else "REFUSED > 5%",
        ", ".join("%s %d" % (k, sum(1 for q in unus if disp(q) == k)) for k in UNUSABLE),
        ", ".join("%s %d" % kv for kv in sorted(Counter(D[q][2] or "(none)" for q in have if q in D).items()))))
    if rate > 0.05:
        L.append("  VERDICT REFUSED: the reference-yield readout would be a floor, not an estimate."); return None
    L.append("")
    L.append("(R1%s) SOLVE STAGE per cell (eligible questions with a cached row; the incumbent = grok-reasoning.db on the SAME questions; CoT = grok-reasoning-cot.db beside, no execution)" % tag)
    L.append("  %-12s %4s %5s | %-52s | %5s %5s %5s | %5s | fix/break (McNemar p) yielded | deploy | CoT fix/break" % ("cell", "n", "yield", "status table", "PoT_y", "PoT_d", "inc", "CoT"))
    pooled = {}
    for anc in QUANT4 + ("QUANT4",):
        qs = [q for q in have if anc == "QUANT4" or anc_of.get(q) == anc]
        if not qs: continue
        st = Counter(disp(q) for q in qs); y = [q for q in qs if A[q][0]]
        pot_y = sum(A[q][1] for q in y) / max(1, len(y)); pot_d = sum(A[q][1] for q in qs) / len(qs)
        inc_all = sum(I.get(q, ("", 0))[1] for q in qs) / len(qs); inc_y = sum(I.get(q, ("", 0))[1] for q in y) / max(1, len(y))
        fix = sum(1 for q in y if A[q][1] and not I.get(q, ("", 0))[1]); brk = sum(1 for q in y if I.get(q, ("", 0))[1] and not A[q][1])
        fix_d = sum(1 for q in qs if A[q][1] and not I.get(q, ("", 0))[1]); brk_d = sum(1 for q in qs if I.get(q, ("", 0))[1] and not A[q][1])
        cfix = sum(1 for q in qs if C.get(q, ("", 0))[1] and not I.get(q, ("", 0))[1]); cbrk = sum(1 for q in qs if I.get(q, ("", 0))[1] and not C.get(q, ("", 0))[1])
        cot_acc = sum(C.get(q, ("", 0))[1] for q in qs) / len(qs) if C else float("nan")
        L.append("  %-12s %4d %.3f | %-52s | %.3f %.3f %.3f | %.3f | %3d / %3d (p=%.4f) [inc on yielded %.3f] | %3d / %3d | %3d / %3d"
                 % (anc, len(qs), len(y) / len(qs), ", ".join("%s %d" % kv for kv in sorted(st.items())), pot_y, pot_d, inc_all, cot_acc, fix, brk, mcn(fix, brk), inc_y, fix_d, brk_d, cfix, cbrk))
        pooled[anc] = dict(n=len(qs), y=len(y), pot_y=pot_y, inc_y=inc_y, pot_d=pot_d, inc=inc_all, fix=fix, brk=brk, st=st, fix_d=fix_d, brk_d=brk_d,
                           incw=sum(1 for q in y if not I.get(q, ("", 0))[1]), incr=sum(1 for q in y if I.get(q, ("", 0))[1]),
                           right=sum(A[q][1] for q in y), guard=sum(1 for q in qs if disp(q) in UNUSABLE), trunc=sum(1 for q in qs if disp(q) == "truncated"))
    Q = pooled.get("QUANT4")
    if Q:
        L.append("")
        gain = Q["pot_y"] - Q["inc_y"]; p = mcn(Q["fix"], Q["brk"]); Q["gain"] = gain; Q["p"] = p
        Q["c1"] = "HELD" if (gain >= 0.02 and p < 0.05 and Q["fix"] > Q["brk"]) else "FAILED"
        L.append("  C1%s (form is a lever on the REFERENCE): among-yielded PoT %.3f vs incumbent %.3f on the same %d q = %+.1fpp (bar >= +2pp) | fix %d : break %d, McNemar p=%.4f (bar < 0.05) -> %s"
                 % (tag, Q["pot_y"], Q["inc_y"], Q["y"], 100 * gain, Q["fix"], Q["brk"], p, Q["c1"]))
        deg = Q["st"].get("degenerate", 0) / Q["n"]; yr = Q["y"] / Q["n"]
        fr = Q["fix"] / max(1, Q["incw"]); br = Q["brk"] / max(1, Q["incr"])
        L.append("  PREDICTIONS%s: yield %.3f (0.80-0.92) %s | degenerate %.3f (<= 0.05) %s | fix rate %.3f on %d incumbent-wrong yielded (0.25-0.40) %s | break rate %.3f (0.01-0.03) %s | among-yielded gain %+.1fpp (+1..+3) %s | deployment %+.1fpp (-3..+2) %s"
                 % (tag, yr, "HELD" if 0.80 <= yr <= 0.92 else "FAILED", deg, "HELD" if deg <= 0.05 else "FAILED", fr, Q["incw"], "HELD" if 0.25 <= fr <= 0.40 else "FAILED",
                    br, "HELD" if 0.01 <= br <= 0.03 else "FAILED", 100 * gain, "HELD" if 0.01 <= gain <= 0.03 else "FAILED", 100 * (Q["pot_d"] - Q["inc"]), "HELD" if -0.03 <= Q["pot_d"] - Q["inc"] <= 0.02 else "FAILED"))
        for anc, lo, hi in (("Math", 0.95, 0.98), ("Physics", 0.92, 0.96), ("Chemistry", 0.88, 0.93), ("Engineering", 0.80, 0.88)):
            if anc in pooled: L.append("     %-12s PoT among yielded %.3f (predicted %.2f-%.2f) %s%s" % (anc, pooled[anc]["pot_y"], lo, hi, "HELD" if lo <= pooled[anc]["pot_y"] <= hi else "FAILED", "" if anc in CELLS_READ else "  [descriptive row: Engineering UNDETERMINED-by-support]"))
    return pooled


def report(pilot=False):
    if not os.path.exists(CACHE): print("[REPORT] no cache at %s: nothing to report" % CACHE); return
    kd, META, K, P, elig = population()
    c = ro(CACHE)
    A = {q: (a or "", int(cc or 0)) for q, a, cc in c.execute("SELECT question_id, answer, correct FROM answers")}
    R = dict(c.execute("SELECT question_id, raw FROM answers"))
    D = {q: (s, reason, fin) for q, s, reason, fin in c.execute("SELECT question_id, status, reason, finish_reason FROM pot_detail")}
    V1 = repost_columns(c)
    meta = dict(c.execute("SELECT key, value FROM meta")); c.close()
    T = {q: truncated(R[q])[0] for q in R}
    have = [q for q in elig if q in A]
    L = ["=== REF-FORM-BY-CELL solve stage (R1 / R2 / C1) | cache %s | %d of %d eligible questions cached | protocol pinned %s%s ===" % (
        os.path.basename(CACHE), len(have), len(elig), meta.get("started"), "" if not V1 else " | %d stop-truncated rows RE-POSTED once (%s)" % (len(V1), meta.get("reposted_truncated", "")[:19]))]
    if meta.get("set_hash") != set_hash(elig): L.append("  [META] cached set hash %s != current eligible set %s: the population changed since first launch" % (meta.get("set_hash"), set_hash(elig)))
    inc = ro(INCUMBENT_DB); I = {q: (a or "", int(cc or 0)) for q, a, cc in inc.execute("SELECT question_id, answer, correct FROM answers")}; inc.close()
    C = {}
    if os.path.exists(COT_DB):
        cot = ro(COT_DB); C = {q: (a or "", int(cc or 0)) for q, a, cc in cot.execute("SELECT question_id, answer, correct FROM answers")}; cot.close()
    anc_of = {}
    for r in kd: anc_of.setdefault(r["q"], r["anchor"])
    # GUARD + R1 + C1 on the current state (after the re-post when one happened)
    pooled = readout(A, D, T, have, elig, anc_of, I, C, L)
    if pooled is None:
        txt = "\n".join(L); print(txt); open(OUT.replace("outcome", "REFUSED"), "w", encoding="utf-8").write(txt + "\n"); return
    # R2 leakage on the reference itself: per-contestant answer agreement, PoT letter vs incumbent letter, yielded eligible questions
    L.append("")
    L.append("(R2) LEAKAGE on the reference itself (no judge call): per-contestant answer agreement on the %d yielded eligible questions" % len([q for q in have if A[q][0]]))
    ys = [q for q in have if A[q][0]]; worst = 0.0
    for m in sorted(p8.ARENA12):
        both = [q for q in ys if P[q].get(m) and I.get(q, ("", 0))[0]]
        if not both: continue
        ap_ = sum(1 for q in both if A[q][0] == P[q][m]) / len(both); ai = sum(1 for q in both if I[q][0] == P[q][m]) / len(both)
        if m in FRONTIER: worst = max(worst, ap_ - ai)
        L.append("      %-30s PoT %.3f | incumbent %.3f | %+.3f (n=%d)%s" % (m[:30], ap_, ai, ap_ - ai, len(both), "   <- frontier" if m in FRONTIER else ""))
    gem = [q for q in ys if P[q].get("gemini-3.1-pro_5-shots") and I.get(q, ("", 0))[0]]
    if gem:
        d = sum(1 for q in gem if A[q][0] == P[q]["gemini-3.1-pro_5-shots"]) / len(gem) - sum(1 for q in gem if I[q][0] == P[q]["gemini-3.1-pro_5-shots"]) / len(gem)
        L.append("  PREDICTION gemini agreement within +-3pp of the incumbent's: %+.1fpp -> %s | worst frontier delta %+.3f (REF-QUAL gate (3) bar 0.03, informational here)" % (100 * d, "HELD" if abs(d) <= 0.03 else "FAILED", worst))
    complete = len(have) == len(elig)
    if V1:
        # DIFF block: the before-state reconstructed from the v1 columns (answer '', status truncated), the after-state = the cache now
        A0 = dict(A); D0 = dict(D); T0 = dict(T)
        for q, (raw_v1, st_v1, rs_v1, rof, ts) in V1.items():
            A0[q] = ("", 0); D0[q] = (st_v1, rs_v1, D[q][2]); T0[q] = truncated(raw_v1)[0]
        L0 = []; before = readout(A0, D0, T0, have, elig, anc_of, I, C, L0, tag=" [BEFORE the re-post]")
        L.append("")
        L.append("(DIFF) the %d re-posted stop-truncations: BEFORE (the outcome of record 9322e44, reconstructed from raw_v1 / status_v1: answer '', status truncated) -> AFTER (this cache)" % len(V1))
        L.extend(L0)
        L.append("")
        L.append("  %-12s | %-13s | %-13s | %-13s | %-17s | %-11s | %-15s | %s" % ("cell", "yield b -> a", "deploy b -> a", "PoT_y b -> a", "fix/break b -> a", "trunc b -> a", "guard b -> a", "right/yielded b -> a"))
        for anc in QUANT4 + ("QUANT4",):
            b, a = before.get(anc), pooled.get(anc)
            if not b or not a: continue
            L.append("  %-12s | %.3f -> %.3f | %.3f -> %.3f | %.3f -> %.3f | %2d/%2d -> %2d/%2d     | %3d -> %-3d  | %3d -> %-3d (%.1f%% -> %.1f%%) | %3d/%3d -> %3d/%3d"
                     % (anc, b["y"] / b["n"], a["y"] / a["n"], b["pot_d"], a["pot_d"], b["pot_y"], a["pot_y"], b["fix"], b["brk"], a["fix"], a["brk"],
                        b["trunc"], a["trunc"], b["guard"], a["guard"], 100 * b["guard"] / len(elig), 100 * a["guard"] / len(elig), b["right"], b["y"], a["right"], a["y"]))
        Qb, Qa = before["QUANT4"], pooled["QUANT4"]
        L.append("  C1 before: %+.1fpp, fix %d : break %d, p=%.4f -> %s | C1 after: %+.1fpp, fix %d : break %d, p=%.4f -> %s"
                 % (100 * Qb["gain"], Qb["fix"], Qb["brk"], Qb["p"], Qb["c1"], 100 * Qa["gain"], Qa["fix"], Qa["brk"], Qa["p"], Qa["c1"]))
        L.append("  usable-response yield: before %d / %d = %.3f (the review's 0.846) | after %d / %d = %.3f" % (
            Qb["y"], Qb["n"] - Qb["guard"], Qb["y"] / max(1, Qb["n"] - Qb["guard"]), Qa["y"], Qa["n"] - Qa["guard"], Qa["y"] / max(1, Qa["n"] - Qa["guard"])))
        L.append("  the re-posted rows one by one (status_v1 -> status; letter / key / incumbent letter; tokens; second truncation flagged):")
        st2 = Counter(); n_y = n_r = n_fix = n_brk = 0
        c2 = ro(CACHE); TOK = dict(c2.execute("SELECT question_id, tokens FROM answers")); c2.close()
        for q in sorted(V1):
            raw_v1, st_v1, rs_v1, rof, ts = V1[q]; st_now = "truncated" if T.get(q) else D[q][0]; st2[st_now] += 1
            y = bool(A[q][0]); n_y += y; n_r += A[q][1]
            n_fix += int(y and A[q][1] and not I.get(q, ("", 0))[1]); n_brk += int(y and I.get(q, ("", 0))[1] and not A[q][1])
            L.append("     q %-6d %-12s %-10s -> %-10s letter %-2s key %s inc %-2s correct %d tokens %-5s repost_of %s | %s" % (
                q, anc_of.get(q, "?"), st_v1, st_now, A[q][0] or "-", META[q][2], I.get(q, ("", 0))[0] or "-", A[q][1], TOK.get(q), (rof or "")[:36], (D[q][1] or "")[:60]))
        L.append("  re-posted %d: statuses %s | yield %d | right %d | fix %d / break %d against the incumbent | second truncation %d" % (
            len(V1), dict(sorted(st2.items())), n_y, n_r, n_fix, n_brk, st2.get("truncated", 0)))
    L.append("")
    L.append("  STATUS: %s (%d of %d eligible cached)%s" % ("COMPLETE - outcome of record" if complete and not V1 else ("COMPLETE - re-posted cache (the outcome of record pot_ref_outcome.txt stands, write-once)" if complete else ("PILOT" if pilot or len(have) <= 12 else "PARTIAL")),
                                                            len(have), len(elig), "; the judged stage (refform_cell.py) is CONDITIONAL on C1 HELD" if complete else "; no outcome of record is written"))
    txt = "\n".join(L); print(txt)
    if V1: path = OUT_REPOST
    elif complete: path = OUT
    else: path = OUT.replace("outcome", "PILOT" if (pilot or len(have) <= 12) else "partial")
    if path == OUT and os.path.exists(OUT):
        print("[REPORT] %s exists and is the outcome of record (write-once): NOT rewritten; printed only" % OUT); return
    open(path, "w", encoding="utf-8").write(txt + "\n"); print("[REPORT] -> %s" % path)


def selftest():
    """The eligibility rule, the code extractor and the truncation detector on synthetic inputs (no call, no container),
    then the detector against the cache (mode=ro): the ORIGINAL raw of every cached row (raw_v1 where re-posted) must
    flag exactly TRUNCATED_OF_RECORD; the current raws are counted for second truncations."""
    assert eligible(["6 lbs", "7 lbs", "4.5 lbs", "5.8 lbs", "x"]) and not eligible(["a", "b", "3 m", "4 m"]) and not eligible([])
    assert eligible(["$4.20 \\times 10^{-2}$ atm", "1.00 \u00d7 10^6 N/m^2", "16,704 years", "-18 joules, -18 joules"])
    assert extract_code("text\n```python\nimport math\npick(2)\n```\nmore") == "import math\npick(2)"
    assert extract_code("```python\nx=1\n```\n```py\nimport math\npick(math.sqrt(4))\n```") == "import math\npick(math.sqrt(4))"
    assert extract_code("no code here") == "" and extract_code("x = 2 * 3\npick(x)") == "x = 2 * 3\npick(x)"
    assert amendment_number() is None or amendment_number().isdigit()
    # truncation detector, synthetic
    T = lambda s: truncated(s)[0]
    assert T("```python\nimport math\nx = 2 *")                       # (a) open fence, incomplete last line
    assert T("```python\nimport math\nr2 = 6")                        # (a) open fence, complete last line (cut after it)
    assert T("```python\nx = 1\n# Compute (")                          # (a) open fence, comment cut
    assert T("```python\nx = 1\n```\nprose\nlambda_m = lambda_nm * 1e-")   # (b) closed block, unfenced tail cut mid-literal
    assert not T("```python\nx = 2 * 3\npick(x)\n```")                  # closed program
    assert not T("```python\nx = 2 * 3\npick(x)\n```\n```")             # stray empty trailing fence (15 rows of the run)
    assert not T("```python\nx = 2 * 3\npick(x)\n```\n```\nYes.")      # stray fence + prose (q 9188)
    assert not T("```python\nx = 2 * 3\npick(x)\n```\nThe pick(6500) call selects the closest option (see above).")  # prose tail ending in punctuation
    assert not T("") and not T(None) and not T("x = 2 * 3\npick(x)")   # empty; bare complete program
    assert not T("ANSWER: B\nx = (")                                    # an ANSWER line settles it
    print("[POT-REF] selftest PASS (eligibility rule, code extraction, truncation detector synthetic, amendment lookup = %r)" % amendment_number())
    if not os.path.exists(CACHE):
        print("[POT-REF] no cache at %s: the 27-of-record check is skipped" % CACHE); return
    c = ro(CACHE)
    R = dict(c.execute("SELECT question_id, raw FROM answers")); V1 = repost_columns(c); c.close()
    orig = {q: (V1[q][0] if q in V1 else R[q]) for q in R}
    flagged = sorted(q for q in orig if truncated(orig[q])[0])
    print("[POT-REF] cache %s: %d rows | ORIGINAL raws flagged truncated: %d %s" % (os.path.basename(CACHE), len(R), len(flagged), flagged))
    extra = sorted(set(flagged) - set(TRUNCATED_OF_RECORD)); missing = sorted(set(TRUNCATED_OF_RECORD) - set(flagged))
    assert not extra and not missing, "detector != the 27 of record: extra %s, missing %s" % (extra, missing)
    now = sorted(q for q in R if truncated(R[q])[0])
    print("[POT-REF] exactly the %d of record flagged and no other of the %d | re-posted rows %d | CURRENT raws flagged (second truncations): %d %s"
          % (len(TRUNCATED_OF_RECORD), len(R), len(V1), len(now), now))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--run", action="store_true")
    ap.add_argument("--report", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--repost-truncated", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    pool_guard.assert_pool_of_record(POOL)
    if a.dry_run: dry_run()
    elif a.report: report()
    elif a.repost_truncated: repost_truncated(a.workers)
    elif a.pilot or a.run: run(a.pilot, a.workers)
    else: ap.print_help()
