"""K46-REPOST: the re-posting engine on the ARCH-V2-PILOT-K46 store for RP21's v2 leg (G17-CANARY v2 canary) and RP20
(V2-NONE-TEMPLATE, plus its optional ONE leg REF-PAIRED-V2). ZERO CALLS TO BUILD; every mode below except a --go launch is 0 calls.

REGISTRATION. NONE AT BUILD TIME. Built to the registrable drafts docs/agents/plans/2026-10-02_rp21_rp20_drafts.md (commit
41cd5cbd): section 1 (RP21 INSTRUMENT "v2 leg", THE v2 CANARY DRAW, Passes, READOUTS AND CRITERIA C0 / C1-v2 / C2-v2 / C3-v2,
PREDICTIONS P1-P4, P6, FALSIFIER), section 2 (RP20 INSTRUMENT arms C / T, Interleaving, Pilot, Analysis; C0, C1, C2, STRATA,
LEAKAGE; P1-P6; FALSIFIER), section 2b (the ONE leg: arms C1 / T1; its CRITERION, strata, P, FALSIFIER) and section 3 rows "v2 canary
draw" and "v2 repost engine". The registered texts BIND; any drift between them and this code is a delta of this script before its
READY (docs/reviews/READY_k46_repost.md, one READY for the canary and RP20 modes, under the RP32a template). The ONE leg is
ABOVE 4,000 matches with RP20 and needs the AUTHOR'S GO, quoted in the plan: AUTHOR_GO_ONE below is None and every ONE-leg
posting launch REFUSES until a delta sets it to that quotation.

[DELTA 2026-10-01, k46-repost2, the engine-coder, insertion only; after READY_paid_prereqs 89b50493 C-K1..C-K4, C-K6 and the merge
3679bae4; zero calls] REGISTERED since: G17-CANARY (RP21) docs/judge_v2_program.md L22762-L22784 and V2-NONE-TEMPLATE (RP20, with its
ONE leg) L22786-L22810 (767ebb79; headings "## Registered 2026-10-01 (before any code or call) — G17-CANARY (RP21): ..." / "— V2-NONE-
TEMPLATE (RP20), with its ONE leg REF-PAIRED-V2: ..."); the "NOT REGISTERED at build time" words below are history (D9).
  C-K1 THE INTERVAL FORM IS NORMAL (point +- z x the component-clustered SE) for RP21 C1-v2, RP20 C1 and the ONE leg's C1 (the
       orchestrator's ruling relayed 2026-10-01; R1 of 89b50493 for RP20 / ONE by registration); the percentile bounds are printed
       beside and decide nothing. PRECONDITIONS["interval_form"] = "normal".
  C-K2 THE ONE-LEG GO IS A COUNT CHECK (R6): AUTHOR_GO_ONE = "Yes, include it", and a ONE posting launch REFUSES unless that quotation
       occurs EXACTLY ONCE in the body of the section headed "## Amendment 34" of docs/plan_2026-09-15.md (the heading line excluded).
       Every rp20 / one launch and dry-run prints THE COMBINED STATEMENT: RP20 3,692 + ONE 1,636 = 5,328 matches > 4,000 (the
       4,000-match rule), authorised by Amendment 34 (verified / NOT verified).
  C-K3 the selftest kills OK8 (C1-v2 read on convention B), OK4 (a both-unusable pair not a difference) and OK5 (C0 (b)'s
       key-decidable census check removed): mutants c1v2_conv_b, both_unusable_same, census_off.
  C-K4 the canary set file experiment_results/archv2/g17_canary/g17_v2_canary_set.json is drawn (--freeze-canary, zero calls) and
       committed with this delta.
  C-K6 ORDERING OF RECORD: an rp20 or one POSTING launch REFUSES unless RP21's canary outcome of record exists and carries a "C1-v2: "
       line, and REFUSES when that word is FAILED (a FAILED C1-v2 re-registers RP20 pre-data); relaxing it is the research-lead's,
       in the record, by a delta.
  D5 the 20 extra seeds now run at the full B (registered "B 2,000 ... 20 more seeds beside").

LAUNCH SEQUENCE (the run-operator; each line 0 calls unless it carries --go):
  python tools/analysis/k46_repost.py --selftest                     fixtures under tempfile; a FAKE poster; socket guard
  python tools/analysis/k46_repost.py --mutants                      the mutant table, each mutant run against the selftest
  python tools/analysis/k46_repost.py --freeze-canary --dry-run      the v2 canary draw printed (set hash, order sha), NOT written
  python tools/analysis/k46_repost.py --freeze-canary                writes the set file WRITE-ONCE (mode "x"); committed BEFORE READY
  python tools/analysis/k46_repost.py --leg canary --pass v2-1 --dry-run   (and --leg rp20 / --leg one): pins, identity gate,
                                                                     every body decoded and checked, the TRANSPORT PREFLIGHT, the
                                                                     schedule sha, exact match and call counts, the day ledger
  python tools/analysis/k46_repost.py --leg canary --pass v2-1 --pilot 12 --go --budget 24
  python tools/analysis/k46_repost.py --leg canary --pass v2-1 --run --go --budget 576
  python tools/analysis/k46_repost.py --leg canary --pass v2-2 --pilot 12 --go --budget 24     (<= 7,200 s after v2-1's last row)
  python tools/analysis/k46_repost.py --leg canary --pass v2-2 --run --go --budget 576
  python tools/analysis/k46_repost.py --analyze-canary               -> g17_v2_canary_outcome.txt (write-once; complete caches only)
  python tools/analysis/k46_repost.py --leg rp20 --pilot 12 --go --budget 48   then --run --go --budget 7336
  python tools/analysis/k46_repost.py --analyze-rp20                 -> rp20_outcome.txt (write-once)
  (ONE leg: --leg one ..., --analyze-one, only after AUTHOR_GO_ONE is set by a delta)

GUARDS (every real mode):
  (1) The first line printed by every dry-run and analysis is the pool id pv2_41dbd3dbcd399df0 (the v2 split, draw 5a3e756; a posting
      launch prints its fail-closed [GATE] line first, before any database), checked against the store's run_meta
      pool_id; pool_guard.py's registry does not carry the pv2 pools (the draft's "verified by pool_guard.py --pool" cannot run as
      written: a registration item), so the pool is pinned through the store and the eval view sha (K46-KEY-READ's pins).
  (2) THE STORE experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db is opened ONLY mode=ro&immutable=1 (data_v2.ro.open_ro,
      sidecars refused), its sha256 44724d25... checked BEFORE and AFTER every launch, dry-run and analysis: a changed store REFUSES.
  (3) THE DB GUARD: every sqlite3.connect in the process is rewritten to mode=ro&immutable=1 after the -wal / -journal check; the
      ONLY writable file is the cache of the leg / pass being posted. stack_judge is STUBBED (sys.modules) before anything that could
      import it; consensus_fit (which imports it) is imported only after the stub, for the descriptive KEY coefficient.
  (4) BODIES: each stored body is zlib-decoded and must (a) hash to the stored payload_sha256, (b) equal
      rejudge_reasoning.payload_bytes(system, user) rebuilt from its own two messages (keys model / max_tokens / messages), with
      (c) rr.TEMPERATURE None and rr.MAX_TOKENS 8192; assert_body_source() checks rr.payload_body's SOURCE and that call_judge_full
      posts payload_bytes(system, user). Arm C posts the stored body byte-identically. Arm T swaps pair_noref.REF_SENTENCE ->
      NOREF_SENTENCE in messages[0] (exactly one occurrence before, none after), the user turn byte-identical, and the re-serialised
      body equals C's body outside the swapped span byte for byte. Arm T1 (ONE leg) removes "\n\n" + REFERENCE_MARKER + "\n" +
      <rendered reference> from the question slot (exactly one marker), asserts the result equals rejudge_grok.build_user_prompt
      (question, trace, trace), and swaps the system turn as T. The N1 sentences are read by AST from tools/analysis/pair_noref.py
      at the pinned blob (git blob of the LF rendering) 2696e2340e7c3cd982de3db66fe0a276a290dcd1, never imported (it imports
      stack_judge), never retyped.
  (5) POSTING: only with --go, an explicit --budget (calls) and the committed READY whose FIRST verdict line names K46-REPOST and
      this script's LF sha16. Before any post the launch PRINTS the exact matches and calls it will post and REFUSES (never trims)
      on: (i) the leg's ceiling (its cache rows vs its rows in every day ledger, the larger, + this launch); (ii) the 4,000-match
      rule (an arm-match is a match of record: RP20 = 1,846 x 2 = 3,692); (iii) THE DAY CAP: today's experiment_results/
      day_calls_<date>.json (every test) + this launch <= 14,000; (iv) planned calls <= --budget. The --budget is ALSO a hard cap
      inside the poster (the post that would exceed it is never made); a local-date change stops the launch (the 64ff708 rollover
      class); every invocation of call_judge_full is counted and appended to the posting-day ledger in a `finally`.
  (6) TRANSPORT (RP32a; the dry-run-skips-transport lesson): archv2_pilot.pilot.load_transport (rejudge_reasoning.load_env against the
      .env of $K46_REPOST_ENV_ROOT, else archv2_pilot's data root) and transport_preflight are IMPORTED and run inside --dry-run and
      before any cache, post or ledger row of a launch; a failure REFUSES. transport_check.py (b) runs with --env-var K46_REPOST_ENV_ROOT.
  (7) Every call is rejudge_reasoning.call_judge_full (rule 9); each order's reply is classified by judge_v2.writer.classify
      (parse version asserted equal to the store's: jv2-classify-1 + rj.parse_judge + rr.strip_think); the two orders are combined
      exactly as the store's match_verdict view (CONTENT_FILTER > NON_TERMINATED > INVALID > TIE on flip); finish_reason, response
      id and the provider fingerprint are cached; a foreign fingerprint STOPS the run (rr's content-filter sentinel excepted, cached as
      an unusable row, never re-posted); NON_TERMINATED is never a verdict and never a tie.
  (8) CACHES: one per leg / pass under experiment_results/archv2/k46_repost/, the K46 verdict-table columns keyed (arm, match_id,
      presentation_order); run_meta pinned at the first launch (test, leg, pass, judge, cap, temperature, protocol, set / schedule
      sha, store sha, N1 sha, script LF sha16) and a relaunch that differs is REFUSED; a relaunch never re-posts a cached job.
  (9) PILOT: the first 12 matches of the schedule (canary: 24 calls; RP20 / ONE: both arms, 48 calls); the truncation guard REFUSES
      --run above 5% unusable on the deciding subset (canary: all rows; RP20 / ONE: the key-decidable pilot rows) and on all rows.
  (10) OUTCOMES are WRITE-ONCE (mode "x"); a partial or pilot readout goes to a TIMESTAMPED *_PILOT / *_partial file, never
      overwritten, never the outcome of record. The interval form is a PRECONDITION (PRECONDITIONS["interval_form"]: "normal",
      "percentile" or "both_agree"; the drafts fix the cluster unit and the level, not the form: AMBIGUITY K1-class for the
      registrar); an analysis of record REFUSES while it is unset.

INTERVALS. Component-clustered bootstrap (CK-CLOSE components from the eval view's side table), B 2,000, numpy default_rng(42), 20
more seeds (43-62) beside; normal = point +- z x SE, percentile = the bootstrap quantiles; both printed.

MUTANT TABLE (--mutants; each a module switch K46R_MUTANT read by the code under test; KILLED = the selftest exits non-zero; the run
of record is in the commit message): swap_all (str.replace without the exactly-one check) | outside_byte_ok (the outside-span
equality not checked) | store_sha_off | transport_skipped (no preflight in the dry-run) | budget_cap_off | day_cap_off |
combine_flip_first (a flip reads as order 1's vote) | conv_b_decides (RP20 C1) | eq_95 (EQUIVALENT read on the 95% CI) |
c1v2_bar_strict (HELD iff UB < 0.15) | d_r_from_k46 (C1-v2 read on K46 vs v2-1) | window_off (v2-2's 2 h window) | one_per_comp_off
(the draw admits a second match of a component) | write_mode_w | kd_guard_off (the pilot guard on all rows only) |
falsifier_silent (RP20 GAIN/LOSS prints no falsifier sentence). Run of record at the build: 16 of 16 KILLED (python), the selftest
70 checks OK under python and python -O, 73 of 73 readout branches executed.
ZERO-CALL CHECK ON THE STORE OF RECORD at the build (read-only, immutable; no draw): identity gate PASS (2,664 / 818 / 1,846 / 2,661 /
3 / 3; combine() = the view on 2,664 of 2,664); RP20 3,692 jobs, every C and T slot (7,384) passing (4); ONE 1,636 jobs, every C1 and
T1 slot (3,272) passing (4); store sha256 equal after; transport_check.py (b) on --leg rp20 --dry-run: PASS (3,692 matches of record /
7,384 calls printed).
"""
import argparse
import ast
import datetime
import hashlib
import json
import math
import os
import sqlite3
import sys
import threading
import time
import types
import zlib
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ============================================================================================ stack_judge stub (FIRST)
class StubRefusal(RuntimeError):
    pass


class _StackJudgeStub(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        raise StubRefusal("stack_judge.%s refused: k46_repost never imports stack_judge (its open_cache opens read-write)" % name)


def install_stub():
    ex = sys.modules.get("stack_judge")
    if ex is not None and type(ex).__name__ != "_StackJudgeStub":     # a stub installed by this module run as __main__ is the same class by name
        raise SystemExit("[STUB] the real stack_judge module is loaded in this process; refused")
    if ex is None:
        sys.modules["stack_judge"] = _StackJudgeStub("stack_judge")
    return sys.modules["stack_judge"]


install_stub()
import numpy as np  # noqa: E402
import accepted_tests_ledger as atl  # noqa: E402
import rejudge_grok as rj  # noqa: E402
import rejudge_reasoning as rr  # noqa: E402
from data_v2 import ro as dv2ro  # noqa: E402
from judge_v2 import writer as JW  # noqa: E402
from judge_v2._base import REFERENCE_MARKER  # noqa: E402

TEST = "K46-REPOST"
POOL = "pv2_41dbd3dbcd399df0"
CV = "mmlu-pro-v2"
VINTAGE = "grok-reasoning-v0"
STORE_REL = os.path.join("experiment_results", "archv2", "pilot_k46", "pilot_k46_verdicts_run2.db")
STORE_SHA = "44724d25aa8653b49cef5ea85e99016f4e27f1c99819edc62073416eeec27793"
SPLIT_LABEL = "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"
EVAL_REL = os.path.join("data_v2", SPLIT_LABEL, "eval_view_REG.db")
EVAL_SHA = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"
RUN_ID = "ARCH-V2-PILOT-K46-run1"
JUDGE = "grok-4-1-fast-non-reasoning"
CAP = 8192
EXPECTED_FP = "azure:" + JUDGE
REFUSAL_FP = "azure:refusal"
BODY_KEYS = ["model", "max_tokens", "messages"]
PAIR_NOREF_REL = "pair_noref.py"
PAIR_NOREF_BLOB = "2696e2340e7c3cd982de3db66fe0a276a290dcd1"
VOTES = ("FIRST", "SECOND", "TIE", "INVALID", "NON_TERMINATED", "CONTENT_FILTER")
UNUSABLE = ("INVALID", "NON_TERMINATED", "CONTENT_FILTER")
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
IDENTITY = dict(scheduled=2664, one=818, none=1846, usable=2661, invalid=3, invalid_none=3, kd_none=1258, kd_none_comps=360,
                kd_one=544, kd_one_comps=160)
LEGS = {
    "canary": dict(test="G17-CANARY-V2", passes=("v2-1", "v2-2"), arms=("C",), ceiling=1260, registered_calls=1200, n_set=300,
                   seed="G17-V2-CANARY|20261002|"),
    "rp20": dict(test="V2-NONE-TEMPLATE", passes=(None,), arms=("T", "C"), ceiling=7750, registered_calls=7384, klass="NONE",
                 seed="V2-NONE-TEMPLATE|20261002|"),
    "one": dict(test="REF-PAIRED-V2", passes=(None,), arms=("T1", "C1"), ceiling=3440, registered_calls=3272, klass="ONE",
                seed="REF-PAIRED-V2|20261002|"),
}
AUTHOR_GO_ONE = "Yes, include it"   # [C-K2] the author's go, verbatim, plan Amendment 34; VERIFIED by count (go_one_check) at every ONE launch
PLAN_FILE = os.path.join(ROOT, "docs", "plan_2026-09-15.md")
GO_HEADING = "## Amendment 34"
COMBINED_MATCHES = 5328   # RP20 3,692 + ONE 1,636 (registration L22786-L22810; Amendment 34)
PILOT_N = 12
GUARD_RATE = 0.05
WINDOW_S = 7200
DAY_CAP = 14000
MATCH_RULE = 4000
C1V2_BAR = 0.15
EQ_DELTA = 0.040
BOOT_B, BOOT_SEED, EXTRA_SEEDS = 2000, 42, tuple(range(43, 63))
PRECONDITIONS = dict(interval_form="normal")    # [C-K1] NORMAL decides for RP21 C1-v2, RP20 and the ONE leg (orchestrator's ruling 2026-10-01)
INTERVAL_FORMS = ("normal", "percentile", "both_agree")
OUT_DIR = os.path.join(ROOT, "experiment_results", "archv2", "k46_repost")
SET_FILE = os.path.join(ROOT, "experiment_results", "archv2", "g17_canary", "g17_v2_canary_set.json")
READY_FILE = os.path.join(ROOT, "docs", "reviews", "READY_k46_repost.md")
LEDGER_DIR = os.path.join(DATA_ROOT, "experiment_results")
MUTANT = os.environ.get("K46R_MUTANT") or None
MUTANTS = ("swap_all", "outside_byte_ok", "store_sha_off", "transport_skipped", "budget_cap_off", "day_cap_off", "combine_flip_first",
           "conv_b_decides", "eq_95", "c1v2_bar_strict", "d_r_from_k46", "window_off", "one_per_comp_off", "write_mode_w",
           "kd_guard_off", "falsifier_silent", "c1v2_conv_b", "both_unusable_same", "census_off", "go_presence_only", "order_gate_off",
           "deff_boot", "analyze_no_configure")
_REAL_CALL_JUDGE_FULL = rr.call_judge_full
FORCE_C1_IV = {}      # SELFTEST-ONLY: leg -> interval fields that replace C1's computed interval (prescribed bounds through the REAL readout)
BRANCHES = frozenset([
    "CAN:C0:PASS", "CAN:C0:FAIL", "CAN:C1:HELD", "CAN:C1:FAILED", "CAN:C1:UND", "CAN:C1:UND_VALIDITY", "CAN:FALS:C1_FAILED",
    "CAN:FALS:P1_LOW", "CAN:FALS:NOT_FIRED", "CAN:FALS:NOT_EVALUATED",
    "RP20:C0:PASS", "RP20:C0:FAIL", "RP20:C1:EQUIVALENT", "RP20:C1:EQUIVALENT_SHIFT", "RP20:C1:GAIN", "RP20:C1:LOSS",
    "RP20:C1:UND", "RP20:C1:UND_VALIDITY", "RP20:C2:CHANGES", "RP20:C2:NOT_SHOWN", "RP20:C2:NO_FLOOR",
    "RP20:FALS:MOVES", "RP20:FALS:EQUIVALENT", "RP20:FALS:NEITHER", "RP20:FALS:NOT_EVALUATED",
    "ONE:C1:LOSS", "ONE:C1:GAIN", "ONE:C1:UND", "ONE:C1:UND_VALIDITY", "ONE:FALS:FIRES", "ONE:FALS:NOT_FIRED",
    "WRITE:RECORD", "WRITE:PARTIAL", "WRITE:REFUSED_EXISTS"]
    + ["CAN:%s:%s" % (p, v) for p in ("P1", "P2", "P3", "P4", "P6") for v in ("HELD", "FAILED", "UND")]
    + ["RP20:%s:%s" % (p, v) for p in ("P1", "P2", "P3", "P4", "P5", "P6") for v in ("HELD", "FAILED", "UND")]
    + ["ONE:%s:%s" % (p, v) for p in ("P1", "P2") for v in ("HELD", "FAILED", "UND")])
HIT = set()


def hit(tag):
    if tag not in BRANCHES:
        raise SystemExit("[BRANCH] undeclared branch tag %r" % tag)
    HIT.add(tag)


class Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    return Cfg(store_path=os.path.join(DATA_ROOT, STORE_REL), store_sha=STORE_SHA, eval_path=os.path.join(DATA_ROOT, EVAL_REL),
               eval_sha=EVAL_SHA, pool=POOL, cv=CV, run_id=RUN_ID, identity=dict(IDENTITY), n_set=LEGS["canary"]["n_set"],
               set_file=SET_FILE, out_dir=OUT_DIR, ledger_dir=LEDGER_DIR, ready=READY_FILE, pre=dict(PRECONDITIONS),
               pair_noref=os.path.join(HERE, PAIR_NOREF_REL), pair_noref_blob=PAIR_NOREF_BLOB, boot=BOOT_B,
               author_go_one=AUTHOR_GO_ONE, plan_file=PLAN_FILE, today=lambda: datetime.date.today(), now=time.time)


def say_factory(lines):
    def say(s):
        lines.append(s)
        print(s, flush=True)
    return say


# ============================================================================================ identities and pins
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def script_sha16_lf():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def git_blob_lf(path):
    b = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def load_n1(path, blob):
    """(REF_SENTENCE, NOREF_SENTENCE) read by AST from pair_noref.py at the pinned LF blob; never imported, never retyped."""
    got = git_blob_lf(path)
    if got != blob:
        raise SystemExit("[N1] %s is blob %s, not the pinned %s: refused" % (path, got, blob))
    tree = ast.parse(open(path, encoding="utf-8").read())
    vals = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in ("REF_SENTENCE", "NOREF_SENTENCE") and isinstance(node.value, ast.Constant):
            vals[node.targets[0].id] = node.value.value
    if set(vals) != {"REF_SENTENCE", "NOREF_SENTENCE"}:
        raise SystemExit("[N1] REF_SENTENCE / NOREF_SENTENCE not found as constants in %s" % path)
    return vals["REF_SENTENCE"], vals["NOREF_SENTENCE"]


def configure_rr():
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = CAP; rr.TEMPERATURE = None


def assert_body_source():
    import inspect
    src = inspect.getsource(rr.payload_body)
    if not ('payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src):
        raise SystemExit("[BODY] rejudge_reasoning.payload_body changed: refused")
    if "payload_bytes(system, user)" not in inspect.getsource(_REAL_CALL_JUDGE_FULL):
        raise SystemExit("[BODY] call_judge_full no longer posts payload_bytes(system, user): refused")
    if rr.TEMPERATURE is not None or rr.MAX_TOKENS != CAP or rr.JUDGE_MODEL != JUDGE:
        raise SystemExit("[BODY] rr is not configured to the recipe (temperature %r, max_tokens %r, model %r)"
                         % (rr.TEMPERATURE, rr.MAX_TOKENS, rr.JUDGE_MODEL))


# ============================================================================================ the DB guard
_TRUE_CONNECT = getattr(sqlite3.connect, "_true_connect", None) or sqlite3.connect
_WRITABLE = [None]
_OPENED = []


def _norm(database):
    s = str(database)
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
        if len(s) > 2 and s[0] == "/" and s[2] == ":":
            s = s[1:]
    return os.path.normcase(os.path.abspath(s))


def _guarded_connect(database, *a, **k):
    s = str(database)
    if s == ":memory:":
        return _TRUE_CONNECT(database, *a, **k)
    p = _norm(database)
    if _WRITABLE[0] is not None and p == _norm(_WRITABLE[0]):
        _OPENED.append(("rw", p))
        return _TRUE_CONNECT(database, *a, **k)
    ro = s.startswith("file:") and k.get("uri") and "mode=ro" in s.split("?", 1)[-1]
    if not ro:
        raise SystemExit("[DBGUARD] REFUSED: a read-write open of %s; the only writable file is %s" % (s, _WRITABLE[0]))
    if not os.path.isfile(p):
        raise SystemExit("[DBGUARD] %s is missing" % p)
    for suf in ("-wal", "-journal"):
        if os.path.exists(p + suf) and os.path.getsize(p + suf) > 0:
            raise SystemExit("[DBGUARD] REFUSED: %s%s is non-empty: a FAILED PRECONDITION" % (p, suf))
    k = dict(k); k["uri"] = True
    _OPENED.append(("ro-immutable", p))
    return _TRUE_CONNECT("file:%s?mode=ro&immutable=1" % p.replace("\\", "/"), *a, **k)


_guarded_connect._true_connect = _TRUE_CONNECT


def install_db_guard(writable=None):
    _WRITABLE[0] = writable
    sqlite3.connect = _guarded_connect


def remove_db_guard():
    sqlite3.connect = _TRUE_CONNECT
    _WRITABLE[0] = None


# ============================================================================================ the store
def to_contestant(vote, order, m):
    """vote FIRST / SECOND at presentation order -> 'A' / 'B' (the store's vote_contestant view); anything else unchanged."""
    if vote == "FIRST":
        return "A" if m["shown_first"][order] == m["a"] else "B"
    if vote == "SECOND":
        return "A" if m["shown_second"][order] == m["a"] else "B"
    return vote


def combine(c1, c2):
    """The store's match_verdict view: CONTENT_FILTER > NON_TERMINATED > INVALID > TIE on a flip > the common vote."""
    for bad in ("CONTENT_FILTER", "NON_TERMINATED", "INVALID"):
        if bad in (c1, c2):
            return bad
    if c1 != c2:
        return c1 if MUTANT == "combine_flip_first" else "TIE"
    return c1


def read_store(cfg, say):
    before = sha256_file(cfg.store_path)
    say("  store %s | sha256 BEFORE %s (%s)" % (cfg.store_path, before, "= the pin" if before == cfg.store_sha else "NOT the pin %s" % cfg.store_sha))
    if before != cfg.store_sha and MUTANT != "store_sha_off":
        raise SystemExit("[PIN] store sha256 %s != the pinned %s: refused" % (before, cfg.store_sha))
    c = dv2ro.open_ro(cfg.store_path)
    meta = dict(c.execute("SELECT key, value FROM run_meta").fetchall())
    sched = c.execute("SELECT run_id, match_id, presentation_order, variant_id, stem_key, component_id, contestant_a, contestant_b,"
                      " shown_first, shown_second, reference_row_id, batch_id FROM schedule").fetchall()
    verd = c.execute("SELECT match_id, presentation_order, vote, payload_sha256, body_zlib, finish_reason, response_model FROM verdict").fetchall()
    status = dict(c.execute("SELECT match_id, combined FROM match_status").fetchall())
    c.close()
    M = {}
    for rid, mid, order, var, stem, comp, a, b, sf, ss, ref, batch in sched:
        m = M.setdefault(mid, dict(mid=mid, run_id=rid, variant=var, stem=stem, comp=comp, a=a, b=b, ref=ref, anchor=(batch or "").strip().lower(),
                                   klass="ONE" if ref is not None else "NONE", shown_first={}, shown_second={}, vote={}, psha={},
                                   body={}, finish={}, model={}))
        m["shown_first"][order] = sf; m["shown_second"][order] = ss
    for mid, order, vote, psha, bz, fin, rm in verd:
        m = M[mid]
        m["vote"][order] = vote; m["psha"][order] = psha; m["body"][order] = bz; m["finish"][order] = fin; m["model"][order] = rm
    for m in M.values():
        m["k46"] = status.get(m["mid"], "PENDING")
        m["k46_mine"] = combine(*(to_contestant(m["vote"].get(o), o, m) for o in (1, 2))) if len(m["vote"]) == 2 else "PENDING"
    return M, meta, before


def store_after(cfg, before, say):
    a = sha256_file(cfg.store_path)
    say("  store sha256 AFTER %s (%s)" % (a, "EQUAL" if a == before else "DIFFERS from %s" % before))
    if a != before:
        raise SystemExit("[PIN] the store changed during this mode: refused")
    return a


def identity_gate(cfg, M, meta, say):
    I = cfg.identity
    comb = Counter(m["k46"] for m in M.values())
    rows = [("scheduled matches", len(M), I["scheduled"]),
            ("ONE (reference)", sum(1 for m in M.values() if m["klass"] == "ONE"), I["one"]),
            ("NONE (no reference)", sum(1 for m in M.values() if m["klass"] == "NONE"), I["none"]),
            ("usable (A / B / TIE)", comb["A"] + comb["B"] + comb["TIE"], I["usable"]),
            ("INVALID", comb["INVALID"], I["invalid"]),
            ("INVALID with NONE", sum(1 for m in M.values() if m["k46"] == "INVALID" and m["klass"] == "NONE"), I["invalid_none"]),
            ("both order verdicts", sum(1 for m in M.values() if len(m["vote"]) == 2), I["scheduled"]),
            ("the view's combined = this script's combine()", sum(1 for m in M.values() if m["k46"] == m["k46_mine"]), I["scheduled"])]
    ok = True
    say("IDENTITY GATE (refused on any mismatch, before any body is decoded):")
    for name, got, want in rows:
        ok &= got == want
        say("  %-48s %6d (registered %6d) %s" % (name, got, want, "OK" if got == want else "MISMATCH"))
    for key, want in (("pool_id", cfg.pool), ("run_id", cfg.run_id), ("judge_requested", JUDGE), ("max_tokens", str(CAP)),
                      ("temperature_label", "omitted"), ("parse_version", JW.PARSE_VERSION)):
        got = meta.get(key)
        ok &= got == want
        say("  run_meta %-38s %s %s" % (key, got, "OK" if got == want else "MISMATCH (want %s)" % want))
    if not ok:
        raise SystemExit("[IDENTITY-GATE] the store is not the object of record: refused")
    say("  -> IDENTITY GATE: PASS")


# ============================================================================================ bodies and arms
def stored_body(m, order):
    """-> (system, user, body bytes): the three assertions of (4)."""
    b = zlib.decompress(m["body"][order])
    if hashlib.sha256(b).hexdigest() != m["psha"][order]:
        raise SystemExit("[BODY] %s order %d: the decoded body does not hash to its payload_sha256" % (m["mid"], order))
    d = json.loads(b.decode("utf-8"))
    if list(d) != BODY_KEYS or d["model"] != JUDGE or d["max_tokens"] != CAP or len(d["messages"]) != 2 \
            or [x["role"] for x in d["messages"]] != ["system", "user"]:
        raise SystemExit("[BODY] %s order %d: the stored body is not the recipe's (keys %s)" % (m["mid"], order, list(d)))
    system, user = d["messages"][0]["content"], d["messages"][1]["content"]
    if rr.payload_bytes(system, user) != b:
        raise SystemExit("[BODY] %s order %d: rr.payload_bytes(system, user) != the stored body" % (m["mid"], order))
    return system, user, b


def swap_system(system, n1, where):
    ref, noref = n1
    if MUTANT != "swap_all":
        if system.count(ref) != 1:
            raise SystemExit("[SWAP] %s: the system turn carries REF_SENTENCE %d times (exactly one required)" % (where, system.count(ref)))
        if noref in system:
            raise SystemExit("[SWAP] %s: NOREF_SENTENCE already present before the swap" % where)
    s2 = system.replace(ref, noref)
    if ref in s2:
        raise SystemExit("[SWAP] %s: REF_SENTENCE still present after the swap" % where)
    return s2


def check_outside_span(bc, bt, n1, where):
    """Every byte of the T body outside the swapped span equals C's."""
    er, en = json.dumps(n1[0])[1:-1].encode("utf-8"), json.dumps(n1[1])[1:-1].encode("utf-8")
    if bc.count(er) != 1:
        raise SystemExit("[SWAP] %s: the serialised REF span occurs %d times in the stored body" % (where, bc.count(er)))
    i = bc.index(er)
    ok = bt == bc[:i] + en + bc[i + len(er):]
    if not ok and MUTANT != "outside_byte_ok":
        raise SystemExit("[SWAP] %s: the T body differs from C's outside the swapped span" % where)
    return True


def _fragments():
    t = rj.USER_TEMPLATE
    f0, rest = t.split("$query"); f1, rest = rest.split("$traceA"); f2, f3 = rest.split("$traceB")
    return f0, f1, f2, f3


def strip_reference(user, where):
    """T1: the question slot without "\\n\\n" + REFERENCE_MARKER + "\\n" + rendered; asserted equal to rj.build_user_prompt."""
    f0, f1, f2, f3 = _fragments()
    if not (user.startswith(f0) and user.endswith(f3)):
        raise SystemExit("[T1] %s: the user turn does not open / close with the template" % where)
    mid_ = user[len(f0):len(user) - len(f3)]
    qi = mid_.find(f1); q = mid_[:qi]; rest = mid_[qi + len(f1):]
    bi = rest.rfind(f2); ta, tb = rest[:bi], rest[bi + len(f2):]
    if f0 + q + f1 + ta + f2 + tb + f3 != user:
        raise SystemExit("[T1] %s: the user turn does not decompose into the template and three slots" % where)
    marker = "\n\n" + REFERENCE_MARKER + "\n"
    if q.count(REFERENCE_MARKER) != 1 or q.count(marker) != 1:
        raise SystemExit("[T1] %s: the reference marker occurs %d times in the question slot (exactly one, as \n\n<marker>\n)"
                         % (where, q.count(REFERENCE_MARKER)))
    question = q[:q.index(marker)]
    u1 = f0 + question + f1 + ta + f2 + tb + f3
    if u1 != rj.build_user_prompt(question, ta, tb):
        raise SystemExit("[T1] %s: the stripped user turn != rejudge_grok.build_user_prompt(question, traces)" % where)
    if user != f0 + question + q[q.index(marker):] + f1 + ta + f2 + tb + f3:
        raise SystemExit("[T1] %s: the stripped span does not reconstruct the stored user turn" % where)
    return u1


def arm_payload(m, arm, order, n1):
    """-> (system, user, stored payload sha, swap_ok) for one (match, arm, order)."""
    system, user, b = stored_body(m, order)
    where = "%s/%s/o%d" % (m["mid"], arm, order)
    if arm in ("C", "C1"):
        return system, user, m["psha"][order], 1
    s2 = swap_system(system, n1, where)
    if arm == "T":
        check_outside_span(b, rr.payload_bytes(s2, user), n1, where)
        return s2, user, m["psha"][order], 1
    if arm == "T1":
        if m["klass"] != "ONE":
            raise SystemExit("[T1] %s is not a ONE match" % m["mid"])
        return s2, strip_reference(user, where), m["psha"][order], 1
    raise SystemExit("[ARM] unknown arm %r" % arm)


# ============================================================================================ the v2 canary draw
def draw_canary(cfg, M):
    seed = LEGS["canary"]["seed"]
    frame = [m for m in M.values() if m["k46"] in ("A", "B", "TIE")]
    key = lambda m: hashlib.sha256((seed + m["mid"]).encode("utf-8")).hexdigest()
    strata = sorted({(m["klass"], m["anchor"]) for m in frame})
    cnt = Counter((m["klass"], m["anchor"]) for m in frame)
    N = cfg.n_set
    quota = {s: N * cnt[s] / len(frame) for s in strata}
    alloc = {s: int(math.floor(q)) for s, q in quota.items()}
    rem = N - sum(alloc.values())
    for s in sorted(strata, key=lambda s: (-(quota[s] - alloc[s]), s))[:rem]:
        alloc[s] += 1
    used, picked = set(), []
    short = []
    for s in strata:
        cand = sorted((m for m in frame if (m["klass"], m["anchor"]) == s), key=key)
        got = 0
        for m in cand:
            if got == alloc[s]:
                break
            if m["comp"] in used and MUTANT != "one_per_comp_off":
                continue
            used.add(m["comp"]); picked.append(m); got += 1
        if got < alloc[s]:
            short.append("%s/%s needs %d, has %d fresh components" % (s[0], s[1], alloc[s], got))
    if short:
        raise SystemExit("[DRAW] REFUSED, not filled: " + "; ".join(short))
    picked.sort(key=key)
    lines = ["%s|%s|%s|%s" % (m["mid"], m["klass"], m["anchor"], m["comp"]) for m in picked]
    set_hash = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    order_sha = hashlib.sha256(",".join(m["mid"] for m in picked).encode("utf-8")).hexdigest()
    return dict(seed=seed, frame=len(frame), strata={"%s/%s" % s: dict(frame=cnt[s], alloc=alloc[s]) for s in strata},
                matches=[dict(match_id=m["mid"], klass=m["klass"], anchor=m["anchor"], component=m["comp"],
                              k46_state="TIE" if m["k46"] == "TIE" else "decisive") for m in picked],
                set_hash=set_hash, order_sha=order_sha, n=len(picked),
                components=len({m["comp"] for m in picked}))


def draw_lines(d, say):
    say("THE v2 CANARY DRAW: frame %d usable K46 matches | seed string %r | strata (frame -> alloc): %s"
        % (d["frame"], d["seed"], ", ".join("%s %d -> %d" % (k, v["frame"], v["alloc"]) for k, v in sorted(d["strata"].items()))))
    say("  set %d matches in %d CK-CLOSE components (Kish mean cluster size %.2f) | set hash %s | order sha %s | K46 state: %s"
        % (d["n"], d["components"], d["n"] / max(1, d["components"]), d["set_hash"], d["order_sha"],
           dict(Counter(x["k46_state"] for x in d["matches"]))))
    say("  the v0 reference-correct flag of the ONE matches is NOT read by the draw (the eval view's reference.correct is read at"
        " --analyze-canary only; a deviation from the draft's 'printed with the set', for the registrar)")


def load_or_verify_set(cfg, M, say, write=False):
    d = draw_canary(cfg, M)
    if os.path.exists(cfg.set_file):
        s = json.load(open(cfg.set_file, encoding="utf-8"))
        ok = (s.get("set_hash"), s.get("order_sha"), [x["match_id"] for x in s.get("matches", [])]) == \
             (d["set_hash"], d["order_sha"], [x["match_id"] for x in d["matches"]])
        say("  set file %s: hash %s / order sha %s -> %s" % (cfg.set_file, s.get("set_hash", "?")[:16], s.get("order_sha", "?")[:16],
                                                            "REPRODUCED by the draw" if ok else "NOT REPRODUCED"))
        if not ok:
            raise SystemExit("[SET] the committed set is not reproduced by the draw from the store: refused")
        return d, True
    if write:
        os.makedirs(os.path.dirname(cfg.set_file), exist_ok=True)
        with open(cfg.set_file, "x", encoding="utf-8", newline="\n") as f:
            json.dump(dict(d, test="G17-CANARY (RP21) v2 canary", store_sha=cfg.store_sha, pool=cfg.pool,
                           script_sha16_lf=script_sha16_lf(), drawn_at=time.strftime("%Y-%m-%d %H:%M:%S")), f, indent=1)
        say("  set file WRITTEN (write-once) %s" % cfg.set_file)
        return d, True
    return d, False


# ============================================================================================ schedules
def leg_schedule(cfg, leg, M, setd=None):
    """[(match_id, arm)] in posting order; T and C adjacent per match, arm order by sha256(match_id) parity."""
    L = LEGS[leg]
    if leg == "canary":
        return [(x["match_id"], "C") for x in setd["matches"]]
    mids = sorted((m["mid"] for m in M.values() if m["klass"] == L["klass"]),
                  key=lambda mid: hashlib.sha256((L["seed"] + mid).encode("utf-8")).hexdigest())
    out = []
    for mid in mids:
        first_t = int(hashlib.sha256(mid.encode("utf-8")).hexdigest(), 16) % 2 == 0
        arms = L["arms"] if first_t else tuple(reversed(L["arms"]))
        out.extend((mid, a) for a in arms)
    return out


def schedule_sha(sched):
    return hashlib.sha256(",".join("%s:%s" % x for x in sched).encode("utf-8")).hexdigest()


def pilot_jobs(sched):
    mids = []
    for mid, _a in sched:
        if mid not in mids:
            mids.append(mid)
        if len(mids) > PILOT_N:
            break
    keep = set(mids[:PILOT_N])
    return [j for j in sched if j[0] in keep]


# ============================================================================================ caches
DDL = """CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS verdict (
    arm TEXT NOT NULL, match_id TEXT NOT NULL, presentation_order INTEGER NOT NULL CHECK (presentation_order IN (1, 2)),
    vote TEXT NOT NULL CHECK (vote IN ('FIRST', 'SECOND', 'TIE', 'INVALID', 'NON_TERMINATED', 'CONTENT_FILTER')),
    raw_text TEXT, parse_version TEXT NOT NULL, payload_sha256 TEXT NOT NULL, body_zlib BLOB NOT NULL, body_codec TEXT NOT NULL,
    stored_payload_sha256 TEXT NOT NULL, swap_ok INTEGER NOT NULL, judge_requested TEXT NOT NULL, provider TEXT NOT NULL,
    response_model TEXT, response_id TEXT, finish_reason TEXT, completion_tokens INTEGER, max_tokens INTEGER NOT NULL,
    temperature_label TEXT NOT NULL, content_filter INTEGER NOT NULL CHECK (content_filter IN (0, 1)), latency_ms INTEGER,
    post_index INTEGER, script_sha16_lf TEXT NOT NULL, created_at TEXT NOT NULL, created_ts REAL NOT NULL,
    CHECK (content_filter = (vote = 'CONTENT_FILTER')),
    CHECK ((COALESCE(finish_reason, '') = 'length') = (vote = 'NON_TERMINATED')),
    PRIMARY KEY (arm, match_id, presentation_order)) WITHOUT ROWID;"""


def cache_path(cfg, leg, pass_=None):
    return os.path.join(cfg.out_dir, "k46_repost_%s%s.db" % (leg, "_" + pass_.replace("-", "") if pass_ else ""))


def open_cache(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.commit()
    return con


def read_cache(path):
    """{(arm, match_id): {order: row dict}}, run_meta; None when absent."""
    if not os.path.exists(path):
        return None, {}
    con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(path).replace("\\", "/"), uri=True)
    cols = ["arm", "match_id", "presentation_order", "vote", "payload_sha256", "stored_payload_sha256", "swap_ok", "provider",
            "finish_reason", "created_ts", "body_zlib"]
    out = defaultdict(dict)
    for r in con.execute("SELECT %s FROM verdict" % ", ".join(cols)):
        d = dict(zip(cols, r))
        out[(d["arm"], d["match_id"])][d["presentation_order"]] = d
    meta = dict(con.execute("SELECT key, value FROM run_meta").fetchall())
    con.close()
    return dict(out), meta


def pin_meta(con, cur, path):
    old = dict(con.execute("SELECT key, value FROM run_meta").fetchall())
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    if old:
        bad = [(k, old.get(k), v) for k, v in cur.items() if old.get(k) != v]
        if bad:
            raise SystemExit("[META] refusing to resume into %s: produced under a different record\n  %s"
                             % (path, "\n  ".join("%s: recorded %r | now %r" % b for b in bad)))
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)", (json.dumps(json.loads(old.get("resumed", "[]")) + [now]),))
    else:
        for k, v in cur.items():
            con.execute("INSERT INTO run_meta VALUES (?, ?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
        con.execute("INSERT INTO run_meta VALUES ('started_ts', ?)", (repr(time.time()),))
    con.commit()


def arm_combined(cache, m, arm):
    rows = cache.get((arm, m["mid"])) if cache else None
    if not rows or set(rows) != {1, 2}:
        return None
    return combine(*(to_contestant(rows[o]["vote"], o, m) for o in (1, 2)))


# ============================================================================================ keys (the eval view, via K46-KEY-READ)
def read_keys(cfg, M, say, mids=None):
    """{match_id: dict(kd, side, v0, comp)} through k46_key_read's sealed view read (the record's key rule); only for mids."""
    import k46_key_read as KR
    sub = {mid: M[mid] for mid in (mids if mids is not None else M)}
    MK = {}
    for mid, m in sub.items():
        MK[mid] = dict(run_id=m["run_id"], match_id=mid, draw=0, variant=m["variant"], stem=m["stem"], comp_s=m["comp"], a=m["a"], b=m["b"],
                       ref=m["ref"], vintage=VINTAGE if m["ref"] else None, orders={1, 2}, combined=m["k46"])
    kcfg = Cfg(eval_path=cfg.eval_path, eval_sha=cfg.eval_sha)
    vw, before = KR.open_view(kcfg, say)
    var_item, side = KR.view_structure(vw, cfg.cv)
    KR.attach_structure(MK, var_item, side)
    vw.unseal("K46-REPOST: key-decidability and the v0 flag for the guard / the analysis")
    key, refused, refs, missing = KR.read_keys(vw, cfg.cv, MK, VINTAGE)
    vw.close()
    if sha256_file(cfg.eval_path) != before:
        raise SystemExit("[PIN] the eval view changed during the key read")
    out = {}
    for mid, mk in MK.items():
        ka, kb = key.get((mk["a"], mk["variant"])), key.get((mk["b"], mk["variant"]))
        kd = ka is not None and kb is not None and ka + kb == 1
        out[mid] = dict(kd=kd, side=("A" if ka == 1 else "B") if kd else None, ka=ka, kb=kb, comp=mk["comp"], anchor=mk["anchor"],
                        v0=refs.get(mk["ref"]) if mk["ref"] else None)
    say("  KEYS (K46-KEY-READ's sealed read): %d matches, key-decidable %d, refused sides %s" % (len(out), sum(v["kd"] for v in out.values()),
                                                                                             dict(refused) or 0))
    return out


# ============================================================================================ accounting
def budget_gate(cfg, leg, planned, what, budget, refuse=True):
    L = LEGS[leg]
    own_c = 0
    for ps in L["passes"]:
        c, _m = read_cache(cache_path(cfg, leg, ps))
        own_c += sum(len(v) for v in (c or {}).values())
    own_l = atl.ledger_calls(L["test"], cfg.ledger_dir)
    own = max(own_c, own_l)
    day = cfg.today().strftime("%Y-%m-%d")
    day_total = sum(int(r["calls"]) for r in atl._rows(atl.day_ledger_path(cfg.ledger_dir, day)))
    after = own + planned
    br = []
    if after > L["ceiling"]:
        br.append("(i) %s would reach %d calls > its ceiling %d" % (L["test"], after, L["ceiling"]))
    if (after + 1) // 2 > MATCH_RULE:
        br.append("(ii) %d matches > the %d-match rule" % ((after + 1) // 2, MATCH_RULE))
    if day_total + planned > DAY_CAP and MUTANT != "day_cap_off":
        br.append("(iii) the day cap: day_calls_%s.json %d + this launch %d = %d > %d" % (day, day_total, planned, day_total + planned, DAY_CAP))
    if refuse and planned > 0:
        if budget is None:
            br.append("(iv) a posting launch needs an explicit --budget (calls)")
        elif planned > budget:
            br.append("(iv) this launch plans %d calls > --budget %d" % (planned, budget))
    print("[ACCOUNT] %s (%s): (i) own %d (caches %d, ledgers %d) + %d = %d of %d | (ii) matches %d of %d | (iii) day %s: %d + %d = %d of %d | "
          "(iv) budget %s -> %s" % (L["test"], what, own, own_c, own_l, planned, after, L["ceiling"], (after + 1) // 2, MATCH_RULE, day, day_total,
                                    planned, day_total + planned, DAY_CAP, budget, "OK" if not br else "REFUSED: " + "; ".join(br)), flush=True)
    if br and refuse:
        raise SystemExit("[ACCOUNT] REFUSED, not trimmed (0 calls posted): " + "; ".join(br))
    return dict(own=own, own_cache=own_c, own_ledger=own_l, day=day, day_total=day_total, breaches=br)


# ============================================================================================ transport (RP32a)
def transport(out=print):
    if MUTANT == "transport_skipped":
        return None
    from archv2_pilot import pilot as PL
    root = os.environ.get("K46_REPOST_ENV_ROOT") or None
    PL.load_transport(root=root, out=out)
    return PL.transport_preflight(out=out)


# ============================================================================================ READY gate
def parse_ready(text, sha):
    import re
    lines = list(re.finditer(r"^[ \t]*#{0,6}[ \t]*\**[ \t]*(NOT READY|READY-WITH-CONDITIONS|READY)\b[ \t]*\**[ \t]*:", text, re.M))
    if not lines:
        return None, ["no verdict line"]
    first = text[lines[0].start():].split("\n", 1)[0]
    reasons = []
    if any(x.group(1) == "NOT READY" for x in lines): reasons.append("a NOT READY verdict")
    if TEST not in first: reasons.append("the verdict line does not name %s" % TEST)
    if sha not in first: reasons.append("the verdict line does not name this script's LF sha16 %s" % sha)
    return lines[0].group(1), reasons


def ready_gate(cfg, what, go):
    import subprocess
    exists = os.path.exists(cfg.ready)
    tracked = clean = False
    if exists:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", cfg.ready], cwd=ROOT, capture_output=True).returncode == 0
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", cfg.ready], cwd=ROOT, capture_output=True).returncode == 0
    verdict, reasons = parse_ready(open(cfg.ready, encoding="utf-8").read(), script_sha16_lf()) if exists else (None, ["READY missing"])
    ok = bool(go and exists and tracked and clean and not reasons)
    s = "--go %s | %s %s (tracked %s, clean %s) | verdict %r%s" % (bool(go), cfg.ready, "exists" if exists else "MISSING", tracked, clean,
                                                                  verdict, "" if not reasons else " | REFUSES: " + "; ".join(reasons))
    print("[GATE] %s: %s -> %s" % (what, s, "OPEN" if ok else "REFUSED"), flush=True)
    if not ok:
        raise SystemExit("[GATE] %s REFUSED (0 calls, no database opened): %s" % (what, s))


# ============================================================================================ posting
class _Stop(Exception):
    pass


class _Foreign(Exception):
    pass


def post_jobs(cfg, jobs, M, n1, con, workers, budget, day, index):
    """Both orders of each (match, arm) job through rr.call_judge_full (counted); rows cached per job after both orders return.
    Hard cap = --budget; a local-date change stops; a foreign fingerprint stops (nothing cached for that job)."""
    lock = threading.Lock(); posted = []; stop = []; halt = threading.Event(); ok = [0]; err = [0]
    real = rr.call_judge_full

    def counted(*a, **k):
        with lock:
            if halt.is_set():
                raise _Stop("halted")
            if len(posted) >= budget and MUTANT != "budget_cap_off":
                raise _Stop("[BUDGET-STOP] the --budget %d is reached: this post is NOT made" % budget)
            if cfg.today().strftime("%Y-%m-%d") != day:
                raise _Stop("[ROLLOVER] the local date changed from %s: the launch stops; relaunch on the new day" % day)
            posted.append(1)
        return real(*a, **k)

    def one(job):
        mid, arm = job
        m = M[mid]
        rows = []
        for order in (1, 2):
            system, user, spsha, swap_ok = arm_payload(m, arm, order, n1)
            body = rr.payload_bytes(system, user)
            t0 = time.time()
            content, provider, ctok, lat, finish, msg = rr.call_judge_full(system, user)
            if not (provider == EXPECTED_FP or (provider == REFUSAL_FP and finish == "content_filter")):
                raise _Foreign("%s/%s order %d: fingerprint %r != %r" % (mid, arm, order, provider, EXPECTED_FP))
            vote, raw = JW.classify(content, finish, msg)
            rows.append((arm, mid, order, vote, raw, JW.PARSE_VERSION, hashlib.sha256(body).hexdigest(), zlib.compress(body), "zlib", spsha,
                         swap_ok, JUDGE, provider, (provider or "").split(":", 1)[-1], (msg or {}).get("_response_id"), finish, ctok, CAP,
                         "omitted", int(vote == "CONTENT_FILTER"), int(1000 * (lat or (time.time() - t0))), index.get(job), script_sha16_lf(),
                         time.strftime("%Y-%m-%d %H:%M:%S"), time.time()))
        return rows
    rr.call_judge_full = counted
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(one, j): j for j in jobs}
            for f in as_completed(futs):
                try:
                    rows = f.result()
                except (_Stop, _Foreign) as e:
                    halt.set()
                    if str(e) != "halted" and not stop:
                        stop.append(("[FINGERPRINT] " if isinstance(e, _Foreign) else "") + str(e))
                    continue
                except Exception as e:  # noqa: BLE001  a transport error: a posted call, counted, never cached
                    err[0] += 1
                    print("  ERROR %s: %s" % (futs[f], str(e)[:140]), flush=True)
                    continue
                with lock:
                    con.executemany("INSERT INTO verdict VALUES (%s)" % ",".join("?" * 25), rows)
                    con.commit()
                ok[0] += 1
    finally:
        rr.call_judge_full = real
    return ok[0], err[0], posted, stop


def leg_preflight(cfg, leg, pass_, M, say):
    """canary v2-2: v2-1 complete (every job, both orders) and this launch within WINDOW_S of v2-1's last row, measured from
    v2-2's PERSISTED start once a v2-2 cache exists. Returns refusals."""
    probs = []
    if leg == "canary" and pass_ == "v2-2":
        c1, _m1 = read_cache(cache_path(cfg, "canary", "v2-1"))
        n_done = sum(1 for v in (c1 or {}).values() if set(v) == {1, 2})
        if n_done != cfg.n_set:
            probs.append("pass v2-1 holds %d of %d complete matches: v2-2 follows a COMPLETE v2-1" % (n_done, cfg.n_set))
        else:
            last = max(r["created_ts"] for v in c1.values() for r in v.values())
            c2, m2 = read_cache(cache_path(cfg, "canary", "v2-2"))
            start = float(m2["started_ts"]) if m2.get("started_ts") else cfg.now()
            gap = start - last
            say("[WINDOW] v2-1's last row -> v2-2 %s: %.0f s against %d s -> %s" % ("persisted start" if m2.get("started_ts") else "now", gap,
                                                                                 WINDOW_S, "WITHIN" if gap <= WINDOW_S else "OUTSIDE"))
            if gap > WINDOW_S and MUTANT != "window_off":
                probs.append("v2-2 would start %.0f s after v2-1's last row (> %d s): the rung would be UNDETERMINED BY VALIDITY" % (gap, WINDOW_S))
    return probs


def guard_rows(cache, jobs, M, keys=None):
    """(unusable, total, kd_unusable, kd_total) over the jobs' cached arm-matches (errored = absent = not counted here)."""
    u = t = ku = kt = 0
    for mid, arm in jobs:
        c = arm_combined(cache, M[mid], arm)
        if c is None:
            continue
        bad = c in UNUSABLE
        u += bad; t += 1
        if keys is not None and keys.get(mid, {}).get("kd"):
            ku += bad; kt += 1
    return u, t, ku, kt


def guard_ok(u, t, ku, kt, use_kd):
    a = u <= GUARD_RATE * max(1, t)
    b = (ku <= GUARD_RATE * max(1, kt)) if (use_kd and MUTANT != "kd_guard_off") else True
    return a and b


def common_open(cfg, leg, say, writable=None):
    install_db_guard(writable=writable)
    say("POOL %s (%s; leg %s; the first line of every mode)" % (cfg.pool, TEST, leg))
    M, meta, before = read_store(cfg, say)
    identity_gate(cfg, M, meta, say)
    n1 = load_n1(cfg.pair_noref, cfg.pair_noref_blob)
    say("  N1: pair_noref.py blob %s | REF_SENTENCE sha256 %s | NOREF_SENTENCE sha256 %s"
        % (cfg.pair_noref_blob[:16], hashlib.sha256(n1[0].encode()).hexdigest()[:16], hashlib.sha256(n1[1].encode()).hexdigest()[:16]))
    return M, meta, before, n1


def check_all_bodies(sched, M, n1, say):
    c = Counter()
    for mid, arm in sched:
        for order in (1, 2):
            arm_payload(M[mid], arm, order, n1)
            c[arm] += 1
    say("  BODIES: %s slots decoded; C / C1 byte-identical to the stored payload (sha256 equality and rr.payload_bytes rebuild); T / T1 swapped"
        " exactly once with every byte outside the span equal (T) / the reference block stripped (T1)" % dict(c))
    return c


def go_one_check(cfg):
    """C-K2 (R6): (ok, line). The configured quotation must occur EXACTLY ONCE in the BODY of the "## Amendment 34" section of the plan
    (the heading line excluded; the section ends at the next '## ' heading)."""
    quote = cfg.author_go_one
    if not quote:
        return False, "no go configured (AUTHOR_GO_ONE is empty)"
    if not os.path.exists(cfg.plan_file):
        return False, "the plan %s is missing" % cfg.plan_file
    lines = open(cfg.plan_file, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    heads = [i for i, l in enumerate(lines) if l.startswith(GO_HEADING + " ") or l == GO_HEADING]
    if len(heads) != 1:
        return False, "%d sections headed %r in the plan (exactly one required)" % (len(heads), GO_HEADING)
    body = []
    for l in lines[heads[0] + 1:]:
        if l.startswith("## "):
            break
        body.append(l)
    n = "\n".join(body).count('"%s"' % quote)
    ok = n == 1 or (MUTANT == "go_presence_only" and n >= 1)
    hn = lines[heads[0]].count('"%s"' % quote)
    return ok, ("the quotation \"%s\" occurs %d time(s) in the BODY of %r (exactly one required; the heading line, which carries it %d"
                " time(s), is not counted: b3dd18ab)" % (quote, n, GO_HEADING, hn))


def combined_statement(cfg, M, say):
    """C-K2: the RP20 + ONE statement against the 4,000-match rule, printed by every rp20 / one launch and dry-run."""
    n20 = 2 * sum(1 for m in M.values() if m["klass"] == "NONE")
    n1 = 2 * sum(1 for m in M.values() if m["klass"] == "ONE")
    ok, why = go_one_check(cfg)
    say("[4K-RULE] RP20 %d + ONE %d = %d matches %s %d (the 4,000-match rule; registered %d): the author's go, plan Amendment 34 -> %s (%s)"
        % (n20, n1, n20 + n1, ">" if n20 + n1 > MATCH_RULE else "<=", MATCH_RULE, COMBINED_MATCHES, "VERIFIED" if ok else "NOT VERIFIED", why))
    return ok


def canary_c1_word(cfg):
    """C-K6: the C1-v2 word of RP21's canary outcome of record, or None when the outcome / its C1-v2 line is absent."""
    p = outcome_path(cfg, "canary")
    if not os.path.exists(p):
        return None
    for l in open(p, encoding="utf-8").read().split("\n"):
        if l.startswith("C1-v2: "):
            return l[len("C1-v2: "):].split(" (")[0].strip()
    return None


def order_gate(cfg, leg):
    """C-K6: RP20 (and its ONE leg) posts only after RP21's C1-v2 is read, and not after a FAILED C1-v2."""
    if MUTANT == "order_gate_off":
        return
    w = canary_c1_word(cfg)
    if w is None:
        raise SystemExit("[ORDER] %s REFUSED: RP21's canary outcome of record (%s) with its C1-v2 line does not exist; RP20 posts after RP21's"
                         " C1-v2 is read (C-K6)" % (leg, outcome_path(cfg, "canary")))
    if w == "FAILED":
        raise SystemExit("[ORDER] %s REFUSED: RP21's C1-v2 is FAILED: RP20 is re-registered pre-data (delta raised or DESCRIPTIVE-ONLY) before"
                         " it posts (C-K6)" % leg)
    print("[ORDER] RP21's C1-v2 reads %s: RP20 may post (C-K6)" % w, flush=True)


def launch(cfg, leg, pass_, pilot, full, go, budget, workers=8, dry=False):
    L = LEGS[leg]
    lines = []; say = say_factory(lines)
    if pass_ not in L["passes"]:
        raise SystemExit("[LEG] leg %s takes passes %s, not %r" % (leg, L["passes"], pass_))
    what = "--leg %s%s %s" % (leg, " --pass %s" % pass_ if pass_ else "", "--dry-run" if dry else ("--pilot %d" % (pilot or 0) if pilot else "--run"))
    if not dry:
        if not pilot and not full:
            raise SystemExit("[MODE] a posting launch needs --pilot 12 or --run, with --go and --budget")
        if pilot and pilot != PILOT_N:
            raise SystemExit("[MODE] --pilot %d REFUSED: the registered pilot is %d matches" % (pilot, PILOT_N))
        if leg == "one":
            ok_go, why_go = go_one_check(cfg)
            if not ok_go:
                raise SystemExit("[GO] the ONE leg (REF-PAIRED-V2) is above 4,000 matches with RP20: it posts only on the AUTHOR'S GO, verified"
                                 " by count in plan Amendment 34: %s; refused" % why_go)
        if leg in ("rp20", "one"):
            order_gate(cfg, leg)
        if os.path.exists(outcome_path(cfg, leg)):
            raise SystemExit("[RECORD] %s exists: the leg's outcome of record is written; nothing more is posted" % outcome_path(cfg, leg))
        ready_gate(cfg, what, go)
        if budget is None:
            raise SystemExit("[ACCOUNT] REFUSED: a posting launch needs an explicit --budget (calls); 0 calls posted")
    cpath = cache_path(cfg, leg, pass_)
    M, meta, before, n1 = common_open(cfg, leg, say, writable=None if dry else cpath)
    setd = None
    if leg == "canary":
        setd, present = load_or_verify_set(cfg, M, say)
        draw_lines(setd, say)
        if not present:
            if not dry:
                raise SystemExit("[SET] the canary set file is not committed (run --freeze-canary first, commit it before the READY)")
            say("  (dry-run) the set file is ABSENT: the draw above is what --freeze-canary would write")
    sched = leg_schedule(cfg, leg, M, setd)
    ssha = schedule_sha(sched)
    if leg in ("rp20", "one"):
        combined_statement(cfg, M, say)
    pj = pilot_jobs(sched)
    say("SCHEDULE: %d (match, arm) jobs = %d matches of record x 2 orders = %d calls | schedule sha %s | pilot %d jobs (%d calls), first %s"
        % (len(sched), len(sched), 2 * len(sched), ssha, len(pj), 2 * len(pj), sched[:2]))
    configure_rr(); assert_body_source()
    check_all_bodies(sched, M, n1, say)
    line = transport(out=say)
    say("TRANSPORT: %s" % (line or "NO PREFLIGHT RUN"))
    probs = leg_preflight(cfg, leg, pass_, M, say)
    if dry:
        say("[DRY-RUN] pre-flight: %s" % ("would GO" if not probs else "would REFUSE: " + "; ".join(probs)))
        cache, _ = read_cache(cpath)
        todo = [j for j in sched if not (cache and set(cache.get((j[1], j[0]), {})) == {1, 2})]   # cache keys are (arm, match_id); jobs (match_id, arm)
        budget_gate(cfg, leg, 2 * len(todo), what + " (the remaining jobs, 0 posted)", None, refuse=False)
        say("[DRY-RUN] would post %d matches of record (%d calls) | registered %d calls | ceiling %d | 0 posted"
            % (len(todo), 2 * len(todo), L["registered_calls"], L["ceiling"]))
        store_after(cfg, before, say)
        remove_db_guard()
        return dict(lines=lines, sched=sched, setd=setd)
    if probs:
        raise SystemExit("[PRE-FLIGHT] REFUSED before any call:\n  %s" % "\n  ".join(probs))
    cur = dict(test=L["test"], leg=leg, pass_id=str(pass_), judge=JUDGE, max_tokens=str(CAP), temperature="omitted",
               protocol="K46 stored bodies re-posted (%s) via rr.call_judge_full; dual order; jv2 classify; TIE on flip" % "/".join(L["arms"]),
               schedule_sha=ssha, set_hash=(setd or {}).get("set_hash", "-"), store_sha=cfg.store_sha,
               n1_sha=hashlib.sha256(n1[1].encode()).hexdigest(), script_sha16_lf=script_sha16_lf())
    con = open_cache(cpath)
    try:
        pin_meta(con, cur, cpath)
        cache, _ = read_cache(cpath)
        done = {(mid, arm) for (arm, mid), v in (cache or {}).items() if set(v) == {1, 2}}   # jobs are (match_id, arm)
        use_kd = leg in ("rp20", "one")
        keys = None
        if full:
            miss = [j for j in pj if j not in done]
            if miss:
                raise SystemExit("[RUN] REFUSED: the pilot (%d jobs) is not cached (%d missing): run --pilot 12 first" % (len(pj), len(miss)))
            keys = read_keys(cfg, M, say, mids={j[0] for j in pj}) if use_kd else None
            u, t, ku, kt = guard_rows(cache, pj, M, keys)
            say("[GUARD] pilot rows: unusable %d of %d | key-decidable %s" % (u, t, "%d of %d" % (ku, kt) if use_kd else "n/a (canary: all rows)"))
            if not guard_ok(u, t, ku, kt, use_kd):
                raise SystemExit("[GUARD] the pilot is above 5%% unusable: --run REFUSED")
        jobs = pj if pilot else sched
        todo = [j for j in jobs if j not in done]
        planned = 2 * len(todo)
        day = cfg.today().strftime("%Y-%m-%d")
        budget_gate(cfg, leg, planned, what, budget)
        say("[PLAN] %s: matches of record to post %d | calls %d | cached %d | --budget %d (hard cap) | posting day %s | schedule sha %s"
            % (what, len(todo), planned, len(jobs) - len(todo), budget, day, ssha[:16]))
        index = {j: i for i, j in enumerate(sched)}
        posted, stop, err = [], [], 0
        try:
            okn, err, posted, stop = post_jobs(cfg, todo, M, n1, con, workers, budget, day, index)
        finally:
            atl.append(L["test"], what, len(posted), cfg.ledger_dir, day=day)
            say("done: %d calls posted (errors and stopped calls are posted calls, counted, never cached)%s"
                % (len(posted), " | STOPPED: " + stop[0] if stop else ""))
        store_after(cfg, before, say)
        if stop:
            raise SystemExit(stop[0])
        if pilot:
            cache, _ = read_cache(cpath)
            keys = read_keys(cfg, M, say, mids={j[0] for j in pj}) if use_kd else None
            u, t, ku, kt = guard_rows(cache, pj, M, keys)
            u += err; t += err
            say("[GUARD] pilot: unusable %d of %d (errors counted) | key-decidable %s" % (u, t, "%d of %d" % (ku, kt) if use_kd else "n/a"))
            if not guard_ok(u, t, ku, kt, use_kd):
                raise SystemExit("[GUARD] the pilot FAILED its truncation guard (> 5%% unusable): --run is refused")
    finally:
        con.close()
        remove_db_guard()
    return dict(lines=lines, posted=len(posted))


# ============================================================================================ statistics
def boot_mean(vals, comps, B, seed, level_z=1.96):
    """Component-clustered bootstrap of the mean of per-match values -> dict(point, se, n_lo, n_hi, p_lo, p_hi, se_iid, n, k)."""
    v = np.asarray(vals, dtype=np.float64)
    n = len(v)
    if n == 0:
        return dict(point=float("nan"), se=float("nan"), n=0, k=0)
    keys = sorted(set(comps)); pos = {k: i for i, k in enumerate(keys)}
    g = np.array([pos[c] for c in comps], dtype=np.int64)
    ng = len(keys)
    s = np.bincount(g, weights=v, minlength=ng); c = np.bincount(g, minlength=ng).astype(np.float64)
    rng = np.random.default_rng(seed)
    reps = np.empty(B)
    for b in range(B):
        w = np.bincount(rng.integers(0, ng, ng), minlength=ng)
        reps[b] = (w @ s) / (w @ c)
    rng2 = np.random.default_rng(seed)
    reps_iid = np.empty(B)
    for b in range(B):
        idx = rng2.integers(0, n, n)
        reps_iid[b] = v[idx].mean()
    pt = float(v.mean())
    se = float(np.std(reps, ddof=1)) if B > 1 else 0.0
    out = dict(point=pt, se=se, se_iid=float(np.std(reps_iid, ddof=1)) if B > 1 else 0.0, n=n, k=ng, reps=reps)
    # [2026-10-01, POSTRUN_rp21_v2 cb40d39e D1] the DEFF of record is ANALYTIC, free of Monte-Carlo noise: the linearised (plug-in)
    # component-clustered variance of the ratio mean, sum_g (s_g - pt c_g)^2 / N^2 (the large-B limit of the cluster bootstrap), over
    # the plug-in iid variance sum_i (v_i - pt)^2 / N^2 (its iid limit). One match per component gives exactly 1. Kish = sum c_g^2 / N.
    out["var_c_lin"] = float(np.sum((s - pt * c) ** 2)) / (n * n)
    out["var_iid_an"] = float(np.sum((v - pt) ** 2)) / (n * n)
    out["kish"] = float(np.sum(c * c)) / n
    for lev, z in (("90", 1.6448536269514722), ("95", 1.959963984540054)):
        q = (100 - float(lev)) / 2
        out["n_lo" + lev], out["n_hi" + lev] = pt - z * se, pt + z * se
        out["p_lo" + lev], out["p_hi" + lev] = (float(x) for x in np.percentile(reps, [q, 100 - q]))
    return out


def bounds(iv, form, lev):
    """(lo, hi) for a form ('normal' / 'percentile')."""
    return (iv["n_lo" + lev], iv["n_hi" + lev]) if form == "normal" else (iv["p_lo" + lev], iv["p_hi" + lev])


def decide(fn, iv, form):
    """Apply a word function fn(bounds_of) under the interval form; both_agree -> UNDETERMINED when the forms disagree."""
    if form in ("normal", "percentile"):
        return fn(lambda lev: bounds(iv, form, lev)), None
    a, b = fn(lambda lev: bounds(iv, "normal", lev)), fn(lambda lev: bounds(iv, "percentile", lev))
    return (a, None) if a == b else ("UNDETERMINED", (a, b))


def word_c1v2(bnd):
    lo, hi = bnd("95")
    held = (hi < C1V2_BAR) if MUTANT == "c1v2_bar_strict" else (hi <= C1V2_BAR)
    if held:
        return "HELD"
    if lo > C1V2_BAR:
        return "FAILED"
    return "UNDETERMINED"


def word_rp20(bnd):
    lo90, hi90 = bnd("95" if MUTANT == "eq_95" else "90")
    lo95, hi95 = bnd("95")
    if -EQ_DELTA < lo90 and hi90 < EQ_DELTA:
        if lo95 > 0:
            return "EQUIVALENT, with a detectable shift of +"
        if hi95 < 0:
            return "EQUIVALENT, with a detectable shift of -"
        return "EQUIVALENT"
    if lo95 > 0:
        return "GAIN"
    if hi95 < 0:
        return "LOSS"
    return "UNDETERMINED"


def word_one(bnd):
    lo, hi = bnd("95")
    if hi < 0:
        return "LOSS"
    if lo > 0:
        return "GAIN"
    return "UNDETERMINED"


def iv_text(iv):
    return ("%+.4f | 90%% normal [%+.4f, %+.4f] percentile [%+.4f, %+.4f] | 95%% normal [%+.4f, %+.4f] percentile [%+.4f, %+.4f] | SE %.4f"
            % (iv["point"], iv["n_lo90"], iv["n_hi90"], iv["p_lo90"], iv["p_hi90"], iv["n_lo95"], iv["n_hi95"], iv["p_lo95"], iv["p_hi95"], iv["se"]))


def deff_analytic(iv):
    """D1 (cb40d39e): the analytic DEFF = linearised clustered variance / plug-in iid variance (nan when the iid variance is 0)."""
    if MUTANT == "deff_boot":
        return (iv["se"] / iv["se_iid"]) ** 2 if iv.get("se_iid") else float("nan")
    vi = iv.get("var_iid_an", 0.0)
    return iv["var_c_lin"] / vi if vi > 0 else float("nan")


def support_text(iv, n, k, label):
    deff = deff_analytic(iv)
    ratio = (iv["se"] / iv["se_iid"]) ** 2 if iv.get("se_iid") else float("nan")
    return ("SUPPORT (%s, MEASURED): n %d in %d CK-CLOSE components (Kish mean cluster size %.3f%s) | DEFF %.3f (ANALYTIC: linearised"
            " component-clustered variance / iid variance) | n_eff %.1f | SE %.4f (component-clustered bootstrap, deciding) | MDE80 (2.80 x SE)"
            " %.4f | beside, NOT a measurement: the bootstrap SE ratio squared %.3f (%.4f vs %.4f iid; Monte-Carlo noise between two streams)"
            % (label, n, k, iv.get("kish", float("nan")), ", one per component" if k == n else "", deff,
               n / deff if deff == deff and deff > 0 else float("nan"), iv["se"], 2.80 * iv["se"], ratio, iv["se"], iv.get("se_iid", float("nan"))))


def seeds_line(vals, comps, B):
    return ", ".join("%d:%.4f" % (sd, boot_mean(vals, comps, B, sd)["se"]) for sd in EXTRA_SEEDS)


def key_coefficient(rows):
    """CONSENSUS-FIT's logistic (imported after the stub and the DB guard): winner ~ 1 + KEY contrast; REF not estimable."""
    try:
        import consensus_fit as cf
    except Exception as e:  # noqa: BLE001
        return "KEY coefficient NOT READ (consensus_fit import refused: %s)" % str(e)[:120]
    X, y, w = [], [], []
    for kcon, win in rows:
        if win == "TIE":
            X += [[1.0, kcon], [1.0, kcon]]; y += [1.0, 0.0]; w += [0.5, 0.5]
        elif win in ("A", "B"):
            X.append([1.0, kcon]); y.append(1.0 if win == "A" else 0.0); w.append(1.0)
    if len(X) < 4:
        return "KEY coefficient NOT READ (fewer than 4 rows)"
    b, se = cf.logistic(X, y, w)
    return "KEY %+.3f +- %.3f (n %d rows) | REF NOT ESTIMABLE (no reference in the arm)" % (b[1], se[1], len(X))


# ============================================================================================ outcomes
def outcome_path(cfg, leg):
    return os.path.join(cfg.out_dir, {"canary": "g17_v2_canary_outcome.txt", "rp20": "rp20_outcome.txt", "one": "ref_paired_v2_outcome.txt"}[leg])


def write_outcome(cfg, leg, text, complete):
    path = outcome_path(cfg, leg)
    os.makedirs(cfg.out_dir, exist_ok=True)
    if not complete:
        hit("WRITE:PARTIAL")
        stem = path[:-4] + "_partial_%s" % time.strftime("%Y%m%d_%H%M%S")
        p, k = stem + ".txt", 0
        while os.path.exists(p):
            k += 1; p = "%s_%d.txt" % (stem, k)
        with open(p, "x", encoding="utf-8", newline="\n") as f:
            f.write("NOT OF RECORD - incomplete caches; no line below is a registered reading.\n\n" + text)
        print("[ANALYZE] incomplete: wrote %s; NO outcome of record" % p, flush=True)
        return 2, p
    try:
        with open(path, "w" if MUTANT == "write_mode_w" else "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        hit("WRITE:REFUSED_EXISTS")
        print("[ANALYZE] REFUSED: %s exists and is WRITE-ONCE; nothing was overwritten" % path, flush=True)
        return 3, path
    hit("WRITE:RECORD")
    print("[ANALYZE] wrote %s (write-once)" % path, flush=True)
    return 0, path


def require_form(cfg):
    f = cfg.pre.get("interval_form")
    if f not in INTERVAL_FORMS:
        raise SystemExit("[PRECONDITION] the interval form is unset (%r): the registrar fixes it (normal / percentile / both_agree) before"
                         " an analysis of record" % f)
    return f


def changed(a, b):
    """Convention A difference: an unusable combined verdict on either side is a difference."""
    if a is None or b is None:
        return None
    if MUTANT == "both_unusable_same" and a in UNUSABLE and b in UNUSABLE:
        return 0
    if a in UNUSABLE or b in UNUSABLE:
        return 1
    return int(a != b)


def decisive(c):
    return c in ("A", "B")


def analyze_canary(cfg):
    form = require_form(cfg)
    lines = []; say = say_factory(lines)
    if MUTANT != "analyze_no_configure":
        configure_rr()    # [2026-10-02, incident aaf12c77] the analysis rebuilds bodies through rr: the recipe's model / cap / temperature
    M, meta, before, n1 = common_open(cfg, "canary", say)
    setd, present = load_or_verify_set(cfg, M, say)
    if not present:
        raise SystemExit("[SET] no committed canary set: nothing to analyze")
    sched = leg_schedule(cfg, "canary", M, setd)
    mids = [mid for mid, _ in sched]
    c1, m1 = read_cache(cache_path(cfg, "canary", "v2-1"))
    c2, m2 = read_cache(cache_path(cfg, "canary", "v2-2"))
    keys = read_keys(cfg, M, say, mids=set(mids))
    V1 = {mid: arm_combined(c1, M[mid], "C") for mid in mids}
    V2 = {mid: arm_combined(c2, M[mid], "C") for mid in mids}
    K = {mid: M[mid]["k46"] for mid in mids}
    n = len(mids)
    complete = all(V1[x] is not None for x in mids) and all(V2[x] is not None for x in mids)
    comps = [M[x]["comp"] for x in mids]
    # C0
    rows = [r for c in (c1 or {}, c2 or {}) for v in c.values() for r in v.values()]
    psha_ok = sum(1 for r in rows if r["payload_sha256"] == r["stored_payload_sha256"])
    fps = Counter(r["provider"] for r in rows)
    foreign = sorted(set(fps) - {EXPECTED_FP, REFUSAL_FP})
    last1 = max((r["created_ts"] for v in (c1 or {}).values() for r in v.values()), default=None)
    st2 = float(m2["started_ts"]) if m2.get("started_ts") else None
    gap = (st2 - last1) if (st2 is not None and last1 is not None) else float("inf")
    pj = pilot_jobs(sched)
    pil = [(sum(1 for j in pj if arm_combined(c, M[j[0]], "C") in UNUSABLE), sum(1 for j in pj if arm_combined(c, M[j[0]], "C") is not None))
           for c in (c1, c2)]
    c0 = [("(a) set hash and order sha reproduced by the draw", True, "%s / %s" % (setd["set_hash"][:16], setd["order_sha"][:16])),
          ("(b) store sha256 equal before and after", True, "checked at the end"),
          ("(c) every re-posted body byte-identical to its stored body", psha_ok == len(rows) == 4 * n, "%d of %d (registered %d)" % (psha_ok, len(rows), 4 * n)),
          ("(d) every call fingerprinted %s" % EXPECTED_FP, not foreign and len(rows) > 0, dict(fps)),
          ("(e) v2-2 started within %d s of v2-1's last row" % WINDOW_S, MUTANT == "window_off" or gap <= WINDOW_S, "%.0f s" % gap),
          ("(f) both pilots pass the truncation guard (<= 5%)", all(t == PILOT_N and u <= GUARD_RATE * PILOT_N for u, t in pil), pil)]
    valid = complete and all(ok for _l, ok, _d in c0)
    L = []; p = L.append
    p("=== G17-CANARY (RP21) v2 leg | %s | registered L22762-L22784 (767ebb79); interval form NORMAL (C-K1) ===" % TEST)
    p("POOL %s | store %s | set %s (%d matches, %d components) | judge %s | cap %d | temperature omitted | script sha256-lf16 %s | interval form %s"
      % (cfg.pool, cfg.store_sha[:16], setd["set_hash"][:16], n, len(set(comps)), JUDGE, CAP, script_sha16_lf(), form))
    p("(C0) VALIDITY, FIRST:")
    for lab, ok, det in c0:
        p("     %-64s %s  %s" % (lab, "PASS" if ok else "FAIL", det))
    hit("CAN:C0:PASS" if valid else "CAN:C0:FAIL")
    if not complete:
        p("     the caches are INCOMPLETE (v2-1 %d, v2-2 %d of %d): every readout below is NOT of record"
          % (sum(v is not None for v in V1.values()), sum(v is not None for v in V2.values()), n))
    pairs_r = [x for x in mids if V1[x] is not None and V2[x] is not None]
    if MUTANT == "c1v2_conv_b":
        pairs_r = [x for x in pairs_r if V1[x] not in UNUSABLE and V2[x] not in UNUSABLE]
    dr = [changed(V2[x], K[x]) if MUTANT == "d_r_from_k46" else changed(V1[x], V2[x]) for x in pairs_r]
    iv = boot_mean(dr, [M[x]["comp"] for x in pairs_r], cfg.boot, BOOT_SEED)
    if FORCE_C1_IV.get("canary") and pairs_r:
        iv = dict(iv, **FORCE_C1_IV["canary"])
    okB = [x for x in pairs_r if V1[x] not in UNUSABLE and V2[x] not in UNUSABLE]
    dB = sum(int(V1[x] != V2[x]) for x in okB)
    p("")
    if not pairs_r:
        hit("CAN:C1:UND_VALIDITY"); word = "UNDETERMINED BY VALIDITY"
        p("(C1-v2) no paired rows: UNDETERMINED BY VALIDITY")
    else:
        p("(C1-v2) FLOOR-ADMISSIBLE: d_r(v2) = share of the %d matches whose combined verdict differs between v2-1 and v2-2 = %d/%d = %s"
          % (len(pairs_r), sum(dr), len(pairs_r), iv_text(iv)))
        p("     convention B (usable in both) %d/%d = %.4f, beside; HELD iff the 95%% upper bound <= %.2f; FAILED iff the lower bound > %.2f"
          % (dB, len(okB), dB / max(1, len(okB)), C1V2_BAR, C1V2_BAR))
        w, dis = decide(word_c1v2, iv, form)
        if not valid:
            hit("CAN:C1:UND_VALIDITY"); word = "UNDETERMINED BY VALIDITY"
        else:
            word = w; hit({"HELD": "CAN:C1:HELD", "FAILED": "CAN:C1:FAILED"}.get(w, "CAN:C1:UND"))
        p("C1-v2: %s%s" % (word, "" if not dis else " (the forms disagree: normal %s, percentile %s)" % dis))
        p("     " + support_text(iv, len(pairs_r), iv["k"], "C1-v2"))
        p("     bootstrap SE at seeds 43-62: %s" % seeds_line(dr, [M[x]["comp"] for x in pairs_r], cfg.boot))
    # C2
    pe = [x for x in mids if V1[x] is not None]
    de = [changed(K[x], V1[x]) for x in pe]
    ive = boot_mean(de, [M[x]["comp"] for x in pe], cfg.boot, BOOT_SEED)
    both = [x for x in pairs_r]
    delta = [changed(K[x], V1[x]) - changed(V1[x], V2[x]) for x in both]
    ivd = boot_mean(delta, [M[x]["comp"] for x in both], cfg.boot, BOOT_SEED)
    rev = lambda A, B, xs: sum(1 for x in xs if decisive(A[x]) and decisive(B[x]) and A[x] != B[x])
    p("")
    p("(C2-v2) DESCRIPTIVE: d_e(v2) (K46 vs v2-1) = %d/%d = %s" % (sum(de), len(pe), iv_text(ive) if pe else "-"))
    p("     Delta = d_e - d_r (paired, same matches) = %s" % (iv_text(ivd) if both else "-"))
    p("     reversals: (K46, v2-1) %d | (v2-1, v2-2) %d" % (rev(K, V1, pe), rev(V1, V2, both)))
    p("     TIE share: K46 %.4f | v2-1 %.4f | v2-2 %.4f" % tuple(sum(1 for x in mids if D[x] == "TIE") / max(1, n) for D in (K, V1, V2)))
    strata = {}
    for x in both:
        kl = M[x]["klass"]
        st = "NONE" if kl == "NONE" else ("ONE-reference-correct" if keys[x]["v0"] == 1 else "ONE-reference-wrong" if keys[x]["v0"] == 0 else "ONE-v0-missing")
        for s in (st, M[x]["anchor"]):
            strata.setdefault(s, []).append(changed(V1[x], V2[x]))
    p("     strata d_r: %s" % ", ".join("%s %d/%d" % (s, sum(v), len(v)) for s, v in sorted(strata.items())))
    if pe:
        p("(C3-v2) THE v2 RULE FIXED NOW (not live at this epoch): floor of record d_e(v2) = %.4f; alarm bar = d_e + 3 x SE(d_e) = %.4f + 3 x %.4f = %.4f"
          % (ive["point"], ive["point"], ive["se"], ive["point"] + 3 * ive["se"]))
    p("LEAKAGE: n/a by design (identical bodies); per-contestant verdict-change share v2-1 -> v2-2: %s"
      % ", ".join("%s %d/%d" % (mo, sum(changed(V1[x], V2[x]) for x in both if mo in (M[x]["a"], M[x]["b"])),
                                sum(1 for x in both if mo in (M[x]["a"], M[x]["b"])))
                  for mo in sorted({M[x]["a"] for x in both} | {M[x]["b"] for x in both})))
    p("     agreement with the reference side (ONE): NOT BUILT (needs the responses' pred column, refused by the K46 key tripwire)")
    # predictions
    rv = valid and bool(pairs_r)
    none_dr = [changed(V1[x], V2[x]) for x in both if M[x]["klass"] == "NONE"]
    one_dr = [changed(V1[x], V2[x]) for x in both if M[x]["klass"] == "ONE"]
    unus = sum(1 for r in rows if r["vote"] in UNUSABLE)
    p4 = (sum(none_dr) / max(1, len(none_dr))) - (sum(one_dr) / max(1, len(one_dr)))
    preds = [("P1", "d_r(v2) = 0.10 [0.07, 0.14]", lambda: 0.07 <= iv["point"] <= 0.14, "%.4f" % iv.get("point", float("nan"))),
             ("P2", "d_e(v2) [0.07, 0.15] and Delta [-0.04, +0.06]", lambda: 0.07 <= ive["point"] <= 0.15 and -0.04 <= ivd["point"] <= 0.06,
              "%.4f / %+.4f" % (ive.get("point", float("nan")), ivd.get("point", float("nan")))),
             ("P3", "reversals 0 [0, 2] in each pair", lambda: rev(K, V1, pe) <= 2 and rev(V1, V2, both) <= 2, "%d / %d" % (rev(K, V1, pe), rev(V1, V2, both))),
             ("P4", "NONE d_r - ONE d_r = +0.03 [-0.03, +0.08]", lambda: -0.03 <= p4 <= 0.08, "%+.4f" % p4),
             ("P6", "fingerprint on 1,200 of 1,200; unusable 0 [0, 3]", lambda: not foreign and len(rows) == 4 * cfg.n_set and unus <= 3,
              "%d calls, foreign %s, unusable %d" % (len(rows), foreign or "none", unus))]
    p("")
    p("PREDICTIONS (draft; scored on the points):")
    for pid, text, test, val in preds:
        tag = ("HELD" if bool(test()) else "FAILED") if rv else "UND"
        hit("CAN:%s:%s" % (pid, tag))
        p("  %s %-50s %-36s -> %s" % (pid, text, val, tag if tag != "UND" else "UNDETERMINED BY VALIDITY"))
    p("")
    fired = False
    if not rv:
        hit("CAN:FALS:NOT_EVALUATED"); p("FALSIFIER: NOT EVALUATED (C0 failed or no paired rows)."); fired = True
    else:
        if word == "FAILED":
            hit("CAN:FALS:C1_FAILED"); fired = True
            p("FALSIFIER FIRES: C1-v2 FAILED (the v2 within-session floor is above 0.15 by interval): RP20's C1 is under 0.70 power at delta 4pp;"
              " before RP20 posts it is re-registered pre-data (delta raised or DESCRIPTIVE-ONLY), and RP19's planning discordance is re-priced.")
        if iv["point"] < 0.07:
            hit("CAN:FALS:P1_LOW"); fired = True
            p("P1 FAILS LOW (d_r < 0.07): the v2 floor is below the v1 floor; the planning discordance of RP20 / RP19 is conservative.")
    if not fired:
        hit("CAN:FALS:NOT_FIRED"); p("FALSIFIER: NOT FIRED.")
    acc = budget_gate(cfg, "canary", 0, "outcome", None, refuse=False)
    p("ACCOUNTING (day ledgers): %s %d of %d calls (caches %d, ledgers %d) | registered %d" % (LEGS["canary"]["test"], acc["own"], LEGS["canary"]["ceiling"],
                                                                                         acc["own_cache"], acc["own_ledger"], LEGS["canary"]["registered_calls"]))
    store_after(cfg, before, say)
    remove_db_guard()
    text = "\n".join(L) + "\n"
    print(text, flush=True)
    rc, path = write_outcome(cfg, "canary", text, complete)
    return dict(rc=rc, text=text, word=word, iv=iv, path=path)


def analyze_pair(cfg, leg):
    """RP20 (arms T / C on the NONE matches) or the ONE leg (T1 / C1 on the ONE matches)."""
    form = require_form(cfg)
    L_ = LEGS[leg]
    tarm, carm = L_["arms"]
    lines = []; say = say_factory(lines)
    if MUTANT != "analyze_no_configure":
        configure_rr()    # [2026-10-02, incident aaf12c77: C0 (d) read 0 of N because rr.JUDGE_MODEL stayed at its default]
    M, meta, before, n1 = common_open(cfg, leg, say)
    sched = leg_schedule(cfg, leg, M)
    mids = sorted({mid for mid, _ in sched})
    cache, cm = read_cache(cache_path(cfg, leg, None))
    keys = read_keys(cfg, M, say, mids=set(mids))
    T = {x: arm_combined(cache, M[x], tarm) for x in mids}
    C = {x: arm_combined(cache, M[x], carm) for x in mids}
    K = {x: M[x]["k46"] for x in mids}
    complete = all(T[x] is not None and C[x] is not None for x in mids)
    rows = [r for v in (cache or {}).values() for r in v.values()]
    c_rows = [r for r in rows if r["arm"] == carm]
    t_rows = [r for r in rows if r["arm"] == tarm]
    fps = Counter(r["provider"] for r in rows)
    foreign = sorted(set(fps) - {EXPECTED_FP, REFUSAL_FP})
    kd = [x for x in mids if keys[x]["kd"] and T[x] is not None and C[x] is not None]
    kd_all = [x for x in mids if keys[x]["kd"]]
    kd_comps = len({keys[x]["comp"] for x in kd_all})
    I = cfg.identity
    want_kd = (I["kd_none"], I["kd_none_comps"]) if leg == "rp20" else (I["kd_one"], I["kd_one_comps"])
    # the T rows' recorded swap check AND a re-check of every cached T body against its stored body
    t_ok = 0
    t_bad = []          # [2026-10-02, incident aaf12c77] a failed re-check is COUNTED AND PRINTED (the first one), never swallowed silently
    for r in t_rows:
        try:
            s, u, _sp, _sw = arm_payload(M[r["match_id"]], r["arm"], r["presentation_order"], n1)
            ok_r = zlib.decompress(r["body_zlib"]) == rr.payload_bytes(s, u) and r["swap_ok"] == 1
            if not ok_r:
                t_bad.append("%s/%s/o%d: the cached body != rr.payload_bytes(rebuilt system, user) (rr model %r, cap %r, temperature %r)"
                             % (r["match_id"], r["arm"], r["presentation_order"], rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE))
            t_ok += int(ok_r)
        except SystemExit as e:
            t_bad.append("%s/%s/o%d: %s (rr model %r, cap %r, temperature %r)" % (r["match_id"], r["arm"], r["presentation_order"],
                                                                               str(e)[:200], rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE))
    if t_bad:
        say("[BODY-RECHECK] %d of %d %s rows FAIL the re-check; the first: %s" % (len(t_bad), len(t_rows), tarm, t_bad[0]))
    pj = pilot_jobs(sched)
    pkeys = {x: keys[x] for x in {j[0] for j in pj}}
    pu, pt, pku, pkt = guard_rows(cache, pj, M, pkeys)
    c0 = [("(a) store sha256 equal before and after", True, "checked at the end"),
          ("(b) identity: %s scheduled %d; key-decidable %d in %d components" % (L_["klass"], I["none"] if leg == "rp20" else I["one"], want_kd[0], want_kd[1]),
           len(mids) == (I["none"] if leg == "rp20" else I["one"]) and ((len(kd_all), kd_comps) == want_kd or MUTANT == "census_off"),
           "%d scheduled; key-decidable %d in %d" % (len(mids), len(kd_all), kd_comps)),
          ("(c) %s bodies byte-identical to the stored bodies" % carm, sum(1 for r in c_rows if r["payload_sha256"] == r["stored_payload_sha256"]) == len(c_rows) == 2 * len(mids),
           "%d of %d (registered %d)" % (sum(1 for r in c_rows if r["payload_sha256"] == r["stored_payload_sha256"]), len(c_rows), 2 * len(mids))),
          ("(d) %s bodies differ from %s exactly in the swapped span%s" % (tarm, carm, "" if tarm == "T" else " / the stripped reference"),
           t_ok == len(t_rows) == 2 * len(mids), "%d of %d%s" % (t_ok, len(t_rows), "" if not t_bad else "; first mismatch: " + t_bad[0][:200])),
          ("(e) every call fingerprinted %s" % EXPECTED_FP, not foreign and len(rows) > 0, dict(fps)),
          ("(f) the pilot's truncation guard (all rows and key-decidable rows <= 5%)", pt > 0 and guard_ok(pu, pt, pku, pkt, True),
           "all %d of %d, key-decidable %d of %d" % (pu, pt, pku, pkt))]
    valid = complete and all(ok for _l, ok, _d in c0)
    tag = "RP20" if leg == "rp20" else "ONE"
    L = []; p = L.append
    p("=== %s (%s) | %s | registered L22786-L22810 (767ebb79) section %s; interval form NORMAL (C-K1) ===" % (L_["test"], "RP20" if leg == "rp20" else "RP20's ONE leg", TEST,
                                                                                         "2" if leg == "rp20" else "2b"))
    p("POOL %s | store %s | %s matches %d | arms %s / %s | judge %s | cap %d | temperature omitted | N1 sha %s | script sha256-lf16 %s | interval form %s"
      % (cfg.pool, cfg.store_sha[:16], L_["klass"], len(mids), tarm, carm, JUDGE, CAP, hashlib.sha256(n1[1].encode()).hexdigest()[:16],
         script_sha16_lf(), form))
    p("(C0) VALIDITY, FIRST:")
    for lab, ok, det in c0:
        p("     %-78s %s  %s" % (lab, "PASS" if ok else "FAIL", det))
    if leg == "rp20":
        hit("RP20:C0:PASS" if valid else "RP20:C0:FAIL")
    rightA = lambda V, x: int(V[x] == keys[x]["side"])
    dA = [rightA(T, x) - rightA(C, x) for x in kd]
    comps = [keys[x]["comp"] for x in kd]
    iv = boot_mean(dA, comps, cfg.boot, BOOT_SEED) if kd else None
    if MUTANT == "conv_b_decides" and leg == "rp20":
        kdb = [x for x in kd if decisive(T[x]) and decisive(C[x])]
        iv = boot_mean([rightA(T, x) - rightA(C, x) for x in kdb], [keys[x]["comp"] for x in kdb], cfg.boot, BOOT_SEED) if kdb else None
    if FORCE_C1_IV.get(leg) and iv is not None:
        iv = dict(iv, **FORCE_C1_IV[leg])
    kdB = [x for x in kd if decisive(T[x]) and decisive(C[x])]
    dB = [rightA(T, x) - rightA(C, x) for x in kdB]
    accT = sum(rightA(T, x) for x in kd) / max(1, len(kd)); accC = sum(rightA(C, x) for x in kd) / max(1, len(kd))
    p("")
    word = "UNDETERMINED BY VALIDITY"
    if iv is None:
        hit("%s:C1:UND_VALIDITY" % tag)
        p("(C1) no key-decidable paired rows: UNDETERMINED BY VALIDITY")
    else:
        p("(C1) Delta_A = acc_A(%s) - acc_A(%s), paired by match, on %d key-decidable %s matches in %d components: acc %.4f - %.4f = %s"
          % (tarm, carm, len(kd), L_["klass"], iv["k"], accT, accC, iv_text(iv)))
        p("     convention B (committed in both arms, paired; %d matches): Delta_B = %+.4f, beside, deciding nothing"
          % (len(kdB), sum(dB) / max(1, len(kdB))))
        if leg == "rp20":
            w, dis = decide(word_rp20, iv, form)
            if not valid:
                hit("RP20:C1:UND_VALIDITY")
            else:
                word = w
                hit("RP20:C1:EQUIVALENT_SHIFT" if w.startswith("EQUIVALENT, with") else {"EQUIVALENT": "RP20:C1:EQUIVALENT", "GAIN": "RP20:C1:GAIN",
                                                                                          "LOSS": "RP20:C1:LOSS"}.get(w, "RP20:C1:UND"))
            p("     EQUIVALENT iff the 90%% CI lies inside (-%.3f, +%.3f); GAIN / LOSS iff not EQUIVALENT and the 95%% CI excludes 0 on that side"
              % (EQ_DELTA, EQ_DELTA))
        else:
            w, dis = decide(word_one, iv, form)
            if not valid:
                hit("ONE:C1:UND_VALIDITY")
            else:
                word = w; hit({"LOSS": "ONE:C1:LOSS", "GAIN": "ONE:C1:GAIN"}.get(w, "ONE:C1:UND"))
            p("     LOSS (the reference helps) iff the 95% upper bound < 0; GAIN iff the 95% lower bound > 0")
        p("C1: %s%s" % (word, "" if not dis else " (the forms disagree: normal %s, percentile %s)" % dis))
        p("     " + support_text(iv, len(kd), iv["k"], "C1"))
        p("     bootstrap SE at seeds 43-62: %s" % seeds_line(dA, comps, cfg.boot))
    allm = [x for x in mids if T[x] is not None and C[x] is not None]
    dtc = [changed(T[x], C[x]) for x in allm]
    ivtc = boot_mean(dtc, [M[x]["comp"] for x in allm], cfg.boot, BOOT_SEED) if allm else None
    dck = [changed(C[x], K[x]) for x in allm]
    ivck = boot_mean(dck, [M[x]["comp"] for x in allm], cfg.boot, BOOT_SEED) if allm else None
    tie = lambda V: sum(1 for x in mids if V[x] == "TIE") / max(1, len(mids))
    rev = sum(1 for x in allm if decisive(T[x]) and decisive(C[x]) and T[x] != C[x])
    p("")
    p("(C2) DESCRIPTIVE: TIE share %s - %s on all %d = %.4f - %.4f = %+.4f" % (tarm, carm, len(mids), tie(T), tie(C), tie(T) - tie(C)))
    if ivtc:
        p("     d(%s, %s) on all %d = %d/%d = %s" % (tarm, carm, len(allm), sum(dtc), len(allm), iv_text(ivtc)))
        p("     d(%s, K46) (a second v2 time point) = %d/%d = %s" % (carm, sum(dck), len(allm), iv_text(ivck)))
    p("     reversals (%s vs %s, decisive in both, opposite) %d" % (tarm, carm, rev))
    dr = None
    if leg == "rp20" and ivtc:
        dr = canary_floor(cfg, M)
        if dr is None:
            hit("RP20:C2:NO_FLOOR")
            p("     d_r(v2) from RP21 C1-v2: NOT READ (the canary caches are absent or incomplete); 'the sentence changes verdicts' is NOT written")
        else:
            diff = ivtc["point"] - dr[0]
            se = math.sqrt(ivtc["se"] ** 2 + dr[1] ** 2)
            lo = diff - 1.959963984540054 * se
            p("     d(T, C) - d_r(v2) = %.4f - %.4f = %+.4f (between-sample; SE %.4f; 95%% lower bound %+.4f)" % (ivtc["point"], dr[0], diff, se, lo))
            if lo > 0:
                hit("RP20:C2:CHANGES"); p("     THE SENTENCE CHANGES VERDICTS (d(T, C) above the v2 within-session floor by interval)")
            else:
                hit("RP20:C2:NOT_SHOWN"); p("     'the sentence changes verdicts' is NOT shown (the interval does not exclude the floor)")
    p("STRATA (descriptive): %s" % "; ".join(
        "%s n %d Delta_A %+.4f" % (s, len(v), sum(v) / max(1, len(v))) for s, v in sorted(_strata(kd, M, keys, T, C, rightA, leg).items())))
    if leg == "rp20":
        p("     reference-correct / reference-wrong: NOT APPLICABLE (no NONE match carries a reference); contested / cross-tier: NOT BUILT (no"
          " registered definition for the v2 roster; for the registrar)")
    per = {}
    for x in kd:
        for mo in (M[x]["a"], M[x]["b"]):
            per.setdefault(mo, []).append(x)
    p("LEAKAGE (descriptive): per-contestant key accuracy and change share (%s / %s): %s" % (tarm, carm, ", ".join(
        "%s n %d acc %.3f/%.3f chg %.3f" % (mo, len(xs), sum(rightA(T, x) for x in xs) / len(xs), sum(rightA(C, x) for x in xs) / len(xs),
                                            sum(changed(T[x], C[x]) for x in xs) / len(xs)) for mo, xs in sorted(per.items()))))
    for arm, V in ((tarm, T), (carm, C)):
        krows = []
        for x in allm:
            ka, kb = keys[x]["ka"], keys[x]["kb"]
            if ka is None or kb is None:
                continue
            krows.append((float(ka - kb), V[x]))
        p("     CONSENSUS-FIT [%s]: %s" % (arm, key_coefficient(krows)))
    if leg == "one":
        p("     per-contestant agreement with the reference side (C1 vs T1): NOT BUILT (needs the responses' pred column, refused by the K46 key"
          " tripwire; registrar b3dd18ab)")
        p("     CONSENSUS-FIT REF coefficient: NOT BUILT (the reference-agreement contrast needs the pred column, refused by the key tripwire)")
    # predictions
    rv = valid and iv is not None
    p("")
    p("PREDICTIONS (draft; scored on the points):")
    if leg == "rp20":
        per_move = [abs(sum(rightA(T, x) for x in xs) / len(xs) - sum(rightA(C, x) for x in xs) / len(xs)) for xs in per.values() if len(xs) >= 40]
        unT = sum(1 for r in t_rows if r["vote"] in UNUSABLE) / max(1, len(t_rows)); unC = sum(1 for r in c_rows if r["vote"] in UNUSABLE) / max(1, len(c_rows))
        preds = [("P1", "Delta_A = +0.5pp [-2.0, +3.5]", lambda: -0.020 <= iv["point"] <= 0.035, "%+.4f" % (iv["point"] if iv else float("nan"))),
                 ("P2", "TIE share T - C = -1.0pp [-4.0, +2.0]", lambda: -0.040 <= tie(T) - tie(C) <= 0.020, "%+.4f" % (tie(T) - tie(C))),
                 ("P3", "d(T, C) [0.08, 0.15]; d(T, C) - d_r [-0.03, +0.05]",
                  lambda: 0.08 <= ivtc["point"] <= 0.15 and (dr is not None and -0.03 <= ivtc["point"] - dr[0] <= 0.05),
                  "%.4f / %s" % (ivtc["point"] if ivtc else float("nan"), "%+.4f" % (ivtc["point"] - dr[0]) if (dr and ivtc) else "no floor")),
                 ("P4", "d(C, K46) [0.07, 0.15]", lambda: 0.07 <= ivck["point"] <= 0.15, "%.4f" % (ivck["point"] if ivck else float("nan"))),
                 ("P5", "per-contestant movement <= 3pp (>= 40 kd rows)", lambda: all(v <= 0.03 for v in per_move),
                  "max %.4f over %d" % (max(per_move) if per_move else 0.0, len(per_move))),
                 ("P6", "fingerprint 7,384 of 7,384; unusable <= 0.3% per arm",
                  lambda: not foreign and len(rows) == 4 * len(mids) and unT <= 0.003 and unC <= 0.003,
                  "%d calls, foreign %s, unusable %.4f / %.4f" % (len(rows), foreign or "none", unT, unC))]
    else:
        wrong = [x for x in kd if keys[x]["v0"] == 0]
        dwr = sum(rightA(T, x) - rightA(C, x) for x in wrong) / max(1, len(wrong))
        preds = [("P1", "Delta1_A = -10pp [-15, -5]", lambda: -0.15 <= iv["point"] <= -0.05, "%+.4f" % (iv["point"] if iv else float("nan"))),
                 ("P2", "reference-wrong stratum Delta1 = +35pp [+10, +55]", lambda: 0.10 <= dwr <= 0.55, "%+.4f (n %d)" % (dwr, len(wrong)))]
    for pid, text, test, val in preds:
        t_ = ("HELD" if bool(test()) else "FAILED") if rv else "UND"
        hit("%s:%s:%s" % (tag, pid, t_))
        p("  %s %-52s %-44s -> %s" % (pid, text, val, t_ if t_ != "UND" else "UNDETERMINED BY VALIDITY"))
    p("")
    if leg == "rp20":
        if not rv:
            hit("RP20:FALS:NOT_EVALUATED"); p("FALSIFIER: NOT EVALUATED (C0 failed or no key-decidable rows).")
        elif word in ("GAIN", "LOSS"):
            hit("RP20:FALS:MOVES")
            if MUTANT != "falsifier_silent":
                p("FALSIFIER FIRES: C1 %s: K46's NONE-branch accuracy (0.7512) and its verdicts may NOT be quoted or reused as the v2 recipe's"
                  " no-reference branch; the K46-KEY-READ sentence gains \"with a false reference sentence, priced at %+.4f\"; RP19 posts the N1"
                  " template on its NONE branch or discloses the false sentence; D2's reuse option is withdrawn." % (word, iv["point"]))
        elif word.startswith("EQUIVALENT"):
            hit("RP20:FALS:EQUIVALENT")
            p("C1 EQUIVALENT: reuse is admissible with the disclosure \"a false reference sentence, key accuracy equivalent within +-4pp (RP20)\";"
              " nothing is promoted beyond that.")
        else:
            hit("RP20:FALS:NEITHER"); p("FALSIFIER: NOT FIRED (C1 UNDETERMINED: neither the reuse nor its withdrawal is supported).")
    else:
        if rv and word in ("UNDETERMINED", "GAIN"):
            hit("ONE:FALS:FIRES")
            p("FALSIFIER FIRES: C1 %s: the reference's value does not transfer to the v2 recipe on content-closed data at this n; the [P-FAM]"
              " +12.6pp stays history and no v2 sentence cites it." % word)
        else:
            hit("ONE:FALS:NOT_FIRED"); p("FALSIFIER: NOT FIRED%s." % ("" if rv else " (not evaluated: C0 failed)"))
    acc = budget_gate(cfg, leg, 0, "outcome", None, refuse=False)
    p("ACCOUNTING (day ledgers): %s %d of %d calls (cache %d, ledgers %d) | registered %d"
      % (L_["test"], acc["own"], L_["ceiling"], acc["own_cache"], acc["own_ledger"], L_["registered_calls"]))
    store_after(cfg, before, say)
    remove_db_guard()
    text = "\n".join(L) + "\n"
    print(text, flush=True)
    rc, path = write_outcome(cfg, leg, text, complete)
    return dict(rc=rc, text=text, word=word, iv=iv, path=path)


def _strata(kd, M, keys, T, C, rightA, leg):
    out = {}
    for x in kd:
        d = rightA(T, x) - rightA(C, x)
        ss = [M[x]["anchor"], "K46 " + ("TIE" if M[x]["k46"] == "TIE" else "decisive")]
        if leg == "one":
            ss.append("reference-correct" if keys[x]["v0"] == 1 else "reference-wrong (DESCRIPTIVE-ONLY)" if keys[x]["v0"] == 0 else "v0 missing")
        for s in ss:
            out.setdefault(s, []).append(d)
    return out


def canary_floor(cfg, M):
    """(d_r, SE) from the complete RP21 canary caches, else None (component-clustered, B as cfg.boot)."""
    c1, _ = read_cache(cache_path(cfg, "canary", "v2-1"))
    c2, _ = read_cache(cache_path(cfg, "canary", "v2-2"))
    if not c1 or not c2:
        return None
    mids = sorted({mid for (_a, mid) in c1} & {mid for (_a, mid) in c2})
    pairs = [(arm_combined(c1, M[x], "C"), arm_combined(c2, M[x], "C"), x) for x in mids]
    pairs = [p for p in pairs if p[0] is not None and p[1] is not None]
    if len(pairs) != cfg.n_set:
        return None
    iv = boot_mean([changed(a, b) for a, b, _ in pairs], [M[x]["comp"] for _a, _b, x in pairs], cfg.boot, BOOT_SEED)
    return iv["point"], iv["se"]


def _unguard_on_exit(fn):
    """Every mode that installs the DB guard removes it on ANY exit (a refusal included), so a refused launch never leaves the
    process with sqlite3.connect rewritten."""
    def wrapped(*a, **k):
        try:
            return fn(*a, **k)
        finally:
            remove_db_guard()
    wrapped.__name__ = fn.__name__
    wrapped.__wrapped__ = fn
    return wrapped


launch = _unguard_on_exit(launch)
analyze_canary = _unguard_on_exit(analyze_canary)
analyze_pair = _unguard_on_exit(analyze_pair)


# ============================================================================================ CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--freeze-canary", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--leg", choices=sorted(LEGS))
    ap.add_argument("--pass", dest="pass_", choices=["v2-1", "v2-2"], default=None)
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--budget", type=int, default=None, help="the explicit call budget of a posting launch (also a hard cap)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze-canary", action="store_true")
    ap.add_argument("--analyze-rp20", action="store_true")
    ap.add_argument("--analyze-one", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        import k46_repost_selftest as ST
        return ST.selftest()
    if a.mutants:
        import k46_repost_selftest as ST
        return ST.mutants()
    cfg = real_cfg()
    if a.freeze_canary:
        lines = []; say = say_factory(lines)
        M, meta, before, n1 = common_open(cfg, "canary", say)
        d, present = load_or_verify_set(cfg, M, say, write=not a.dry_run)
        draw_lines(d, say)
        store_after(cfg, before, say)
        remove_db_guard()
        return 0
    if a.analyze_canary:
        return analyze_canary(cfg)["rc"]
    if a.analyze_rp20:
        return analyze_pair(cfg, "rp20")["rc"]
    if a.analyze_one:
        return analyze_pair(cfg, "one")["rc"]
    if not a.leg:
        ap.error("give --leg (canary / rp20 / one) or a mode")
    pass_ = a.pass_ if a.leg == "canary" else None
    if a.leg == "canary" and pass_ is None:
        ap.error("--leg canary needs --pass v2-1 or v2-2")
    launch(cfg, a.leg, pass_, a.pilot, a.run, a.go, a.budget, workers=a.workers, dry=a.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
