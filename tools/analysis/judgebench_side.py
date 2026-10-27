"""JUDGEBENCH-REASONING-SIDE: on JudgeBench's GPT-4o split (correctness-grounded pairs, NO reference), does the reasoning
deployment of grok (arm S1, grok-4-1-fast-reasoning) reach the gold label more often than the generic judge (arm G,
grok-4-1-fast-non-reasoning) under the same recipe? (docs/judge_v2_program.md, "## Registered 2026-09-25 (before any code or
call; zero calls) - JUDGEBENCH-REASONING-SIDE", registration commit 6134573, section L17330-L17533, verbatim L17335-L17498;
POSTING GATE bracket L17502: POSTING AWAITS THE AUTHOR'S SIZE CONFIRMATION, 350 / 250 / 150.)

LAUNCH SEQUENCE (run-operator, after the READY and the author's size choice; L17498):
  python tools/ingest/judgebench_ingest.py --build ...                      # the corpus DB (see its docstring)
  python tools/analysis/judgebench_side.py --selftest                       # also under python -O
  python tools/analysis/judgebench_side.py --arm both --size N --dry-run    # 0 calls: pool line, payload anchors, costs
  python tools/analysis/judgebench_side.py --arm both --size N --pilot --go # 12 pairs x 2 orders x 2 arms = 48 calls;
                                                                            # guard per arm; writes judgebench_side_PILOT.txt
  python tools/analysis/judgebench_side.py --arm both --size N --go         # the run (refused unless BOTH pilots passed)
  python tools/analysis/judgebench_side.py --analyze --size N               # refuses partial caches for the file of record
N is the author's choice among the registered sizes {350, 250, 150}; there is NO default: every mode but --selftest refuses
without an explicit --size, and every posting mode refuses without --go.

INSTRUMENT (INSTRUMENT (a)-(c), L17367-L17379), nothing retyped:
  SYSTEM = pair_noref.noref_system_template()  [PAIR-NOREF's one-sentence swap REF_SENTENCE -> NOREF_SENTENCE, IMPORTED]
           .replace("$systemPrompt", rubric_value_contrast.GENERIC_SYSTEM)       [sha256 3a5e223c..., 130 chars]
           .replace("$rubric", rubric_value_contrast.GENERIC_RUBRIC)             [sha256 67f843eb..., 81 chars]
           + "\\n\\n" + rejudge_grok.SCHEMA_INSTRUCTION
  USER   = rejudge_grok.build_user_prompt(question, response_A, response_B) in order 1 and (question, response_B, response_A)
           in order 2; question and responses VERBATIM from the corpus DB (no robust_trace, no envelope unwrap).
  POST   = rejudge_reasoning.call_judge_full (PROVIDER azure, MAX_TOKENS 8192, TEMPERATURE None = the field OMITTED).
  PARSE  = rejudge_grok.parse_judge(rejudge_reasoning.strip_think(content)); combine = rejudge_grok.combine_orders (TIE on
           flip). The confidence field is kept in the raw content and never read.
  rejudge_reasoning.JUDGE_MODEL is a module global read by payload_body (rule-11 hazard): the arms run as TWO PROCESSES
  (--arm both spawns them together over the same registered order), each sets and re-asserts its model before every post
  and writes ITS OWN cache: judgebench_side_G_v1.db / judgebench_side_S1_v1.db at the repo root (ignored by .gitignore L58).

POPULATION AND ORDER (INSTRUMENT (d), L17380; SUPPORT variants L17443-L17447): the GPT split's pairs sorted by
  sha256("JUDGEBENCH-REASONING-SIDE|" + pair_id). 350 = all, no draw. 250 = the first K110 / R70 / M40 / C30 of each category
  in that order. 150 = K66 / R42 / M24 / C18 (the registration lists the 300 and 250 quotas, both exactly proportional to
  154 / 98 / 56 / 42 (x 6/7, x 5/7); 150's quotas are the same rule at x 3/7: a BUILDER'S DERIVATION, flagged for the READY).
  PILOT = the first 12 pairs of the size's schedule that give 3 per category.

CACHE (one per arm, WRITE-AHEAD; errors never cached; content_filter cached as an unusable row, rule 10):
  meta   pinned at first launch (test, arm, judge model, provider, max_tokens, temperature OMITTED, protocol, size, schedule
         set sha, pilot set sha, SYSTEM sha, corpus pairs table sha, script blob LF, payload_body source sha); any mismatch at
         a later launch REFUSES.
  posts  one row per (pair_id, order): payload sha256, content, provider, completion_tokens, elapsed, finish_reason,
         response id, refusal body, HTTP posts; INSERT-only (UPDATE / DELETE abort).
  invocation / resolution  the write-ahead journal: a PENDING row is committed BEFORE every call_judge_full; RETURNED /
         RAISED (with the HTTP posts it made) after it; an unresolved row at the next launch is an ORPHAN (counted as 1 post
         and disclosed). Append-only.
  launch the DB opens the arm process made (sqlite3.connect audit hook), per launch; the analysis's C0 (g) reads them.
GUARDS:
  - the post counter wraps urllib.request.urlopen in the arm process: every HTTP post (transport retries included) is
    counted; a post beyond the arm's cap ceil(1.1 x 2N) (770 at 350) or whose body sha differs from the journaled payload
    RAISES before the post;
  - PILOT GUARD per arm (INSTRUMENT (f), L17383): UNPARSED = parse INVALID, finish_reason length, content_filter, any other
    non-stop finish, or STOP-TRUNCATION (finish_reason stop and no strict-JSON verdict: parse_judge found it only by its
    regex fallback). The count and the bar are printed on every run; it REFUSES above 5% (2 or more of 24);
  - RUN LEVEL per arm: unparsed <= 5% of 2N posts, else C1 is UNDETERMINED BY VALIDITY (C0 (d));
  - ACCOUNTING (accepted_tests_ledger, CEILINGS["JUDGEBENCH-REASONING-SIDE"] = 1,540): before the first post each arm prints
    atl.guard (own = the test's ledgered calls; planned = its own remaining posts + the other arm's maximum remaining, so two
    simultaneous launches cannot jointly pass the ceiling), refuses a posting day that carries an ARCH-V2-PILOT-K46 row
    (L17461: never with the pilot) or a day total above 14,000, records a 0-call row "CEILING 1540" in the day ledger
    BEFORE the first post, and appends its HTTP posts at the end (finally), under a lock file; the ledger's per-arm rows must
    EQUAL the journal's posts at the start and the end of every launch (a ledger behind after a crash is caught up and
    labelled, a ledger ahead refuses);
  - the arm process refuses any sqlite3.connect other than its own cache and the corpus DB (audit hook; C0 (g)); reads_pool
    is none;
  - the analysis refuses to write the file of record from a partial cache (350 x 2 x 2 at N = 350); outcome files are
    WRITE-ONCE (mode "x").
READOUTS AND CRITERIA as registered (L17389-L17431): conventions A, B and JB; exact McNemar; pair bootstrap (10,000, seed
string "JUDGEBENCH-REASONING-SIDE" -> numpy seed int(sha256[:16], 16)); decomposition; length; position; side strata; C0-C3,
P1-P10 (the registrar's readings L17526 for the two-clause predictions), F1. P4b's formula (the registration names none; an
OPEN ITEM for the READY, L17526) is PINNED HERE: the symmetric (Shapley) split of the convention-A gain,
  accA = share x disc (share = committed / N, disc = committed accuracy);
  decisiveness part = (share_S1 - share_G) x (disc_G + disc_S1) / 2; discrimination part = (disc_S1 - disc_G) x
  (share_G + share_S1) / 2 (they sum to the gain exactly); P4b HELD iff gain > 0 and decisiveness part >= gain / 2,
  UNDETERMINED iff gain <= 0.

MUTANT (JBSIDE_SELFTEST_MUTANT) is a SELFTEST-ONLY switch; every posting mode refuses when it is set.

[DELTA 2026-09-25 on READY docs/reviews/READY_judgebench_reasoning_side.md (NOT READY at e5cac52), insertion only:
  D1  THE LAUNCH DAY: a launch fixes its day once (today()); no post is made once the local date differs from it (the launch
      stops cleanly, exit 6, and a relaunch resumes from the cache); the CEILING row and the launch's posts row are appended
      with day = the launch day, so journal and ledger agree PER DAY; the day checks (K46 row, day cap) read that day.
      Selftest: a simulated midnight (0 posts after it; ledger == journal per day; the relaunch reconciles); mutant
      day_rollover_unguarded.
  D2  at N 150 (DESCRIPTIVE_ONLY_SIZES) C1 prints its point, interval and p under C1.DESCRIPTIVE_ONLY and is never scored;
      P3 prints NOT SCORED; F1 is scored as registered and so labelled.
  D3  the MDE labels are the size's registered values (C1 8.4 / 10.0 / 12.9pp; interaction 17.5pp at 350 only, else the
      registration's formula at the size's group sizes, labelled planning).
  D4  (b) --go is admitted only with --arm both (a single-arm --go only as the child that parent spawned: --from-both and
      JBSIDE_BOTH_PARENT = its parent pid); (a) the refusal on a day carrying an ARCH-V2-PILOT-K46 row is kept.
  D6  --analyze / --pilot-report REFUSE --go.]
[DELTA 2 2026-09-25 on the delta READY (NOT READY at 20a6462, D11), insertion only:
  D11 (a) the selftest's main() probes run with arm_main / both_main / analyze / pilot_report replaced by SENTINELS that
      raise (restored in finally): a gate that fails to refuse FAILS the check, never executes; (b) analyze() and
      pilot_report() REFUSE the repo root whenever JBSIDE_SELFTEST_MUTANT is set; (c) mutant both_gate_open (KILLED by (a)).
  D12 the 0-call CEILING row is written by record_ceiling(day = the launch day) and checked on the launch day's ledger.
  D13 a launch (the pilot included) that stops at a date rollover exits 6 "STOPPED AT DATE ROLLOVER ... relaunch", not
      "the run is refused".]
"""
import argparse
import base64
import hashlib
import inspect
import json
import math
import os
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from fractions import Fraction

# ── the DB-open audit (installed BEFORE the imports below, so an import-time open is seen) ─────────────────────────────
_DB_OPENS = []
_DB_ALLOWED = None          # None = record only; a set of normalised paths = refuse anything else (the arm process)


def _norm_db(p):
    s = str(p)
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
    return os.path.normcase(os.path.abspath(s))


def _audit(event, args):
    if event == "sqlite3.connect":
        p = _norm_db(args[0])
        _DB_OPENS.append(p)
        if _DB_ALLOWED is not None and p not in _DB_ALLOWED:
            raise RuntimeError("[JBSIDE-LINT] sqlite3.connect(%s) REFUSED: the arm process may open only its own cache and"
                               " the corpus DB (C0 (g))" % p)


sys.addaudithook(_audit)

import urllib.request  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import sqlite3  # noqa: E402
import numpy as np  # noqa: E402
import rejudge_grok as rj  # noqa: E402
import rejudge_reasoning as rr  # noqa: E402
import pair_noref as pnr  # noqa: E402
import rubric_value_contrast as rvc  # noqa: E402
import accepted_tests_ledger as atl  # noqa: E402

IMPORT_DB_OPENS = list(_DB_OPENS)

TEST = "JUDGEBENCH-REASONING-SIDE"
ARMS = {"G": "grok-4-1-fast-non-reasoning", "S1": "grok-4-1-fast-reasoning"}
OTHER = {"G": "S1", "S1": "G"}
CCE_PER_CALL = {"G": 1, "S1": 10}           # COST (L17449): a reasoning call is priced 10 cce (FRAMEWORK L201, transported)
SIZES = (350, 250, 150)
CATS = ("knowledge", "reasoning", "math", "coding")
QUOTAS = {350: None, 250: {"knowledge": 110, "reasoning": 70, "math": 40, "coding": 30},
          150: {"knowledge": 66, "reasoning": 42, "math": 24, "coding": 18}}
CEILING_CALLS = 1540
CEILING_CCE = 8470
PILOT_PER_CAT = 3
PILOT_PAIRS = 12
UNPARSED_BAR = 0.05
FLOOR = 0.057                               # the test-retest floor (C1)
REG_MDE_C1 = {350: "8.4", 250: "10.0", 150: "12.9"}   # SUPPORT variants L17443-L17447 (d 0.33)
REG_MDE_INTERACTION = {350: "17.5"}                  # C2 SUPPORT L17439 (registered at 350 only)
DESCRIPTIVE_ONLY_SIZES = {150}                       # SUPPORT L17447 and the registrar's (f): C1 DESCRIPTIVE-ONLY at 150 (READY D2)
SEED = "JUDGEBENCH-REASONING-SIDE"
N_BOOT = 10000
MAX_TOKENS = 8192
PROVIDER = "azure"
DAY_CAP = 14000
PILOT_TEST = "ARCH-V2-PILOT-K46"
PROTOCOL = ("jbside-v1: SYSTEM = pair_noref.noref_system_template() with GENERIC_SYSTEM / GENERIC_RUBRIC + SCHEMA_INSTRUCTION;"
            " USER = rejudge_grok.build_user_prompt verbatim, order 1 (A, B), order 2 (B, A); call_judge_full azure, max_tokens"
            " 8192, temperature omitted; parse_judge(strip_think); combine_orders")
GENERIC_SYSTEM_SHA = "3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9"
GENERIC_RUBRIC_SHA = "67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc"
CORPUS_DB = os.path.join(ROOT, "judgebench_corpus_v1.db")
CORPUS_PAIRS_TABLE_SHA = "eee0193c4abf8f0003d319a9e7a04f3ba5a641d6498b4ea75d1832d9ab9b2064"   # ingest_manifest.json
SOURCE_GPT_SHA = "d5106306b38dead1b2e964ecf5534a3e7b2fc4b8d3b8da327599edfcebd76042"
OUT_DIR = os.path.join(ROOT, "experiment_results", "judgebench_side")
LEDGER_DIR = os.path.join(ROOT, "experiment_results")
MUTANT = os.environ.get("JBSIDE_SELFTEST_MUTANT") or None
MUTANTS = ("s1_temperature", "s1_max_tokens", "noref_swap_dropped", "size_gate_open", "guard_ignores_stop_trunc",
           "day_rollover_unguarded", "both_gate_open")


def refuse(msg):
    raise SystemExit("[JBSIDE] " + msg)


def need(cond, msg):
    if not cond:
        refuse(msg)


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def cache_path(arm, root=ROOT):
    return os.path.join(root, "judgebench_side_%s_v1.db" % arm)


def git_blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def script_pins():
    p = os.path.abspath(__file__)
    raw = open(p, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return {"blob": git_blob_lf(p), "sha256-lf16": hashlib.sha256(lf).hexdigest()[:16],
            "sha256-crlf16": hashlib.sha256(raw).hexdigest()[:16] if raw != lf else None}


def payload_body_source_sha():
    return sha256_text(inspect.getsource(rr.payload_body))


# ── the size gate ─────────────────────────────────────────────────────────────────────────────────────────────────────

def size_gate(size, go, mode):
    """mode in {'dry-run', 'post', 'analyze', 'pilot-report'}. No default size; posting needs --go."""
    if MUTANT == "size_gate_open":
        return size
    if size is None:
        refuse("--size is REQUIRED: the author's choice among %s (POSTING GATE, L17502); there is no default" % (SIZES,))
    if size not in SIZES:
        refuse("--size %r is not a registered size %s; refused" % (size, SIZES))
    if mode == "post" and not go:
        refuse("posting needs an explicit --go (the author's size confirmation is recorded by the registrar first)")
    if mode != "post" and go:
        refuse("--go is only for a posting launch")
    return size


# ── corpus, order, schedule ──────────────────────────────────────────────────────────────────────────────────────────

def open_ro(path):
    need(os.path.isfile(path), "%s not found" % path)
    for suf in ("-journal", "-wal"):
        need(not (os.path.exists(path + suf) and os.path.getsize(path + suf) > 0),
             "%s%s is non-empty: a writer is live or crashed; refused" % (path, suf))
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/"), uri=True)


def table_sha(conn, table, order):
    h = hashlib.sha256()
    for row in conn.execute("SELECT * FROM %s ORDER BY %s" % (table, order)):
        h.update((repr(row) + "\n").encode("utf-8"))
    return h.hexdigest()


def load_pairs(path=CORPUS_DB, expect_sha=CORPUS_PAIRS_TABLE_SHA):
    """{pair_id: row} of the GPT split, after the table sha and the source pin are verified (C0 (a))."""
    conn = open_ro(path)
    try:
        got = table_sha(conn, "pairs", "pair_id")
        if expect_sha is not None:
            need(got == expect_sha, "the corpus pairs table sha256 is %s, not the pinned %s (ingest_manifest.json); refused"
                 % (got, expect_sha))
        meta = dict(conn.execute("SELECT key, value FROM meta"))
        if expect_sha is not None:
            need(meta.get("source_gpt_sha256") == SOURCE_GPT_SHA, "the corpus's GPT source sha is not the pin")
        cols = ("pair_id", "category", "question", "response_A", "response_B", "label", "len_A", "len_B", "side_v2", "source")
        rows = {r[0]: dict(zip(cols, r)) for r in
                conn.execute("SELECT %s FROM pairs WHERE split = 'gpt' ORDER BY pair_id" % ", ".join(cols))}
    finally:
        conn.close()
    if expect_sha is not None:
        need(len(rows) == 350, "the corpus carries %d GPT rows, not 350 (C0 (a))" % len(rows))
    return rows, got


def registered_order(pids):
    return sorted(pids, key=lambda p: hashlib.sha256(("%s|%s" % (SEED, p)).encode("utf-8")).hexdigest())


def schedule(pairs, size):
    order = registered_order(pairs)
    q = QUOTAS[size]
    if q is None:
        need(len(order) == size, "size %d but %d pairs" % (size, len(order)))
        return order
    taken, sel = Counter(), []
    for p in order:
        c = pairs[p]["category"]
        if taken[c] < q[c]:
            taken[c] += 1
            sel.append(p)
    need(dict(taken) == q and len(sel) == size, "the draw gave %s, not the quotas %s" % (dict(taken), q))
    return sel


def pilot_of(pairs, sched):
    taken, sel = Counter(), []
    for p in sched:
        c = pairs[p]["category"]
        if taken[c] < PILOT_PER_CAT:
            taken[c] += 1
            sel.append(p)
        if len(sel) == PILOT_PAIRS:
            break
    need(len(sel) == PILOT_PAIRS and all(taken[c] == PILOT_PER_CAT for c in CATS), "pilot draw %s" % dict(taken))
    return sel


def set_sha(pids):
    return sha256_text("".join(p + "\n" for p in pids))


# ── prompts and bodies ───────────────────────────────────────────────────────────────────────────────────────────────

def system_prompt():
    need(sha256_text(rvc.GENERIC_SYSTEM) == GENERIC_SYSTEM_SHA and sha256_text(rvc.GENERIC_RUBRIC) == GENERIC_RUBRIC_SHA,
         "the GENERIC slot texts are not the registered ones (3a5e223c / 67f843eb)")
    if MUTANT == "noref_swap_dropped":
        import prompt_v2
        tmpl = prompt_v2.v2_system_template()
    else:
        tmpl = pnr.noref_system_template()
    return tmpl.replace("$systemPrompt", rvc.GENERIC_SYSTEM).replace("$rubric", rvc.GENERIC_RUBRIC) + "\n\n" + rj.SCHEMA_INSTRUCTION


def user_prompt(row, order):
    if order == 1:
        return rj.build_user_prompt(row["question"], row["response_A"], row["response_B"])
    return rj.build_user_prompt(row["question"], row["response_B"], row["response_A"])


def setup_arm(arm):
    """The arm process's ONE model: set the module globals payload_body reads (rule 11: once, in this process only)."""
    need(arm in ARMS, "arm %r" % arm)
    rr.PROVIDER = PROVIDER
    rr.JUDGE_MODEL = ARMS[arm]
    rr.MAX_TOKENS = MAX_TOKENS
    rr.TEMPERATURE = None
    if MUTANT == "s1_temperature" and arm == "S1":
        rr.TEMPERATURE = 0.0
    if MUTANT == "s1_max_tokens" and arm == "S1":
        rr.MAX_TOKENS = 4096


def assert_arm(arm):
    """Before every post (explicit raise: holds under -O)."""
    need(rr.JUDGE_MODEL == ARMS[arm] and rr.PROVIDER == PROVIDER and rr.MAX_TOKENS == MAX_TOKENS and rr.TEMPERATURE is None,
         "arm %s: rr globals drifted (model %r, provider %r, max_tokens %r, temperature %r); refused before the post"
         % (arm, rr.JUDGE_MODEL, rr.PROVIDER, rr.MAX_TOKENS, rr.TEMPERATURE))


def local_body(model, system, user):
    """A local rendering of rr.payload_body for the analysis's re-derivation (no global touched); the selftest and the
    analysis assert it equals rr.payload_bytes byte-for-byte for rr's current model."""
    return json.dumps({"model": model, "max_tokens": MAX_TOKENS,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode("utf-8")


def check_local_body(system, user):
    need(rr.TEMPERATURE is None and rr.MAX_TOKENS == MAX_TOKENS, "rr defaults drifted")
    need(local_body(rr.JUDGE_MODEL, system, user) == rr.payload_bytes(system, user),
         "local_body differs from rr.payload_bytes: rr.payload_body's rendering changed; refused")


def bodies_differ_only_in_model(b1, b2, m1, m2):
    """(ok, reasons): the two arms' request bodies are equal except "model"; no temperature; max_tokens 8192."""
    j1, j2 = json.loads(b1), json.loads(b2)
    why = []
    if j1.get("model") != m1 or j2.get("model") != m2:
        why.append("models %r / %r, expected %r / %r" % (j1.get("model"), j2.get("model"), m1, m2))
    for j in (j1, j2):
        if "temperature" in j:
            why.append("temperature present (%r)" % j["temperature"])
        if j.get("max_tokens") != MAX_TOKENS:
            why.append("max_tokens %r" % j.get("max_tokens"))
    r1 = {k: v for k, v in j1.items() if k != "model"}
    r2 = {k: v for k, v in j2.items() if k != "model"}
    if r1 != r2:
        why.append("the bodies differ outside 'model' (keys %s / %s)" % (sorted(r1), sorted(r2)))
    return (not why), why


def noref_swap_check(system):
    """(ok, reasons): SYSTEM == stack_norubric's generic system with REF_SENTENCE -> NOREF_SENTENCE and nothing else."""
    import prompt_v2
    import stack_norubric as snr
    ref_sys = (prompt_v2.v2_system_template().replace("$systemPrompt", snr.GENERIC_SYSTEM).replace("$rubric", snr.GENERIC_RUBRIC)
               + "\n\n" + rj.SCHEMA_INSTRUCTION)
    why = []
    if pnr.REF_SENTENCE not in ref_sys:
        why.append("stack_norubric's generic system lacks PAIR-NOREF's REF_SENTENCE")
    if ref_sys.replace(pnr.REF_SENTENCE, pnr.NOREF_SENTENCE, 1) != system:
        why.append("SYSTEM is not stack_norubric's generic system with the one sentence swapped")
    if pnr.REF_SENTENCE in system or "reference" in system.lower():
        why.append("SYSTEM still names a reference")
    if system.count(pnr.NOREF_SENTENCE) != 1:
        why.append("NOREF_SENTENCE occurs %d times" % system.count(pnr.NOREF_SENTENCE))
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    if any(ln.strip() and ln.strip() in src for ln in pnr.NOREF_SENTENCE.splitlines()):
        why.append("a line of the NOREF sentence is RETYPED in this script (it must be imported)")
    return (not why), why


# ── parsing and the unparsed classes ─────────────────────────────────────────────────────────────────────────────────

VOTE_NORM = {"MODEL A": "Model A", "MODEL B": "Model B", "TIE": "TIE", "DRAW": "TIE", "EQUAL": "TIE"}


def strict_verdict(text):
    """parse_judge's extraction WITHOUT its regex fallback: the JSON object parses and names a winner."""
    clean = text.strip()
    if "```json" in clean:
        ex = clean.split("```json", 1)[1].split("```", 1)[0].strip()
    else:
        a, b = clean.find("{"), clean.rfind("}")
        ex = clean[a:b + 1] if a != -1 and b > a else clean
    try:
        el = json.loads(ex, strict=False)
        return isinstance(el, dict) and str(el.get("winner", "")).strip().upper() in VOTE_NORM
    except Exception:
        return False


def classify(content, finish):
    """-> (vote for combine_orders in {Model A, Model B, TIE, INVALID}, unparsed class or None)."""
    text = rr.strip_think(content or "")
    vote, _conf = rj.parse_judge(text)
    if finish == "content_filter":
        return "INVALID", "content_filter"
    if finish == "length":
        return "INVALID", "length"
    if vote == "INVALID":
        return "INVALID", "parse_invalid"
    if finish != "stop":
        return vote, "finish_%s" % finish
    if MUTANT != "guard_ignores_stop_trunc" and not strict_verdict(text):
        return vote, "stop_truncation"
    return vote, None


def unparsed_readout(posts, pids):
    """(present, expected, unparsed classes Counter) over the posts of pids, both orders."""
    present, cls = 0, Counter()
    for p in pids:
        for o in (1, 2):
            r = posts.get((p, o))
            if r is None:
                continue
            present += 1
            _v, c = classify(r["content"], r["finish_reason"])
            if c:
                cls[c] += 1
    return present, 2 * len(pids), cls


def pilot_guard(arm, posts, pilot, out=print):
    """PASS / REFUSED / INCOMPLETE, printed on every call (rule 11)."""
    present, exp, cls = unparsed_readout(posts, pilot)
    k = sum(cls.values())
    state = "INCOMPLETE" if present < exp else ("PASS" if k <= UNPARSED_BAR * exp else "REFUSED")
    out("[PILOT-GUARD] arm %s: unparsed %d of %d posts (%s) = %.1f%% | bar %.0f%% (refuses at >= %d of %d) | present %d of %d"
        " -> %s" % (arm, k, exp, dict(cls) or "none", 100.0 * k / exp, 100 * UNPARSED_BAR,
                    int(math.floor(UNPARSED_BAR * exp)) + 1, exp, present, exp, state))
    return state


# ── scoring ──────────────────────────────────────────────────────────────────────────────────────────────────────────

INV = {"Model A": "Model B", "Model B": "Model A"}


def pair_outcomes(pairs, sched, posts):
    """Per pair of sched (all posts present): dict of the arm's readout variables."""
    out = []
    for p in sched:
        row = pairs[p]
        gold = "Model A" if row["label"] == "A>B" else "Model B"
        v1, c1 = classify(posts[(p, 1)]["content"], posts[(p, 1)]["finish_reason"])
        v2, c2 = classify(posts[(p, 2)]["content"], posts[(p, 2)]["finish_reason"])
        w, flip, inv = rj.combine_orders(v1, v2)
        v2m = INV.get(v2, v2)
        if v1 == "INVALID" or v2m == "INVALID":
            jb = None
        elif v1 == v2m:
            jb = None if v1 == "TIE" else v1
        elif v1 == "TIE":
            jb = v2m
        elif v2m == "TIE":
            jb = v1
        else:
            jb = None
        longer = "Model A" if row["len_A"] > row["len_B"] else ("Model B" if row["len_B"] > row["len_A"] else None)
        out.append({"pair_id": p, "category": row["category"], "side": row["side_v2"], "gold": gold, "winner": w,
                    "correct": int(w == gold), "committed": int(w in ("Model A", "Model B")), "tie": int(w == "TIE"),
                    "invalid": int(bool(inv)), "flip": int(bool(flip)), "jb_correct": int(jb == gold),
                    "longer": longer, "chose_longer": int(longer is not None and w == longer),
                    "v1": v1, "v2": v2, "unparsed": int(c1 is not None) + int(c2 is not None),
                    "nonterm": int(c1 == "length") + int(c2 == "length"),
                    "cf": int(c1 == "content_filter") + int(c2 == "content_filter"),
                    "stop_trunc": int(c1 == "stop_truncation") + int(c2 == "stop_truncation")})
    return out


def mcnemar_exact(b, c):
    """Exact two-sided McNemar, integer arithmetic (Fraction)."""
    n = b + c
    if n == 0:
        return Fraction(1)
    k = min(b, c)
    return min(Fraction(1), 2 * Fraction(sum(math.comb(n, i) for i in range(k + 1)), 2 ** n))


def rng():
    return np.random.default_rng(int(hashlib.sha256(SEED.encode("utf-8")).hexdigest()[:16], 16))


def arm_stats(o):
    n = len(o)
    com = sum(r["committed"] for r in o)
    cor = sum(r["correct"] for r in o)
    share = com / n
    disc = cor / com if com else float("nan")
    lc = [r for r in o if r["committed"] and r["longer"] is not None]
    d1 = [r["v1"] for r in o if r["v1"] in ("Model A", "Model B")]
    d2 = [r["v2"] for r in o if r["v2"] in ("Model A", "Model B")]
    valid = [r for r in o if not r["invalid"]]
    return {"n": n, "accA": cor / n, "correctA": cor, "committed": com, "accB": disc, "accJB": sum(r["jb_correct"] for r in o) / n,
            "correctJB": sum(r["jb_correct"] for r in o), "tie_rate": sum(r["tie"] for r in o) / n, "ties": sum(r["tie"] for r in o),
            "invalid": sum(r["invalid"] for r in o), "share": share, "disc": disc,
            "unparsed_posts": sum(r["unparsed"] for r in o), "posts": 2 * n,
            "nonterm_posts": sum(r["nonterm"] for r in o), "cf_posts": sum(r["cf"] for r in o),
            "stop_trunc_posts": sum(r["stop_trunc"] for r in o),
            "p_longer": (sum(r["chose_longer"] for r in lc) / len(lc)) if lc else float("nan"), "n_longer": len(lc),
            "flip_rate": (sum(r["flip"] for r in valid) / len(valid)) if valid else float("nan"), "n_valid": len(valid),
            "first_pos_1": (sum(v == "Model A" for v in d1) / len(d1)) if d1 else float("nan"), "n_d1": len(d1),
            "first_pos_2": (sum(v == "Model A" for v in d2) / len(d2)) if d2 else float("nan"), "n_d2": len(d2)}


def score(pairs, sched, postsG, postsS1, n_boot=N_BOOT):
    oG, oS = pair_outcomes(pairs, sched, postsG), pair_outcomes(pairs, sched, postsS1)
    n = len(sched)
    cat = np.array([CATS.index(r["category"]) for r in oG])
    a = {k: np.array([r[k] for r in oG], dtype=float) for k in ("correct", "committed", "jb_correct")}
    s = {k: np.array([r[k] for r in oS], dtype=float) for k in ("correct", "committed", "jb_correct")}
    gA = s["correct"] - a["correct"]
    b = int(((s["correct"] == 1) & (a["correct"] == 0)).sum())
    c = int(((s["correct"] == 0) & (a["correct"] == 1)).sum())
    p = mcnemar_exact(b, c)
    rc = np.isin(cat, [CATS.index("reasoning"), CATS.index("coding")])
    km = np.isin(cat, [CATS.index("knowledge"), CATS.index("math")])
    kr = np.isin(cat, [CATS.index("knowledge"), CATS.index("reasoning")])
    mc = np.isin(cat, [CATS.index("math"), CATS.index("coding")])

    def stats(idx):
        cs, cg = s["correct"][idx], a["correct"][idx]
        ms, mg = s["committed"][idx], a["committed"][idx]
        d = {"gainA": cs.mean() - cg.mean(),
             "gainB": (cs * ms).sum() / max(ms.sum(), 1) - (cg * mg).sum() / max(mg.sum(), 1),
             "gainJB": s["jb_correct"][idx].mean() - a["jb_correct"][idx].mean()}
        cc = cat[idx]
        gains = {}
        for i, nm in enumerate(CATS):
            m = cc == i
            gains[nm] = (cs[m].mean() - cg[m].mean()) if m.any() else float("nan")
        rcm, kmm, krm, mcm = np.isin(cc, [1, 3]), np.isin(cc, [0, 2]), np.isin(cc, [0, 1]), np.isin(cc, [2, 3])
        d["interaction"] = (cs[rcm].mean() - cg[rcm].mean()) - (cs[kmm].mean() - cg[kmm].mean())
        d["difficulty"] = (cs[krm].mean() - cg[krm].mean()) - (cs[mcm].mean() - cg[mcm].mean())
        for nm in CATS:
            d["gain_" + nm] = gains[nm]
        return d
    point = stats(np.arange(n))
    g = rng()
    boots = defaultdict(list)
    for _ in range(n_boot):
        idx = g.integers(0, n, n)
        for k, v in stats(idx).items():
            boots[k].append(v)
    ci = {k: (float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5)), float(np.nanstd(v, ddof=1))) for k, v in boots.items()}
    # support (SUPPORT, L17433-L17442): clusters = distinct question strings; Kish DEFF from the cluster sizes
    sizes = Counter(pairs[pid]["question"] for pid in sched).values()
    deff = sum(m * m for m in sizes) / sum(sizes)
    d_rate = (b + c) / n
    delta = point["gainA"]
    se = math.sqrt(max(d_rate - delta ** 2, 0.0) / n)
    stG, stS = arm_stats(oG), arm_stats(oS)
    dec = (stS["share"] - stG["share"]) * (stG["disc"] + stS["disc"]) / 2
    dis = (stS["disc"] - stG["disc"]) * (stG["share"] + stS["share"]) / 2
    base_longer = [r for r in oG if r["longer"] is not None]
    side = {}
    for sd in ("EVAL", "GATE", "TRAIN"):
        m = [i for i, r in enumerate(oG) if r["category"] == "knowledge" and r["side"] == sd]
        if m:
            side[sd] = (len(m), float(a["correct"][m].mean()), float(s["correct"][m].mean()))
    ncat = Counter(r["category"] for r in oG)
    return {"n": n, "G": stG, "S1": stS, "point": point, "ci": ci, "b": b, "c": c, "p": p, "deff": deff,
            "clusters": len(sizes), "n_eff": n / deff, "d": d_rate, "se": se, "mde": 2.80 * se,
            "dec_part": dec, "dis_part": dis, "base_longer": sum(r["longer"] == r["gold"] for r in base_longer) / max(1, len(base_longer)),
            "n_base_longer": len(base_longer), "side": side, "ncat": dict(ncat),
            "n_rc": int(rc.sum()), "n_km": int(km.sum()), "n_kr": int(kr.sum()), "n_mc": int(mc.sum())}


# ── the readout (every branch is executed by the selftest) ───────────────────────────────────────────────────────────

BRANCHES = ("C0.PASS", "C0.FAIL", "C1.REASONING_BETTER", "C1.GENERIC_BETTER", "C1.UNDETERMINED", "C1.UNDETERMINED_BY_VALIDITY",
            "F1.FIRED", "F1.NOT_FIRED", "F1.NOT_EVALUATED", "P.NOT_SCORED", "C1.DESCRIPTIVE_ONLY", "P3.NOT_SCORED") + tuple(
    "%s.%s" % (pp, v) for pp in ("P1", "P2", "P3", "P4a", "P4b", "P5a", "P5b", "P6", "P7", "P8a", "P8b", "P9a", "P9b")
    for v in ("HELD", "FAILED")) + ("P4b.UNDETERMINED",) + tuple(
    "%s.%s" % (pp, v) for pp in ("P10a", "P10b") for v in ("HELD", "FAILED"))


class Render:
    def __init__(self):
        self.lines, self.hit = [], set()

    def say(self, s=""):
        self.lines.append(s)

    def branch(self, bid, s):
        if bid not in BRANCHES:
            raise SystemExit("[JBSIDE] unregistered print branch %r" % bid)
        self.hit.add(bid)
        self.lines.append(s)


def pct(x):
    return "%.1f%%" % (100.0 * x) if x == x else "n/a"


def pp(x):
    return "%+.1fpp" % (100.0 * x) if x == x else "n/a"


def ci_s(ci, k):
    lo, hi, sd = ci[k]
    return "[%+.1f, %+.1f]pp (bootstrap SE %.1fpp)" % (100 * lo, 100 * hi, 100 * sd)


def hf(cond):
    return "HELD" if bool(cond) else "FAILED"


def render(res, c0, header):
    """res = score(...); c0 = [(label, ok bool, detail)]. Returns Render."""
    R = Render()
    for h in header:
        R.say(h)
    n, G, S = res["n"], res["G"], res["S1"]
    R.say("")
    R.say("=== C0 VALIDITY (first; any failure -> UNDETERMINED BY VALIDITY, no reading) ===")
    valid = True
    for label, ok, detail in c0:
        valid &= bool(ok)
        R.say("  [%s] %s  (%s)" % ("ok" if ok else "FAIL", label, detail))
    if valid:
        R.branch("C0.PASS", "  C0: PASS (all of (a)-(g))")
    else:
        R.branch("C0.FAIL", "  C0: FAILED -> the test is UNDETERMINED BY VALIDITY; C1 is not read")
    R.say("")
    R.say("=== READOUTS (denominator N = %d pairs, one per unique question; both orders; 95%% pair-bootstrap intervals) ===" % n)
    for arm, st in (("G", G), ("S1", S)):
        R.say("  arm %-2s %s: conv A %d / %d = %s | conv B %d / %d committed = %s | conv JB (lenient, descriptive) %d / %d = %s"
              % (arm, ARMS[arm], st["correctA"], n, pct(st["accA"]), st["correctA"], st["committed"], pct(st["accB"]),
                 st["correctJB"], n, pct(st["accJB"])))
        R.say("         ties %d (%s) | INVALID pairs %d | unparsed posts %d / %d (%s; length %d, content_filter %d,"
              " stop-truncation %d)" % (st["ties"], pct(st["tie_rate"]), st["invalid"], st["unparsed_posts"], st["posts"],
                                        pct(st["unparsed_posts"] / st["posts"]), st["nonterm_posts"], st["cf_posts"],
                                        st["stop_trunc_posts"]))
    R.say("  wrong(established): not applicable (no anchor, no board; external same-model pairs)")
    R.say("  PAIRED S1 - G: conv A %s %s | exact McNemar: S1-only %d vs G-only %d, p = %.4g | conv B %s %s | conv JB %s %s"
          % (pp(res["point"]["gainA"]), ci_s(res["ci"], "gainA"), res["b"], res["c"], float(res["p"]),
             pp(res["point"]["gainB"]), ci_s(res["ci"], "gainB"), pp(res["point"]["gainJB"]), ci_s(res["ci"], "gainJB")))
    R.say("  SUPPORT (measured): N %d; clusters (distinct questions) %d; DEFF (Kish, cluster sizes) %.2f; n_eff %.0f; discordance d"
          " = %d / %d = %.3f; SE = sqrt((d - delta^2) / N) = %.4f (bootstrap SE %.4f); MDE (80%%, two-sided 0.05) = 2.80 x SE ="
          " %.1fpp; registered planning MDE %spp at N %d, d 0.33 (SUPPORT variants L17443-L17447)" % (
              n, res["clusters"], res["deff"], res["n_eff"], res["b"] + res["c"], n, res["d"], res["se"], res["ci"]["gainA"][2],
              100 * res["mde"], REG_MDE_C1.get(n, "n/a"), n))
    R.say("")
    g, p = res["point"]["gainA"], res["p"]
    f1_fired = bool(g <= 0)
    R.say("=== C1 PRIMARY (pooled paired difference, convention A, S1 - G; point >= +5.7pp AND exact McNemar p < 0.05) ===")
    descriptive = n in DESCRIPTIVE_ONLY_SIZES
    if not valid:
        R.branch("C1.UNDETERMINED_BY_VALIDITY", "  C1: UNDETERMINED BY VALIDITY (C0 failed; the point %s is not read)" % pp(g))
        R.branch("F1.NOT_EVALUATED", "  FALSIFIER F1: NOT EVALUATED (C0 failed; a validity failure is not a falsification)")
        c1 = "UNDETERMINED BY VALIDITY"
    else:
        if descriptive:
            R.branch("C1.DESCRIPTIVE_ONLY", "  C1: DESCRIPTIVE-ONLY at N %d (registered MDE %spp >= the predicted +12pp; SUPPORT"
                     " L17447): point %s %s, exact McNemar p = %.4g; NOT SCORED, no verdict" % (
                         n, REG_MDE_C1.get(n, "n/a"), pp(g), ci_s(res["ci"], "gainA"), float(p)))
            c1 = "DESCRIPTIVE-ONLY (N %d)" % n
        elif bool(g >= FLOOR) and bool(p < Fraction(1, 20)):
            R.branch("C1.REASONING_BETTER", "  C1: REASONING BETTER (point %s >= +5.7pp, p = %.4g < 0.05)" % (pp(g), float(p)))
            c1 = "REASONING BETTER"
        elif bool(g <= -FLOOR) and bool(p < Fraction(1, 20)):
            R.branch("C1.GENERIC_BETTER", "  C1: GENERIC BETTER (point %s <= -5.7pp, p = %.4g < 0.05)" % (pp(g), float(p)))
            c1 = "GENERIC BETTER"
        else:
            R.branch("C1.UNDETERMINED", "  C1: UNDETERMINED (point %s, p = %.4g: inside the floor or not significant)"
                     % (pp(g), float(p)))
            c1 = "UNDETERMINED"
        if f1_fired:
            R.branch("F1.FIRED", "  FALSIFIER F1: FIRED (pooled conv-A point %s <= 0): the transport of J1's in-corpus +10.4pp"
                                 " is REFUTED on these pairs" % pp(g))
        else:
            R.branch("F1.NOT_FIRED", "  FALSIFIER F1: NOT FIRED (pooled conv-A point %s > 0)" % pp(g))
        if descriptive:
            R.say("  (F1 is scored as registered; at N %d it rests on a DESCRIPTIVE-ONLY contrast)" % n)
        R.say("  JOINED RECORD: C1 %s / F1 %s" % (c1, "FIRED" if f1_fired else "NOT FIRED"))
    R.say("  convention B beside C1 (does not decide): %s %s" % (pp(res["point"]["gainB"]), ci_s(res["ci"], "gainB")))
    R.say("")
    if n in REG_MDE_INTERACTION:
        mde_i = "registered MDE %spp for the interaction at N %d" % (REG_MDE_INTERACTION[n], n)
    else:
        mde_i = ("planning MDE %.1fpp for the interaction at N %d (the registration's formula 2.80 x sqrt(0.33 x (1/%d + 1/%d));"
                 " registered only at N 350)" % (280 * math.sqrt(0.33 * (1 / max(res["n_rc"], 1) + 1 / max(res["n_km"], 1))),
                                                 n, res["n_rc"], res["n_km"]))
    R.say("=== C2 SECONDARY, DESCRIPTIVE-ONLY (does not decide; %s) ===" % mde_i)
    R.say("  INTERACTION gain(reasoning + coding, n %d) - gain(knowledge + math, n %d) = %s %s"
          % (res["n_rc"], res["n_km"], pp(res["point"]["interaction"]), ci_s(res["ci"], "interaction")))
    R.say("  difficulty contrast gain(knowledge + reasoning, n %d) - gain(math + coding, n %d) = %s %s"
          % (res["n_kr"], res["n_mc"], pp(res["point"]["difficulty"]), ci_s(res["ci"], "difficulty")))
    for cn in CATS:
        R.say("  gain %-9s (n %3d): %s %s" % (cn, res["ncat"].get(cn, 0), pp(res["point"]["gain_" + cn]), ci_s(res["ci"], "gain_" + cn)))
    R.say("")
    R.say("=== C3 DESCRIPTIVE ===")
    for arm, st in (("G", G), ("S1", S)):
        R.say("  arm %-2s decisiveness (committed share) %s | discrimination (committed accuracy) %s | P(choose longer | committed,"
              " n %d) %s | flip rate %s of %d valid | first-position win share order 1 %s (n %d), order 2 %s (n %d)" % (
                  arm, pct(st["share"]), pct(st["disc"]), st["n_longer"], pct(st["p_longer"]), pct(st["flip_rate"]), st["n_valid"],
                  pct(st["first_pos_1"]), st["n_d1"], pct(st["first_pos_2"]), st["n_d2"]))
    R.say("  base rate: the longer response is correct on %s of %d pairs (registered 0.460 at N 350)"
          % (pct(res["base_longer"]), res["n_base_longer"]))
    R.say("  decomposition of the conv-A gain %s (P4b formula, pinned): decisiveness part %s + discrimination part %s"
          % (pp(g), pp(res["dec_part"]), pp(res["dis_part"])))
    for sd, (m, ag, as1) in sorted(res["side"].items()):
        R.say("  knowledge side %-5s (n %3d, mixed-side, disclosed): G %s, S1 %s, gain %s" % (sd, m, pct(ag), pct(as1), pp(as1 - ag)))
    R.say("  leakage readout: STRUCTURALLY NOT APPLICABLE (no reference; one response model); replaced by length and position")
    R.say("")
    R.say("=== PREDICTIONS (scored HELD / FAILED; the registrar's readings L17526) ===")
    upG, upS = G["unparsed_posts"] / G["posts"], S["unparsed_posts"] / S["posts"]
    if not valid:
        R.branch("P.NOT_SCORED", "  P1-P9: NOT SCORED (C0 failed: UNDETERMINED BY VALIDITY)")
    else:
        R.branch("P1." + hf(0.42 <= G["accA"] <= 0.62), "  P1 G conv A %s in [42%%, 62%%]: %s" % (pct(G["accA"]), hf(0.42 <= G["accA"] <= 0.62)))
        R.branch("P2." + hf(0.55 <= S["accA"] <= 0.75), "  P2 S1 conv A %s in [55%%, 75%%]: %s" % (pct(S["accA"]), hf(0.55 <= S["accA"] <= 0.75)))
        if descriptive:
            R.branch("P3.NOT_SCORED", "  P3 NOT SCORED: C1 is DESCRIPTIVE-ONLY at N %d (point %s, descriptive)" % (n, pp(g)))
        else:
            p3 = c1 == "REASONING BETTER" and 0.05 <= g <= 0.20
            R.branch("P3." + hf(p3), "  P3 C1 = REASONING BETTER with the point in [+5, +20]pp (C1 %s, point %s): %s" % (c1, pp(g), hf(p3)))
        p4a = G["tie_rate"] - S["tie_rate"] >= 0.05
        R.branch("P4a." + hf(p4a), "  P4a G tie rate %s - S1 tie rate %s = %s >= +5pp: %s" % (
            pct(G["tie_rate"]), pct(S["tie_rate"]), pp(G["tie_rate"] - S["tie_rate"]), hf(p4a)))
        if bool(g > 0):
            p4b = res["dec_part"] >= 0.5 * g
            R.branch("P4b." + hf(p4b), "  P4b decisiveness part %s >= half the conv-A gain %s: %s" % (pp(res["dec_part"]), pp(g), hf(p4b)))
        else:
            R.branch("P4b.UNDETERMINED", "  P4b UNDETERMINED (the conv-A gain %s is not > 0)" % pp(g))
        gb = res["point"]["gainB"]
        R.branch("P5a." + hf(gb > 0), "  P5a conv B gain %s > 0: %s" % (pp(gb), hf(gb > 0)))
        R.branch("P5b." + hf(gb < g), "  P5b conv B gain %s smaller than conv A's %s: %s" % (pp(gb), pp(g), hf(gb < g)))
        it = res["point"]["interaction"]
        R.branch("P6." + hf(it > 0), "  P6 INTERACTION %s > 0: %s" % (pp(it), hf(it > 0)))
        dc = res["point"]["difficulty"]
        R.branch("P7." + hf(abs(dc) < 0.10), "  P7 |difficulty contrast| %s < 10pp: %s" % (pp(dc), hf(abs(dc) < 0.10)))
        gains = {cn: res["point"]["gain_" + cn] for cn in CATS}
        top = max(CATS, key=lambda cn: gains[cn])
        R.branch("P8a." + hf(top in ("reasoning", "coding")), "  P8a the largest per-category gain is %s (%s): %s" % (
            top, pp(gains[top]), hf(top in ("reasoning", "coding"))))
        R.branch("P8b." + hf(gains["knowledge"] >= 0), "  P8b knowledge gain %s >= 0: %s" % (pp(gains["knowledge"]), hf(gains["knowledge"] >= 0)))
        p9a = G["p_longer"] > S["p_longer"]
        R.branch("P9a." + hf(p9a), "  P9a G P(longer | committed) %s > S1's %s: %s" % (pct(G["p_longer"]), pct(S["p_longer"]), hf(p9a)))
        base = res["base_longer"]
        p9b = G["p_longer"] > base or S["p_longer"] > base
        R.branch("P9b." + hf(p9b), "  P9b at least one arm above the measured base rate %s (registered 0.460): %s" % (pct(base), hf(p9b)))
    R.branch("P10a." + hf(upS <= 0.05), "  P10a S1 run-level unparsed %s <= 5%%: %s" % (pct(upS), hf(upS <= 0.05)))
    R.branch("P10b." + hf(upG <= 0.02), "  P10b G run-level unparsed %s <= 2%%: %s" % (pct(upG), hf(upG <= 0.02)))
    R.say("")
    R.say("NOT SHOWN: anything about the deployed recipe (it carries the reference), domain specialisation, the partition's cells,"
          " CodeJudgeBench (declined), other contestants, human preference, freedom from contamination; no word 'calibrated';"
          " every per-category or region reading is DESCRIPTIVE-ONLY at this size.")
    return R


# ── caches, journal, accounting ──────────────────────────────────────────────────────────────────────────────────────

CACHE_DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE posts (pair_id TEXT NOT NULL, ord INTEGER NOT NULL CHECK (ord IN (1, 2)), payload_sha256 TEXT NOT NULL,
    content TEXT NOT NULL, provider TEXT, completion_tokens INTEGER, elapsed REAL, finish_reason TEXT, response_id TEXT,
    refusal TEXT, http_posts INTEGER NOT NULL, ts TEXT NOT NULL, PRIMARY KEY (pair_id, ord));
CREATE TABLE invocation (seq INTEGER PRIMARY KEY, ts TEXT NOT NULL, day TEXT NOT NULL, launch TEXT NOT NULL,
    pair_id TEXT NOT NULL, ord INTEGER NOT NULL, payload_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK (state = 'PENDING'));
CREATE TABLE resolution (seq INTEGER PRIMARY KEY REFERENCES invocation(seq), ts TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('RETURNED', 'RAISED', 'ORPHAN')), http_posts INTEGER NOT NULL, note TEXT);
CREATE TABLE launch (launch TEXT PRIMARY KEY, arm TEXT NOT NULL, mode TEXT NOT NULL, started TEXT NOT NULL,
    db_opens TEXT NOT NULL);
CREATE TRIGGER invocation_cap BEFORE INSERT ON invocation WHEN (SELECT COUNT(*) FROM invocation) >=
    (SELECT CAST(value AS INTEGER) FROM meta WHERE key = 'arm_cap')
    BEGIN SELECT RAISE(ABORT, 'the arm cap of invocations is reached: refused BEFORE the post'); END;
CREATE TRIGGER resolution_needs_invocation BEFORE INSERT ON resolution WHEN NOT EXISTS
    (SELECT 1 FROM invocation i WHERE i.seq = NEW.seq) BEGIN SELECT RAISE(ABORT, 'no such invocation'); END;
"""
for _t in ("meta", "posts", "invocation", "resolution"):
    CACHE_DDL += ("CREATE TRIGGER %(t)s_no_update BEFORE UPDATE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
                  "CREATE TRIGGER %(t)s_no_delete BEFORE DELETE ON %(t)s BEGIN SELECT RAISE(ABORT, 'append-only'); END;\n"
                  % {"t": _t})


def arm_cap(size):
    """2N + 10%, rounded up, integer arithmetic (770 at 350; the two arms' caps sum to the registered 1,540)."""
    return (22 * size + 9) // 10


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"


def cache_meta(arm, size, sched, pilot, corpus_sha, system):
    return {"test": TEST, "arm": arm, "judge_model": ARMS[arm], "provider": PROVIDER, "max_tokens": str(MAX_TOKENS),
            "temperature": "OMITTED", "protocol": PROTOCOL, "size": str(size), "schedule_set_sha256": set_sha(sched),
            "pilot_set_sha256": set_sha(pilot), "system_sha256": sha256_text(system), "corpus_pairs_table_sha256": corpus_sha,
            "script_blob": script_pins()["blob"], "payload_body_source_sha256": payload_body_source_sha(),
            "arm_cap": str(arm_cap(size))}


def open_cache_rw(path, meta):
    """Create (meta pinned) or reopen (meta must match; 'created' excepted)."""
    exists = os.path.exists(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=DELETE")
    if not exists:
        conn.executescript(CACHE_DDL)
        conn.executemany("INSERT INTO meta VALUES (?, ?)", sorted(meta.items()) + [("created", now_iso())])
        conn.commit()
    got = dict(conn.execute("SELECT key, value FROM meta"))
    got.pop("created", None)
    if got != meta:
        diff = sorted(k for k in set(got) | set(meta) if got.get(k) != meta.get(k))
        conn.close()
        refuse("the cache %s was pinned with other meta (%s): judge, cap, temperature, protocol, set, corpus or script changed;"
               " refused" % (path, ", ".join("%s: %r -> %r" % (k, got.get(k), meta.get(k)) for k in diff)))
    return conn


def read_posts(conn):
    cols = ("pair_id", "ord", "payload_sha256", "content", "provider", "completion_tokens", "elapsed", "finish_reason",
            "response_id", "refusal", "http_posts")
    return {(r[0], r[1]): dict(zip(cols, r)) for r in conn.execute("SELECT %s FROM posts" % ", ".join(cols))}


def journal_state(conn):
    n_inv = conn.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
    unresolved = [r[0] for r in conn.execute("SELECT seq FROM invocation i WHERE NOT EXISTS (SELECT 1 FROM resolution r WHERE"
                                             " r.seq = i.seq) ORDER BY seq")]
    posts = conn.execute("SELECT COALESCE(SUM(http_posts), 0) FROM resolution").fetchone()[0]
    per_day = defaultdict(int)
    for day, hp in conn.execute("SELECT i.day, r.http_posts FROM invocation i JOIN resolution r ON r.seq = i.seq"):
        per_day[day] += hp
    by = dict(conn.execute("SELECT outcome, COUNT(*) FROM resolution GROUP BY outcome"))
    return {"invocations": n_inv, "unresolved": unresolved, "http_posts": int(posts), "per_day": dict(per_day), "by_outcome": by}


def resolve_orphans(conn, out=print):
    st = journal_state(conn)
    for seq in st["unresolved"]:
        conn.execute("INSERT INTO resolution VALUES (?, ?, 'ORPHAN', 1, ?)",
                     (seq, now_iso(), "posted with no reply recorded (the process died); counted as 1 post"))
        out("[ACCOUNT] invocation %d was POSTED with no reply recorded: an ORPHAN, counted as 1 post and disclosed" % seq)
    conn.commit()
    return len(st["unresolved"])


class LedgerLock:
    """An exclusive lock file beside the ledgers: the two arm processes append to one day file."""

    def __init__(self, ledger_dir, timeout=120):
        self.path = os.path.join(ledger_dir, ".judgebench_side_ledger.lock")
        self.timeout = timeout

    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.time() - t0 > self.timeout:
                    refuse("the ledger lock %s is held for more than %d s; refused (remove it only if no arm runs)"
                           % (self.path, self.timeout))
                time.sleep(0.2)

    def __exit__(self, *exc):
        os.close(self.fd)
        os.remove(self.path)


def arm_ledgered(arm, ledger_dir, day=None):
    """The test's day-ledger calls whose launch label names this arm ('arm=<arm> ...'); per day when day is None."""
    per = defaultdict(int)
    for f in atl.ledger_files(ledger_dir):
        b = os.path.basename(f)
        d = b[len("day_calls_"):-len(".json")] if b.startswith("day_calls_") else b
        for r in atl._rows(f):
            if r.get("test") == TEST and str(r.get("launch", "")).startswith("arm=%s " % arm):
                per[d] += int(r["calls"])
    return per if day is None else per.get(day, 0)


def reconcile(arm, conn, ledger_dir, out=print):
    orphans = resolve_orphans(conn, out)
    st = journal_state(conn)
    led = arm_ledgered(arm, ledger_dir)
    for day in sorted(set(st["per_day"]) | set(led)):
        j, l_ = int(st["per_day"].get(day, 0)), int(led.get(day, 0))
        need(l_ <= j, "the ledger of %s carries %d posts of arm %s but its journal %d: a ledger AHEAD is never reconciled"
             " downward; refused" % (day, l_, arm, j))
        if l_ < j:
            with LedgerLock(ledger_dir):
                atl.append(TEST, "arm=%s reconciled after crash: %d post(s) journaled on %s not ledgered" % (arm, j - l_, day),
                           j - l_, ledger_dir, day=day)
    check_equal(arm, conn, ledger_dir, "after the reconciliation")
    return orphans


def check_equal(arm, conn, ledger_dir, when):
    j = journal_state(conn)["http_posts"]
    l_ = sum(arm_ledgered(arm, ledger_dir).values())
    need(l_ == j, "(%s) the ledgers carry %d posts of arm %s but its journal %d: they must be EQUAL; refused" % (when, l_, arm, j))
    return j


def day_rows(ledger_dir, day):
    return atl._rows(atl.day_ledger_path(ledger_dir, day))


def accounting_guard(arm, size, own_remaining, ledger_dir, what, refuse_on_breach=True, out=print, day=None):
    """atl.guard with planned = own remaining + the other arm's maximum remaining; plus the day checks."""
    other_max = max(0, 2 * size - sum(arm_ledgered(OTHER[arm], ledger_dir).values()))
    planned = int(own_remaining) + other_max
    nums = atl.guard(TEST, planned, {}, ledger_dir, "%s; arm %s: own remaining %d + arm %s maximum remaining %d"
                     % (what, arm, own_remaining, OTHER[arm], other_max), refuse=refuse_on_breach)
    day = day or today()
    rows = day_rows(ledger_dir, day)
    total = sum(int(r["calls"]) for r in rows)
    pilot_today = sum(int(r["calls"]) for r in rows if r.get("test") == PILOT_TEST)
    has_pilot_row = any(r.get("test") == PILOT_TEST for r in rows)
    breaches = []
    if total + planned > DAY_CAP:
        breaches.append("day %s: %d + %d > %d" % (day, total, planned, DAY_CAP))
    if has_pilot_row:
        breaches.append("day %s carries %s rows (%d calls): this test never shares a posting day with it (L17461)"
                        % (day, PILOT_TEST, pilot_today))
    out("[ACCOUNT-DAY] %s arm %s: day %s ledger total %d + planned %d = %d of %d | %s rows today: %s -> %s" % (
        TEST, arm, day, total, planned, total + planned, DAY_CAP, PILOT_TEST, "yes" if has_pilot_row else "none",
        "OK" if not breaches else "REFUSED: " + "; ".join(breaches)))
    if breaches and refuse_on_breach:
        refuse("accounting: " + "; ".join(breaches))
    nums["day_breaches"] = breaches
    return nums


# ── the post counter (HTTP level) ────────────────────────────────────────────────────────────────────────────────────

class PostCapReached(RuntimeError):
    pass


class PostCounter:
    """Wraps urllib.request.urlopen IN THIS PROCESS: counts every HTTP post (transport retries included), refuses a post
    beyond the cap or whose body sha differs from the journaled one. The posted bytes are not touched."""

    def __init__(self, cap, already):
        self.cap, self.total, self.lock, self.tls = int(cap), int(already), threading.Lock(), threading.local()
        self.real = None

    def install(self):
        self.real = urllib.request.urlopen
        urllib.request.urlopen = self.urlopen

    def uninstall(self):
        if self.real is not None:
            urllib.request.urlopen = self.real

    def begin(self, sha):
        self.tls.n, self.tls.sha = 0, sha

    def count(self):
        return getattr(self.tls, "n", 0)

    def urlopen(self, req, *a, **k):
        data = getattr(req, "data", None)
        exp = getattr(self.tls, "sha", None)
        if exp is None or data is None or hashlib.sha256(data).hexdigest() != exp:
            raise PostCapReached("[JBSIDE] a post whose body is not the journaled payload (sha %s): refused BEFORE the post" % exp)
        with self.lock:
            if self.total + 1 > self.cap:
                raise PostCapReached("[JBSIDE] the arm cap of %d HTTP posts is reached: refused BEFORE the post" % self.cap)
            self.total += 1
        self.tls.n += 1
        return self.real(req, *a, **k)


# ── the arm process ──────────────────────────────────────────────────────────────────────────────────────────────────

def arm_main(arm, size, mode, go, workers, out=print):
    """mode in {'dry-run', 'pilot', 'run'}."""
    global _DB_ALLOWED
    size_gate(size, go, "dry-run" if mode == "dry-run" else "post")
    if mode != "dry-run":
        need(MUTANT is None, "JBSIDE_SELFTEST_MUTANT=%r is set: a selftest switch; posting refused" % MUTANT)
    cpath = cache_path(arm)
    _DB_ALLOWED = {_norm_db(CORPUS_DB), _norm_db(cpath)}
    out("[POOL] reads_pool: none (external JudgeBench pairs; no pool, view or verdict DB of record is opened)")
    out("[LINT] DB opens at import: %s" % (IMPORT_DB_OPENS or "none"))
    need(not IMPORT_DB_OPENS, "a DB was opened at import: %s" % IMPORT_DB_OPENS)
    setup_arm(arm)
    pairs, corpus_sha = load_pairs()
    sched = schedule(pairs, size)
    pilot = pilot_of(pairs, sched)
    system = system_prompt()
    ok, why = noref_swap_check(system)
    need(ok, "the no-reference swap check failed: %s" % why)
    anchor_body = rr.payload_bytes(system, user_prompt(pairs[sched[0]], 1))
    out("[ARM %s] judge %s | size %d | schedule set sha256 %s | pilot set sha256 %s (%d pairs, %d per category)"
        % (arm, ARMS[arm], size, set_sha(sched), set_sha(pilot), len(pilot), PILOT_PER_CAT))
    out("[ARM %s] SYSTEM sha256 %s (%d chars) | GENERIC_SYSTEM %s | GENERIC_RUBRIC %s | payload_body source sha256 %s"
        % (arm, sha256_text(system), len(system), GENERIC_SYSTEM_SHA[:16], GENERIC_RUBRIC_SHA[:16], payload_body_source_sha()[:16]))
    out("[ARM %s] PAYLOAD ANCHOR (pair 1 %s, order 1) sha256 %s" % (arm, sched[0], hashlib.sha256(anchor_body).hexdigest()))
    out("[ANCHOR-BODY %s] %s" % (arm, base64.b64encode(anchor_body).decode("ascii")))
    todo_pids = pilot if mode == "pilot" else sched
    shas = sorted(hashlib.sha256(rr.payload_bytes(system, user_prompt(pairs[p], o))).hexdigest() for p in sched for o in (1, 2))
    out("[ARM %s] payload set sha256 (the %d bodies of the schedule, sorted shas) %s" % (arm, len(shas), sha256_text("".join(s + "\n" for s in shas))))
    n_calls = 2 * size
    out("[COST] arm %s: %d calls x %d cce = %d cce (pilot %d calls = %d cce, inside the count) | arm HTTP cap %d"
        % (arm, n_calls, CCE_PER_CALL[arm], n_calls * CCE_PER_CALL[arm], 2 * PILOT_PAIRS, 2 * PILOT_PAIRS * CCE_PER_CALL[arm], arm_cap(size)))
    out("[COST] test at size %d: %d calls / %d cce (G %d + S1 %d); registered ceiling %d calls / %d cce (350 + 10%%)"
        % (size, 4 * size, 2 * size * (CCE_PER_CALL["G"] + CCE_PER_CALL["S1"]), 2 * size, 20 * size, CEILING_CALLS, CEILING_CCE))
    if mode == "dry-run":
        accounting_guard(arm, size, n_calls, LEDGER_DIR, "--dry-run (0 calls)", refuse_on_breach=False, out=out)
        out("[LINT] DB opens in this process: %s" % sorted(set(_DB_OPENS)))
        out("[DRY-RUN] arm %s: nothing posted" % arm)
        return 0
    # posting
    meta = cache_meta(arm, size, sched, pilot, corpus_sha, system)
    conn = open_cache_rw(cpath, meta)
    launch = "arm=%s size=%d %s %s pid %d" % (arm, size, mode, now_iso(), os.getpid())
    try:
        reconcile(arm, conn, LEDGER_DIR, out)
        posts = read_posts(conn)
        if mode == "run":
            need(pilot_guard(arm, posts, pilot, out) == "PASS", "the pilot guard of arm %s has not PASSED on this cache;"
                 " the run is refused" % arm)
        todo = [(p, o) for p in todo_pids for o in (1, 2) if (p, o) not in posts]
        out("[ARM %s] %s: %d posts to make (%d cached)" % (arm, mode, len(todo), len(posts)))
        st = journal_state(conn)
        day = today()                      # THE LAUNCH DAY (READY D1): every post, journal row and ledger row of this launch
        accounting_guard(arm, size, len(todo), LEDGER_DIR, "--%s --go" % mode, out=out, day=day)
        record_ceiling(arm, launch, day, LEDGER_DIR)
        counter = PostCounter(arm_cap(size), st["http_posts"])
        rr.load_env()
        counter.install()
        try:
            res = post_jobs(conn, todo, pairs, system, arm, launch, day, counter, workers, out, mode=mode)
        finally:
            counter.uninstall()
        return _after_launch(conn, arm, mode, pilot, res, out)
    finally:
        conn.close()


def today():
    """The local posting date (the day ledger's key). The selftest replaces it to simulate midnight."""
    return time.strftime("%Y-%m-%d")


def post_jobs(conn, todo, pairs, system, arm, launch, day, counter, workers, out, call_full=None, ledger_dir=None, mode="run"):
    """Post the jobs of ONE launch, all on the launch day `day`: once the local date differs from it, no further post is
    made (READY D1: a post after midnight would be journaled on one day and ledgered on another); the launch stops
    cleanly, its ledger row is appended ON `day` by finish_launch, and a relaunch resumes from the cache.
    Returns {"ok", "err", "posts", "rolled_over"}."""
    call_full = call_full or rr.call_judge_full
    lock = threading.Lock()
    stop = threading.Event()
    state = {"posts": 0, "rolled_over": False}

    def one(job):
        p, o = job
        if stop.is_set():
            return None
        if MUTANT != "day_rollover_unguarded" and today() != day:
            stop.set()
            state["rolled_over"] = True
            return None
        assert_arm(arm)
        user = user_prompt(pairs[p], o)
        body = rr.payload_bytes(system, user)
        sha = hashlib.sha256(body).hexdigest()
        with lock:
            try:
                cur = conn.execute("INSERT INTO invocation (ts, day, launch, pair_id, ord, payload_sha256, state) VALUES"
                                   " (?, ?, ?, ?, ?, ?, 'PENDING')", (now_iso(), day, launch, p, o, sha))
                conn.commit()
            except sqlite3.DatabaseError as e:
                conn.rollback()
                stop.set()
                raise PostCapReached("[JBSIDE] the journal refuses the invocation BEFORE the post: %s" % e)
            seq = cur.lastrowid
        counter.begin(sha)
        try:
            content, provider, tok, el, finish, msg = call_full(system, user)
        except BaseException as e:
            with lock:
                conn.execute("INSERT INTO resolution VALUES (?, ?, 'RAISED', ?, ?)",
                             (seq, now_iso(), counter.count(), "%s: %s" % (type(e).__name__, str(e)[:200])))
                conn.commit()
                state["posts"] += counter.count()
            if isinstance(e, PostCapReached):
                stop.set()
            raise
        with lock:
            conn.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (p, o, sha, content or "", provider, tok, el, finish, (msg or {}).get("_response_id"),
                          (msg or {}).get("_refusal"), counter.count(), now_iso()))
            conn.execute("INSERT INTO resolution VALUES (?, ?, 'RETURNED', ?, NULL)", (seq, now_iso(), counter.count()))
            conn.commit()
            state["posts"] += counter.count()
        return finish

    ok = err = 0
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(one, j): j for j in todo}
            for i, f in enumerate(as_completed(futs), 1):
                try:
                    if f.result() is not None:
                        ok += 1
                except Exception as e:  # noqa: BLE001  (never cached; the journal holds the RAISED row)
                    err += 1
                    out("  ERROR %s: %s" % (futs[f], str(e)[:160]))
                if i % 25 == 0 or i == len(todo):
                    out("  arm %s: %d/%d (ok %d, err %d, HTTP posts this launch %d)" % (arm, i, len(todo), ok, err, state["posts"]))
    finally:
        finish_launch(conn, arm, launch, mode, day, state["posts"], ledger_dir or LEDGER_DIR, out)
    if state["rolled_over"]:
        out("[ARM %s] the local date rolled over past the launch day %s: the launch STOPPED CLEANLY (no post after it; %d"
            " posts ledgered on %s); relaunch to resume from the cache" % (arm, day, state["posts"], day))
    return {"ok": ok, "err": err, "posts": state["posts"], "rolled_over": state["rolled_over"]}


def finish_launch(conn, arm, launch, mode, day, posts, ledger_dir, out):
    """The launch's ledger row ON its launch day (READY D1), its lint row, then ledger == journal."""
    with LedgerLock(ledger_dir):
        atl.append(TEST, "%s posts" % launch, posts, ledger_dir,
                   day=today() if MUTANT == "day_rollover_unguarded" else day)
    conn.execute("INSERT INTO launch VALUES (?, ?, ?, ?, ?)", (launch, arm, mode, now_iso(), json.dumps(sorted(set(_DB_OPENS)))))
    conn.commit()
    check_equal(arm, conn, ledger_dir, "at the end of the launch")


def record_ceiling(arm, launch, day, ledger_dir):
    """The 0-call CEILING row, ON the launch day (READY D1 / D12), before the first post."""
    with LedgerLock(ledger_dir):
        atl.append(TEST, "arm=%s CEILING %d calls / %d cce (registered) recorded before the first post of %s"
                   % (arm, CEILING_CALLS, CEILING_CCE, launch), 0, ledger_dir, day=day)


def _after_launch(conn, arm, mode, pilot, res, out):
    posts = read_posts(conn)
    state = pilot_guard(arm, posts, pilot, out)
    if res["rolled_over"]:                    # READY D13: a rollover is a clean stop, not a refusal (the pilot included)
        out("[ARM %s] %s STOPPED AT DATE ROLLOVER (pilot guard so far: %s); relaunch the same command to resume"
            % (arm, mode, state))
        return 6
    if mode == "pilot" and state != "PASS":
        out("[ARM %s] PILOT GUARD %s: the run is refused on this cache" % (arm, state))
        return 3
    return 0 if res["err"] == 0 else 4


# ── both arms: spawn together ────────────────────────────────────────────────────────────────────────────────────────

def both_gate(arm, go, from_both, env=None, ppid=None):
    """READY D4 (b): a posting launch (--go) is admitted ONLY as --arm both (the parent checks BOTH arms' pilot guards and
    launches the two arms together); a single-arm --go is admitted only as the child that parent spawned (--from-both AND
    the environment names this process's parent)."""
    if not go or arm == "both" or MUTANT == "both_gate_open":
        return
    env = os.environ if env is None else env
    ppid = os.getppid() if ppid is None else ppid
    if not (from_both and env.get("JBSIDE_BOTH_PARENT") == str(ppid)):
        refuse("--go with --arm %s is REFUSED: post only with --arm both (READY D4 (b): the parent checks both arms' pilot"
               " guards and launches the arms together)" % arm)


def spawn_arms(argv_tail, out=print):
    """Launch the two arm processes together; relay their lines prefixed; returns ({arm: rc}, {arm: lines})."""
    cmd0 = [sys.executable] + (["-O"] if sys.flags.optimize else []) + [os.path.abspath(__file__)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", JBSIDE_BOTH_PARENT=str(os.getpid()))
    procs = {arm: subprocess.Popen(cmd0 + ["--arm", arm, "--from-both"] + argv_tail, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace", env=env) for arm in ("G", "S1")}
    lines = {arm: [] for arm in procs}

    def pump(arm):
        for ln in procs[arm].stdout:
            ln = ln.rstrip("\n")
            lines[arm].append(ln)
            if not ln.startswith("[ANCHOR-BODY"):
                out("[%s] %s" % (arm, ln))
    th = [threading.Thread(target=pump, args=(a,)) for a in procs]
    for t in th:
        t.start()
    for t in th:
        t.join()
    return {arm: p.wait() for arm, p in procs.items()}, lines


def anchor_bodies(lines):
    got = {}
    for arm, ls in lines.items():
        for ln in ls:
            if ln.startswith("[ANCHOR-BODY %s] " % arm):
                got[arm] = base64.b64decode(ln.split("] ", 1)[1])
    return got


def both_main(size, mode, go, workers, out=print):
    size_gate(size, go, "dry-run" if mode == "dry-run" else "post")
    tail = ["--size", str(size), "--workers", str(workers)]
    tail += ["--dry-run"] if mode == "dry-run" else (["--pilot", "--go"] if mode == "pilot" else ["--go"])
    if mode == "run":
        pairs, _ = load_pairs()
        pilot = pilot_of(pairs, schedule(pairs, size))
        for arm in ("G", "S1"):
            need(os.path.exists(cache_path(arm)), "arm %s has no cache: run the pilot first" % arm)
            c = open_ro(cache_path(arm))
            try:
                need(pilot_guard(arm, read_posts(c), pilot, out) == "PASS", "arm %s's pilot guard has not PASSED: the run is"
                     " refused for BOTH arms (C0 (c))" % arm)
            finally:
                c.close()
    rcs, lines = spawn_arms(tail, out)
    bodies = anchor_bodies(lines)
    if set(bodies) == {"G", "S1"}:
        ok, why = bodies_differ_only_in_model(bodies["G"], bodies["S1"], ARMS["G"], ARMS["S1"])
        out("[BODY-DIFF] the two arms' anchor bodies differ ONLY in 'model' (no temperature, max_tokens %d): %s%s"
            % (MAX_TOKENS, "OK" if ok else "FAILED", "" if ok else " " + "; ".join(why)))
        if not ok:
            return 5
    else:
        out("[BODY-DIFF] anchors missing (%s): an arm failed before printing it" % sorted(bodies))
    out("[BOTH] exit codes %s" % rcs)
    if mode == "pilot" and all(rc == 0 for rc in rcs.values()):
        pilot_report(size, out)
    return max(rcs.values())


# ── pilot report and analysis (the parent reads both caches read-only) ───────────────────────────────────────────────

def load_arm_posts(arm, root=ROOT):
    c = open_ro(cache_path(arm, root))
    try:
        meta = dict(c.execute("SELECT key, value FROM meta"))
        posts = read_posts(c)
        js = journal_state(c)
        launches = [(r[0], json.loads(r[1])) for r in c.execute("SELECT launch, db_opens FROM launch ORDER BY launch")]
    finally:
        c.close()
    return meta, posts, js, launches


def write_once(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        refuse("%s exists; an outcome file is WRITE-ONCE (never overwritten); refused" % path)
    return sha256_text(text)


def refuse_mutant_on_root(root, what):
    """READY D11 (b): a process carrying a SELFTEST mutant never reads or writes the real caches and outcomes."""
    if MUTANT is not None and os.path.normcase(os.path.abspath(root)) == os.path.normcase(os.path.abspath(ROOT)):
        refuse("%s REFUSED: JBSIDE_SELFTEST_MUTANT=%r is set and the root is the repo root (selftest processes never touch"
               " the real caches or outcome files)" % (what, MUTANT))


def pilot_report(size, out=print, root=ROOT, out_dir=OUT_DIR, expect_sha=CORPUS_PAIRS_TABLE_SHA):
    refuse_mutant_on_root(root, "--pilot-report")
    size_gate(size, False, "pilot-report")
    pairs, _ = load_pairs(os.path.join(root, os.path.basename(CORPUS_DB)), expect_sha)
    pilot = pilot_of(pairs, schedule(pairs, size))
    L = ["=== JUDGEBENCH-REASONING-SIDE PILOT (12 pairs x 2 orders x 2 arms; registered guard, INSTRUMENT (f)) ===",
         "size %d | pilot set sha256 %s | pairs %s" % (size, set_sha(pilot), ", ".join(pilot))]
    states = {}
    for arm in ("G", "S1"):
        meta, posts, js, _ = load_arm_posts(arm, root)
        need(meta.get("size") == str(size), "arm %s's cache is pinned at size %s" % (arm, meta.get("size")))
        states[arm] = pilot_guard(arm, posts, pilot, L.append)
        L.append("  arm %s journal: invocations %d, HTTP posts %d, outcomes %s, unresolved %d" % (
            arm, js["invocations"], js["http_posts"], js["by_outcome"], len(js["unresolved"])))
    L.append("PILOT GUARD: %s" % ("PASS in both arms: the run may launch" if all(s == "PASS" for s in states.values())
                                  else "NOT PASSED (%s): the run is REFUSED" % states))
    L.append("(no accuracy is read from the pilot)")
    sha = write_once(os.path.join(out_dir, "judgebench_side_PILOT.txt"), "\n".join(L) + "\n")
    for ln in L:
        out(ln)
    out("[PILOT] wrote judgebench_side_PILOT.txt (write-once), sha256 %s" % sha)
    return states


def analyze(size, out=print, root=ROOT, out_dir=OUT_DIR, ledger_dir=LEDGER_DIR, expect_sha=CORPUS_PAIRS_TABLE_SHA):
    refuse_mutant_on_root(root, "--analyze")
    size_gate(size, False, "analyze")
    pairs, corpus_sha = load_pairs(os.path.join(root, os.path.basename(CORPUS_DB)), expect_sha)
    sched = schedule(pairs, size)
    pilot = pilot_of(pairs, sched)
    system = system_prompt()
    arms = {arm: load_arm_posts(arm, root) for arm in ("G", "S1")}
    c0 = [("(a) corpus pairs table sha256 = the pin, 350 GPT rows, source sha = the pin", corpus_sha == expect_sha,
           corpus_sha[:16])]
    check_local_body(system, user_prompt(pairs[sched[0]], 1))
    body_ok, body_why = True, []
    for arm, (meta, posts, _js, _l) in arms.items():
        need(meta.get("size") == str(size), "arm %s's cache is pinned at size %s, not %d" % (arm, meta.get("size"), size))
        exp = cache_meta(arm, size, sched, pilot, corpus_sha, system)
        for k in ("judge_model", "max_tokens", "temperature", "protocol", "schedule_set_sha256", "system_sha256",
                  "corpus_pairs_table_sha256", "payload_body_source_sha256"):
            if meta.get(k) != exp[k]:
                body_ok = False
                body_why.append("arm %s meta %s %r != %r" % (arm, k, meta.get(k), exp[k]))
        for (p, o), r in posts.items():
            if hashlib.sha256(local_body(ARMS[arm], system, user_prompt(pairs[p], o))).hexdigest() != r["payload_sha256"]:
                body_ok = False
                body_why.append("arm %s post %s/%d payload sha differs" % (arm, p, o))
                break
    bG = local_body(ARMS["G"], system, user_prompt(pairs[sched[0]], 1))
    bS = local_body(ARMS["S1"], system, user_prompt(pairs[sched[0]], 1))
    d_ok, d_why = bodies_differ_only_in_model(bG, bS, ARMS["G"], ARMS["S1"])
    c0.append(("(b) bodies differ only in 'model'; every cached payload sha re-derives; anchors G %s / S1 %s"
               % (hashlib.sha256(bG).hexdigest()[:16], hashlib.sha256(bS).hexdigest()[:16]), body_ok and d_ok,
               "; ".join(body_why + d_why) or "ok"))
    pg = {arm: pilot_guard(arm, v[1], pilot, lambda s: None) for arm, v in arms.items()}
    c0.append(("(c) pilot-12 guard passes in both arms", all(s == "PASS" for s in pg.values()), pg))
    complete = {arm: all((p, o) in v[1] for p in sched for o in (1, 2)) for arm, v in arms.items()}
    unp = {}
    for arm, v in arms.items():
        present, exp_n, cls = unparsed_readout(v[1], sched)
        unp[arm] = (sum(cls.values()), exp_n, dict(cls))
    c0.append(("(d) run-level unparsed <= 5% per arm", all(k <= UNPARSED_BAR * e for k, e, _ in unp.values()),
               "; ".join("%s %d/%d %s" % (a, k, e, c) for a, (k, e, c) in unp.items())))
    posted = {arm: v[2]["http_posts"] + 0 for arm, v in arms.items()}
    led = atl.ledger_calls(TEST, ledger_dir)
    tot = sum(posted.values())
    c0.append(("(e) posted calls <= %d and the day ledger agrees" % CEILING_CALLS, tot <= CEILING_CALLS and led == tot,
               "journal HTTP posts G %d + S1 %d = %d; ledgers %d" % (posted["G"], posted["S1"], tot, led)))
    c0.append(("(f) cache complete (%d x 2 x 2)" % size, all(complete.values()), complete))
    allowed = {arm: {_norm_db(os.path.join(root, os.path.basename(CORPUS_DB))), _norm_db(cache_path(arm, root))} for arm in arms}
    bad = {arm: [p for _l, opens in v[3] for p in opens if p not in allowed[arm]] for arm, v in arms.items()}
    c0.append(("(g) no DB other than its own cache and the corpus DB opened by either arm process",
               all(not b for b in bad.values()) and all(v[3] for v in arms.values()),
               "launches G %d / S1 %d; foreign %s" % (len(arms["G"][3]), len(arms["S1"][3]), bad)))
    header = ["=== JUDGEBENCH-REASONING-SIDE outcome (docs/judge_v2_program.md L17330-L17533; commit 6134573) ===",
              "size %d | schedule set sha256 %s | script blob %s | corpus pairs table %s" % (
                  size, set_sha(sched), script_pins()["blob"], corpus_sha),
              "reads_pool: none | %s" % atl.summary_line(TEST, {}, ledger_dir)]
    if not all(complete.values()):
        L = header + ["PARTIAL: the caches are incomplete (%s); no criterion is read. C0 so far:" % complete] + [
            "  [%s] %s (%s)" % ("ok" if ok else "FAIL", lab, det) for lab, ok, det in c0]
        path = os.path.join(out_dir, "judgebench_side_outcome_partial.txt")
        os.makedirs(out_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:     # a partial is not of record
            f.write("\n".join(L) + "\n")
        for ln in L:
            out(ln)
        out("[ANALYZE] PARTIAL -> %s (not of record)" % path)
        return None
    res = score(pairs, sched, arms["G"][1], arms["S1"][1])
    R = render(res, c0, header)
    sha = write_once(os.path.join(out_dir, "judgebench_side_outcome.txt"), "\n".join(R.lines) + "\n")
    for ln in R.lines:
        out(ln)
    out("[ANALYZE] wrote judgebench_side_outcome.txt (write-once), sha256 %s" % sha)
    return R


# ── selftest ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def _verdict(w):
    return json.dumps({"critique_a": "x", "critique_b": "y", "comparison": "z", "winner": w, "confidence": "0.8"})


def _synthetic(n_per_cat=(154, 98, 56, 42)):
    pairs = {}
    k = 0
    for cn, m in zip(CATS, n_per_cat):
        for i in range(m):
            pid = "syn-%s-%03d" % (cn, i)
            pairs[pid] = {"pair_id": pid, "category": cn, "question": "q %d" % k, "response_A": "a" * (10 + k % 7),
                          "response_B": "b" * (10 + (k * 3) % 11), "label": "A>B" if k % 2 else "B>A",
                          "len_A": 10 + k % 7, "len_B": 10 + (k * 3) % 11,
                          "side_v2": ("EVAL", "GATE", "TRAIN")[k % 3] if cn == "knowledge" else "NOT_IN_SPLIT", "source": cn}
            k += 1
    return pairs


def _posts_for(pairs, sched, rates, seed, unparsed=0.0, tie=0.0):
    """rates[cat] = P(correct committed) per pair; tie = P(tie); unparsed = P(stop-truncation on order 1)."""
    g = np.random.default_rng(seed)
    posts = {}
    for p in sched:
        gold = "Model A" if pairs[p]["label"] == "A>B" else "Model B"
        u = g.random()
        if u < tie:
            w1, w2 = "TIE", "TIE"
        elif u < tie + rates[pairs[p]["category"]] * (1 - tie):
            w1 = gold
            w2 = INV[gold]
        else:
            w1 = INV[gold]
            w2 = gold
        c1 = _verdict(w1)
        if g.random() < unparsed:
            c1 = '{"critique_a": "trunc... "winner": "%s"' % w1       # stop-truncation: regex finds the winner
        posts[(p, 1)] = {"content": c1, "finish_reason": "stop", "payload_sha256": "x"}
        posts[(p, 2)] = {"content": _verdict(w2), "finish_reason": "stop", "payload_sha256": "x"}
    return posts


def _e2e_fixture(root, syn, drop_one=False, foreign_open=False):
    """A temp root: a synthetic corpus DB (350 GPT rows, the pairs schema), both arms' caches written through open_cache_rw
    with the real meta, payload shas and journal rows, launch rows, and the matching day ledger. Returns (table sha, ledger dir)."""
    os.makedirs(root)
    cp = os.path.join(root, os.path.basename(CORPUS_DB))
    c = sqlite3.connect(cp)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    c.execute("INSERT INTO meta VALUES ('source_gpt_sha256', ?)", (SOURCE_GPT_SHA,))
    c.execute("CREATE TABLE pairs (pair_id TEXT PRIMARY KEY, split TEXT, source TEXT, category TEXT, question TEXT, response_A TEXT,"
              " response_B TEXT, label TEXT, len_A INTEGER, len_B INTEGER, side_v2 TEXT)")
    c.executemany("INSERT INTO pairs VALUES (?, 'gpt', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  [(p, r["source"], r["category"], r["question"], r["response_A"], r["response_B"], r["label"], r["len_A"],
                    r["len_B"], r["side_v2"]) for p, r in sorted(syn.items())])
    c.commit()
    c.close()
    pairs, csha = load_pairs(cp, None)
    sched = schedule(pairs, 350)
    pilot = pilot_of(pairs, sched)
    system = system_prompt()
    led = os.path.join(root, "ledgers")
    os.makedirs(led)
    rates = {"G": {k: 0.5 for k in CATS}, "S1": {k: 0.7 for k in CATS}}
    for i, arm in enumerate(("G", "S1")):
        posts = _posts_for(pairs, sched, rates[arm], 11 + i, 0.0, 0.1)
        conn = open_cache_rw(cache_path(arm, root), cache_meta(arm, 350, sched, pilot, csha, system))
        n = 0
        for p in sched:
            for o in (1, 2):
                if drop_one and arm == "S1" and p == sched[-1] and o == 2:
                    continue
                sha = hashlib.sha256(local_body(ARMS[arm], system, user_prompt(pairs[p], o))).hexdigest()
                cur = conn.execute("INSERT INTO invocation (ts, day, launch, pair_id, ord, payload_sha256, state) VALUES (?, '2026-01-02',"
                                   " 'arm=%s e2e', ?, ?, ?, 'PENDING')" % arm, (now_iso(), p, o, sha))
                conn.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (p, o, sha, posts[(p, o)]["content"], "azure:x", 10, 1.0,
                                                                                  "stop", "rid", None, 1, now_iso()))
                conn.execute("INSERT INTO resolution VALUES (?, ?, 'RETURNED', 1, NULL)", (cur.lastrowid, now_iso()))
                n += 1
        opens = [_norm_db(cp), _norm_db(cache_path(arm, root))] + ([_norm_db(os.path.join(root, "pool.db"))] if foreign_open else [])
        conn.execute("INSERT INTO launch VALUES ('arm=%s e2e', ?, 'run', ?, ?)" % arm, (arm, now_iso(), json.dumps(opens)))
        conn.commit()
        conn.close()
        atl.append(TEST, "arm=%s e2e posts" % arm, n, led, day="2026-01-02")
    return csha, led


def selftest():
    global _DB_ALLOWED
    import tempfile
    fails = []

    def check(cond, what):
        cond = bool(cond)
        print("  [%s] %s" % ("ok" if cond else "FAIL", what))
        if not cond:
            fails.append(what)
        return cond

    print("[JBSIDE SELFTEST] mutant %r | python -O %s" % (MUTANT, bool(sys.flags.optimize)))
    check(not IMPORT_DB_OPENS, "no DB is opened by the import chain (audit hook): %s" % (IMPORT_DB_OPENS or "none"))
    # 1 slot texts and the swap (imported, not retyped)
    check(sha256_text(rvc.GENERIC_SYSTEM) == GENERIC_SYSTEM_SHA and len(rvc.GENERIC_SYSTEM) == 130, "GENERIC_SYSTEM 3a5e223c, 130 chars")
    check(sha256_text(rvc.GENERIC_RUBRIC) == GENERIC_RUBRIC_SHA and len(rvc.GENERIC_RUBRIC) == 81, "GENERIC_RUBRIC 67f843eb, 81 chars")
    system = system_prompt()
    ok, why = noref_swap_check(system)
    check(ok, "SYSTEM = stack_norubric's generic system with REF -> NOREF only; NOREF imported, not retyped %s" % (why or ""))
    # 2 bodies: the two arm processes (spawned) differ only in model
    rcs, lines = {}, {}
    tmpd = tempfile.mkdtemp(prefix="jbside_selftest_")
    for arm in ("G", "S1"):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable] + (["-O"] if sys.flags.optimize else []) + [os.path.abspath(__file__), "--emit-anchor",
                            "--arm", arm], capture_output=True, text=True, env=env, encoding="utf-8")
        rcs[arm], lines[arm] = r.returncode, r.stdout.splitlines()
    bodies = anchor_bodies(lines)
    if check(set(bodies) == {"G", "S1"}, "both arm processes emitted their anchor body (rc %s)" % rcs):
        ok, why = bodies_differ_only_in_model(bodies["G"], bodies["S1"], ARMS["G"], ARMS["S1"])
        check(ok, "the two arms' request bodies differ ONLY in 'model'; no temperature; max_tokens 8192 %s" % (why or ""))
    check(json.loads(rr.payload_bytes("s", "u")).keys() == {"model", "max_tokens", "messages"} and rr.TEMPERATURE is None,
          "rr.payload_body omits temperature by default")
    try:
        check_local_body("s", "u")
        check(True, "local_body == rr.payload_bytes for rr's current model")
    except SystemExit as e:
        check(False, "local_body == rr.payload_bytes for rr's current model (%s)" % e)
    # 3 size gate
    for size, go, mode, want in ((None, True, "post", False), (300, True, "post", False), (350, False, "post", False),
                                 (350, True, "post", True), (250, True, "post", True), (150, False, "dry-run", True),
                                 (0, False, "dry-run", False), (350, True, "analyze", False)):
        try:
            size_gate(size, go, mode)
            got = True
        except SystemExit:
            got = False
        check(got == want, "size gate size=%r go=%r mode=%s -> %s" % (size, go, mode, "admitted" if got else "REFUSED"))
    # 4 the unparsed classes and the pilot guard
    check(classify(_verdict("Model A"), "stop") == ("Model A", None), "a clean verdict is parsed")
    check(classify('{"winner": "Model A", "comparison": "cut', "stop")[1] == "stop_truncation",
          "a stop-truncation (regex-only verdict) is UNPARSED")
    check(classify("", "content_filter") == ("INVALID", "content_filter"), "content_filter is UNPARSED, INVALID")
    check(classify(_verdict("Model B"), "length") == ("INVALID", "length"), "finish length is UNPARSED, INVALID")
    check(classify("no json at all", "stop") == ("INVALID", "parse_invalid"), "parse INVALID is UNPARSED")
    check(classify("<think>x</think>" + _verdict("TIE"), "stop") == ("TIE", None), "strip_think before parsing")
    pids = ["p%02d" % i for i in range(12)]
    good = {(p, o): {"content": _verdict("Model A"), "finish_reason": "stop"} for p in pids for o in (1, 2)}
    one_bad = dict(good)
    one_bad[("p00", 1)] = {"content": '{"winner": "Model A", "comp', "finish_reason": "stop"}
    two_bad = dict(one_bad)
    two_bad[("p01", 2)] = {"content": '{"winner": "Model B", "comp', "finish_reason": "stop"}
    two_len = dict(good)
    two_len[("p02", 1)] = {"content": "", "finish_reason": "length"}
    two_len[("p03", 1)] = {"content": "", "finish_reason": "content_filter"}
    part = {k: v for k, v in good.items() if k[0] != "p11"}
    q = []
    check(pilot_guard("G", good, pids, q.append) == "PASS", "pilot guard: 0 of 24 -> PASS")
    check(pilot_guard("G", one_bad, pids, q.append) == "PASS", "pilot guard: 1 of 24 (4.2%) -> PASS")
    check(pilot_guard("G", two_bad, pids, q.append) == "REFUSED", "pilot guard: 2 stop-truncations of 24 -> REFUSED")
    check(pilot_guard("G", two_len, pids, q.append) == "REFUSED", "pilot guard: length + content_filter of 24 -> REFUSED")
    check(pilot_guard("G", part, pids, q.append) == "INCOMPLETE", "pilot guard: 22 of 24 present -> INCOMPLETE")
    check(all("bar 5%" in s for s in q), "the guard prints its count and bar on every call")
    # 5 order, draws, pilot
    syn = _synthetic()
    for size in SIZES:
        sc = schedule(syn, size)
        cnt = Counter(syn[p]["category"] for p in sc)
        want = QUOTAS[size] or dict(zip(CATS, (154, 98, 56, 42)))
        check(dict(cnt) == want and sc == schedule(syn, size) and len(set(sc)) == size, "size %d draw %s" % (size, dict(cnt)))
        pl = pilot_of(syn, sc)
        check(Counter(syn[p]["category"] for p in pl) == Counter({c: 3 for c in CATS}) and pl == [p for p in sc if p in set(pl)],
              "size %d pilot = the first 3 per category in the schedule's order" % size)
    check(schedule(syn, 250) == [p for p in registered_order(syn) if p in set(schedule(syn, 250))], "the draw keeps the registered order")
    # 6 McNemar exact
    check(mcnemar_exact(0, 0) == 1 and mcnemar_exact(10, 0) == Fraction(2, 1024) and mcnemar_exact(5, 5) == 1, "exact McNemar")
    # 7 the readout: every registered print branch executed across scenarios
    sc = schedule(syn, 350)
    base = {c: 0.5 for c in CATS}
    scen = {  # name: (G rates, S1 rates, G stop-truncation rate, S1 stop-truncation rate, G tie rate, S1 tie rate)
        "reasoning_better": (dict(base), {c: 0.75 for c in CATS}, 0.0, 0.0, 0.25, 0.05),
        "moderate": ({c: 0.55 for c in CATS}, {c: 0.68 for c in CATS}, 0.0, 0.0, 0.10, 0.10),
        "generic_better": ({c: 0.75 for c in CATS}, dict(base), 0.0, 0.0, 0.05, 0.25),
        "equal": (dict(base), dict(base), 0.0, 0.0, 0.10, 0.10),
        "small": (dict(base), {"knowledge": 0.52, "reasoning": 0.60, "math": 0.52, "coding": 0.6}, 0.0, 0.0, 0.10, 0.10),
        "mixed": ({"knowledge": 0.4, "reasoning": 0.7, "math": 0.4, "coding": 0.7},
                  {"knowledge": 0.8, "reasoning": 0.7, "math": 0.8, "coding": 0.7}, 0.03, 0.03, 0.30, 0.0),
        "invalid": (dict(base), {c: 0.75 for c in CATS}, 0.10, 0.30, 0.25, 0.05),
    }
    hits = set()
    texts = {}
    for name, (rg, rs, upg, ups, tieg, ties) in scen.items():
        pg = _posts_for(syn, sc, rg, 1, upg, tieg)
        if name == "equal":
            ps = pg
        elif name == "moderate":       # paired: S1 = G with 24% of G's non-correct pairs turned correct (a ~ +12pp gain)
            g2 = np.random.default_rng(7)
            ps = dict(pg)
            for p_ in sc:
                gold = "Model A" if syn[p_]["label"] == "A>B" else "Model B"
                if classify(pg[(p_, 1)]["content"], "stop")[0] != gold and g2.random() < 0.24:
                    ps[(p_, 1)] = {"content": _verdict(gold), "finish_reason": "stop", "payload_sha256": "x"}
                    ps[(p_, 2)] = {"content": _verdict(INV[gold]), "finish_reason": "stop", "payload_sha256": "x"}
        else:
            ps = _posts_for(syn, sc, rs, 2, ups, ties)
        res = score(syn, sc, pg, ps, n_boot=300)
        valid = name != "invalid"
        c0 = [("(synthetic)", valid, "selftest")]
        R = render(res, c0, ["SELFTEST %s" % name])
        hits |= R.hit
        texts[name] = "\n".join(R.lines)
        check(abs(res["dec_part"] + res["dis_part"] - res["point"]["gainA"]) < 1e-12, "%s: decomposition parts sum to the gain" % name)
    check("C1: REASONING BETTER" in texts["reasoning_better"] and "JOINED RECORD: C1 REASONING BETTER / F1 NOT FIRED" in texts["reasoning_better"],
          "reasoning_better -> C1 REASONING BETTER / F1 NOT FIRED")
    check("C1: GENERIC BETTER" in texts["generic_better"] and "F1: FIRED" in texts["generic_better"], "generic_better -> GENERIC BETTER, F1 FIRED")
    check("C1: UNDETERMINED (" in texts["equal"] and "F1: FIRED" in texts["equal"], "equal -> UNDETERMINED / F1 FIRED (point 0)")
    check("(C1 REASONING BETTER, point" in texts["moderate"] and "P3.HELD" in hits, "moderate -> C1 REASONING BETTER, P3 HELD")
    check("UNDETERMINED BY VALIDITY" in texts["invalid"] and "F1: NOT EVALUATED" in texts["invalid"], "invalid -> UNDETERMINED BY VALIDITY, F1 NOT EVALUATED")
    # READY D2: at N 150 C1 and P3 are DESCRIPTIVE-ONLY (never scored); D3: the size's registered MDE labels
    sc150 = schedule(syn, 150)
    pg150 = _posts_for(syn, sc150, {c: 0.45 for c in CATS}, 3, 0.0, 0.10)
    ps150 = dict(pg150)
    for p_ in sc150:
        gold = "Model A" if syn[p_]["label"] == "A>B" else "Model B"
        ps150[(p_, 1)] = {"content": _verdict(gold), "finish_reason": "stop", "payload_sha256": "x"}
        ps150[(p_, 2)] = {"content": _verdict(INV[gold]), "finish_reason": "stop", "payload_sha256": "x"}
    R150 = render(score(syn, sc150, pg150, ps150, n_boot=300), [("(synthetic)", True, "selftest")], ["SELFTEST size150"])
    hits |= R150.hit
    t150 = "\n".join(R150.lines)
    check("C1.DESCRIPTIVE_ONLY" in R150.hit and "P3.NOT_SCORED" in R150.hit and not (R150.hit & {"C1.REASONING_BETTER",
          "C1.GENERIC_BETTER", "C1.UNDETERMINED", "P3.HELD", "P3.FAILED"}) and "C1: REASONING BETTER" not in t150,
          "N 150 (a +55pp gain): C1 DESCRIPTIVE-ONLY and P3 NOT SCORED, never a verdict (READY D2)")
    check("JOINED RECORD: C1 DESCRIPTIVE-ONLY (N 150) / F1 NOT FIRED" in t150, "N 150: F1 still scored, joined with C1 DESCRIPTIVE-ONLY")
    check("registered planning MDE 12.9pp at N 150" in t150 and "planning MDE" in t150 and "at N 150 (the registration's formula" in t150
          and "registered planning MDE 8.4pp at N 350" in texts["moderate"] and "registered MDE 17.5pp for the interaction at N 350"
          in texts["moderate"], "MDE labels follow the size: 8.4 / 17.5 at 350, 12.9 and the computed interaction MDE at 150 (READY D3)")
    missing = sorted(set(BRANCHES) - hits)
    check(not missing, "every registered print branch was EXECUTED (%d of %d)%s" % (len(set(BRANCHES) & hits), len(BRANCHES),
                                                                                  "; missing %s" % missing if missing else ""))
    # 8 write-once
    wp = os.path.join(tmpd, "o.txt")
    write_once(wp, "x\n")
    try:
        write_once(wp, "y\n")
        check(False, "an outcome file is write-once")
    except SystemExit:
        check(open(wp).read() == "x\n", "an outcome file is write-once (the second write refused, the first kept)")
    # 9 the cache: meta pin, append-only, the journal cap, orphans, ledger equality
    cp = os.path.join(tmpd, "judgebench_side_G_v1.db")
    meta = {"test": TEST, "arm": "G", "arm_cap": "3", "x": "1"}
    conn = open_cache_rw(cp, meta)
    for i in range(3):
        conn.execute("INSERT INTO invocation (ts, day, launch, pair_id, ord, payload_sha256, state) VALUES (?, '2026-01-01',"
                     " 'arm=G t', ?, 1, 's', 'PENDING')", (now_iso(), "p%d" % i))
    conn.commit()
    try:
        conn.execute("INSERT INTO invocation (ts, day, launch, pair_id, ord, payload_sha256, state) VALUES (?, '2026-01-01',"
                     " 'arm=G t', 'p9', 1, 's', 'PENDING')", (now_iso(),))
        check(False, "the journal's cap trigger refuses the invocation beyond the arm cap")
    except sqlite3.DatabaseError:
        conn.rollback()
        check(True, "the journal's cap trigger refuses the invocation beyond the arm cap")
    try:
        conn.execute("UPDATE meta SET value = '9' WHERE key = 'x'")
        check(False, "meta is append-only")
    except sqlite3.DatabaseError:
        conn.rollback()
        check(True, "meta is append-only")
    conn.execute("INSERT INTO resolution VALUES (1, ?, 'RETURNED', 2, NULL)", (now_iso(),))
    conn.commit()
    led = os.path.join(tmpd, "ledgers")
    os.makedirs(led)
    try:
        check_equal("G", conn, led, "selftest")
        check(False, "a ledger behind the journal is refused by the equality check")
    except SystemExit:
        check(True, "a ledger behind the journal is refused by the equality check")
    reconcile("G", conn, led, lambda s: None)
    st = journal_state(conn)
    check(st["by_outcome"].get("ORPHAN") == 2 and st["http_posts"] == 4 and sum(arm_ledgered("G", led).values()) == 4,
          "orphans resolved (2 x 1 post) and the ledger caught up to the journal (4 posts)")
    conn.close()
    try:
        open_cache_rw(cp, dict(meta, x="2"))
        check(False, "a cache pinned with other meta is refused")
    except SystemExit:
        check(True, "a cache pinned with other meta is refused")
    with LedgerLock(led):
        check(os.path.exists(os.path.join(led, ".judgebench_side_ledger.lock")), "the ledger lock is held")
    check(not os.path.exists(os.path.join(led, ".judgebench_side_ledger.lock")), "the ledger lock is released")
    # 10 the post counter
    pc = PostCounter(2, 1)
    seen = []

    class Req:
        def __init__(self, d):
            self.data = d
    pc.real = lambda req, *a, **k: seen.append(req.data) or "resp"
    pc.begin(hashlib.sha256(b"body").hexdigest())
    check(pc.urlopen(Req(b"body")) == "resp" and pc.total == 2 and pc.count() == 1, "the post counter counts and delegates")
    try:
        pc.urlopen(Req(b"body"))
        check(False, "a post beyond the arm cap is refused before the post")
    except PostCapReached:
        check(len(seen) == 1, "a post beyond the arm cap is refused before the post")
    pc2 = PostCounter(10, 0)
    pc2.real = pc.real
    pc2.begin(hashlib.sha256(b"body").hexdigest())
    try:
        pc2.urlopen(Req(b"other"))
        check(False, "a post whose body is not the journaled payload is refused")
    except PostCapReached:
        check(len(seen) == 1, "a post whose body is not the journaled payload is refused")
    # 11 the DB-open audit refuses a foreign DB in arm mode
    saved = _DB_ALLOWED
    _DB_ALLOWED = {_norm_db(cp)}
    try:
        sqlite3.connect(os.path.join(tmpd, "foreign.db")).close()
        check(False, "the arm-mode audit hook refuses a foreign sqlite3.connect")
    except RuntimeError:
        check(True, "the arm-mode audit hook refuses a foreign sqlite3.connect")
    finally:
        _DB_ALLOWED = saved
    # 12 static lint: every sqlite3.connect of this file sits in open_ro / open_cache_rw (plus the selftest's probe)
    import ast
    tree = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    owners = []
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "connect":
                    owners.append(fn.name)
    check(set(owners) <= {"open_ro", "open_cache_rw", "selftest", "_e2e_fixture"},
          "sqlite3.connect only in open_ro / open_cache_rw (lint): %s" % sorted(set(owners)))
    check([arm_cap(n) for n in SIZES] == [770, 550, 330] and 2 * arm_cap(350) == CEILING_CALLS, "arm caps 770 / 550 / 330; 2 x 770 = 1,540")
    # 13 end to end on a temp root: the real read path of --pilot-report and --analyze (caches, journal, ledgers, lint rows)
    root = os.path.join(tmpd, "e2e")
    csha, led = _e2e_fixture(root, syn, drop_one=False)
    q = []
    st = pilot_report(350, q.append, root=root, out_dir=os.path.join(root, "out"), expect_sha=csha)
    check(st == {"G": "PASS", "S1": "PASS"} and os.path.exists(os.path.join(root, "out", "judgebench_side_PILOT.txt")),
          "e2e: --pilot-report reads both caches, PASS, writes the PILOT file")
    R = analyze(350, q.append, root=root, out_dir=os.path.join(root, "out"), ledger_dir=led, expect_sha=csha)
    check(R is not None and "C0.PASS" in R.hit and os.path.exists(os.path.join(root, "out", "judgebench_side_outcome.txt")),
          "e2e: --analyze on complete caches -> C0 PASS (a)-(g), the outcome of record written")
    try:
        analyze(350, q.append, root=root, out_dir=os.path.join(root, "out"), ledger_dir=led, expect_sha=csha)
        check(False, "e2e: a second --analyze is refused (write-once)")
    except SystemExit:
        check(True, "e2e: a second --analyze is refused (write-once)")
    root2 = os.path.join(tmpd, "e2e_partial")
    csha2, led2 = _e2e_fixture(root2, syn, drop_one=True)
    R2 = analyze(350, q.append, root=root2, out_dir=os.path.join(root2, "out"), ledger_dir=led2, expect_sha=csha2)
    check(R2 is None and os.path.exists(os.path.join(root2, "out", "judgebench_side_outcome_partial.txt"))
          and not os.path.exists(os.path.join(root2, "out", "judgebench_side_outcome.txt")),
          "e2e: a partial cache writes only the _partial file (not of record)")
    root3 = os.path.join(tmpd, "e2e_foreign")
    csha3, led3 = _e2e_fixture(root3, syn, drop_one=False, foreign_open=True)
    R3 = analyze(350, q.append, root=root3, out_dir=os.path.join(root3, "out"), ledger_dir=led3, expect_sha=csha3)
    check(R3 is not None and "C0.FAIL" in R3.hit and "C1.UNDETERMINED_BY_VALIDITY" in R3.hit,
          "e2e: a launch that opened a foreign DB fails C0 (g) -> UNDETERMINED BY VALIDITY")
    # 14 READY D6 / D4 (b): --go refused with --analyze / --pilot-report and with a single arm
    for argv, what in ((["--analyze", "--size", "350", "--go"], "--analyze --go"), (["--pilot-report", "--size", "350", "--go"],
                       "--pilot-report --go"), (["--arm", "G", "--size", "350", "--go"], "--arm G --go"),
                       (["--arm", "S1", "--size", "350", "--pilot", "--go"], "--arm S1 --pilot --go"),
                       (["--arm", "S1", "--size", "350", "--go", "--from-both"], "--arm S1 --go --from-both without the parent's env")):
        # READY D11 (a): every real entry point main() could reach is a SENTINEL here, so a gate that fails to refuse
        # FAILS this check instead of executing (no real launch, analysis or pilot report from a selftest, mutant or not)
        G_ = globals()
        real_eps = {k: G_[k] for k in ("arm_main", "both_main", "analyze", "pilot_report")}

        def _sentinel(name):
            def f(*a, **k):
                raise RuntimeError("SENTINEL: main() reached the real %s" % name)
            return f
        try:
            for k in real_eps:
                G_[k] = _sentinel(k)
            main(argv)
            check(False, "%s is REFUSED (main returned)" % what)
        except SystemExit as e:
            check("--go" in str(e) or "REFUSED" in str(e), "%s is REFUSED by its gate (%s)" % (what, str(e)[:70]))
        except RuntimeError as e:
            check(False, "%s is REFUSED by its gate (%s)" % (what, e))
        finally:
            G_.update(real_eps)
    # READY D11 (b): with a selftest mutant set, analyze() / pilot_report() refuse the repo root before anything is read
    # (probed with out_dir / ledger_dir in the temp dir, so even a broken guard writes nothing real)
    saved_mut = MUTANT
    try:
        globals()["MUTANT"] = "probe"
        for name, fn in (("--analyze", lambda: analyze(350, lambda s: None, root=ROOT, out_dir=os.path.join(tmpd, "probe_out"),
                                                        ledger_dir=os.path.join(tmpd, "probe_led"))),
                         ("--pilot-report", lambda: pilot_report(350, lambda s: None, root=ROOT,
                                                                 out_dir=os.path.join(tmpd, "probe_out")))):
            try:
                fn()
                check(False, "%s with a mutant set refuses the repo root" % name)
            except SystemExit as e:
                check("JBSIDE_SELFTEST_MUTANT" in str(e), "%s with a mutant set refuses the repo root (%s)" % (name, str(e)[:60]))
    finally:
        globals()["MUTANT"] = saved_mut
    check(not os.path.exists(os.path.join(tmpd, "probe_out")), "the mutant-root probe wrote nothing")
    try:
        both_gate("S1", True, True, env={"JBSIDE_BOTH_PARENT": "4242"}, ppid=4242)
        check(True, "the child spawned by --arm both (--from-both, parent env = its ppid) is admitted")
    except SystemExit:
        check(False, "the child spawned by --arm both (--from-both, parent env = its ppid) is admitted")
    # 15 READY D1: a launch that crosses local midnight stops cleanly; its posts and ledger rows stay on the launch day
    global today
    real_today = today
    saved_rr = (rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE)
    rdir = os.path.join(tmpd, "rollover")
    os.makedirs(rdir)
    rled = os.path.join(rdir, "ledgers")
    os.makedirs(rled)
    rconn = open_cache_rw(os.path.join(rdir, "judgebench_side_S1_v1.db"), {"test": TEST, "arm": "S1", "arm_cap": "100"})
    clock = {"day": "2026-01-05", "posts": 0}
    try:
        setup_arm("S1")
        today = lambda: clock["day"]  # noqa: E731
        rpc = PostCounter(100, 0)
        rpc.real = lambda req, *a, **k: None

        def fake_call(system_, user_):
            rpc.urlopen(Req(rr.payload_bytes(system_, user_)))
            clock["posts"] += 1
            if clock["posts"] == 3:
                clock["day"] = "2026-01-06"          # midnight passes while the 3rd post is in flight
            return (_verdict("Model A"), "azure:fake", 5, 0.1, "stop", {"_response_id": "r"})
        rpairs = {p_: syn[p_] for p_ in sc[:4]}
        jobs = [(p_, o) for p_ in sc[:4] for o in (1, 2)]
        q = []
        record_ceiling("S1", "arm=S1 selftest-1", "2026-01-05", rled)
        check(any("CEILING" in str(r.get("launch")) and int(r["calls"]) == 0 for r in day_rows(rled, "2026-01-05")),
              "the 0-call CEILING row sits on the LAUNCH day's ledger (READY D12)")
        r1 = post_jobs(rconn, jobs, rpairs, system, "S1", "arm=S1 selftest-1", "2026-01-05", rpc, 1, q.append,
                       call_full=fake_call, ledger_dir=rled, mode="pilot")
        q13 = []
        check(_after_launch(rconn, "S1", "pilot", list(rpairs), r1, q13.append) == 6
              and any("STOPPED AT DATE ROLLOVER" in s and "relaunch" in s for s in q13),
              "a pilot launch that rolls over exits 6 'stopped at date rollover; relaunch' (not 'refused') (READY D13)")
        js = journal_state(rconn)
        check(r1["rolled_over"] and r1["posts"] == 3 and len(read_posts(rconn)) == 3,
              "rollover: the launch STOPS at midnight (3 posts, 0 after the date change) (READY D1)")
        check(js["per_day"] == {"2026-01-05": 3} and dict(arm_ledgered("S1", rled)) == {"2026-01-05": 3},
              "rollover: journal and ledger both carry the 3 posts on the LAUNCH day (%s / %s)" % (js["per_day"], dict(arm_ledgered("S1", rled))))
        try:
            reconcile("S1", rconn, rled, q.append)
            ok_rec = True
        except SystemExit:
            ok_rec = False
        rest = [j for j in jobs if j not in read_posts(rconn)]
        r2 = post_jobs(rconn, rest, rpairs, system, "S1", "arm=S1 selftest-2", "2026-01-06", rpc, 1, q.append,
                       call_full=fake_call, ledger_dir=rled, mode="run")
        js = journal_state(rconn)
        check(ok_rec and not r2["rolled_over"] and len(read_posts(rconn)) == 8 and js["per_day"] == dict(arm_ledgered("S1", rled))
              == {"2026-01-05": 3, "2026-01-06": 5},
              "rollover: the relaunch reconciles cleanly and resumes; ledger == journal PER DAY {01-05: 3, 01-06: 5}")
    except SystemExit as e:
        check(False, "rollover: a guard refused (%s)" % str(e)[:120])
    finally:
        today = real_today
        rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE = saved_rr
        rconn.close()
    print("[JBSIDE SELFTEST] %d failure(s)%s" % (len(fails), "" if not fails else ": " + "; ".join(fails)))
    return fails


def mutant_battery():
    """Each mutant must be KILLED: its selftest (a child process with JBSIDE_SELFTEST_MUTANT set) must report >= 1 failure."""
    killed = {}
    for m in MUTANTS:
        env = dict(os.environ, JBSIDE_SELFTEST_MUTANT=m, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable] + (["-O"] if sys.flags.optimize else []) + [os.path.abspath(__file__), "--selftest-one"],
                           capture_output=True, text=True, env=env, encoding="utf-8")
        fl = [ln for ln in r.stdout.splitlines() if ln.startswith("  [FAIL]")]
        killed[m] = (r.returncode != 0 and bool(fl), fl[:3])
        print("  [%s] mutant %-26s %s: %s" % ("ok" if killed[m][0] else "FAIL", m, "KILLED" if killed[m][0] else "SURVIVED",
                                               "; ".join(s.strip() for s in fl[:2]) or r.stdout[-300:]))
    return killed


def main(argv=None):
    ap = argparse.ArgumentParser(description="JUDGEBENCH-REASONING-SIDE (see the module docstring)")
    ap.add_argument("--arm", choices=["G", "S1", "both"])
    ap.add_argument("--size", type=int, default=None)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot-report", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-one", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--emit-anchor", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--from-both", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    if a.selftest or a.selftest_one:
        fails = selftest()
        if a.selftest_one:
            return 1 if fails else 0
        need(MUTANT is None, "run the battery without JBSIDE_SELFTEST_MUTANT")
        print("[JBSIDE SELFTEST] mutant battery (each must be KILLED):")
        killed = mutant_battery()
        n_surv = sum(1 for v in killed.values() if not v[0])
        print("[JBSIDE SELFTEST] %d check failure(s); mutants killed %d of %d" % (len(fails), len(killed) - n_surv, len(killed)))
        return 1 if (fails or n_surv) else 0
    if a.emit_anchor:
        # selftest helper: the arm process's anchor body on a synthetic pair (no DB, no post)
        need(a.arm in ARMS, "--emit-anchor needs --arm G|S1")
        setup_arm(a.arm)
        row = {"question": "Q?\n(A) x\n(B) y", "response_A": "resp A", "response_B": "resp B"}
        body = rr.payload_bytes(system_prompt(), user_prompt(row, 1))
        print("[ANCHOR-BODY %s] %s" % (a.arm, base64.b64encode(body).decode("ascii")))
        return 0
    if a.analyze:
        size_gate(a.size, a.go, "analyze")          # READY D6: --go with --analyze is REFUSED, never ignored
        analyze(a.size)
        return 0
    if a.pilot_report:
        size_gate(a.size, a.go, "pilot-report")
        pilot_report(a.size)
        return 0
    mode = "dry-run" if a.dry_run else ("pilot" if a.pilot else "run")
    need(a.arm, "--arm G | S1 | both is required")
    both_gate(a.arm, a.go, a.from_both)
    if a.arm == "both":
        return both_main(a.size, mode, a.go, a.workers)
    return arm_main(a.arm, a.size, mode, a.go, a.workers)


if __name__ == "__main__":
    sys.exit(main())
