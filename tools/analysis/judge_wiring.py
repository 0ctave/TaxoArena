"""JUDGE-WIRING (FRAMEWORK.md item 25; docs/judge_v2_program.md; docs/plan_2026-09-15.md) - the Python side of the
Kotlin-vs-Python paired contrast: "Kotlin production path on grok + recipe vs the Python cache on identical matches.
Criterion: |delta| <= 1.9pp under both conventions. Consequence: no mixed-judge board until a whole-board re-judge."

Every mode below is ZERO CALLS. The 600-match paired run itself is the Kotlin harness (`gradlew judgeWiring
-Dmode=run -Dconfirm=JUDGE-WIRING`, launched by the author under the plan's Block 4), and it refuses to post unless the
Kotlin payload shas equal the Python shas this script writes.

  python tools/analysis/judge_wiring.py --export-kit          write experiment_results/judge_wiring/stack_v2_kit.db from the
                                                              sources of record (anchor rubrics, routing, cached references)
  python tools/analysis/judge_wiring.py --freeze-only         build judge_wiring_set.json (600 = 300 contested + 300 cross-tier
                                                              of the 1,974 RECIPE-GROK matches, seed 42); prints the hash the
                                                              author registers in SET_HASH_OF_RECORD
  python tools/analysis/judge_wiring.py --dump-payload <mid>  write the exact bytes call_judge_full would post (both orders)
                                                              + sha256, to diff `cmp` against the Kotlin dump
  python tools/analysis/judge_wiring.py --shas                payload_shas_python.csv for the whole set (the run precondition)
  python tools/analysis/judge_wiring.py --gen-fixtures        the JSON fixtures the Kotlin unit tests pin against (ASCII-escaped)
  python tools/analysis/judge_wiring.py --dry-run             assert set / kit / hashes / EXCLUDED / source-level payload identity
  python tools/analysis/judge_wiring.py --analyze <kotlin.db> the paired readout (conventions A and B, bootstrap CI, McNemar,
                                                              agreement, finish_reason counts, sha equality) -> PASS/FAIL

BOARD MODE (the consequence of the FAIL: the whole-board re-judge through the Kotlin path; author's go above the 4,000-match rule).
The set is every match GROK-CALIB judged whose question has a cached grok-reasoning reference (9,123 of grok_calib.db's 9,142 =
the x12 MAIN schedule with 4389 / 6528 absent), in match_id order. The 19 reference-less matches (10 questions) are EXCLUDED
from the set by construction (author decision (b), 2026-09-16): the Kotlin production path skips a match whose question has no
reference (JudgeRecipeConfig.onMissingReference accepts only SKIP), so they can carry no Kotlin verdict; their ids and qids
are kept in the set's meta under `excluded_no_reference` and GROK-CALIB's readings on them (judged without a reference) are
printed beside the board outcome. The 600-set files and constants are untouched; the harness runs the board under
-DsetJson=judge_wiring_board_set.json -DoutDir=experiment_results/judge_wiring/board.
  python tools/analysis/judge_wiring.py --freeze-board         build judge_wiring_board_set.json; prints the hash for BOARD_HASH_OF_RECORD
  python tools/analysis/judge_wiring.py --shas-board           payload_shas_python_board.csv through grok_calib.Assembler (the bytes
                                                              GROK-CALIB posted) + a byte copy under board/payload_shas_python.csv
  python tools/analysis/judge_wiring.py --dry-run-board        every payload assembled and asserted, nothing posted
  python tools/analysis/judge_wiring.py --analyze-board <db>   (a) the board of record (BT, rho + CI, top-4, conventions A/B, rates),
                                                              (b) the pairing with GROK-CALIB, (c) the widener readout, (d)
                                                              board_outcome.txt (DESCRIPTIVE; _partial while the cache is short)

WHAT IS COMPARED. The Python arm is the RECIPE-GROK cache (experiment_results/x12_crossdomain/stack_v2_promptv2_grok.db,
1,974 verdicts, judged 2026-09-10 through stack_judge.py --prompt v2 --judge grok -> rejudge_reasoning.call_judge, max_tokens
8192, temperature omitted). The Kotlin arm re-judges 600 of those matches through TaxonomyArenaService's recipe branch with
byte-identical payloads. Even at byte identity the provider is nondeterministic: DECOMP's test-retest floor is 5.7% verdict
disagreement on byte-identical prompts, so the delta reads against that floor.

TEMPERATURE (flagged for the author, not decided here). FRAMEWORK Stage 4 asks the Kotlin path for an explicit literal;
Amendment 1 D2 records that every cache of record omitted it. Byte identity with the cache requires omission, so this
contrast posts WITHOUT the field and records the literal string "omitted" in run_meta, every judge_calls row and the
fingerprint. The Kotlin path can post a literal (judgeRecipeTemperature); adopting one is a later registration.

INVARIANTS. pool_guard.assert_pool_of_record() first; every set question in p2dca21ab5f4ef3ae; Meta-Llama-3-70B-Instruct
absent; the kit carries NO `correct` column (answer-key blindness stays structural; --analyze joins ref_correct by qid from
the Python cache); all inputs opened ?mode=ro; the only writes are under experiment_results/judge_wiring/ and the fixtures.
"""
import os, sys, csv, json, time, math, random, sqlite3, hashlib, argparse
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj
import rubric_512 as r512
import judge_free_tests as jf                          # board_from / rho / violations (BOARD mode)

POOL = pool_guard.FROZEN_POOL_ID                       # p2dca21ab5f4ef3ae
JUDGE = "grok-4-1-fast-non-reasoning"                  # the deployed judge (FRAMEWORK.md Stage 3; Amendment 1 D1)
REFERENCE = "grok-reasoning"                           # STACK-v2's cached reasoning reference
TREE = "bareq512_s42"                                  # the clean promoted tree whose anchors the ladder was induced on
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
SEED = 42
PER_STRATUM = 300
N_SET = 2 * PER_STRATUM
MAXTOK = rr.MAX_TOKENS                                 # 8192
TEMPERATURE = None                                     # omitted (see module docstring)
CRITERION_PP = 1.9
DECOMP_FLOOR = 0.057
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
PY_CACHE = os.path.join(X12DIR, "stack_v2_promptv2_grok.db")          # RECIPE-GROK
OUTDIR = os.path.join(ROOT, "experiment_results", "judge_wiring")
KIT = os.path.join(OUTDIR, "stack_v2_kit.db")
SET_JSON = os.path.join(OUTDIR, "judge_wiring_set.json")
SHAS_PY = os.path.join(OUTDIR, "payload_shas_python.csv")
FIXTURES = os.path.join(ROOT, "src", "test", "resources", "judge_wiring")
# The author registers the frozen set's hash here (plan amendment). While None, --freeze-only prints the hash it produced and
# every judged-side mode (--shas, --dump-payload, --dry-run, --analyze) refuses a set file whose hash is not the one on record.
SET_HASH_OF_RECORD = "ae92da306544f453"   # registered 2026-09-16 (plan Amendment 2) before any call

# ── BOARD mode (the consequence of JUDGE-WIRING's FAIL: the whole-board re-judge through the Kotlin path) ────────────────
# The board set is every match GROK-CALIB judged (experiment_results/x12_crossdomain/grok_calib.db: the 9,142 matches of the
# x12 MAIN schedule, 4389 and 6528 absent) whose question has a reference in the kit (9,123; the 19 reference-less matches are
# excluded by construction, see NOREF_DECISION), re-judged through the Kotlin recipe path on the deployed judge, cap 8192,
# temperature omitted, dual order. Nothing above changes: the board has its own set file, hash constant, sha file and outcome
# file, and every board-side write of the Kotlin harness goes under BOARD_DIR (its -DoutDir), because the harness's `shas`
# and `run` modes use FIXED file names inside outDir (payload_shas_kotlin.csv, payload_shas_python.csv, kotlin_<hash>.db).
GC_CACHE = os.path.join(X12DIR, "grok_calib.db")                    # GROK-CALIB's cache (grok_calib.cache_path() at the default cap)
BOARD_JSON = os.path.join(OUTDIR, "judge_wiring_board_set.json")
SHAS_PY_BOARD = os.path.join(OUTDIR, "payload_shas_python_board.csv")
BOARD_DIR = os.path.join(OUTDIR, "board")                           # gradlew judgeWiring ... -DoutDir=experiment_results/judge_wiring/board
SHAS_PY_BOARD_HARNESS = os.path.join(BOARD_DIR, "payload_shas_python.csv")   # byte copy of SHAS_PY_BOARD under the harness's fixed name
SB_BOARD = os.path.join(OUTDIR, "board_systematic_budget.txt")
BOARD_OUTCOME = os.path.join(OUTDIR, "board_outcome.txt")
N_GC = 9142                                                         # GROK-CALIB's cache: every x12 MAIN match it judged
N_EXCLUDED_NOREF = 19                                               # of those, judged WITHOUT a reference (kit has none): excluded from the board set
N_BOARD = N_GC - N_EXCLUDED_NOREF                                   # 9,123: the board set of record; the Kotlin run posts 2 x N_BOARD = 18,246 calls
ABSENT_FROM_X12 = {4389, 6528}                                      # Mistral content-filter refusals in ARENA-V2; absent from every board
BOOT_B = 1000                                                       # question-resampled bootstrap draws for the board's rho CI
# The author registers the board set's hash here before any call (as SET_HASH_OF_RECORD above). While None, --freeze-board prints
# the hash it produced and every board mode warns; once set, every board mode refuses a board file whose hash differs, and
# analyze_board writes the outcome OF RECORD only from BOARD_DIR/kotlin_<BOARD_HASH_OF_RECORD>.db (see board_of_record_gate).
BOARD_HASH_OF_RECORD = "c0d3f708cbc3930e"   # 9,123 matches, frozen 2026-09-16 (author decision (b): the 19 reference-less excluded); registered in the plan by the author
# Why the 19 reference-less matches are excluded from the board set (author decision (b), 2026-09-16; read from the source):
NOREF_DECISION = ("EXCLUDED from the board set by construction: the Kotlin production path SKIPS a match whose question has no reference in "
                  "the kit (StackV2JudgeRecipe.assemble returns Assembly.Skipped('no reference for question ...') when kit.referenceOf(qid) "
                  "is null, TaxonomyArenaService.assembleRecipe returns null (recipeSkipped++), and JudgeRecipeConfig.onMissingReference "
                  "accepts only SKIP: validate() rejects any other value, no switch exists to judge without a reference). GROK-CALIB judged "
                  "these 19 matches WITHOUT a reference block; the Kotlin board can carry no verdict for them, so the set of record is the "
                  "9,123 matches with a reference and the Kotlin run posts exactly 2 x 9,123 = 18,246 calls. GROK-CALIB's readings on the 19 "
                  "are printed beside the board outcome for the record.")


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


def ro(path):
    return sqlite3.connect("file:%s?mode=ro" % path, uri=True)


def temp_label():
    return "omitted" if TEMPERATURE is None else repr(TEMPERATURE)


def configure_rr():
    """Point rejudge_reasoning at the deployed judge exactly as stack_judge.py --judge grok does (stack_judge.run: rr.PROVIDER
    = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"); MAX_TOKENS is the module default 8192; TEMPERATURE None."""
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE
    sj.PROMPT = "v2"; sj.JUDGE = "grok"


def sha_hex(b):
    return hashlib.sha256(b).hexdigest()


# ── the kit ─────────────────────────────────────────────────────────────────────

def kit_rows():
    """(rubrics: label -> (system_prompt, rubric), anchors: qid -> (leaf_id, anchor), refs: qid -> (letter, text)) from the
    sources of record, read-only: rubric_ladder.db kind='anchor'; the promoted routing CSV + snapshots.db graph
    (rubric_512.primary_routing / anchor_fn); judge_solve/grok-reasoning.db resolved against the gpt-4o row's options_json
    (rejudge_reference.references). The `correct` flag rref returns is DROPPED here."""
    rubrics = sj.anchor_rubrics()
    snap = r512.snapshot_id(TREE); nodes = r512.load_graph(snap); route = r512.primary_routing(TREE); anchor = r512.anchor_fn(nodes)
    anchors = {q: (leaf, anchor(leaf)) for q, leaf in route.items()}
    rref.set_reference(REFERENCE)
    refs = {q: (letter, text) for q, (letter, text, _correct) in rref.references().items()}
    missing = sorted({a for _, a in anchors.values()} - set(rubrics))
    assert not missing, "no anchor rubric for %s" % missing
    return rubrics, anchors, refs, snap


def kit_hash(rubrics, anchors, refs):
    """Canonical row dump, identical in StackV2Kit.canonicalHash (Kotlin): R/A/F lines, sorted, json.dumps (ensure_ascii) for text."""
    lines = []
    for label in sorted(rubrics):
        sp, rb = rubrics[label]; lines.append("R\t%s\t%s\t%s" % (label, json.dumps(sp), json.dumps(rb)))
    for q in sorted(anchors):
        leaf, a = anchors[q]; lines.append("A\t%d\t%s\t%s" % (q, leaf, a))
    for q in sorted(refs):
        letter, text = refs[q]; lines.append("F\t%d\t%s\t%s" % (q, letter, json.dumps(text)))
    return sha_hex("\n".join(lines).encode("utf-8"))


def git_head():
    try:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        return "?"


def file_sha(p):
    return sha_hex(open(p, "rb").read()) if os.path.exists(p) else "missing"


def export_kit(force=False):
    rubrics, anchors, refs, snap = kit_rows()
    h = kit_hash(rubrics, anchors, refs)
    os.makedirs(OUTDIR, exist_ok=True)
    if os.path.exists(KIT):
        old = dict(ro(KIT).execute("SELECT key, value FROM meta"))
        if old.get("kit_hash") == h and not force:
            print("[KIT] %s already holds this kit (hash %s); nothing written" % (rel(KIT), h)); return h
        if not force:
            raise SystemExit("[KIT] %s exists with hash %s != %s from the current sources; move it aside or --force" % (rel(KIT), old.get("kit_hash"), h))
        os.remove(KIT)
    con = sqlite3.connect(KIT)
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE anchor_rubrics (label TEXT PRIMARY KEY, system_prompt TEXT NOT NULL, rubric TEXT NOT NULL)")
    con.execute("CREATE TABLE question_anchor (question_id INTEGER PRIMARY KEY, leaf_id TEXT NOT NULL, anchor TEXT NOT NULL)")
    con.execute("CREATE TABLE reference (question_id INTEGER PRIMARY KEY, letter TEXT NOT NULL, option_text TEXT NOT NULL)")
    con.executemany("INSERT INTO anchor_rubrics VALUES (?,?,?)", [(l, sp, rb) for l, (sp, rb) in sorted(rubrics.items())])
    con.executemany("INSERT INTO question_anchor VALUES (?,?,?)", [(q, leaf, a) for q, (leaf, a) in sorted(anchors.items())])
    con.executemany("INSERT INTO reference VALUES (?,?,?)", [(q, letter, text) for q, (letter, text) in sorted(refs.items())])
    meta = dict(recipe="STACK-v2", tree=TREE, snapshot_id=snap, reference_model=REFERENCE, judge=JUDGE,
                ladder_sha256=file_sha(sj.LADDER), solve_sha256=file_sha(rref.SOLVE_DB),
                routing_csv_sha256=file_sha(os.path.join(r512.PROMOTED, "%s_reserved_leaf_assignments.csv" % TREE)),
                ladder_outcome=rel(os.path.join(X12DIR, "rubric_ladder_outcome.txt")),
                git_head=git_head(), export_ts=time.strftime("%Y-%m-%d %H:%M:%S"), kit_hash=h,
                n_rubrics=str(len(rubrics)), n_questions=str(len(anchors)), n_references=str(len(refs)))
    con.executemany("INSERT INTO meta VALUES (?,?)", sorted(meta.items()))
    con.commit(); con.close()
    print("[KIT] wrote %s: %d anchor rubrics | %d routed questions | %d references | hash %s" % (rel(KIT), len(rubrics), len(anchors), len(refs), h))
    return h


def open_kit():
    """Read the exported kit read-only, recompute and verify its hash (the Kotlin loader does the same)."""
    assert os.path.exists(KIT), "[KIT] %s missing: run --export-kit" % rel(KIT)
    c = ro(KIT)
    meta = dict(c.execute("SELECT key, value FROM meta"))
    rubrics = {l: (sp, rb) for l, sp, rb in c.execute("SELECT label, system_prompt, rubric FROM anchor_rubrics")}
    anchors = {q: (leaf, a) for q, leaf, a in c.execute("SELECT question_id, leaf_id, anchor FROM question_anchor")}
    refs = {q: (letter, text) for q, letter, text in c.execute("SELECT question_id, letter, option_text FROM reference")}
    cols = [d[1] for d in c.execute("PRAGMA table_info(reference)")]
    assert "correct" not in cols, "[KIT] the reference table must not carry the answer key"
    h = kit_hash(rubrics, anchors, refs)
    assert meta.get("kit_hash") == h, "[KIT] recorded hash %s != recomputed %s" % (meta.get("kit_hash"), h)
    assert meta.get("recipe") == "STACK-v2"
    return meta, rubrics, anchors, refs


# ── the frozen set ──────────────────────────────────────────────────────────────

def pool_qids():
    return {q for (q,) in ro(rj.EVAL_DB).execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}


def set_hash(matches):
    canon = "\n".join("%d:%d:%s:%s:%s" % (m["match_id"], m["qid"], m["model_a"], m["model_b"], m["stratum"]) for m in matches)
    return sha_hex(canon.encode("utf-8"))[:16]


def python_cache_rows(path=PY_CACHE):
    """RECIPE-GROK's 1,974 verdicts: match_id -> row dict (any stack_judge-shaped cache with `path`, e.g. GROK-CALIB's)."""
    c = ro(path)
    return {r[0]: dict(mid=r[0], a=r[1], b=r[2], nid=r[3], q=r[4], anchor=r[5], ref_letter=r[6], ref_correct=r[7],
                       v1=r[8], v2=r[9], c1=r[10], c2=r[11], w=r[12], flip=r[13], inv=r[14], raw1=r[15], raw2=r[16])
            for r in c.execute("SELECT match_id, model_a, model_b, node_id, qid, anchor, ref_letter, ref_correct, vote1, vote2_raw, "
                               "conf1, conf2, winner, flip, invalid, raw1, raw2 FROM verdicts")}


def freeze_set(allow_freeze=False):
    pool = pool_qids()
    if os.path.exists(SET_JSON):
        d = json.load(open(SET_JSON, encoding="utf-8")); ms = d["matches"]
        assert d["pool_id"] == POOL and set_hash(ms) == d["set_hash"], "judge_wiring_set.json does not verify"
        if SET_HASH_OF_RECORD is not None:
            assert d["set_hash"] == SET_HASH_OF_RECORD, "set hash %s is not the hash of record %s" % (d["set_hash"], SET_HASH_OF_RECORD)
        else:
            print("[SET] WARNING: SET_HASH_OF_RECORD is not registered yet; the set on disk has hash %s" % d["set_hash"])
        assert len(ms) == N_SET and all(m["qid"] in pool for m in ms)
        assert not ({m["model_a"] for m in ms} | {m["model_b"] for m in ms}) & EXCLUDED
        return ms, d
    if not allow_freeze:
        raise SystemExit("[SET] %s is missing; --freeze-only builds it (zero calls) and the author registers its hash" % rel(SET_JSON))
    import canary_baseline as cb                        # strata_of: frontier / key-tie / cross, as the canary set
    py = python_cache_rows()
    rref.set_reference(REFERENCE); refs = rref.references(); anchors = sj.routed_anchor()
    x12 = {r[0]: r for r in sj.all_x12_matches()}       # id, eval_question_id, model_a, model_b, node_id, winner, is_tie
    models = sorted({r[2] for r in x12.values()} | {r[3] for r in x12.values()})
    kind, tiers, acc = cb.strata_of(models)
    cand = defaultdict(list); dropped = Counter()
    for mid, r in sorted(py.items()):
        q = int(r["q"])
        if mid not in x12: dropped["not in x12 MAIN"] += 1; continue
        if q not in pool: dropped["outside pool"] += 1; continue
        if q not in refs: dropped["no reference"] += 1; continue
        if q not in anchors: dropped["no anchor"] += 1; continue
        if r["a"] in EXCLUDED or r["b"] in EXCLUDED: dropped["excluded model"] += 1; continue
        if anchors[q] != r["anchor"]: dropped["anchor differs from cache"] += 1; continue
        k = kind(r["a"], r["b"]); s = "contested" if k in ("frontier", "keytie") else "cross"
        cand[s].append(dict(match_id=mid, qid=q, model_a=r["a"], model_b=r["b"], node_id=r["nid"], anchor=anchors[q], stratum=s, pair_kind=k))
    rng = random.Random(SEED); out = []
    for s in ("contested", "cross"):
        lst = sorted(cand[s], key=lambda m: m["match_id"]); rng.shuffle(lst)
        assert len(lst) >= PER_STRATUM, "stratum %s has only %d candidates" % (s, len(lst))
        out.extend(lst[:PER_STRATUM])
    rng.shuffle(out)
    meta = dict(test="JUDGE-WIRING", pool_id=POOL, source="RECIPE-GROK cache %s (x12 MAIN, snapshot %s)" % (os.path.basename(PY_CACHE), rj.SNAP_MAIN),
                seed=SEED, per_stratum=PER_STRATUM, key_gap=cb.xr.KEY_GAP, top_cluster=sorted(rj.TOP_CLUSTER), key_tiers=tiers,
                candidates={s: len(v) for s, v in cand.items()}, dropped=dict(dropped),
                pair_kind_counts=dict(Counter(m["pair_kind"] for m in out)),
                frozen_at=time.strftime("%Y-%m-%d %H:%M:%S"), set_hash=set_hash(out), matches=out)
    if SET_HASH_OF_RECORD is not None and meta["set_hash"] != SET_HASH_OF_RECORD:
        raise SystemExit("[SET] re-frozen hash %s != hash of record %s; nothing written" % (meta["set_hash"], SET_HASH_OF_RECORD))
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(meta, open(SET_JSON, "w", encoding="utf-8"), indent=1)
    print("[SET] froze %d matches -> %s | hash %s | candidates %s | dropped %s" % (len(out), rel(SET_JSON), meta["set_hash"], meta["candidates"], meta["dropped"]))
    print("[SET] register this hash as SET_HASH_OF_RECORD in judge_wiring.py and in the plan amendment before any call")
    return out, meta


# ── payloads (through the modules of record) ────────────────────────────────────

def build_jobs(matches):
    """(match, ref, system, user1, user2) per match, assembled exactly as stack_judge.run's `one` assembles them: anchors from
    sj.routed_anchor(), rubrics from sj.anchor_rubrics(), references from rejudge_reference, traces from rj.robust_trace, the
    system from sj.system_for under PROMPT='v2'. The kit is NOT read here: the sha diff then checks the kit export too."""
    configure_rr()
    rref.set_reference(REFERENCE); refs = rref.references(); rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    evals = rj.load_eval_rows([m["qid"] for m in matches], {m["model_a"] for m in matches} | {m["model_b"] for m in matches})
    jobs = []
    for m in matches:
        ra, rb, ref, anc = evals.get((m["qid"], m["model_a"])), evals.get((m["qid"], m["model_b"])), refs.get(m["qid"]), anchors.get(m["qid"])
        if ra is None or rb is None or ref is None or anc is None:
            jobs.append((m, None, None, None, None)); continue
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = sj.system_for(anc, rubrics)
        jobs.append((m, ref, system, rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)))
    return jobs


def assert_source_identity():
    """call_judge_full must post exactly payload_bytes(system, user) (source-level, as canary_baseline's dry-run asserts)."""
    src = open(rr.__file__, encoding="utf-8").read()
    assert 'body = payload_bytes(system, user)' in src, "rejudge_reasoning.call_judge_full no longer posts payload_bytes()"
    assert '"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src
    assert 'return json.dumps(payload_body(system, user)).encode("utf-8")' in src


def match_by_id(mid, matches=None):
    """The set's record of a match when the set exists, else the RECIPE-GROK cache row (any of the 1,974 matches can be dumped)."""
    if matches is None and os.path.exists(SET_JSON):
        matches, _ = freeze_set()
    for m in matches or []:
        if m["match_id"] == mid: return m
    py = python_cache_rows().get(mid)
    if py is None and os.path.exists(BOARD_JSON):                 # BOARD mode: any of the 9,123 board matches
        for m in freeze_board()[0]:
            if m["match_id"] == mid: return m
    assert py is not None, "match %d is neither in the set nor in the RECIPE-GROK cache nor in the board set" % mid
    return dict(match_id=mid, qid=int(py["q"]), model_a=py["a"], model_b=py["b"], node_id=py["nid"], anchor=py["anchor"], stratum="(outside set)", pair_kind="?")


def dump_payload(mid):
    assert_source_identity()
    m = match_by_id(mid)
    (m, ref, system, u1, u2), = build_jobs([m])
    assert ref is not None, "match %d has no traces / reference / anchor" % mid
    d = os.path.join(OUTDIR, "dump"); os.makedirs(d, exist_ok=True)
    for order, u in ((1, u1), (2, u2)):
        b = rr.payload_bytes(system, u)
        p = os.path.join(d, "match_%d_order%d.python.json" % (mid, order))
        open(p, "wb").write(b); open(p + ".sha256", "w", newline="\n").write(sha_hex(b) + "\n")
        open(os.path.join(d, "match_%d_order%d.python.user.txt" % (mid, order)), "w", encoding="utf-8", newline="").write(u)
        print("[DUMP] order %d -> %s (%d bytes, sha256 %s)" % (order, rel(p), len(b), sha_hex(b)))
    open(os.path.join(d, "match_%d.python.system.txt" % mid), "w", encoding="utf-8", newline="").write(system)
    print("[DUMP] match %d | qid %d | %s vs %s | anchor %s | ref (%s) | model %s | max_tokens %d | temperature %s"
          % (mid, m["qid"], m["model_a"], m["model_b"], m["anchor"], ref[0], rr.JUDGE_MODEL, rr.MAX_TOKENS, temp_label()))
    print("[DUMP] diff against the Kotlin side: gradlew judgeWiring -Dmode=dump -DmatchId=%d, then cmp the *.json files" % mid)


def write_shas():
    assert_source_identity()
    matches, meta = freeze_set()
    jobs = build_jobs(matches)
    os.makedirs(OUTDIR, exist_ok=True)
    n_ok = 0
    with open(SHAS_PY, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["match_id", "sha_order1", "sha_order2", "anchor", "ref_letter", "skipped_reason"])
        for m, ref, system, u1, u2 in jobs:
            if ref is None:
                w.writerow([m["match_id"], "", "", m["anchor"], "", "no traces/reference/anchor"]); continue
            w.writerow([m["match_id"], sha_hex(rr.payload_bytes(system, u1)), sha_hex(rr.payload_bytes(system, u2)), m["anchor"], ref[0], ""]); n_ok += 1
    print("[SHAS] %d/%d matches x 2 orders -> %s (model %s, max_tokens %d, temperature %s, set %s)"
          % (n_ok, len(jobs), rel(SHAS_PY), rr.JUDGE_MODEL, rr.MAX_TOKENS, temp_label(), meta["set_hash"]))


# ── fixtures for the Kotlin unit tests ──────────────────────────────────────────

def gen_fixtures():
    """ASCII-escaped JSON fixtures (json.dump default ensure_ascii) so a CRLF checkout cannot alter a byte inside them.
    Synthetic inputs only: no database is read, so this runs in any checkout."""
    configure_rr()
    import prompt_v2
    os.makedirs(FIXTURES, exist_ok=True)

    def dump(name, obj):
        p = os.path.join(FIXTURES, name)
        with open(p, "w", encoding="ascii", newline="\n") as f:
            json.dump(obj, f, indent=1); f.write("\n")          # insertion order kept: the json cases pin key order
        print("[FIXTURE] %s" % rel(p))

    # 1. json.dumps cases: value (as JSON) -> the exact json.dumps string. Numbers: ints stay ints; floats carry a point.
    vals = ["ascii only", "em—dash", "en–dash", "中文 CJK", "emoji \U0001F600 astral", "line sep",
            "del\x7fchar", "ctrl\x01\x1f", "tab\tnl\ncr\r", 'quote"q', "back\\slash", "slash/keep", "nbsp ", "≤ le",
            "", " ", "~", "\x00nul", "éüñ", "😀".encode("utf-16", "surrogatepass").decode("utf-16")]
    cases = []
    for v in vals:
        cases.append(dict(value=v, dumps=json.dumps(v)))
    for body in ({"model": "m", "max_tokens": 8192, "messages": [{"role": "system", "content": "s—"}, {"role": "user", "content": "u/\\\"\n"}]},
                 {"model": "m", "max_tokens": 1, "messages": [], "temperature": 0.0},
                 {"a": [1, 2.5, -3, True, False, None, "x"], "b": {}, "c": [], "d": 0.7, "e": 1.0, "f": 1e-05, "g": 1e16, "h": 123.456, "i": 100.0, "j": 0.0001, "k": -0.5}):
        cases.append(dict(value=body, dumps=json.dumps(body)))
    dump("python_json_cases.json", cases)

    # 2. templates
    dump("templates.json", dict(v2_system_template=prompt_v2.v2_system_template(), user_template=rj.USER_TEMPLATE,
                                schema_instruction=rj.SCHEMA_INSTRUCTION,
                                with_reference=rref.with_reference("Q", ("B", "txt", True)),
                                reference_marker="[Reference solution — produced independently, may be wrong]"))

    # 3. assembly golden on a synthetic match (arx envelope on A, a \r + non-ASCII on B; a bare-pred fallback variant)
    q = "A Carnot engine runs between 500 K and 300 K — efficiency to 1 dp?"
    options = ["40.0%", "60.0%", "25.0%", "η = 1 − T_c/T_h ≈ 0.4", ""]
    trace_a = json.dumps({"response": "Let's think step-by-step:\nη = 1 − 300/500 = 0.4.\nThe answer is (A).", "reason_code": "A", "difficulty": 0})
    trace_b = "Efficiency is 60% — see below.\r\nThe answer is (B)."
    sp, rb = "You are an expert evaluator in Physics — thermodynamics.", "Grade on: (1) state functions; (2) sign convention kept; (3) units.\n"
    ref = ("A", options[0], True)
    ta, tb = rj.robust_trace(trace_a, "A", options), rj.robust_trace(trace_b, "B", options)
    system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rb) + "\n\n" + rj.SCHEMA_INSTRUCTION
    qq = rref.with_reference(q, ref)
    u1, u2 = rj.build_user_prompt(qq, ta, tb), rj.build_user_prompt(qq, tb, ta)
    b1, b2 = rr.payload_bytes(system, u1), rr.payload_bytes(system, u2)
    rr.TEMPERATURE = 0.0
    b1t = rr.payload_bytes(system, u1)
    rr.TEMPERATURE = None
    bare_a = rj.robust_trace("   ", "C", options); bare_none = rj.robust_trace("", None, options); bare_oor = rj.robust_trace(None, "K", options)
    dump("assembly_golden.json", dict(
        question_text=q, options=options, trace_a_output=trace_a, trace_a_pred="A", trace_b_output=trace_b, trace_b_pred="B",
        anchor="Physics", anchor_system_prompt=sp, anchor_rubric=rb, ref_letter=ref[0], ref_text=ref[1],
        model=rr.JUDGE_MODEL, max_tokens=rr.MAX_TOKENS,
        expected=dict(trace_a=ta, trace_b=tb, system=system, user1=u1, user2=u2, body1=b1.decode("ascii"), body2=b2.decode("ascii"),
                      sha1=sha_hex(b1), sha2=sha_hex(b2), body1_temperature_0=b1t.decode("ascii"),
                      bare_pred_c=bare_a, bare_no_pred=bare_none, bare_out_of_range=bare_oor)))

    # 4. trace preparation cases (rj.robust_trace port vs TracePreparation.robustTrace)
    tp = []
    def case(model_output, pred, opts, mode, label):
        out = rj.robust_trace(model_output, pred, opts) if mode == "RESOLVED" else \
            (rj.unwrap_envelope(model_output) if (model_output and model_output.strip()) else rj.robust_trace(model_output, pred, opts))
        tp.append(dict(label=label, model_output=model_output, pred=pred, options=opts, mode=mode, expected=out))
    case(trace_a, "A", options, "RESOLVED", "envelope unwrap + RESOLVED injection")
    case(trace_a, "A", options, "OPTIONS", "envelope unwrap, no injection under OPTIONS")
    case(trace_b, "B", options, "BLIND", "verbatim under BLIND")
    case(trace_b, "b", options, "RESOLVED", "lowercase pred resolves")
    case(trace_b, " (E)", options, "RESOLVED", "pred with a paren is not a letter: no injection")
    case(trace_b, "E", options, "RESOLVED", "pred resolves to an EMPTY option text: no injection")
    case(trace_b, "K", options, "RESOLVED", "pred out of range: no injection")
    case(trace_b, None, options, "RESOLVED", "no pred: no injection")
    case("", "C", options, "RESOLVED", "blank output, pred in range -> selected-option fallback")
    case("  \n", "Z", options, "RESOLVED", "blank output, pred out of range -> predicted fallback")
    case(None, None, options, "RESOLVED", "no output, no pred")
    case('{"response": "", "reason_code": "B"}', "B", options, "RESOLVED", "envelope with empty response stays raw")
    case("{not json", "A", options, "RESOLVED", "brace but not JSON stays raw")
    dump("trace_prep_cases.json", tp)

    # 5. parse / combine cases through rj.parse_judge + rj.combine_orders (winner parity; confidence where both agree)
    raws = [('{"critique_a":"a","critique_b":"b","comparison":"c","winner":"Model A","confidence":0.9}', "plain"),
            ('```json\n{"winner": "model b", "confidence": "0.75"}\n```', "fenced, lowercase, string confidence"),
            ('prose before {"winner":"TIE","confidence":0.4} prose after', "braces inside prose"),
            ('{"winner":"Draw","confidence":0.5}', "draw synonym"),
            ('no json here at all', "unparseable"),
            ('{"winner":"Model A","confidence":0.8,"comparison":"uses \\\\alpha and \\( x \\)"}', "latex escapes"),
            ('<think>reasoning</think>\n{"winner":"Model B","confidence":0.7}', "think block stripped before parse")]
    pc = []
    for raw, label in raws:
        w, c = rj.parse_judge(rr.strip_think(raw)); pc.append(dict(label=label, raw=raw, winner=w, confidence=c))
    dump("parse_cases.json", pc)
    comb = [dict(vote1=v1, vote2_raw=v2, winner=w, flip=f, invalid=i) for v1 in ("Model A", "Model B", "TIE", "INVALID") for v2 in ("Model A", "Model B", "TIE", "INVALID")
            for (w, f, i) in [rj.combine_orders(v1, v2)]]
    dump("combine_cases.json", comb)


# ── dry run ─────────────────────────────────────────────────────────────────────

def dry_run(pilot=None):
    matches, meta = freeze_set()
    kmeta, rubrics, anchors, refs = open_kit()
    assert_source_identity(); configure_rr()
    if pilot: matches = matches[:pilot]
    jobs = build_jobs(matches)
    n = 0
    for m, ref, system, u1, u2 in jobs:
        assert ref is not None, "match %d lost its traces/reference/anchor" % m["match_id"]
        assert anchors.get(m["qid"], (None, None))[1] == m["anchor"], "kit anchor differs for q %d" % m["qid"]
        assert refs.get(m["qid"]) == (ref[0], ref[1]), "kit reference differs for q %d" % m["qid"]
        for u in (u1, u2):
            body = rr.payload_body(system, u)
            assert tuple(body) == ("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ()), tuple(body)
            assert body["model"] == JUDGE and body["max_tokens"] == MAXTOK and body.get("temperature") == TEMPERATURE
            n += 1
    print("[DRY-RUN] pool %s | set %s (hash %s%s) | %d matches (%s) | %d payloads assembled, 0 posted"
          % (POOL, rel(SET_JSON), meta["set_hash"], " = record" if meta["set_hash"] == SET_HASH_OF_RECORD else ", NOT registered",
             len(matches), ", ".join("%s %d" % kv for kv in sorted(Counter(m["stratum"] for m in matches).items())), n))
    print("[DRY-RUN] kit %s hash %s | %s rubrics | %s questions | %s references | reference_model %s | exported at %s from %s"
          % (rel(KIT), kmeta["kit_hash"], kmeta["n_rubrics"], kmeta["n_questions"], kmeta["n_references"], kmeta["reference_model"], kmeta["export_ts"], kmeta["git_head"]))
    print("[DRY-RUN] judge %s | route /models/chat/completions?api-version=2024-05-01-preview | max_tokens %d | temperature %s | Python cache %s (%d verdicts)"
          % (JUDGE, MAXTOK, temp_label(), rel(PY_CACHE), len(python_cache_rows())))
    print("[DRY-RUN] Python shas: %s (%s)" % (rel(SHAS_PY), "present" if os.path.exists(SHAS_PY) else "missing: run --shas before the Kotlin run"))
    print("[DRY-RUN] criterion: |delta| <= %.1fpp under conventions A and B | test-retest floor beside it: %.3f (DECOMP)" % (CRITERION_PP, DECOMP_FLOOR))


# ── analysis ────────────────────────────────────────────────────────────────────

def clustered_ci(byq, stat, B=2000, seed=SEED):
    qs = sorted(byq); rng = random.Random(seed); out = []
    for _ in range(B):
        bs = [v for _ in qs for v in byq[qs[rng.randrange(len(qs))]]]
        out.append(stat(bs))
    out.sort(); return out[int(0.025 * B)], out[int(0.975 * B) - 1]


def mcnemar_p(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); return min(1.0, 2.0 * sum(math.comb(n, i) * 0.5 ** n for i in range(k + 1)))


def analyze(kotlin_db, pilot=None):
    matches, meta = freeze_set()
    kmeta, _, _, _ = open_kit()
    py = python_cache_rows()
    kc = ro(kotlin_db)
    km = dict(kc.execute("SELECT key, value FROM run_meta"))
    L = ["=== JUDGE-WIRING: Kotlin recipe path vs the Python RECIPE-GROK cache on the frozen %d-match set (hash %s) ===" % (N_SET, meta["set_hash"]),
         "  Kotlin db %s | run_meta: judge %s | recipe %s | max_tokens %s | temperature %s | kit %s | fingerprint %s | set %s | started %s"
         % (rel(kotlin_db), km.get("judge"), km.get("recipe"), km.get("max_tokens"), km.get("temperature"), km.get("kit_hash"), km.get("fingerprint"), km.get("set_hash"), km.get("started")),
         "  Python cache %s | judge %s | max_tokens %d | temperature omitted | kit of record %s" % (rel(PY_CACHE), JUDGE, MAXTOK, kmeta["kit_hash"])]
    guard = []
    if km.get("set_hash") != meta["set_hash"]: guard.append("set hash %s != %s" % (km.get("set_hash"), meta["set_hash"]))
    if km.get("kit_hash") != kmeta["kit_hash"]: guard.append("kit hash %s != %s" % (km.get("kit_hash"), kmeta["kit_hash"]))
    if km.get("judge") != JUDGE: guard.append("judge %s != %s" % (km.get("judge"), JUDGE))
    if km.get("max_tokens") != str(MAXTOK): guard.append("max_tokens %s != %d" % (km.get("max_tokens"), MAXTOK))
    if km.get("temperature") != temp_label(): guard.append("temperature %s != %s" % (km.get("temperature"), temp_label()))
    if guard:
        L.append("  PROTOCOL GUARD: the Kotlin run was not posted under the record (%s); the arms are NOT comparable and no delta is read." % "; ".join(guard))
        print("\n".join(L)); return
    kv = {r[0]: dict(mid=r[0], a=r[1], b=r[2], q=r[3], v1=r[4], v2=r[5], w=r[6], flip=r[7], inv=r[8], f1=r[9], f2=r[10], sha1=r[11], sha2=r[12])
          for r in kc.execute("SELECT match_id, model_a, model_b, qid, vote1, vote2_raw, winner, flip, invalid, finish1, finish2, sha1, sha2 FROM verdicts")}
    fp = {r[0] for r in kc.execute("SELECT DISTINCT deployment_fingerprint FROM judge_calls")} if kc.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='judge_calls'").fetchone()[0] else set()
    if len(fp) > 1:
        L.append("  PROTOCOL GUARD: judge_calls carries %d fingerprints %s; rows from different deployments are never pooled." % (len(fp), sorted(fp)))
        print("\n".join(L)); return
    set_ids = [m["match_id"] for m in matches]
    if pilot: set_ids = set_ids[:pilot]
    paired = [mid for mid in set_ids if mid in kv and mid in py]
    partial = len(paired) < len(set_ids)
    L.append("  paired %d of %d (%s)" % (len(paired), len(set_ids), "PARTIAL: not the outcome of record" if partial else "complete"))
    # sha equality against payload_shas_python.csv
    if os.path.exists(SHAS_PY):
        pysha = {int(r["match_id"]): (r["sha_order1"], r["sha_order2"]) for r in csv.DictReader(open(SHAS_PY, encoding="utf-8"))}
        eq = sum(1 for mid in paired if pysha.get(mid) == (kv[mid]["sha1"], kv[mid]["sha2"]))
        L.append("  payload sha equality (Kotlin posted bytes == Python bytes, both orders): %d/%d%s" % (eq, len(paired), "" if eq == len(paired) else "  <- NOT byte-identical: the contrast is void"))
    else:
        L.append("  payload_shas_python.csv missing: sha equality not checked")
    ev = ro(rj.EVAL_DB)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    okA, okB = paired_contrast(L, kv, py, paired, G)
    L.append("  test-retest floor of the deployed judge on byte-identical prompts: %.3f (DECOMP); a paired delta inside +/-%.1fpp is within that floor" % (DECOMP_FLOOR, CRITERION_PP))
    verdict = "PASS" if (okA and okB and not partial) else ("PARTIAL" if partial else "FAIL")
    L.append("  JUDGE-WIRING REGISTERED (|delta| <= %.1fpp under both conventions): %s" % (CRITERION_PP, verdict))
    L.append("  consequence on FAIL: no mixed-judge board until a whole-board re-judge (FRAMEWORK.md item 25)")
    txt = "\n".join(L); print(txt)
    out = os.path.join(OUTDIR, "judge_wiring_outcome%s.txt" % ("_partial" if partial else ""))
    os.makedirs(OUTDIR, exist_ok=True); open(out, "w", encoding="utf-8").write(txt + "\n")


def paired_contrast(L, kv, py, paired, G, plabel="Python"):
    """Item 25's match-for-match readout of a Kotlin cache (kv) against a Python cache (py) on `paired` match ids: finish_reason
    and NON_TERMINATED counts, invalid, raw agreement, tie / flip rates, then the key-decidable accuracy delta under conventions
    A and B with the question-clustered bootstrap CI and McNemar (full set; both-committed under B). Returns (okA, okB) against
    CRITERION_PP. Extracted from analyze() for the BOARD mode; the 600-set output is byte-identical (plabel = "Python")."""
    fin = Counter(); nonterm = 0
    for mid in paired:
        fin[kv[mid]["f1"]] += 1; fin[kv[mid]["f2"]] += 1
        if kv[mid]["f1"] in ("length", "content_filter") or kv[mid]["f2"] in ("length", "content_filter"): nonterm += 1
    L.append("  Kotlin finish_reason over %d calls: %s | matches touched by the NON_TERMINATED rule: %d (the %s cache had no such rule; expected 0 at 8192)"
             % (2 * len(paired), dict(fin), nonterm, plabel))
    inv_k = sum(kv[mid]["inv"] for mid in paired); inv_p = sum(py[mid]["inv"] for mid in paired)
    L.append("  invalid: Kotlin %d | %s %d" % (inv_k, plabel, inv_p))
    agree = sum(1 for mid in paired if kv[mid]["w"] == py[mid]["w"]) / max(1, len(paired))
    valid = [mid for mid in paired if not kv[mid]["inv"] and not py[mid]["inv"]]
    tie_k = sum(kv[mid]["w"] == "TIE" for mid in valid) / max(1, len(valid)); tie_p = sum(py[mid]["w"] == "TIE" for mid in valid) / max(1, len(valid))
    flip_k = sum(kv[mid]["flip"] for mid in valid) / max(1, len(valid)); flip_p = sum(py[mid]["flip"] for mid in valid) / max(1, len(valid))
    L.append("  raw 3-way agreement (winner identical incl. TIE/INVALID): %.3f | tie rate Kotlin %.3f vs %s %.3f | flip rate Kotlin %.3f vs %s %.3f (valid n=%d)"
             % (agree, tie_k, plabel, tie_p, flip_k, plabel, flip_p, len(valid)))
    # key-decidable subset
    dec = []
    for mid in paired:
        r = py[mid]; ca, cb = G.get((r["q"], r["a"])), G.get((r["q"], r["b"]))
        if ca is None or cb is None or ca == cb: continue
        dec.append((mid, r["a"] if ca else r["b"]))
    L.append("  key-decidable paired matches: %d" % len(dec))

    def convention(tag, committed_only):
        byq = defaultdict(list); nk = np_ = 0; ck = cp = 0
        for mid, d in dec:
            wk, wp = kv[mid]["w"], py[mid]["w"]
            okk, okp = wk == d, wp == d
            comk = wk in (kv[mid]["a"], kv[mid]["b"]); comp = wp in (py[mid]["a"], py[mid]["b"])
            byq[py[mid]["q"]].append((okk, okp, comk, comp))
            if not committed_only or comk: nk += 1; ck += okk
            if not committed_only or comp: np_ += 1; cp += okp
        ak, ap = ck / max(1, nk), cp / max(1, np_)

        def stat(rows):
            if committed_only:
                k = [o for o, _, c, _ in rows if c]; p = [o for _, o, _, c in rows if c]
            else:
                k = [o for o, _, _, _ in rows]; p = [o for _, o, _, _ in rows]
            return sum(k) / max(1, len(k)) - sum(p) / max(1, len(p))
        lo, hi = clustered_ci(byq, stat)
        # McNemar on the full key-decidable set (every paired match contributes; a TIE / INVALID / non-terminated arm counts as wrong)
        b = sum(1 for mid, d in dec if kv[mid]["w"] == d and py[mid]["w"] != d); c = sum(1 for mid, d in dec if py[mid]["w"] == d and kv[mid]["w"] != d)
        delta = ak - ap
        ok = abs(delta) * 100 <= CRITERION_PP
        L.append("  %-46s Kotlin %.3f (n=%d) vs %s %.3f (n=%d) | delta %+.1fpp  95%% CI [%+.1f, %+.1f]pp (question-clustered bootstrap) | McNemar discordant %d:%d p=%.4f (full key-decidable set, n=%d) -> %s"
                 % (tag, ak, nk, plabel, ap, np_, 100 * delta, 100 * lo, 100 * hi, b, c, mcnemar_p(b, c), len(dec), "OK" if ok else "FAIL"))
        if committed_only:
            # under convention B the discordant pair is also restricted to matches where BOTH arms committed to a model,
            # so the sign test is read on the same population as the two accuracies above
            both = [(mid, d) for mid, d in dec if kv[mid]["w"] in (kv[mid]["a"], kv[mid]["b"]) and py[mid]["w"] in (py[mid]["a"], py[mid]["b"])]
            bb = sum(1 for mid, d in both if kv[mid]["w"] == d and py[mid]["w"] != d); cb = sum(1 for mid, d in both if py[mid]["w"] == d and kv[mid]["w"] != d)
            L.append("  %-46s McNemar discordant %d:%d p=%.4f (both arms committed, n=%d of %d key-decidable)"
                     % ("", bb, cb, mcnemar_p(bb, cb), len(both), len(dec)))
        return ok
    okA = convention("convention A (TIE / INVALID / non-terminated wrong):", False)
    okB = convention("convention B (committed verdicts only):", True)
    return okA, okB


# ── BOARD mode ──────────────────────────────────────────────────────────────────

def _gc():
    """grok_calib, the module that posted GROK-CALIB: its schedule() and Assembler are the board's sources of record."""
    import grok_calib as gc
    assert (gc.JUDGE, gc.MAXTOK, gc.REFERENCE, gc.TREE, gc.POOL) == (JUDGE, MAXTOK, REFERENCE, TREE, POOL), "grok_calib constants drifted from the record"
    assert os.path.normcase(os.path.abspath(gc.cache_path())) == os.path.normcase(os.path.abspath(GC_CACHE)), gc.cache_path()
    assert set(gc.EXCLUDED) == EXCLUDED
    return gc


def board_rows():
    """GROK-CALIB's 9,142 verdicts (the same columns as python_cache_rows reads): match_id -> row dict."""
    assert os.path.exists(GC_CACHE), "[BOARD] %s missing: GROK-CALIB's cache is the board's source" % rel(GC_CACHE)
    return python_cache_rows(GC_CACHE)


def freeze_board(allow_freeze=False):
    """Load and verify the board set, or build it under --freeze-board: every match GROK-CALIB judged whose question has a
    reference in the kit (9,123 of 9,142), in match_id order (GROK-CALIB's schedule order), with the 600 set's fields; the
    stratum / pair_kind labels are canary_baseline.strata_of's (frontier / keytie -> contested, else cross) so the board can be
    read per stratum. The 19 reference-less matches are EXCLUDED by construction (NOREF_DECISION) and recorded in the meta
    under `excluded_no_reference` (match_ids, qids, reason)."""
    pool = pool_qids()
    if os.path.exists(BOARD_JSON):
        d = json.load(open(BOARD_JSON, encoding="utf-8")); ms = d["matches"]
        assert d["pool_id"] == POOL and set_hash(ms) == d["set_hash"], "judge_wiring_board_set.json does not verify"
        if BOARD_HASH_OF_RECORD is not None:
            assert d["set_hash"] == BOARD_HASH_OF_RECORD, "board hash %s is not the hash of record %s" % (d["set_hash"], BOARD_HASH_OF_RECORD)
        else:
            print("[BOARD] WARNING: BOARD_HASH_OF_RECORD is not registered yet; the board set on disk has hash %s" % d["set_hash"])
        assert len(ms) == N_BOARD and all(m["qid"] in pool for m in ms)
        assert not ({m["model_a"] for m in ms} | {m["model_b"] for m in ms}) & EXCLUDED
        ex = d["excluded_no_reference"]; ids = {m["match_id"] for m in ms}
        assert len(ex["match_ids"]) == N_EXCLUDED_NOREF == len(set(ex["match_ids"])) and not set(ex["match_ids"]) & ids
        assert not set(ex["qids"]) & {m["qid"] for m in ms}, "an excluded question is also in the board set"
        return ms, d
    if not allow_freeze:
        raise SystemExit("[BOARD] %s is missing; --freeze-board builds it (zero calls) and the author registers its hash" % rel(BOARD_JSON))
    gc = _gc()
    import canary_baseline as cb
    sched = gc.schedule()                                          # the 9,142 x12 recipe matches; pool + EXCLUDED asserted there
    judged = board_rows()                                          # what GROK-CALIB actually judged
    assert set(judged) == {r[0] for r in sched}, "GROK-CALIB's cache (%d) and its schedule (%d) differ" % (len(judged), len(sched))
    assert len(judged) == N_GC, len(judged)
    x12 = {r[0] for r in sj.all_x12_matches()}
    assert set(judged) <= x12 and x12 - set(judged) == ABSENT_FROM_X12, "x12 MAIN minus GROK-CALIB's cache is not %s" % sorted(ABSENT_FROM_X12)
    _, _, kanchors, krefs = open_kit()
    models = sorted({r["a"] for r in judged.values()} | {r["b"] for r in judged.values()})
    kind, tiers, _acc = cb.strata_of(models)
    out = []; noref = []; counts = Counter()
    for mid in sorted(judged):
        r = judged[mid]; q = int(r["q"])
        assert q in pool and r["a"] not in EXCLUDED and r["b"] not in EXCLUDED
        assert kanchors.get(q, (None, None))[1] == r["anchor"], "kit anchor differs from the one GROK-CALIB saw for q %d" % q
        has_ref = bool(r["ref_letter"])
        assert (q in krefs) == has_ref and (not has_ref or krefs[q][0] == r["ref_letter"]), "kit reference differs from GROK-CALIB's for q %d" % q
        if not has_ref: noref.append(mid); continue                # excluded by construction (NOREF_DECISION)
        k = kind(r["a"], r["b"]); s = "contested" if k in ("frontier", "keytie") else "cross"; counts[k] += 1
        out.append(dict(match_id=mid, qid=q, model_a=r["a"], model_b=r["b"], node_id=r["nid"], anchor=r["anchor"], stratum=s, pair_kind=k))
    assert len(noref) == N_EXCLUDED_NOREF, "expected %d reference-less matches, found %d" % (N_EXCLUDED_NOREF, len(noref))
    assert len(out) == N_BOARD, len(out)
    ex_qids = sorted({int(judged[m]["q"]) for m in noref})
    assert not set(ex_qids) & {m["qid"] for m in out}, "a reference-less question also has a referenced match"
    meta = dict(test="JUDGE-WIRING-BOARD", pool_id=POOL,
                source="GROK-CALIB cache %s (the x12 MAIN schedule of %s, snapshot %s; %s absent): %d judged, %d with a reference in the kit"
                       % (os.path.basename(GC_CACHE), os.path.basename(gc.X12_CACHE), rj.SNAP_MAIN, sorted(ABSENT_FROM_X12), len(judged), len(out)),
                order="match_id ascending (GROK-CALIB's schedule order; the harness's -Dpilot=N takes the first N matches)",
                seed=None, key_gap=cb.xr.KEY_GAP, top_cluster=sorted(rj.TOP_CLUSTER), key_tiers=tiers, models=models,
                stratum_counts=dict(Counter(m["stratum"] for m in out)), pair_kind_counts=dict(counts),
                absent_from_x12=sorted(ABSENT_FROM_X12),
                excluded_no_reference=dict(n=len(noref), match_ids=noref, qids=ex_qids, reason=NOREF_DECISION),
                frozen_at=time.strftime("%Y-%m-%d %H:%M:%S"), set_hash=set_hash(out), matches=out)
    if BOARD_HASH_OF_RECORD is not None and meta["set_hash"] != BOARD_HASH_OF_RECORD:
        raise SystemExit("[BOARD] re-frozen hash %s != hash of record %s; nothing written" % (meta["set_hash"], BOARD_HASH_OF_RECORD))
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(meta, open(BOARD_JSON, "w", encoding="utf-8"), indent=1)
    print("[BOARD] froze %d matches -> %s | hash %s | strata %s | pair kinds %s | %d models" % (len(out), rel(BOARD_JSON), meta["set_hash"], meta["stratum_counts"], meta["pair_kind_counts"], len(models)))
    print("[BOARD] excluded by construction (no reference in the kit): %d of %d GROK-CALIB matches (match_ids %s; qids %s)" % (len(noref), len(judged), noref, ex_qids))
    print("[BOARD] reason: %s" % NOREF_DECISION)
    print("[BOARD] register this hash as BOARD_HASH_OF_RECORD in judge_wiring.py and in the plan amendment before any call")
    return out, meta


def board_jobs(matches):
    """(match, system, user1, user2, ref) per board match through grok_calib.Assembler, the assembler GROK-CALIB posted with (it
    asserts per match that the routed anchor and the reference letter equal the ones Mistral saw). Every board match has a
    reference (the reference-less ones are excluded by construction), so ref is never None here. rr is configured as
    grok_calib.run configures it (PROVIDER azure, the deployed judge, MAX_TOKENS 8192, TEMPERATURE None), so
    rr.payload_bytes(system, user) is the body that was posted."""
    gc = _gc(); configure_rr()
    assert rr.TEMPERATURE is None and rr.JUDGE_MODEL == gc.JUDGE and rr.MAX_TOKENS == gc.MAXTOK
    sched = {r[0]: r for r in gc.schedule()}
    asm = gc.Assembler([sched[m["match_id"]] for m in matches])
    jobs = [(m,) + asm.payload(sched[m["match_id"]]) for m in matches]
    for m, _system, _u1, _u2, ref in jobs:
        assert ref is not None, "board match %d has no reference: it must not be in the set" % m["match_id"]
    return jobs


def write_shas_board():
    assert_source_identity()
    matches, meta = freeze_board()
    jobs = board_jobs(matches)
    os.makedirs(BOARD_DIR, exist_ok=True)
    with open(SHAS_PY_BOARD, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["match_id", "sha_order1", "sha_order2", "anchor", "ref_letter", "skipped_reason"])
        for m, system, u1, u2, ref in jobs:
            w.writerow([m["match_id"], sha_hex(rr.payload_bytes(system, u1)), sha_hex(rr.payload_bytes(system, u2)), m["anchor"], ref[0], ""])
    import shutil; shutil.copyfile(SHAS_PY_BOARD, SHAS_PY_BOARD_HARNESS)
    print("[SHAS-BOARD] %d/%d matches x 2 orders (every match with a reference; shas of the bytes GROK-CALIB posted; no skipped rows) -> %s"
          % (len(jobs), len(matches), rel(SHAS_PY_BOARD)))
    print("[SHAS-BOARD] byte copy for the harness's fixed-name compare -> %s (model %s, max_tokens %d, temperature %s, board %s)"
          % (rel(SHAS_PY_BOARD_HARNESS), rr.JUDGE_MODEL, rr.MAX_TOKENS, temp_label(), meta["set_hash"]))
    print("[SHAS-BOARD] Kotlin side: gradlew judgeWiring -Dmode=shas -DsetJson=%s -DoutDir=%s --offline  (expect %d/%d byte-identical -> ok)"
          % (rel(BOARD_JSON), rel(BOARD_DIR), len(jobs), len(jobs)))


def dry_run_board(pilot=None):
    matches, meta = freeze_board()
    kmeta, rubrics, anchors, refs = open_kit()
    assert_source_identity()
    ex = meta["excluded_no_reference"]; noref = set(ex["match_ids"])
    n_full = len(matches)
    if pilot: matches = matches[:pilot]
    jobs = board_jobs(matches)
    n = 0; nbytes = 0; first = None; gsha = {}
    for m, system, u1, u2, ref in jobs:
        assert m["match_id"] not in noref and ref is not None, "an excluded reference-less match is in the set: %d" % m["match_id"]
        assert anchors.get(m["qid"], (None, None))[1] == m["anchor"], "kit anchor differs for q %d" % m["qid"]
        assert refs.get(m["qid"]) == (ref[0], ref[1]), "kit reference differs for q %d" % m["qid"]
        shas = []
        for u in (u1, u2):
            body = rr.payload_body(system, u)
            assert tuple(body) == ("model", "max_tokens", "messages"), tuple(body)
            assert body["model"] == JUDGE and body["max_tokens"] == MAXTOK and "temperature" not in body
            b = rr.payload_bytes(system, u); nbytes += len(b); shas.append(sha_hex(b)); n += 1
            if first is None: first = (m, body, len(b))
        gsha[m["match_id"]] = tuple(shas)
    for q in ex["qids"]: assert q not in refs, "excluded question %d has a reference in the kit" % q
    # source-level identity of the two Python assemblers: build_jobs (this script's, the --dump-payload path) must give
    # grok_calib.Assembler's bytes, so a --dump-payload of a board match is the bytes GROK-CALIB posted
    same = 0
    for m, ref, system, u1, u2 in build_jobs(matches):
        assert ref is not None, "build_jobs lost match %d" % m["match_id"]
        same += gsha[m["match_id"]] == (sha_hex(rr.payload_bytes(system, u1)), sha_hex(rr.payload_bytes(system, u2)))
    assert same == len(gsha), "build_jobs and grok_calib.Assembler differ on %d matches" % (len(gsha) - same)
    m, body, nb = first
    print("[DRY-RUN-BOARD] pool %s | board %s (hash %s%s) | %d matches%s (%s) | %d payloads assembled, 0 posted | %.1f MB of body bytes"
          % (POOL, rel(BOARD_JSON), meta["set_hash"], " = record" if meta["set_hash"] == BOARD_HASH_OF_RECORD else ", NOT registered",
             len(matches), " [pilot slice of %d]" % n_full if pilot else "", ", ".join("%s %d" % kv for kv in sorted(Counter(x["stratum"] for x in matches).items())), n, nbytes / 1e6))
    print("[DRY-RUN-BOARD] first payload: match %d | %s vs %s | qid %d | anchor %s | model=%s | max_tokens=%d | temperature=%s | keys=%s | %d bytes"
          % (m["match_id"], m["model_a"], m["model_b"], m["qid"], m["anchor"], body["model"], body["max_tokens"], "omitted" if "temperature" not in body else body["temperature"], ",".join(body), nb))
    print("[DRY-RUN-BOARD] excluded by construction (no reference in the kit): %d GROK-CALIB matches, none in the set (match_ids %s; qids %s)" % (ex["n"], ex["match_ids"], ex["qids"]))
    print("[DRY-RUN-BOARD] reason: %s" % NOREF_DECISION)
    print("[DRY-RUN-BOARD] expected Kotlin calls: full set %d x 2 = %d%s (GROK-CALIB posted %d = %d x 2, incl. the %d excluded)"
          % (n_full, 2 * n_full, " | this slice %d x 2 = %d" % (len(matches), n) if pilot else "", 2 * N_GC, N_GC, ex["n"]))
    print("[DRY-RUN-BOARD] Python assemblers agree (build_jobs == grok_calib.Assembler, both orders): %d/%d matches" % (same, len(gsha)))
    print("[DRY-RUN-BOARD] kit %s hash %s | %s rubrics | %s questions | %s references | judge %s | max_tokens %d | temperature %s | GROK-CALIB cache %s (%d verdicts)"
          % (rel(KIT), kmeta["kit_hash"], kmeta["n_rubrics"], kmeta["n_questions"], kmeta["n_references"], JUDGE, MAXTOK, temp_label(), rel(GC_CACHE), len(board_rows())))
    print("[DRY-RUN-BOARD] Python board shas: %s (%s) | harness copy %s (%s)" % (rel(SHAS_PY_BOARD), "present" if os.path.exists(SHAS_PY_BOARD) else "missing: run --shas-board",
                                                                                rel(SHAS_PY_BOARD_HARNESS), "present" if os.path.exists(SHAS_PY_BOARD_HARNESS) else "missing"))
    print("[DRY-RUN-BOARD] the board is DESCRIPTIVE (no pass/fail); its pairing with GROK-CALIB reuses item 25's |delta| <= %.1fpp under conventions A and B" % CRITERION_PP)
    print("[DRY-RUN-BOARD] outcome of record only from %s with a complete judge_calls table (board_of_record_gate); anything else -> board_outcome_partial.txt"
          % rel(os.path.join(BOARD_DIR, "kotlin_%s.db" % (BOARD_HASH_OF_RECORD or "<BOARD_HASH_OF_RECORD>"))))


def board_of_record_gate(kotlin_db, kc, km, n_verdicts):
    """The conditions under which analyze_board may write board_outcome.txt / board_systematic_budget.txt (the files of
    record) rather than board_outcome_partial.txt. Returns (ok, reasons). All four must hold:
      1. BOARD_HASH_OF_RECORD is registered;
      2. kotlin_db resolves to BOARD_DIR/kotlin_<BOARD_HASH_OF_RECORD>.db (the harness's own DB under its board -DoutDir);
      3. a judge_calls table exists with exactly 2 rows per verdict (one per presentation order, per (qid, model_a, model_b));
      4. judge_calls carries a single deployment_fingerprint equal to run_meta.fingerprint."""
    why = []
    if BOARD_HASH_OF_RECORD is None:
        why.append("BOARD_HASH_OF_RECORD not registered")
    else:
        want = os.path.normcase(os.path.abspath(os.path.join(BOARD_DIR, "kotlin_%s.db" % BOARD_HASH_OF_RECORD)))
        got = os.path.normcase(os.path.abspath(kotlin_db))
        if got != want: why.append("kotlin db %s is not %s" % (rel(kotlin_db), rel(want)))
    has_jc = kc.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='judge_calls'").fetchone()[0] == 1
    if not has_jc:
        why.append("no judge_calls table")
    else:
        n_calls = kc.execute("SELECT COUNT(*) FROM judge_calls").fetchone()[0]
        if n_calls != 2 * n_verdicts: why.append("judge_calls has %d rows for %d verdicts (expected %d)" % (n_calls, n_verdicts, 2 * n_verdicts))
        bad = kc.execute("SELECT COUNT(*) FROM (SELECT eval_question_id, model_a, model_b, COUNT(*) n, MIN(presentation_order) lo, MAX(presentation_order) hi "
                         "FROM judge_calls GROUP BY 1, 2, 3 HAVING n != 2 OR lo != 1 OR hi != 2)").fetchone()[0]
        if bad: why.append("%d (qid, model_a, model_b) groups in judge_calls do not hold exactly orders 1 and 2" % bad)
        fps = sorted(r[0] for r in kc.execute("SELECT DISTINCT deployment_fingerprint FROM judge_calls"))
        if len(fps) != 1: why.append("judge_calls carries %d fingerprints %s" % (len(fps), fps))
        elif fps[0] != km.get("fingerprint"): why.append("judge_calls fingerprint %s != run_meta.fingerprint %s" % (fps[0], km.get("fingerprint")))
    return not why, why


def analyze_board(kotlin_db, pilot=None):
    """(a) the board of record from the Kotlin cache; (b) the match-for-match pairing with GROK-CALIB (item 25's readout);
    (c) the widener readout with systematic_budget's helpers (grok_calib.item26_criteria); (d) the outcome file. The files of
    record (board_outcome.txt, board_systematic_budget.txt) are written ONLY when board_of_record_gate passes AND every match
    of the set is cached AND no --pilot slice is read; otherwise board_outcome_partial.txt (and board_systematic_budget_partial.txt)."""
    matches, meta = freeze_board()
    kmeta, _, _, _ = open_kit()
    ex = meta["excluded_no_reference"]; noref = sorted(ex["match_ids"]); models = meta["models"]
    py = board_rows()                                              # GROK-CALIB's 9,142 rows: the 9,123 of the set + the 19 excluded
    kc = ro(kotlin_db)
    km = dict(kc.execute("SELECT key, value FROM run_meta"))
    L = ["=== JUDGE-WIRING BOARD: the x12 MAIN schedule re-judged through the Kotlin recipe path (board set hash %s, %d matches) ===" % (meta["set_hash"], len(matches)),
         "  Kotlin db %s | run_meta: judge %s | recipe %s | max_tokens %s | temperature %s | kit %s | fingerprint %s | set %s | started %s%s"
         % (rel(kotlin_db), km.get("judge"), km.get("recipe"), km.get("max_tokens"), km.get("temperature"), km.get("kit_hash"), km.get("fingerprint"), km.get("set_hash"), km.get("started"),
            (" | resumed %s" % km["resumed"]) if km.get("resumed") else ""),
         "  comparison arm: GROK-CALIB %s (Python rejudge_reasoning.call_judge_full, judge %s, max_tokens %d, temperature omitted) | kit of record %s" % (rel(GC_CACHE), JUDGE, MAXTOK, kmeta["kit_hash"])]
    guard = []
    if km.get("set_hash") != meta["set_hash"]: guard.append("set hash %s != %s" % (km.get("set_hash"), meta["set_hash"]))
    if km.get("kit_hash") != kmeta["kit_hash"]: guard.append("kit hash %s != %s" % (km.get("kit_hash"), kmeta["kit_hash"]))
    if km.get("judge") != JUDGE: guard.append("judge %s != %s" % (km.get("judge"), JUDGE))
    if km.get("max_tokens") != str(MAXTOK): guard.append("max_tokens %s != %d" % (km.get("max_tokens"), MAXTOK))
    if km.get("temperature") != temp_label(): guard.append("temperature %s != %s" % (km.get("temperature"), temp_label()))
    if guard:
        L.append("  PROTOCOL GUARD: the Kotlin run was not posted under the record (%s); nothing is read." % "; ".join(guard)); print("\n".join(L)); return
    kv = {r[0]: dict(mid=r[0], a=r[1], b=r[2], q=r[3], v1=r[4], v2=r[5], w=r[6], flip=r[7], inv=r[8], f1=r[9], f2=r[10], sha1=r[11], sha2=r[12])
          for r in kc.execute("SELECT match_id, model_a, model_b, qid, vote1, vote2_raw, winner, flip, invalid, finish1, finish2, sha1, sha2 FROM verdicts")}
    fp = {r[0] for r in kc.execute("SELECT DISTINCT deployment_fingerprint FROM judge_calls")} if kc.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='judge_calls'").fetchone()[0] else set()
    if len(fp) > 1:
        L.append("  PROTOCOL GUARD: judge_calls carries %d fingerprints %s; rows from different deployments are never pooled." % (len(fp), sorted(fp))); print("\n".join(L)); return
    judgeable = [m["match_id"] for m in matches]                   # the whole set: every match has a reference
    if pilot: judgeable = judgeable[:pilot]
    cached = [mid for mid in judgeable if mid in kv]; missing = [mid for mid in judgeable if mid not in kv]
    stray = sorted(set(kv) - set(judgeable))
    assert not stray or pilot, "the Kotlin cache holds %d verdicts outside the set (first %s)" % (len(stray), stray[:5])
    assert not set(kv) & set(noref), "the Kotlin cache holds a verdict for an excluded reference-less match: %s" % sorted(set(kv) & set(noref))
    partial = bool(missing)
    gate_ok, gate_why = board_of_record_gate(kotlin_db, kc, km, len(kv))
    of_record = gate_ok and not partial and not pilot
    L.append("  set %d = every GROK-CALIB match with a reference in the kit; %d GROK-CALIB matches EXCLUDED by construction (no reference; the Kotlin path skips them: match_ids %s; qids %s)"
             % (len(matches), ex["n"], noref, ex["qids"]))
    L.append("  GROK-CALIB's readings on the %d excluded (judged WITHOUT a reference block; not part of any Kotlin board): %s"
             % (ex["n"], "; ".join("%d q%d %s vs %s -> %s%s%s" % (mid, py[mid]["q"], py[mid]["a"], py[mid]["b"], py[mid]["w"], " flip" if py[mid]["flip"] else "", " INVALID" if py[mid]["inv"] else "")
                                   for mid in noref if mid in py)))
    L.append("  Kotlin cache: %d of %d%s (%s)" % (len(cached), len(judgeable), " [pilot slice %d]" % pilot if pilot else "",
                                                 "PARTIAL: %d missing, not the outcome of record" % len(missing) if partial else "complete"))
    L.append("  outcome-of-record gate (registered hash + BOARD_DIR/kotlin_<hash>.db + judge_calls 2 rows/verdict + single fingerprint = run_meta): %s"
             % ("PASS" if gate_ok else "FAIL: " + "; ".join(gate_why)))
    if os.path.exists(SHAS_PY_BOARD):
        pysha = {int(r["match_id"]): (r["sha_order1"], r["sha_order2"]) for r in csv.DictReader(open(SHAS_PY_BOARD, encoding="utf-8"))}
        eq = sum(1 for mid in cached if pysha.get(mid) == (kv[mid]["sha1"], kv[mid]["sha2"]))
        L.append("  payload sha equality (Kotlin posted bytes == the bytes GROK-CALIB posted, both orders): %d/%d%s" % (eq, len(cached), "" if eq == len(cached) else "  <- NOT byte-identical"))
    else:
        L.append("  %s missing: sha equality not checked" % rel(SHAS_PY_BOARD))
    out = BOARD_OUTCOME if of_record else BOARD_OUTCOME.replace(".txt", "_partial.txt")
    sb_out = SB_BOARD if of_record else SB_BOARD.replace(".txt", "_partial.txt")
    def finish():
        txt = "\n".join(L); print(txt)
        os.makedirs(OUTDIR, exist_ok=True); open(out, "w", encoding="utf-8").write(txt + "\n")
        print("[ANALYZE-BOARD] %s -> %s" % ("outcome of record" if of_record else "PARTIAL readout (not of record)", rel(out)))
    if not cached:
        L.append("  nothing judged yet"); finish(); return
    ev = ro(rj.EVAL_DB)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    # (a) the board of record
    L.append(""); L.append("=== (a) the board of record: question-clustered Bradley-Terry (rejudge_grok.mm_fit) over the %d models on the Kotlin verdicts ===" % len(models))
    rows_k = [dict(q=kv[mid]["q"], a=kv[mid]["a"], b=kv[mid]["b"], w=kv[mid]["w"]) for mid in cached if not kv[mid]["inv"]]
    rows_g = [dict(q=py[mid]["q"], a=py[mid]["a"], b=py[mid]["b"], w=py[mid]["w"]) for mid in cached if not py[mid]["inv"]]
    qs = sorted({r["q"] for r in rows_k})
    acc_j = {m: sum(G[(q, m)] for q in qs if (q, m) in G) / max(1, sum(1 for q in qs if (q, m) in G)) for m in models}
    acc_pool, _ = jf.gt_and_lengths(set(models))
    th = jf.board_from(jf.current_votes(rows_k), models); th_g = jf.board_from(jf.current_votes(rows_g), models)
    rho_j, rho_p = jf.rho(th, acc_j, models), jf.rho(th, acc_pool, models)
    byq = defaultdict(list)
    for r in rows_k: byq[r["q"]].append(r)
    rng = random.Random(SEED); rhos = []
    for _ in range(BOOT_B):
        sub = [r for _ in qs for r in byq[qs[rng.randrange(len(qs))]]]
        rhos.append(jf.rho(jf.board_from(jf.current_votes(sub), models), acc_j, models))
    rhos.sort(); lo, hi = rhos[int(0.025 * BOOT_B)], rhos[int(0.975 * BOOT_B) - 1]
    L.append("  %d valid verdicts over %d judged questions | rho vs key accuracy over those judged questions %.4f, 95%% CI [%.4f, %.4f] (question-resampled bootstrap B=%d, seed %d, key fixed) | rho vs pool key accuracy (3,445; ARENA-V2's comparator) %.4f"
             % (len(rows_k), len(qs), rho_j, lo, hi, BOOT_B, SEED, rho_p))
    L.append("  GROK-CALIB on the same %d matches: rho vs judged-question key accuracy %.4f | Spearman between the two boards' theta %.4f" % (len(cached), jf.rho(th_g, acc_j, models), rj.spearman([th[m] for m in models], [th_g[m] for m in models])))
    TOP4 = sj.TOP4; gt_j = sorted(TOP4, key=lambda m: -acc_j[m]); gt_p = sorted(TOP4, key=lambda m: -acc_pool[m])
    top = [r for r in rows_k if r["a"] in TOP4 and r["b"] in TOP4]
    th4 = jf.board_from(jf.current_votes(top), TOP4); order, pv_j, _ = jf.violations(th4, gt_j); _, pv_p, _ = jf.violations(th4, gt_p)
    order_g, pv_gg, _ = jf.violations(th, gt_j)
    L.append("  top-4 (ungated convention: top-4 board fit on the %d top-cluster matches): %s | key order over judged questions %s -> %d violations | key order over the pool %s -> %d violations | from the 12-model global fit: %s (%d)"
             % (len(top), " > ".join(order), " > ".join(gt_j), pv_j, " > ".join(gt_p), pv_p, " > ".join(order_g), pv_gg))
    dec = []
    for mid in cached:
        r = kv[mid]; ca, cb = G.get((r["q"], r["a"])), G.get((r["q"], r["b"]))
        if ca is None or cb is None or ca == cb: continue
        dec.append((mid, r["a"] if ca else r["b"]))
    accA = sum(kv[mid]["w"] == d for mid, d in dec) / max(1, len(dec))
    com = [(mid, d) for mid, d in dec if kv[mid]["w"] in (kv[mid]["a"], kv[mid]["b"])]
    accB = sum(kv[mid]["w"] == d for mid, d in com) / max(1, len(com))
    valid = [mid for mid in cached if not kv[mid]["inv"]]
    fin = Counter(); nonterm = 0
    for mid in cached:
        fin[kv[mid]["f1"]] += 1; fin[kv[mid]["f2"]] += 1
        if kv[mid]["f1"] in ("length", "content_filter") or kv[mid]["f2"] in ("length", "content_filter"): nonterm += 1
    L.append("  key-decidable accuracy: convention A (TIE / INVALID / non-terminated wrong) %.3f (n=%d) | convention B (committed only) %.3f (n=%d) | decidable tie rate %.3f"
             % (accA, len(dec), accB, len(com), sum(kv[mid]["w"] == "TIE" for mid, _ in dec) / max(1, len(dec))))
    L.append("  tie rate %.3f | flip rate %.3f (valid n=%d) | invalid %d of %d | finish_reason over %d calls: %s | matches touched by NON_TERMINATED: %d"
             % (sum(kv[mid]["w"] == "TIE" for mid in valid) / max(1, len(valid)), sum(kv[mid]["flip"] for mid in valid) / max(1, len(valid)), len(valid),
                len(cached) - len(valid), len(cached), 2 * len(cached), dict(fin), nonterm))
    L.append("  %-28s %9s %11s %9s %9s" % ("model", "theta(K)", "theta(GC)", "key(jdg)", "key(pool)"))
    for m in sorted(models, key=lambda m: -th[m]):
        L.append("  %-28s %+9.3f %+11.3f %9.3f %9.3f" % (m, th[m], th_g[m], acc_j[m], acc_pool[m]))
    # (b) the pairing
    L.append(""); L.append("=== (b) match for match against GROK-CALIB (item 25's readout; the two arms received the same bytes) ===")
    paired = [mid for mid in cached if mid in py]
    L.append("  paired %d of %d cached" % (len(paired), len(cached)))
    okA, okB = paired_contrast(L, kv, py, paired, G, plabel="GROK-CALIB")
    L.append("  test-retest floor of the deployed judge on byte-identical prompts: %.3f (DECOMP); a paired delta inside +/-%.1fpp is within that floor" % (DECOMP_FLOOR, CRITERION_PP))
    # (c) the widener readout on the Kotlin cache, as grok_calib --analyze reads its own
    L.append(""); L.append("=== (c) calibration board for the Kotlin path: systematic_budget's helpers on the Kotlin cache (as GROK-CALIB's --analyze) ===")
    GUARD = 0.05
    sid = {m["match_id"]: m for m in matches}
    def decidable(mid):
        m = sid[mid]; ca, cb = G.get((m["qid"], m["model_a"])), G.get((m["qid"], m["model_b"]))
        return ca is not None and cb is not None and ca != cb
    n_all = len(judgeable); n_dec = sum(1 for mid in judgeable if decidable(mid))
    unp_all = sum(kv[mid]["inv"] for mid in cached) + len(missing)
    unp_dec = sum(kv[mid]["inv"] for mid in cached if decidable(mid)) + sum(1 for mid in missing if decidable(mid))
    L.append("  unparsed on the schedule (INVALID in either order + missing): %d of %d overall (%.1f%%) | %d of %d key-decidable (%.1f%%) | guard %.0f%% | (the %d excluded reference-less matches are not on the Kotlin schedule: %.1f%% of GROK-CALIB's %d)"
             % (unp_all, n_all, 100 * unp_all / max(1, n_all), unp_dec, n_dec, 100 * unp_dec / max(1, n_dec), 100 * GUARD, ex["n"], 100 * ex["n"] / N_GC, N_GC))
    if pilot or len(cached) < 1000:
        L.append("  widener readout: not run on a pilot / a cache under 1,000 matches (the fit needs >= 200 verdicts per anchor)")
    elif unp_all / max(1, n_all) > GUARD or unp_dec / max(1, n_dec) > GUARD:
        L.append("  WIDENER READOUT REFUSED: more than %.0f%% of the schedule is unparsed or missing; a fit here would be on a selected schedule" % (100 * GUARD))
    else:
        _gc().item26_criteria(L, kotlin_db, sb_out)
        L.append("  widener readout written to %s%s" % (rel(sb_out), "" if of_record else " (not of record)"))
    # (d) the registered lines
    L.append("")
    L.append("  JUDGE-WIRING-BOARD REGISTERED: DESCRIPTIVE - the Kotlin cache is the board of record for the production path (item 25's consequence); no pass/fail on the board itself")
    L.append("  pairing line (item 25's criterion reused, |delta| <= %.1fpp under conventions A and B, Kotlin vs GROK-CALIB): %s%s"
             % (CRITERION_PP, "INSIDE under both" if (okA and okB) else "OUTSIDE under " + " and ".join(t for t, ok in (("A", okA), ("B", okB)) if not ok),
                "" if of_record else " (NOT the line of record: %s)" % ("pilot slice" if pilot else "partial cache" if partial else "; ".join(gate_why))))
    finish()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-kit", action="store_true")
    ap.add_argument("--force", action="store_true", help="with --export-kit: replace a kit whose hash differs")
    ap.add_argument("--freeze-only", action="store_true")
    ap.add_argument("--dump-payload", type=int, default=None, metavar="MATCH_ID")
    ap.add_argument("--shas", action="store_true")
    ap.add_argument("--gen-fixtures", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--analyze", default=None, metavar="KOTLIN_DB")
    ap.add_argument("--freeze-board", action="store_true", help="BOARD: build judge_wiring_board_set.json from GROK-CALIB's cache (zero calls)")
    ap.add_argument("--shas-board", action="store_true", help="BOARD: payload_shas_python_board.csv through grok_calib.Assembler")
    ap.add_argument("--dry-run-board", action="store_true", help="BOARD: assemble every payload, assert the kit and the body, post nothing")
    ap.add_argument("--analyze-board", default=None, metavar="KOTLIN_DB", help="BOARD: the board of record + pairing + widener readout")
    a = ap.parse_args()
    if a.gen_fixtures:
        gen_fixtures(); sys.exit(0)                       # synthetic: needs no database, no pool
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)   # pool id mandatory since SPLIT-FUNCTION-IMPL
    print("[POOL] %s (pool of record; active pool verified by pool_guard)" % POOL, flush=True)
    if a.export_kit: export_kit(a.force)
    elif a.freeze_only: freeze_set(allow_freeze=True)
    elif a.dump_payload is not None: dump_payload(a.dump_payload)
    elif a.shas: write_shas()
    elif a.dry_run: dry_run(a.pilot)
    elif a.analyze: analyze(a.analyze, a.pilot)
    elif a.freeze_board: freeze_board(allow_freeze=True)
    elif a.shas_board: write_shas_board()
    elif a.dry_run_board: dry_run_board(a.pilot)
    elif a.analyze_board: analyze_board(a.analyze_board, a.pilot)
    else: ap.print_help()
