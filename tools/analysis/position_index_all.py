"""POSITION-INDEX-ALL — across every CERTIFIED dual-order cache, among order-flips whose two votes are both decisive, what share name the
FIRST-SHOWN side in both orders (s = FF / (FF + SS)), and is one-sided flip composition GENERAL across corpora? (zero calls; plan
Amendment 11 clause 4; a stated dependency, NOT a gate, of BFCL-FLIP-RESEED)

REGISTRATION OF RECORD: docs/judge_v2_program.md L13111-L13227 (commit b25bde0), heading "## Registered 2026-09-23 (before any code or
call) — POSITION-INDEX-ALL: ..."; record docs/agents/results/POSITION-INDEX-ALL.json. Zero judge calls; no key, no reference, no prompt.

LAUNCH SEQUENCE (only AFTER VOTE-FRAME-CERT is HELD and recorded):
  python tools/analysis/position_index_all.py --selftest   (synthetic caches of KNOWN s in both frames, certified by vote_frame_cert under
                                                            tempfile.mkdtemp(); the same s once the transposition is applied, 1 - s when it is
                                                            withheld; every criterion / prediction / falsifier print branch executed)
  python tools/analysis/position_index_all.py --dry-run    (zero calls, writes nothing: the certificate's status, entered and excluded caches, the
                                                            family table with FF, SS, clusters and the Kish mean cluster size; exits)
  python tools/analysis/position_index_all.py --run        (writes experiment_results/position_index_all_outcome.txt WRITE-ONCE, mode "x")

GATE. experiment_results/vote_frame_cert.json must exist, be VOTE-FRAME-CERT's, and read certificate = HELD, else REFUSED. A cache enters
ONLY with cache class CERTIFIED-POSITIONAL or CERTIFIED-CONTESTANT, and only its CERTIFIED tables; the positional votes are read through
vote_frame_cert.unit_votes, which applies the certificate's transposition and REFUSES any other class (one implementation of the frame for
both instruments). Every entered cache's sha256_16 must equal the certificate's, else REFUSED (the cache moved after certification).
HYGIENE. Every file through vote_frame_cert.open_ro (mode=ro&immutable=1 asserted, query_only read back); size and mtime of every
opened file before and after, asserted unchanged. The FIRST printed line lists the pools of the entered caches (from the certificate's
run_meta reading); p2dca21ab5f4ef3ae and paeec37aa28063c75 are verified with pool_guard.assert_pool_of_record; p2035adddedd1becb is NOT
in pool_guard's registry and the BFCL corpus DB carries no reserved_pool table (bfcl_ingest.py writes none; bfcl_judged_pilot.py L20-L28
verifies it from the id file without pool_guard), so for it only the id-file half of assert_pool_of_record is run
(compute_pool_id(judgeable(experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json)) == p2035adddedd1becb) and the line says so.
[DEVIATION FORCED BY THE RECORD, reported to the registrar.]

FAMILIES (corpus, judge model). FAMILY_MAP below is the builder's source reading, one entry per cache path, each with its source line;
a cache absent from it is UNASSIGNED (listed, counted, excluded); _backup/ copies are excluded as copies (their originals enter); a
cache's run_meta judge_model, where present, must agree with the map or the cache is excluded. Within a family, caches are POOLED WITH
CLUSTERING BY QUESTION ACROSS CACHES (cluster = (corpus, question id); task id on BFCL); the per-cache s is printed beside. Question ids:
the row's qid / question_id / eval_question_id, else the cache's schedule joined on the match id, else the x12 match_history
(experiment_results/x12_crossdomain/ratings_x12.db, id -> eval_question_id, the model pair asserted row by row) for the R3 caches that
store only the x12 match id, else stack_v2_promptv2_x12all.db (match_id -> qid) for arenav3.db; a cache with none is clustered by its own
match key and the line says so. BFCL enters on the deciding subset only (verdicts table, schedule stratum 'headline', nj empty), as the
registration's worked case (57 flips) does; its probe table and self-preference stratum do not enter.

STATISTICS. s = FF / (FF + SS) over both-decisive flips (the two POSITIONAL votes name the same position). Interval of record: point +-
1.96 x the question-clustered bootstrap SE (B 2000, seed 42); the exact binomial (Clopper-Pearson, unclustered) beside, never deciding.
SIDEDNESS: FIRST-SIDED iff the interval lies wholly above 0.5, SECOND-SIDED iff wholly below, UNRESOLVED iff it contains 0.5. DEFF
MEASURED = SE_boot^2 / (s(1-s)/n); MDE = 2.80 x 0.5 x sqrt(DEFF / (FF + SS)); SUPPORTED iff MDE <= 0.35.
[BUILDER'S READING, reported to the registrar: at s = 0 or 1 (BFCL's recorded 57 / 0) the binomial variance is 0 and every bootstrap draw
equals s, so the MEASURED DEFF is 0 / 0, UNDEFINED. The registration says BFCL's support "is decided by its MEASURED DEFF for s"; the
instrument does not invent one: such a family's support is UNDECIDABLE, printed with the Kish (rho = 1) bound and the registered
transported DEFF beside it, and C2 is evaluated with and without the family: if the two agree, that is C2; if they differ, C2 is
UNDETERMINED (by support). No verdict is chosen between them in code.]
[RULED 2026-09-23 by the registrar, ruling (3), programme L13691-L13746 (04379d7); the bracket above is SUPERSEDED: a family whose
MEASURED DEFF is undefined (s = 0 or 1 in every replicate) is UNSUPPORTED unless its transported MDE is <= 0.35. BFCL / grok is therefore
UNSUPPORTED FOR C2 ("measured DEFF undefined at s = 1.000; transported MDE 0.352 > 0.35", the MDE recomputed on the family's own n),
and C2's support condition and verdict are computed WITHOUT it: that is the PRIMARY reading. The with-undefined-DEFF-families reading is
PRINTED BESIDE, labelled DESCRIPTIVE, and decides nothing. The "UNDETERMINED (by support) if the two readings differ" trigger is NOT
adopted and does not exist in the code. BFCL is still read at row level under C1 (57 / 0) and its s is reported; P4 is scored on the
POINT only, its sidedness clause not read. If MMLU-Pro is the only corpus with a supported family, C2 reads UNDETERMINED under its own
support condition, and the line says so.]
[CORRECTED 2026-09-23 by the READY review docs/reviews/NOT_READY_vote_frame_family.md (14edeb4), H1 / M2 / M3: ruling (3) is categorical,
so BFCL is EXCLUDED FROM C2's PRIMARY support set UNCONDITIONALLY (whatever its FF / SS; the support line names ruling (3), and a BFCL
family whose data differ from the ruling's premise 57 / 0 is printed "PREMISE DIFFERS" for the registrar); the with-BFCL reading stays
DESCRIPTIVE. The p2035 check REFUSES if a BFCL cache enters without p2035adddedd1becb in its run_meta. The pool checks take an injectable
guard so that the selftest executes both their admit and refuse branches without opening a DB.]
[CORRECTED 2026-09-23 by the READY re-review docs/reviews/READY_vote_frame_family_rr.md (bc2ea7b), D3 / D5 / D6: the certificate is READ only if
its script_sha256_16_lf equals VFC_PIN_LF, the sha256[:16] of the LF bytes of the vote_frame_cert.py build this READY applies to (D3; the pin is
updated in the same commit as any change to vote_frame_cert.py). The selftest's refusal checks match their message tags (D5). The REAL
pool_guard.assert_pool_of_record is not executed by any selftest (a stub guard is injected); its execution is witnessed by the dry-run's first
[POOLS] line, READY condition P-C2 (D6; no code change).]
[CORRECTED 2026-09-23 by the VOTE-FRAME-CERT post-run review docs/reviews/2026-09-23_vote_frame_cert_post.md (abf4db5), D8 / D4 / item 5.2:
(D8) the two Kotlin caches enter ONLY their judge_calls table (tables=("judge_calls",)), as bfcl_judged_pilot enters only verdicts: their WIDE
verdicts table holds the same matches and was kept out only because it has no judge_model column, silently. (D4) extract() recounts, per entered
table, the matches the certificate's own pairing rule makes readable (vfc.long_key_fn over the registered order pair, duplicates excluded) and
prints a [COUNTS] line: paired, dropped for an unresolved label (vfc.unit_votes skips them without a count), outside the subset, without a
corpus or judge, entered; a silent drop is therefore visible in the run output. (5.2) arena13.db enters only as its (ensemble, reversed) pair;
the unpaired arms (selfref, t0a, t0b) are never read as orders (vfc.unit_votes reads the pair only; executed by a fixture). vote_frame_cert.py
and tie_mechanics.py are unchanged by this correction.]
[RULED 2026-09-23 by the registrar, ruling (2) (04379d7): CONFIRMED, the check of record for p2035adddedd1becb is compute_pool_id(judgeable(ids))
over the 228 EVAL ids of the id file; assert_pool_of_record runs for p2dca21ab5f4ef3ae and paeec37aa28063c75.]
[ENGINEERING 2026-09-25, queue VFC-FIXES-2, builder's text, awaiting its delta READY (worktree-only; no code path of a real run changes here):
(D5, review 9d3e261) the selftest's INFO line used to say that a mismatch between VFC_PIN_LF and the imported vote_frame_cert.py "refuses every
real run"; that is false. load_cert compares VFC_PIN_LF with the certificate JSON's script_sha256_16_lf (the WRITER of the certificate of record),
never with the imported module, so a real run proceeds with whichever vote_frame_cert.py reader is imported. The INFO line now says so, and a
selftest check EXECUTES it (a certificate whose writer sha equals the pin is read whatever the imported reader's sha). VFC_PIN_LF stays
72ceddfe919a982e (it pins the certificate of record's writer; no new certificate is written). (R-8 of VFC-RX-RULING, programme L17171-L17328)
vote_frame_cert.unit_votes now REFUSES on an unresolvable label of a CERTIFIED unit instead of skipping it; the sentence in the abf4db5 bracket
above "vfc.unit_votes skips them without a count" is SUPERSEDED: the [COUNTS] line's "dropped for an unresolved label" is 0 by construction on
any run that completes (a drop is now a refusal). FORCED BY THE RULING, reported: the selftest's D4 fixture (an arena13-like cache with 4
unresolvable reversed labels, which the certificate used to certify on the resolved subset and the reader used to skip) would now be UNCERTIFIABLE
(R6) and never enter; it is made fully resolvable (the D4 / 5.2 counting checks keep their subject, dropped 0), and a second fixture carries the 4
unresolvable labels: UNCERTIFIABLE (R6) in the certificate, excluded by plan() by class, and the reader REFUSES it (R-8) when handed it as
CERTIFIED. Nothing else in this file changes.]

CRITERIA C1-C5, PREDICTIONS P1-P6, the FALSIFIER and the BFCL-FLIP-RESEED dependency line are printed by the functions below; the
selftest executes every branch.
"""
import os, sys, json, math, random, argparse, tempfile, shutil, io, contextlib, sqlite3
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard
import rejudge_grok as rj
import vote_frame_cert as vfc

TEST = "POSITION-INDEX-ALL"
REGISTRATION = "docs/judge_v2_program.md L13111-L13227 (b25bde0)"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
CERT_JSON = os.path.join("experiment_results", "vote_frame_cert.json")
OUT = os.path.join("experiment_results", "position_index_all_outcome.txt")
B = 2000; SEED = 42; SUPPORT_MDE = 0.35
POOLS_FULL = ("p2dca21ab5f4ef3ae", "paeec37aa28063c75")
BFCL_POOL = "p2035adddedd1becb"; BFCL_POOL_N = 228; BFCL_ID_FILE = os.path.join("experiment_configs", "reserved_pool_frozen_bfcl_p2035adddedd1becb.json")
MMLU, BFCL, MATH, IFEVAL = "MMLU-Pro", "BFCL", "MATH", "IFEval"
GROK, GROKR, MISTRAL, DSR1 = "grok-4-1-fast-non-reasoning", "grok-4-1-fast-reasoning", "Mistral-Large-3", "DeepSeek-R1-0528"
X12 = "experiment_results/x12_crossdomain/"
X12_MATCH_HISTORY = "x12_match_history"; X12ALL = "x12all_verdicts"
# path -> dict(corpus | corpus_col, judge | judge_col (+ judge_values), qid_from, subset, tables, src) — the builder's source reading.
FAMILY_MAP = {
    X12 + "aggregate.db": dict(corpus=MMLU, judge=GROK, src="aggregate_ties.py L61"),
    X12 + "arena13.db": dict(corpus=MMLU, judge=GROK, src="arena13.py L89 / position_decomp.py L39 (grok-4-1-fast-non-reasoning)"),
    X12 + "arenav3.db": dict(corpus=MMLU, judge=MISTRAL, qid_from=X12ALL, src="arena_v3_compiled.py L6-L7 (Mistral-Large-3 via rubric_p8.call)"),
    X12 + "arxiask.db": dict(corpus=MMLU, judge=GROK, src="arxiask_probe.py (rr.JUDGE_MODEL grok-4-1-fast-non-reasoning)"),
    X12 + "canary_baseline_pass1.db": dict(corpus=MMLU, judge=GROK, src="canary_baseline.py L81"),
    X12 + "canary_baseline_pass2.db": dict(corpus=MMLU, judge=GROK, src="canary_baseline.py L81"),
    X12 + "escalate_llama_law.db": dict(corpus=MMLU, judge=GROKR, src="escalate_llama_law.py L78"),
    X12 + "grok_calib.db": dict(corpus=MMLU, judge=GROK, src="grok_calib.py L87"),
    X12 + "leaf_powered.db": dict(corpus=MMLU, judge=GROK, src="leaf_powered.py (rr.JUDGE_MODEL grok-4-1-fast-non-reasoning)"),
    X12 + "newcomer_placement.db": dict(corpus=MMLU, judge_meta="judge_model", src="newcomer_placement.py L234 (meta judge_model)"),
    X12 + "newcomer_placement_steps.db": dict(corpus=MMLU, judge_meta="judge_model", src="placement_steps.py L327 (meta judge_model)"),
    X12 + "oracle.db": dict(corpus=MMLU, judge=GROK, src="oracle_ref.py"),
    X12 + "pairnoref.db": dict(corpus=MMLU, judge=GROK, src="pair_noref.py"),
    X12 + "placebo.db": dict(corpus=MMLU, judge=GROK, src="placebo_entry.py"),
    X12 + "ref_checklist.db": dict(corpus=MMLU, judge=GROK, src="ref_checklist.py L83"),
    X12 + "refconf_grok.db": dict(corpus=MMLU, judge=GROK, src="refconf.py"),
    X12 + "rejudge_deepseek_r1_0528.db": dict(corpus=MMLU, judge=DSR1, src="rejudge_reasoning.py (cache_path rejudge_%s)"),
    X12 + "rejudge_grok.db": dict(corpus=MMLU, judge=GROK, qid_from=X12_MATCH_HISTORY, src="rejudge_grok.py L60"),
    X12 + "rejudge_grok_4_1_fast_reasoning.db": dict(corpus=MMLU, judge=GROKR, src="rejudge_reasoning.py"),
    X12 + "rejudge_grok_4_1_fast_reasoning_refgrok.db": dict(corpus=MMLU, judge=GROKR, src="rejudge_reasoning.py / escalate_llama_law.py"),
    X12 + "rejudge_mistral_format_stripped.db": dict(corpus=MMLU, judge=MISTRAL, src="format_perturbation.py L6"),
    X12 + "rejudge_mistral_reference.db": dict(corpus=MMLU, judge=MISTRAL, src="rejudge_reference.py MODEL"),
    X12 + "rejudge_mistral_reference_grok_reasoning.db": dict(corpus=MMLU, judge=MISTRAL, src="rejudge_reference.py MODEL"),
    X12 + "rejudge_mistral_two_refs.db": dict(corpus=MMLU, judge=MISTRAL, src="j2d_two_refs.py"),
    X12 + "rejudge_mistral_v2_refgrok.db": dict(corpus=MMLU, judge=MISTRAL, src="prompt_v2.py"),
    X12 + "rubric_contrast.db": dict(corpus=MMLU, judge_col="judge", judge_values={"mistral": MISTRAL, "grok": GROK}, qid_from=X12_MATCH_HISTORY,
                                     src="rubric_value_contrast.py L71-L76"),
    X12 + "rubric_kit.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_kit.py L242 (rubric_p8.call)"),
    X12 + "rubric_ladder.db": dict(corpus=MMLU, judge=MISTRAL, qid_from=X12_MATCH_HISTORY, src="rubric_ladder.py"),
    X12 + "rubric_swap.db": dict(corpus=MMLU, judge=MISTRAL, qid_from=X12_MATCH_HISTORY, src="rubric_swap.py"),
    X12 + "stack_norubric.db": dict(corpus=MMLU, judge=GROK, src="stack_norubric.py L90"),
    X12 + "stack_v2.db": dict(corpus=MMLU, judge=MISTRAL, src="stack_judge.py L6"),
    X12 + "stack_v2_promptv2.db": dict(corpus=MMLU, judge=MISTRAL, src="stack_judge.py L6"),
    X12 + "stack_v2_promptv2_grok.db": dict(corpus=MMLU, judge=GROK, src="stack_judge.py L37 / L98"),
    X12 + "stack_v2_promptv2_x12all.db": dict(corpus=MMLU, judge=MISTRAL, src="stack_judge.py L38 (the x12 board of record)"),
    X12 + "stack_v2_promptv2_x20.db": dict(corpus=MMLU, judge=MISTRAL, src="arena_v2_x20.py L30 (the x20 board of record)"),
    X12 + "stack_v2_kit.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_kit.py L242"),
    X12 + "stack_v2_kit2.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_kit2.py L50"),
    X12 + "stack_v2_kit2_grok.db": dict(corpus=MMLU, judge=GROK, src="rubric_kit2.py L182"),
    "experiment_results/causal_length/grok-reasoning.db": dict(corpus=MMLU, judge=GROKR, src="causal_length.py L24"),
    "experiment_results/causal_length/mistral.db": dict(corpus=MMLU, judge=MISTRAL, src="causal_length.py L24"),
    "experiment_results/causal_length/mistral_refgrok.db": dict(corpus=MMLU, judge=MISTRAL, src="causal_length.py L24"),
    "experiment_results/causal_length/mistral_refgrok_v2.db": dict(corpus=MMLU, judge=MISTRAL, src="causal_length.py L24"),
    "experiment_results/rubric_512/bareq512_s42.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_512.py"),
    "experiment_results/rubric_512/generic_ss.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_512_ss.py"),
    "experiment_results/rubric_512/grok_reasoning_cell.db": dict(corpus=MMLU, judge=GROKR, src="rubric_512_r.py"),
    "experiment_results/rubric_512/grok_reasoning_generic.db": dict(corpus=MMLU, judge=GROKR, src="rubric_512_r.py"),
    "experiment_results/rubric_p8/mistral.db": dict(corpus=MMLU, judge=MISTRAL, src="rubric_p8.py L21"),
    "experiment_results/multicorpus/gen_arena_grok.db": dict(corpus_col="source", corpus_values={"MATH": MATH, "IFEVAL": IFEVAL}, judge=GROK,
                                                             src="generative_arena.py L32 / JUDGE_MODEL"),
    "experiment_results/multicorpus/ifeval_response_oracle.db": dict(corpus=IFEVAL, judge=GROK, src="ifeval_response_oracle.py L135"),
    "experiment_results/multicorpus/stage3_math_grok_v2_capfree.db": dict(corpus_col="source", corpus_values={"MATH": MATH, "IFEVAL": IFEVAL},
                                                                          judge=GROK, src="stage3_math.py L140"),
    "experiment_results/agent/bfcl_judged_pilot.db": dict(corpus=BFCL, judge=GROK, subset="bfcl_deciding", tables=("verdicts",),
                                                          src="bfcl_judged_pilot.py JUDGE_MODEL; deciding subset L1451"),
    "experiment_results/judge_wiring/board/kotlin_c0d3f708cbc3930e.db": dict(corpus=MMLU, judge_col="judge_model", tables=("judge_calls",),
                                                                               src="JudgeCallStore.kt judge_model column; judge_calls only (D8, abf4db5)"),
    "experiment_results/judge_wiring/kotlin_ae92da306544f453.db": dict(corpus=MMLU, judge_col="judge_model", tables=("judge_calls",),
                                                                       src="JudgeCallStore.kt judge_model column; judge_calls only (D8, abf4db5)"),
}
EXCLUDE_PREFIXES = {"experiment_results/_backup/": "a _backup/ copy (its original is certified and enters on its own; a copy is not an independent judging)"}
BFCL_C1 = dict(n=458, FF=57, SS=0)
VFC_PIN_LF = "72ceddfe919a982e"   # sha256[:16] of the LF bytes of tools/analysis/vote_frame_cert.py this READY applies to (D3, bc2ea7b)
# C4: the prior position readouts, as recorded
AGREE_ORDER_REC = {"AGREE": (0.0184, 0.0474, 0.3484), "DISAGREE": (0.0071, 0.0538, 0.1228)}
AGREE_ORDER_N = {"AGREE": 8922, "DISAGREE": 10442}
POSITION_DECOMP_REC = (0.695, 0.560)      # new contestant's win rate first vs second on the frontier matches (direction -0.135)
POSITION_FULL_REC = -0.011                # cross-tier direction (second minus first), p 0.12
FAMILY_PRED = {(MMLU, MISTRAL): ("SECOND-SIDED", (0.10, 0.35)), (MMLU, GROK): ("FIRST-SIDED", (0.55, 0.80)), (BFCL, GROK): ("FIRST-SIDED", (0.93, 1.00))}
DEFF_TRANSPORTED = {(BFCL, GROK): 3.60}   # the registration's Support (b): BFCL-JUDGED-PILOT's task-clustered DEFF, transported


# ── the gate and the plan ────────────────────────────────────────────────────────────────────────────────────────────────────────

def load_cert(root, pin=None):
    pin = pin or VFC_PIN_LF
    p = os.path.join(root, CERT_JSON)
    if not os.path.exists(p):
        raise SystemExit("[CERT] REFUSED: %s is absent; POSITION-INDEX-ALL may not run before VOTE-FRAME-CERT is HELD and recorded" % CERT_JSON)
    d = json.load(open(p, encoding="utf-8"))
    if d.get("test") != vfc.TEST or d.get("certificate") != "HELD":
        raise SystemExit("[CERT] REFUSED: %s is %s / certificate %s, not VOTE-FRAME-CERT HELD" % (CERT_JSON, d.get("test"), d.get("certificate")))
    if d.get("script_sha256_16_lf") != pin:
        raise SystemExit("[CERT] REFUSED: %s was written by vote_frame_cert.py sha256[:16] of the LF bytes %s, not the pinned build %s (D3)"
                         % (CERT_JSON, d.get("script_sha256_16_lf"), pin))
    return d, vfc.sha256_16(p)


def plan(cert, fmap):
    entered, excluded = [], []
    for c in cert["caches"]:
        path = c["path"]
        pref = next((r for p, r in EXCLUDE_PREFIXES.items() if path.startswith(p)), None)
        if c["klass"] not in vfc.CERTIFIED:
            excluded.append((path, "class %s" % c["klass"])); continue
        if pref:
            excluded.append((path, pref)); continue
        if path not in fmap:
            excluded.append((path, "UNASSIGNED: no (corpus, judge) in the builder's FAMILY_MAP (writer %s)" % c.get("writer"))); continue
        spec = fmap[path]
        units = [u for u in c["units"] if u["klass"] in vfc.CERTIFIED and (not spec.get("tables") or u["table"] in spec["tables"])]
        skipped = [(u["table"], u["klass"]) for u in c["units"] if u not in units]
        if not units:
            excluded.append((path, "no certified table in scope")); continue
        entered.append(dict(cache=c, spec=spec, units=units, skipped=skipped))
    return entered, excluded


def verify_pools(entered, say, pool_check=True, root=None, guard=None):
    guard = guard or pool_guard.assert_pool_of_record
    pools = sorted({p.split("=", 1)[1] for e in entered for p in e["cache"].get("pools", []) if "=" in p})
    for e in entered:
        if e["spec"].get("corpus") == BFCL and not any(p.split("=", 1)[-1] == BFCL_POOL for p in e["cache"].get("pools", [])):
            raise SystemExit("[POOL] REFUSED: the BFCL cache %s enters without %s in its run_meta (review 14edeb4, M2)" % (e["cache"]["path"], BFCL_POOL))
    lines = []
    for p in pools:
        if p in POOLS_FULL:
            if pool_check: guard(p)
            lines.append("%s verified by pool_guard.assert_pool_of_record" % p)
        elif p == BFCL_POOL:
            if pool_check:
                ids = json.load(open(os.path.join(root or ROOT, BFCL_ID_FILE), encoding="utf-8"))
                h = pool_guard.compute_pool_id(pool_guard.judgeable(ids))
                n_ids = sum(len(v) for v in pool_guard.judgeable(ids).values())
                if h != BFCL_POOL or n_ids != BFCL_POOL_N:
                    raise SystemExit("[POOL] REFUSED: %s hashes to %s over %d ids, not %s over %d" % (BFCL_ID_FILE, h, n_ids, BFCL_POOL, BFCL_POOL_N))
            lines.append("%s: check of record (ruling (2), 04379d7) compute_pool_id(judgeable(ids)) = %s over the %d ids of %s (not in pool_guard's "
                         "registry; no reserved_pool table in the BFCL corpus)" % (p, BFCL_POOL, BFCL_POOL_N, BFCL_ID_FILE.replace("\\", "/")))
        else:
            lines.append("%s (not a pool of record; printed, not asserted)" % p)
    say("[POOLS] pools of the entered caches: %s" % ("; ".join(lines) if lines else "(none recorded in their run_meta)"))
    return pools


# ── extraction ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def schedule_rows(con, key):
    tc = vfc.table_columns(con)
    if "schedule" not in tc or key not in {c for c, _ in tc["schedule"]}: return None
    cur = con.execute("SELECT * FROM schedule"); cols = [d[0] for d in cur.description]
    return {r[cols.index(key)]: dict(zip(cols, r)) for r in cur}


def qid_maps(root, needed):
    """The two cross-cache question maps, opened read-only only when a cache needs them."""
    out = {}
    if X12_MATCH_HISTORY in needed:
        p = os.path.join(root, X12, "ratings_x12.db")
        if os.path.exists(p):
            con = vfc.open_ro(p)
            try: out[X12_MATCH_HISTORY] = {r[0]: (r[1], r[2], r[3]) for r in con.execute("SELECT id, eval_question_id, model_a, model_b FROM match_history")}
            finally: con.close()
    if X12ALL in needed:
        p = os.path.join(root, X12, "stack_v2_promptv2_x12all.db")
        if os.path.exists(p):
            con = vfc.open_ro(p)
            try: out[X12ALL] = {r[0]: (r[1], r[2], r[3]) for r in con.execute("SELECT match_id, qid, model_a, model_b FROM verdicts")}
            finally: con.close()
    return out


def readable_matches(con, u):
    """D4 (abf4db5): for a LONG unit, the matches the certificate's own pairing rule makes readable (vfc.long_key_fn; both registered order
    values present; no duplicate within them), so that the reader's silent skips of unresolved labels can be COUNTED. None for a WIDE unit
    (every row is a match and nothing is skipped)."""
    if u["kind"] != "LONG": return None
    kf, _ = vfc.long_key_fn(dict(columns=u["columns"], key=u["key"], match_key=u.get("match_key"), pk=u.get("pk")))
    pair = u["pair"]; seen = defaultdict(Counter)
    for row in vfc.fetch_rows(con, u["table"]):
        a = str(row.get(u["key"]))
        if a in pair: seen[kf(row)][a] += 1
    return sum(1 for c in seen.values() if c[pair[0]] == 1 and c[pair[1]] == 1)


def extract(root, entered, say, maps=None):
    """-> list of records dict(family, cluster, p1, p2, cache, table, row, sched) and per-cache notes."""
    needed = {e["spec"].get("qid_from") for e in entered}
    maps = maps if maps is not None else qid_maps(root, needed)
    recs = []; notes = defaultdict(list)
    for e in entered:
        path = e["cache"]["path"]; ap = os.path.join(root, path); spec = e["spec"]
        st0 = vfc.stat_of(ap)
        if vfc.sha256_16(ap) != e["cache"]["sha256_16"]:
            raise SystemExit("[CERT] REFUSED: %s sha256_16 %s differs from the certificate's %s: the cache moved after certification"
                             % (path, vfc.sha256_16(ap), e["cache"]["sha256_16"]))
        con = vfc.open_ro(ap)
        try:
            judge_fixed = spec.get("judge")
            if spec.get("judge_meta"):
                judge_fixed = vfc.meta_value(con, spec["judge_meta"])
                if not judge_fixed: notes[path].append("meta %s absent: cache not assignable" % spec["judge_meta"]); continue
            mj = vfc.meta_value(con, "judge_model")
            if judge_fixed and mj and mj != judge_fixed:
                notes[path].append("EXCLUDED: run_meta judge_model %r disagrees with the map's %r" % (mj, judge_fixed)); continue
            for u in e["units"]:
                votes, vnotes = vfc.unit_votes(con, ap, u)
                notes[path] += ["%s: %s" % (u["table"], n) for n in vnotes]
                readable = readable_matches(con, u)
                tc = dict(read=len(votes), readable=readable, dropped_unresolved=(readable - len(votes)) if readable is not None else 0,
                          outside_subset=0, no_corpus_or_judge=0, entered=0)
                e.setdefault("table_counts", {})[u["table"]] = tc
                mk = u.get("match_key")
                sched = schedule_rows(con, mk) if mk else None
                qmap = maps.get(spec.get("qid_from")) if spec.get("qid_from") else None
                mism = fallback = 0
                for r in votes:
                    row = r["row"]; s = sched.get(row.get(mk)) if sched else None
                    if spec.get("subset") == "bfcl_deciding":
                        if not s or s.get("stratum") != "headline" or (s.get("nj") not in (None, "")):
                            tc["outside_subset"] += 1; continue
                    corpus = spec.get("corpus") or spec.get("corpus_values", {}).get(str(row.get(spec.get("corpus_col")) or (s or {}).get(spec.get("corpus_col"))))
                    judge = judge_fixed
                    if spec.get("judge_col"):
                        jv = row.get(spec["judge_col"]); judge = spec.get("judge_values", {}).get(jv, jv)
                    if not corpus or not judge:
                        tc["no_corpus_or_judge"] += 1; continue
                    q = None
                    if corpus == BFCL and s: q = s.get("task_id")
                    elif u.get("qid") and row.get(u["qid"]) is not None: q = row.get(u["qid"])
                    elif s and any(k in s for k in ("qid", "question_id")): q = s.get("qid", s.get("question_id"))
                    elif qmap is not None and row.get(mk) in qmap:
                        qq, a, b = qmap[row.get(mk)]
                        if "model_a" in row and (row.get("model_a"), row.get("model_b")) != (a, b): mism += 1
                        else: q = qq
                    if q is None:
                        fallback += 1; cl = ("match", path, str(r["key"]))
                    else:
                        cl = (corpus, str(q))
                    recs.append(dict(family=(corpus, judge), cluster=cl, p1=r["p1"], p2=r["p2"], cache=path, table=u["table"], row=row, sched=s))
                    tc["entered"] += 1
                notes[path].append("[COUNTS] %s: %d matches read of %s readable (dropped for an unresolved label %d) | outside the subset %d | without a "
                                   "corpus or judge %d | ENTERED %d" % (u["table"], tc["read"], tc["readable"] if tc["readable"] is not None else "n/a (WIDE: every row)",
                                                                       tc["dropped_unresolved"], tc["outside_subset"], tc["no_corpus_or_judge"], tc["entered"]))
                if mism: notes[path].append("%s: %d rows whose model pair disagrees with the question map were clustered by match" % (u["table"], mism))
                if fallback: notes[path].append("%s: %d rows without a question id are clustered by their own match key" % (u["table"], fallback))
        finally:
            con.close()
        if vfc.stat_of(ap) != st0: raise SystemExit("[HYGIENE] REFUSED: %s changed under the read" % path)
    return recs, notes


# ── statistics ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def flip_kind(p1, p2):
    if p1 == "Model A" and p2 == "Model A": return "FF"
    if p1 == "Model B" and p2 == "Model B": return "SS"
    return None


def binom_cdf(k, n, p):
    if p <= 0: return 1.0
    if p >= 1: return 1.0 if k >= n else 0.0
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(k + 1)))


def clopper_pearson(k, n):
    if n == 0: return (float("nan"), float("nan"))
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) >= 0.025)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) <= 0.025)
    return lower, upper


def support_of(fam, n, s, deff, mde):
    """The family's support FOR C2. BFCL is UNSUPPORTED FOR C2 whatever its data (ruling (3), 04379d7; review 14edeb4 H1), the data reading
    printed beside; every other family is read by _support_data()."""
    v, why = _support_data(fam, n, s, deff, mde)
    if fam[0] == BFCL:
        return "UNSUPPORTED", "ruling (3): BFCL never counts toward C2's two-corpora requirement; data: %s (%s)" % (why, v)
    return v, why


def _support_data(fam, n, s, deff, mde):
    """Ruling (3) (04379d7): SUPPORTED iff MDE <= 0.35 at the MEASURED DEFF; where the measured DEFF is undefined (s = 0 or 1 in every
    replicate) the family is UNSUPPORTED unless its transported MDE (the registration's transported DEFF, on the family's own n) is <= 0.35."""
    if n == 0:
        return "UNDEFINED", "no both-decisive flip (s undefined)"
    if deff is not None:
        return ("SUPPORTED" if mde <= SUPPORT_MDE else "UNSUPPORTED"), "measured DEFF %.2f, MDE %.3f %s 0.35" % (deff, mde, "<=" if mde <= SUPPORT_MDE else ">")
    t = DEFF_TRANSPORTED.get(fam)
    if t is None:
        return "UNSUPPORTED", "measured DEFF undefined at s = %.3f; no transported DEFF" % s
    mt = 2.80 * 0.5 * math.sqrt(t / n)
    if mt <= SUPPORT_MDE:
        return "SUPPORTED", "measured DEFF undefined at s = %.3f; transported DEFF %.2f gives MDE %.3f <= 0.35" % (s, t, mt)
    return "UNSUPPORTED", "measured DEFF undefined at s = %.3f; transported MDE %.3f > 0.35" % (s, mt)


def family_stats(recs, B=B, seed=SEED):
    by = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    per_cache = defaultdict(lambda: [0, 0])
    for r in recs:
        k = flip_kind(r["p1"], r["p2"])
        if not k: continue
        i = 0 if k == "FF" else 1
        by[r["family"]][r["cluster"]][i] += 1
        per_cache[(r["family"], r["cache"])][i] += 1
    out = {}
    for fam, cl in by.items():
        keys = sorted(cl, key=str); ff = sum(cl[k][0] for k in keys); ss = sum(cl[k][1] for k in keys); n = ff + ss
        s = ff / n if n else float("nan")
        rng = random.Random(seed); draws = []
        for _ in range(B):
            a = b = 0
            for _ in keys:
                c = cl[keys[rng.randrange(len(keys))]]; a += c[0]; b += c[1]
            if a + b: draws.append(a / (a + b))
        m = sum(draws) / len(draws); se = (sum((x - m) ** 2 for x in draws) / (len(draws) - 1)) ** 0.5 if len(draws) > 1 else 0.0
        lo, hi = s - 1.96 * se, s + 1.96 * se
        kish = sum((c[0] + c[1]) ** 2 for c in cl.values()) / n if n else float("nan")
        bino = s * (1 - s) / n if n else 0.0
        deff = (se * se / bino) if bino > 0 else None
        mde = 2.80 * 0.5 * math.sqrt(deff / n) if deff is not None else None
        support, reason = support_of(fam, n, s, deff, mde)
        if fam[0] == BFCL and (ff, ss) != (57, 0):
            reason += " [PREMISE DIFFERS: the ruling was made on 57 / 0, the data read %d / %d: for the registrar]" % (ff, ss)
        side = "FIRST-SIDED" if lo > 0.5 else ("SECOND-SIDED" if hi < 0.5 else "UNRESOLVED")
        out[fam] = dict(FF=ff, SS=ss, n=n, s=s, se=se, lo=lo, hi=hi, cp=clopper_pearson(ff, n), clusters=len(keys), kish=kish, deff=deff,
                        mde=mde, support=support, support_reason=reason, deff_undefined=(n > 0 and deff is None), side=side, dropped=B - len(draws),
                        mde_kish=2.80 * 0.5 * math.sqrt(kish / n) if n else None,
                        mde_transported=(2.80 * 0.5 * math.sqrt(DEFF_TRANSPORTED[fam] / n)) if fam in DEFF_TRANSPORTED and n else None,
                        per_cache={c: v for (f, c), v in per_cache.items() if f == fam})
    return out


def c2_rule(fams):
    """fams: {family: side} of the families counted as SUPPORTED. The registration's evaluation order."""
    corpora = {f[0] for f in fams}
    if len(corpora) < 2: return "UNDETERMINED", "fewer than two distinct corpora carry a SUPPORTED certified family (%s)" % sorted(corpora)
    unres = [f for f, side in fams.items() if side == "UNRESOLVED"]
    if unres: return "FAILED", "supported families UNRESOLVED: %s" % unres
    return "HELD", "every supported family is sided (%s)" % {"%s/%s" % f: side for f, side in fams.items()}


def c2_verdict(stats):
    """-> (verdict, why, descriptive line or None, consequence line or None). PRIMARY: the SUPPORTED families only (ruling (3)); the reading
    that also counts the families whose measured DEFF is undefined is printed beside, DESCRIPTIVE, deciding nothing."""
    sup = {f: st["side"] for f, st in stats.items() if st["support"] == "SUPPORTED" and f[0] != BFCL}       # BFCL never (ruling (3))
    v, why = c2_rule(sup)
    und = {f: st["side"] for f, st in stats.items() if f not in sup and st.get("n") != 0 and (f[0] == BFCL or st.get("deff_undefined"))}
    desc = None
    if und:
        v_d, why_d = c2_rule({**sup, **und})
        desc = ("DESCRIPTIVE, decides nothing: counting also BFCL and the families whose measured DEFF is undefined %s, C2 would read %s (%s)"
                % (["%s/%s" % f for f in sorted(und)], v_d, why_d))
    cons = None
    if {f[0] for f in sup} == {MMLU}:
        cons = "MMLU-Pro is the only corpus with a supported family: C2 reads UNDETERMINED under its own support condition"
    return v, why, desc, cons


def c3_lines(stats):
    by_j = defaultdict(list)
    for f, st in stats.items():
        if st["support"] in ("SUPPORTED",): by_j[f[1]].append((f[0], st["side"]))
    L = []
    dirs = {}
    for j, lst in sorted(by_j.items()):
        sides = {s for _, s in lst}
        dirs[j] = sides
        L.append("  C3 judge %s: %s -> %s" % (j, lst, "the same side across its corpora" if len(sides) == 1 else "NOT the same side across its corpora"))
    if len(dirs) >= 2:
        uniq = {j: next(iter(s)) for j, s in dirs.items() if len(s) == 1}
        L.append("  C3 judges differ in direction: %s" % ("YES" if len(set(uniq.values())) > 1 else "NO (or not uniform)"))
    if not L: L.append("  C3 no supported family: nothing to compare")
    return L


# ── C1, C4, predictions, falsifier ───────────────────────────────────────────────────────────────────────────────────────────────

def c1_eval(recs, expected=BFCL_C1):
    rs = [r for r in recs if r["family"][0] == BFCL and r["table"] == "verdicts"]
    n = len({r["row"].get("mid") for r in rs})
    ff = sum(1 for r in rs if flip_kind(r["p1"], r["p2"]) == "FF"); ss = sum(1 for r in rs if flip_kind(r["p1"], r["p2"]) == "SS")
    held = n == expected["n"] and ff == expected["FF"] and ss == expected["SS"]
    return ("HELD" if held else "FAILED"), ("C1 %s: BFCL deciding subset recomputed from the certified frame: n %d (registered %d), FF %d (registered %d), SS %d (registered %d)"
                                            % ("HELD" if held else "FAILED", n, expected["n"], ff, expected["FF"], ss, expected["SS"]))


def c4_lines(recs, root, eval_db=None):
    """Descriptive cross-reads; -> (lines, sign_changes list)."""
    L = []; changes = []
    x = [r for r in recs if r["cache"] in (X12 + "stack_v2_promptv2_x12all.db", X12 + "stack_v2_promptv2_x20.db")]
    if not x:
        L.append("  C4(a) AGREE-ORDER: NOT READ (the x12all / x20 caches did not enter: not certified or not present)")
    else:
        P = {}
        p = eval_db or rj.EVAL_DB
        qs = {r["row"].get("qid") for r in x}
        if os.path.exists(p):
            con = vfc.open_ro(p)
            try:
                for q, m, pr in con.execute("SELECT question_id, model_name, pred FROM eval_results"):
                    if q in qs: P[(q, m)] = (pr or "").strip().upper()[:1]
            finally: con.close()
        groups = defaultdict(list)
        for r in x:
            if "INVALID" in (r["p1"], r["p2"]): continue
            a, b = P.get((r["row"].get("qid"), r["row"].get("model_a")), ""), P.get((r["row"].get("qid"), r["row"].get("model_b")), "")
            k = "UNDETERMINED" if not (a and b and a in "ABCDEFGHIJ" and b in "ABCDEFGHIJ") else ("AGREE" if a == b else "DISAGREE")
            groups[k].append(r); groups["ALL"].append(r)
        L.append("  C4(a) AGREE-ORDER position shares under the certified frame (x12all + x20; partition by the two contestants' answer letters in "
                 "eval_results.pred — this script's partition, the record's counts beside):")
        for k in ("AGREE", "DISAGREE", "UNDETERMINED", "ALL"):
            g = groups.get(k, [])
            if not g: continue
            n = len(g); ff = sum(1 for r in g if flip_kind(r["p1"], r["p2"]) == "FF") / n; ss = sum(1 for r in g if flip_kind(r["p1"], r["p2"]) == "SS") / n
            tie = sum(1 for r in g if rj.combine_orders(r["p1"], r["p2"])[0] == "TIE") / n     # p2 is positional; combine_orders transposes it
            rec = AGREE_ORDER_REC.get(k)
            L.append("    %-12s n %6d | both-FIRST %.4f | both-SECOND %.4f | tie %.4f%s" % (k, n, ff, ss, tie,
                     (" | recorded n %d: %.4f / %.4f / %.4f" % (AGREE_ORDER_N[k], *rec)) if rec else ""))
            if rec:
                sign_now = (ff > ss) - (ff < ss); sign_rec = (rec[0] > rec[1]) - (rec[0] < rec[1])
                if sign_now != sign_rec: changes.append("AGREE-ORDER %s both-FIRST minus both-SECOND" % k)
    a13 = [r for r in recs if r["cache"] == X12 + "arena13.db" and r["sched"] is not None]
    if not a13:
        L.append("  C4(b)/(c) POSITION-DECOMP / POSITION-FULL: NOT READ (arena13.db did not enter)")
    else:
        for tag, fr, rec in (("C4(b) POSITION-DECOMP (frontier)", 1, POSITION_DECOMP_REC[1] - POSITION_DECOMP_REC[0]), ("C4(c) POSITION-FULL (cross-tier)", 0, POSITION_FULL_REC)):
            g = [r for r in a13 if int(r["sched"].get("frontier") or 0) == fr and "INVALID" not in (r["p1"], r["p2"])]
            if not g:
                L.append("  %s: no match with both orders" % tag); continue
            first = sum(1 for r in g if r["p1"] == "Model A") / len(g)          # the new contestant is shown first in order 1
            second = sum(1 for r in g if r["p2"] == "Model B") / len(g)         # and second in order 2
            ff = sum(1 for r in g if flip_kind(r["p1"], r["p2"]) == "FF"); ss = sum(1 for r in g if flip_kind(r["p1"], r["p2"]) == "SS")
            d = second - first
            L.append("  %s: n %d | new contestant's win rate first %.3f, second %.3f, direction (second - first) %+.3f | recorded direction %+.3f | "
                     "s = %s (FF %d, SS %d)" % (tag, len(g), first, second, d, rec, ("%.3f" % (ff / (ff + ss))) if ff + ss else "undefined", ff, ss))
            if (d > 0) != (rec > 0) and d != 0: changes.append(tag)
    L.append("  C4 sign changes under the certified frame: %s" % (changes or "none"))
    return L, changes


def score_predictions(c1, stats, c2, changes):
    hf = lambda b: "HELD" if b else "FAILED"
    out = [("P1", hf(c1 == "HELD"), "P1 %s: C1 %s (registered: HELD, 57 / 0)" % (hf(c1 == "HELD"), c1))]
    for pid, fam in (("P2", (MMLU, MISTRAL)), ("P3", (MMLU, GROK)), ("P4", (BFCL, GROK))):
        want, (lo, hi) = FAMILY_PRED[fam]; st = stats.get(fam)
        if st is None or st["n"] == 0:
            out.append((pid, "FAILED", "%s FAILED: family %s/%s absent or without flips" % (pid, *fam))); continue
        in_band = lo <= st["s"] <= hi
        if pid == "P4":
            ok = in_band      # ruling (3): scored on the POINT only; the "FIRST-SIDED if SUPPORTED" clause is not read
            txt = ("s %.3f in [%.2f, %.2f]: %s (scored on the point only; the sidedness clause is not read, the family being %s for C2)"
                   % (st["s"], lo, hi, in_band, st["support"]))
        else:
            ok = in_band and st["side"] == want
            txt = "s %.3f [%.3f, %.3f] %s (registered %s, s in [%.2f, %.2f])" % (st["s"], st["lo"], st["hi"], st["side"], want, lo, hi)
        out.append((pid, hf(ok), "%s %s: %s/%s %s" % (pid, hf(ok), fam[0], fam[1], txt)))
    gro = [st["side"] for f, st in stats.items() if f[1] == GROK and st["support"] == "SUPPORTED"]
    mis = [st["side"] for f, st in stats.items() if f[1] == MISTRAL and st["support"] == "SUPPORTED"]
    ok5 = c2 == "HELD" and gro and mis and all(s == "FIRST-SIDED" for s in gro) and all(s == "SECOND-SIDED" for s in mis)
    out.append(("P5", hf(ok5), "P5 %s: C2 %s; supported grok families %s, Mistral families %s (registered: C2 HELD, grok first, Mistral second)" % (hf(ok5), c2, gro, mis)))
    out.append(("P6", "EVENT" if changes else "NO EVENT", "P6 (a probability, not a verdict; registered 0.3): a C4 prior readout changed SIGN under the certified frame: %s"
                % (("YES: %s" % changes) if changes else "NO")))
    return out


def falsifier_lines(c1, c2, changes):
    L = []
    L.append("FALSIFIER C2: %s" % ("FIRED: a supported family is UNRESOLVED, which overturns the reading that BFCL's one-sided flip composition reflects a "
                                   "GENERAL property of dual-order judging; BFCL-FLIP-RESEED stays SEPARATING" if c2 == "FAILED" else
                                   "not fired (C2 %s)" % c2))
    L.append("FALSIFIER C1: %s" % ("FIRED: the recorded BFCL flip table (57 / 0) rests on a frame error and is re-read by insertion before any BFCL launch"
                                   if c1 == "FAILED" else "not fired (C1 HELD)"))
    L.append("FALSIFIER C4: %s" % (("FIRED: the DIRECTION of %s is overturned by insertion; magnitudes and boards are re-read separately" % changes) if changes
                                   else "not fired (no sign change)"))
    L.append("NOT OVERTURNED EITHER WAY: ORDER-1's and SELECTIVE-ORDER's verdicts (dual order stays), POSITION-DECOMP's magnitude, any board, profile or "
             "tier, the canary floor.")
    return L


def reseed_line(c1, c2):
    if c1 == "FAILED":
        return ("BFCL-FLIP-RESEED (stated dependency, NOT a gate): C1 FAILED, so the premise of its 57 / 0 table is re-read by insertion BEFORE any "
                "BFCL launch; nothing in its criteria changes here.")
    if c2 == "HELD":
        return ("BFCL-FLIP-RESEED (stated dependency, NOT a gate): C2 HELD, one-sided flip composition is GENERAL across the supported families, so "
                "its C1 HELD would be CONFIRMATORY rather than separating and the author may prefer not to buy its 200 calls; the launch decision is "
                "the author's and the experiment-manager's; nothing in either registration's criteria changes.")
    if c2 == "FAILED":
        return ("BFCL-FLIP-RESEED (stated dependency, NOT a gate): C2 FAILED, one-sided composition is NOT general, so its C1 stays SEPARATING; the "
                "launch decision is the author's and the experiment-manager's; nothing in either registration's criteria changes.")
    return ("BFCL-FLIP-RESEED (stated dependency, NOT a gate): C2 UNDETERMINED, so this index makes it neither confirmatory nor separating; the "
            "launch decision rests on its own grounds (the author's and the experiment-manager's); nothing in either registration's criteria changes.")


# ── the modes ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def family_table(stats, say):
    say("FAMILY TABLE (C5): family | FF SS n | clusters | Kish | s | interval of record (+-1.96 SE_boot) | exact binomial | DEFF measured | "
        "MDE | support | side")
    for fam in sorted(stats):
        st = stats[fam]
        say("  %-14s %-28s FF %4d SS %4d n %4d | clusters %4d | Kish %.3f | s %s | [%.3f, %.3f] SE %.4f | CP [%.3f, %.3f] | DEFF %s | MDE %s | %s | %s"
            % (fam[0], fam[1], st["FF"], st["SS"], st["n"], st["clusters"], st["kish"] if st["n"] else float("nan"),
               ("%.3f" % st["s"]) if st["n"] else "undefined", st["lo"], st["hi"], st["se"], st["cp"][0], st["cp"][1],
               ("%.2f" % st["deff"]) if st["deff"] is not None else "UNDEFINED", ("%.3f" % st["mde"]) if st["mde"] is not None else "-", st["support"], st["side"]))
        if st["deff_undefined"]:
            say("      measured DEFF UNDEFINED (0/0 at s = %.3f): support %s FOR C2 (%s); beside, deciding nothing: Kish (rho = 1) bound MDE %.3f"
                % (st["s"], st["support"], st["support_reason"], st["mde_kish"]))
        for c, (a, b) in sorted(st["per_cache"].items()):
            say("      per cache %-70s FF %4d SS %4d s %s" % (c, a, b, ("%.3f" % (a / (a + b))) if a + b else "undefined"))


def dry_run(root=None, fmap=None, pool_check=True, cert_pin=None):
    root = root or DATA_ROOT; fmap = fmap or FAMILY_MAP
    say = lambda s: print(s, flush=True)
    cert, csha = load_cert(root, cert_pin)
    entered, excluded = plan(cert, fmap)
    verify_pools(entered, say, pool_check, root)
    lf, crlf = vfc.script_shas(__file__)
    say("=== %s --dry-run (zero calls; writes nothing) | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) ===" % (TEST, lf, crlf))
    say("[CERT] %s: %s (sha256_16 %s; certificate script LF %s)" % (CERT_JSON.replace("\\", "/"), cert["certificate"], csha, cert.get("script_sha256_16_lf")))
    say("ENTERED %d caches:" % len(entered))
    for e in entered: say("  %s -> %s | tables %s%s" % (e["cache"]["path"], e["spec"], [u["table"] for u in e["units"]], (" | skipped %s" % e["skipped"]) if e["skipped"] else ""))
    say("EXCLUDED %d caches:" % len(excluded))
    for p, why in excluded: say("  %s: %s" % (p, why))
    recs, notes = extract(root, entered, say)
    for p, ns in notes.items():
        for n in ns: say("  [NOTE] %s: %s" % (p, n))
    family_table(family_stats(recs, B=200), say)
    say("[DRY-RUN] the bootstrap above used B = 200 for speed; the run uses B = %d, seed %d" % (B, SEED))
    return 0


def analyze(root=None, fmap=None, pool_check=True, out_path=None, eval_db=None, expected_c1=BFCL_C1, cert_pin=None):
    root = root or DATA_ROOT; fmap = fmap or FAMILY_MAP
    out = out_path or os.path.join(root, OUT)
    if os.path.exists(out):
        raise SystemExit("[WRITE-ONCE] REFUSED: %s exists; the outcome of record is never rewritten" % vfc.rel(out, root))
    L = []
    def say(s):
        L.append(s); print(s, flush=True)
    cert, csha = load_cert(root, cert_pin)
    entered, excluded = plan(cert, fmap)
    verify_pools(entered, say, pool_check, root)
    lf, crlf = vfc.script_shas(__file__)
    say("=== %s (zero calls) | registration %s | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) ===" % (TEST, REGISTRATION, lf, crlf))
    say("[CERT] %s: %s (sha256_16 %s; certificate script LF %s); caches entered %d, excluded %d" % (CERT_JSON.replace("\\", "/"), cert["certificate"], csha,
        cert.get("script_sha256_16_lf"), len(entered), len(excluded)))
    recs, notes = extract(root, entered, say)
    stats = family_stats(recs)
    say("")
    say("(C5) COUNTS")
    cls = Counter(c["klass"] for c in cert["caches"])
    say("  caches enumerated by the certificate %d (%s); entered %d; excluded %d" % (len(cert["caches"]), dict(cls), len(entered), len(excluded)))
    for p, why in excluded: say("    excluded %s: %s" % (p, why))
    for e in entered: say("    entered %s -> %s (%s) tables %s" % (e["cache"]["path"], e["spec"].get("corpus") or e["spec"].get("corpus_col"),
                                                                   e["spec"].get("judge") or e["spec"].get("judge_col") or e["spec"].get("judge_meta"),
                                                                   [u["table"] for u in e["units"]]))
    for p, ns in notes.items():
        for n in ns: say("    [NOTE] %s: %s" % (p, n))
    ecomb = [(e["cache"]["path"], u["table"], (u.get("combiner_check") or {}).get("pin")) for e in entered for u in e["units"] if u.get("evidence") == "E-COMB"]
    say("  E-COMB-CERTIFIED entered tables (no raw text; certified on a SOURCE-VERIFIED combiner, ruling H3 0104e44): %d %s"
        % (len(ecomb), ["%s:%s (writer blob %s)" % (p, t, (pin or "?")[:12]) for p, t, pin in ecomb]))
    family_table(stats, say)
    say("")
    say("(C1) THE BFCL PARENT, ROW LEVEL")
    c1, c1l = c1_eval(recs, expected_c1)
    bst = stats.get((BFCL, GROK))
    say("  " + c1l + ((" | beside: s %.3f, clusters %d, Kish %.3f, DEFF %s, support %s" % (bst["s"], bst["clusters"], bst["kish"],
        ("%.2f" % bst["deff"]) if bst["deff"] is not None else "UNDEFINED", "%s for C2 (%s)" % (bst["support"], bst["support_reason"]))) if bst and bst["n"] else ""))
    say("")
    say("(C2) GENERALITY (support condition first)")
    c2, why, desc, cons = c2_verdict(stats)
    say("  C2 %s (PRIMARY, the supported families only): %s" % (c2, why))
    if cons: say("  " + cons)
    if desc: say("  " + desc)
    for fam, st in sorted(stats.items()):
        say("    %s/%s: support %s (%s; n_eff %s) | side %s" % (fam[0], fam[1], st["support"], st["support_reason"],
            ("%.1f" % (st["n"] / st["deff"])) if st["deff"] else "-", st["side"]))
    say("")
    say("(C3) DIRECTION BY JUDGE, DESCRIPTIVE")
    for l in c3_lines(stats): say(l)
    say("")
    say("(C4) CROSS-READS OF PRIOR POSITION READOUTS, DESCRIPTIVE")
    c4L, changes = c4_lines(recs, root, eval_db)
    for l in c4L: say(l)
    say("")
    say("PREDICTIONS")
    for _, _, l in score_predictions(c1, stats, c2, changes): say("  " + l)
    say("")
    for l in falsifier_lines(c1, c2, changes): say(l)
    say(reseed_line(c1, c2))
    say("WHAT THIS RUN WILL NOT SHOW: why a judge prefers a position; per-match stability (BFCL-FLIP-RESEED's question; this index is MARGINAL); "
        "anything on caches the certificate excludes; any fidelity number; a recommendation to judge in one order.")
    with open(out, "x", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    print("[WRITTEN] %s (write-once)" % vfc.rel(out, root), flush=True)
    return dict(c1=c1, c2=c2, stats=stats, changes=changes, text="\n".join(L))


# ── selftest ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _votes_for(ff, ss, a_wins, b_wins, ties=5):
    """Positional vote pairs with KNOWN both-decisive flips (FF, SS) and agreements (contestant a wins: (A, B); b wins: (B, A))."""
    return [("Model A", "Model A")] * ff + [("Model B", "Model B")] * ss + [("Model A", "Model B")] * a_wins + [("Model B", "Model A")] * b_wins + \
           [("TIE", "Model A")] * ties


def _wide_cache(path, votes, transposed, q0, source=None):
    ddl = ("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, %s qid INTEGER, model_a TEXT, model_b TEXT, vote1 TEXT, vote2_raw TEXT, winner TEXT, "
           "flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT); CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT);" % ("source TEXT," if source else ""))
    con = sqlite3.connect(path); con.executescript(ddl)
    for i, (p1, p2) in enumerate(votes):
        s2 = vfc.T(p2) if transposed else p2
        w, f, inv = vfc.combine_contestant(p1, s2) if transposed else rj.combine_orders(p1, s2)
        row = [i] + ([source] if source else []) + [q0 + i // 3, "ma", "mb", p1, s2, w, int(f), int(inv), vfc._raw(p1), vfc._raw(p2)]
        con.execute("INSERT INTO verdicts VALUES (%s)" % ",".join("?" * len(row)), row)
    con.commit(); con.close()


def _bfcl_cache(path, votes):
    con = sqlite3.connect(path)
    con.executescript("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, stratum TEXT, task_id TEXT, agent_a TEXT, agent_b TEXT, nj TEXT);"
                      "CREATE TABLE verdicts (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, finish TEXT, PRIMARY KEY (mid, arm));"
                      "CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT); INSERT INTO run_meta VALUES ('pool_id', 'p2035adddedd1becb');"
                      "INSERT INTO run_meta VALUES ('judge_model', 'grok-4-1-fast-non-reasoning');")
    for i, (p1, p2) in enumerate(votes):
        con.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?)", (i, "headline", "t%d" % (i % 25), "a", "b", ""))
        con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?)", (i, "fwd", p1, 0.8, 0, vfc._raw(p1), "stop"))
        con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?)", (i, "rev", p2, 0.8, 0, vfc._raw(p2), "stop"))
    con.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?)", (9999, "headline", "tx", "a", "b", "NON_TERMINATED"))   # an nj match: not deciding
    con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?)", (9999, "fwd", "Model B", 0.8, 0, vfc._raw("Model B"), "stop"))
    con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?)", (9999, "rev", "Model B", 0.8, 0, vfc._raw("Model B"), "stop"))
    con.commit(); con.close()


def selftest():
    tmp = tempfile.mkdtemp(prefix="pia_selftest_")
    ok = True; lines = []
    def check(cond, what):
        nonlocal ok
        lines.append("  [%s] %s" % ("PASS" if cond else "FAIL", what)); ok = ok and bool(cond)
    try:
        with vfc.connect_trap(tmp):
            er = os.path.join(tmp, "experiment_results"); os.makedirs(os.path.join(er, "m"), exist_ok=True); os.makedirs(os.path.join(er, "agent"))
            # KNOWN s: MMLU-Pro family, s = 0.75 in two caches of opposite storage frames (positional / transposed), same votes
            V = _votes_for(30, 10, a_wins=10, b_wins=30)
            _wide_cache(os.path.join(er, "m", "pos.db"), V, False, 0)
            _wide_cache(os.path.join(er, "m", "trans.db"), V, True, 1000)
            # a second corpus: MATH (s = 0.20, clearly second-sided) and an IFEval family that is UNRESOLVED (s = 0.5)
            _wide_cache(os.path.join(er, "m", "math.db"), _votes_for(20, 80, 5, 5), False, 5000, source="MATH")
            _wide_cache(os.path.join(er, "m", "ifeval.db"), _votes_for(40, 40, 5, 5), False, 7000, source="IFEVAL")
            # a MIXED cache (one order-1 row mis-stored) mapped in the family map: plan() must exclude it by class (review M3)
            _wide_cache(os.path.join(er, "m", "mixed.db"), _votes_for(30, 10, 10, 30), False, 9000)
            cm = sqlite3.connect(os.path.join(er, "m", "mixed.db")); cm.execute("UPDATE verdicts SET vote1 = 'Model B' WHERE match_id = 0 AND vote1 = 'Model A'")
            cm.commit(); cm.close()
            ra = sqlite3.connect(os.path.join(er, "m", "rawonly.db"))
            ra.executescript("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, qid INTEGER, model_a TEXT, model_b TEXT, winner TEXT, flip INTEGER, raw1 TEXT, raw2 TEXT);")
            for i, (p1, p2) in enumerate(_votes_for(30, 10, 10, 30)):
                w_, f_, _ = vfc.combine_contestant(p1, p2)
                ra.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?,?)", (i, 11000 + i, "ma", "mb", w_, int(f_), vfc._raw(p1), vfc._raw(p2)))
            ra.commit(); ra.close()
            _bfcl_cache(os.path.join(er, "agent", "bfcl_judged_pilot.db"), _votes_for(12, 0, 20, 20))
            # C4 fixtures at the paths of record: an x12all-like Mistral cache (AGREE rows first-heavy: a SIGN CHANGE against the record) and an
            # arena13-like name-labelled cache (frontier: second > first, a sign change; cross-tier: second < first, as recorded)
            x12d = os.path.join(tmp, X12); os.makedirs(x12d, exist_ok=True)
            VX = _votes_for(30, 10, 40, 40)
            _wide_cache(os.path.join(x12d, "stack_v2_promptv2_x12all.db"), VX, False, 20000)
            ev = sqlite3.connect(os.path.join(tmp, "eval_fixture.db")); ev.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, pred TEXT)")
            for i in range(len(VX)):
                q = 20000 + i // 3
                ev.execute("INSERT INTO eval_results VALUES (?,?,?)", (q, "ma", "C")); ev.execute("INSERT INTO eval_results VALUES (?,?,?)", (q, "mb", "C" if i < 40 else "D"))
            ev.commit(); ev.close()
            new = vfc.source_constant("arena13.py", "NEW")
            a13 = sqlite3.connect(os.path.join(x12d, "arena13.db"))
            a13.executescript("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, qid INTEGER, opponent TEXT, anchor TEXT, frontier INTEGER);"
                              "CREATE TABLE verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm));")
            # frontier: new wins 30% first (ensemble A), 70% second (reversed B); cross-tier: 60% first, 40% second
            for i in range(200):
                fr = int(i < 100); opp = "opp%d" % (i % 3); k = i % 100
                w1 = "Model A" if k < (30 if fr else 60) else "Model B"
                w2 = "Model B" if (k * 7) % 100 < (70 if fr else 40) else "Model A"
                a13.execute("INSERT INTO schedule VALUES (?,?,?,?,?)", (i, 30000 + i, opp, "Law", fr))
                a13.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", (i, "ensemble", {"Model A": new, "Model B": opp}[w1], 0, vfc._raw(w1), 0.0))
                a13.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", (i, "reversed", {"Model A": opp, "Model B": new}[w2], 0, vfc._raw(w2), 0.0))
            a13.commit(); a13.close()
            # D8: a two-table cache (a WIDE verdicts table AND a LONG judge_calls table, BOTH with a judge column): one table may enter
            kd = os.path.join(er, "k"); os.makedirs(kd, exist_ok=True); kp = os.path.join(kd, "kotlin_fixture.db")
            kc = sqlite3.connect(kp)
            kc.executescript("CREATE TABLE judge_calls (id INTEGER PRIMARY KEY AUTOINCREMENT, snapshot_id TEXT, eval_question_id INTEGER, model_a TEXT, "
                             "model_b TEXT, presentation_order INTEGER, judge_model TEXT, raw_content TEXT, parsed_winner TEXT, finish_reason TEXT);"
                             "CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, eval_question_id INTEGER, model_a TEXT, model_b TEXT, judge_model TEXT, "
                             "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT);")
            for i, (p1, p2) in enumerate(_votes_for(10, 5, 5, 5)):
                kc.execute("INSERT INTO judge_calls VALUES (NULL,'s',?,'ma','mb',1,'jk',?,?,'stop')", (40000 + i, vfc._raw(p1), p1))
                kc.execute("INSERT INTO judge_calls VALUES (NULL,'s',?,'ma','mb',2,'jk',?,?,'stop')", (40000 + i, vfc._raw(p2), p2))
                w_, f_, v_ = rj.combine_orders(p1, p2)
                kc.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (i, 40000 + i, "ma", "mb", "jk", p1, p2, w_, int(f_), int(v_), vfc._raw(p1), vfc._raw(p2)))
            kc.commit(); kc.close()
            # D4: judge_calls rows WITHOUT a judge (the silent drop D8 described): 3 of 10 matches carry no judge_model
            kn_ = sqlite3.connect(os.path.join(kd, "kotlin_nojudge.db"))
            kn_.executescript("CREATE TABLE judge_calls (id INTEGER PRIMARY KEY AUTOINCREMENT, snapshot_id TEXT, eval_question_id INTEGER, model_a TEXT, "
                              "model_b TEXT, presentation_order INTEGER, judge_model TEXT, raw_content TEXT, parsed_winner TEXT, finish_reason TEXT);")
            for i, (p1, p2) in enumerate(_votes_for(4, 2, 2, 2, ties=0)):
                jm = None if i < 3 else "jn"
                kn_.execute("INSERT INTO judge_calls VALUES (NULL,'s',?,'ma','mb',1,?,?,?,'stop')", (60000 + i, jm, vfc._raw(p1), p1))
                kn_.execute("INSERT INTO judge_calls VALUES (NULL,'s',?,'ma','mb',2,?,?,?,'stop')", (60000 + i, jm, vfc._raw(p2), p2))
            kn_.commit(); kn_.close()
            # D4 and item 5.2: an arena13-like name-labelled cache with UNPAIRED arms (selfref, t0a), every paired label resolvable (x12u), and its
            # twin with 4 unresolvable reversed labels (x12r): UNCERTIFIABLE (R6) under VFC-RX-RULING R-2, so never entered; the reader refuses it (R-8)
            for sub, n_unres in (("x12u", 0), ("x12r", 4)):
                ud = os.path.join(er, sub); os.makedirs(ud, exist_ok=True)
                uc = sqlite3.connect(os.path.join(ud, "arena13.db"))
                uc.executescript("CREATE TABLE schedule (mid INTEGER PRIMARY KEY, qid INTEGER, opponent TEXT, anchor TEXT, frontier INTEGER);"
                                 "CREATE TABLE verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm));")
                for i in range(30):
                    w1 = "Model A" if i % 3 else "Model B"; w2 = "Model A" if i % 2 else "Model B"
                    uc.execute("INSERT INTO schedule VALUES (?,?,?,?,?)", (i, 50000 + i, "oppu", "Law", 1))
                    uc.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", (i, "ensemble", {"Model A": new, "Model B": "oppu"}[w1], 0, vfc._raw(w1), 0.0))
                    lab2 = "stranger" if i < n_unres else {"Model A": "oppu", "Model B": new}[w2]
                    uc.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", (i, "reversed", lab2, 0, vfc._raw(w2), 0.0))
                    for arm in ("selfref", "t0a"):
                        uc.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", (i, arm, {"Model A": new, "Model B": "oppu"}[w1], 0, vfc._raw(w1), 0.0))
                uc.commit(); uc.close()
            steward = os.path.join(tmp, "steward.txt")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                files, _, listing = vfc.enumerate_caches(tmp, lambda s: None)
                with open(steward, "w") as f: f.write("\n".join(vfc.rel(p, tmp) for p, _ in listing))
                cert = vfc.run(steward, root=tmp, selftest_ok=True)
            check(cert["certificate"] == "HELD" and {c["path"]: c["klass"] for c in cert["caches"]}["experiment_results/m/trans.db"] == "CERTIFIED-CONTESTANT",
                  "fixture certificate HELD; the transposed cache is CERTIFIED-CONTESTANT")
            fm = {"experiment_results/m/pos.db": dict(corpus=MMLU, judge=GROK), "experiment_results/m/trans.db": dict(corpus=MMLU, judge=MISTRAL),
                  "experiment_results/m/math.db": dict(corpus_col="source", corpus_values={"MATH": MATH, "IFEVAL": IFEVAL}, judge=GROK),
                  "experiment_results/m/ifeval.db": dict(corpus_col="source", corpus_values={"MATH": MATH, "IFEVAL": IFEVAL}, judge=GROK),
                  "experiment_results/agent/bfcl_judged_pilot.db": dict(corpus=BFCL, judge=GROK, subset="bfcl_deciding", tables=("verdicts",)),
                  X12 + "stack_v2_promptv2_x12all.db": dict(corpus=MMLU, judge=GROKR), X12 + "arena13.db": dict(corpus=MMLU, judge=DSR1),   # own families: C4 reads them by path
                  "experiment_results/m/mixed.db": dict(corpus=MMLU, judge=GROK), "experiment_results/m/rawonly.db": dict(corpus=MMLU, judge=GROK),
                  "experiment_results/k/kotlin_fixture.db": dict(corpus=MMLU, judge_col="judge_model", tables=("judge_calls",)),
                  "experiment_results/k/kotlin_nojudge.db": dict(corpus=MMLU, judge_col="judge_model", tables=("judge_calls",)),
                  "experiment_results/x12u/arena13.db": dict(corpus=MMLU, judge="judge-unres"),
                  "experiment_results/x12r/arena13.db": dict(corpus=MMLU, judge="judge-r6")}
            entered, excluded = plan(cert, fm)
            check(("experiment_results/m/mixed.db", "class MIXED") in excluded and all(e["cache"]["path"] != "experiment_results/m/mixed.db" for e in entered),
                  "plan() EXCLUDES a MIXED cache that the family map assigns (excluded: %s)" % [x for x in excluded if "mixed" in x[0]])
            ke = [x for x in entered if x["cache"]["path"] == "experiment_results/k/kotlin_fixture.db"]
            kcert = {u["table"]: u["klass"] for c in cert["caches"] if c["path"] == "experiment_results/k/kotlin_fixture.db" for u in c["units"]}
            check(kcert == {"judge_calls": "CERTIFIED-POSITIONAL", "verdicts": "CERTIFIED-POSITIONAL"} and len(ke) == 1
                  and [u["table"] for u in ke[0]["units"]] == ["judge_calls"] and ke[0]["skipped"] == [("verdicts", "CERTIFIED-POSITIONAL")],
                  "D8: a two-table cache with BOTH tables certified and BOTH carrying a judge column enters ONE table only (judge_calls; verdicts skipped)")
            both, _ = plan(cert, {"experiment_results/k/kotlin_fixture.db": dict(corpus=MMLU, judge_col="judge_model")})
            check(sorted(u["table"] for u in both[0]["units"]) == ["judge_calls", "verdicts"],
                  "D8: without the restriction BOTH tables would enter (the double count the restriction prevents)")
            check(all(FAMILY_MAP[k].get("tables") == ("judge_calls",) for k in ("experiment_results/judge_wiring/board/kotlin_c0d3f708cbc3930e.db",
                                                                                "experiment_results/judge_wiring/kotlin_ae92da306544f453.db")),
                  "D8: FAMILY_MAP restricts both Kotlin caches of record to judge_calls")
            check(("experiment_results/m/rawonly.db", "class MIXED") in excluded,
                  "B2 through the index: a raw-only cache whose combiner did not transpose is MIXED and excluded, never entered transposed")
            mc = [c for c in cert["caches"] if c["path"] == "experiment_results/m/mixed.db"][0]
            cmx = vfc.open_ro(os.path.join(tmp, mc["path"])); rr_ = False
            try: vfc.unit_votes(cmx, os.path.join(tmp, mc["path"]), mc["units"][0])
            except SystemExit as e: rr_ = "[FRAME]" in str(e) and "only a CERTIFIED unit is read" in str(e)
            finally: cmx.close()
            check(rr_, "the index's reader REFUSES the MIXED unit even if it were handed one")
            recs, notes = extract(tmp, entered, lambda s: None, maps={})
            st = family_stats(recs, B=300)
            kr = [r for r in recs if r["cache"] == "experiment_results/k/kotlin_fixture.db"]
            check(len(kr) == 30 and {r["table"] for r in kr} == {"judge_calls"},
                  "D8: the two-table fixture contributes its 30 matches ONCE (judge_calls only), not 60")
            ue = [x for x in entered if x["cache"]["path"] == "experiment_results/x12u/arena13.db"][0]
            utc = ue["table_counts"]["verdicts"]
            ur = [r for r in recs if r["cache"] == "experiment_results/x12u/arena13.db"]
            check(utc["readable"] == 30 and utc["dropped_unresolved"] == 0 and utc["read"] == 30 and utc["entered"] == 30 and len(ur) == 30
                  and any("[COUNTS] verdicts: 30 matches read of 30 readable (dropped for an unresolved label 0)" in n
                          for n in notes["experiment_results/x12u/arena13.db"]),
                  "D4: the per-table [COUNTS] line on a name-labelled cache (30 read of 30 readable, dropped for an unresolved label 0, ENTERED 30)")
            rc_ = [c for c in cert["caches"] if c["path"] == "experiment_results/x12r/arena13.db"][0]
            rv_ = [u for u in rc_["units"] if u["table"] == "verdicts"][0]
            check(rc_["klass"] == "UNCERTIFIABLE" and rv_.get("uncert_reason") == "R6" and rv_["counts"]["unresolvable_labels"] == 4
                  and ("experiment_results/x12r/arena13.db", "class UNCERTIFIABLE") in excluded and not any(e["cache"]["path"] == rc_["path"] for e in entered),
                  "R-2 / R-5 through the index: the twin with 4 unresolvable labels is UNCERTIFIABLE (R6) in the certificate and EXCLUDED by class, never entered")
            crx = vfc.open_ro(os.path.join(tmp, rc_["path"])); r8 = ""
            try: vfc.unit_votes(crx, os.path.join(tmp, rc_["path"]), dict(rv_, klass=rv_["resolved_klass"]))
            except SystemExit as e: r8 = str(e)
            finally: crx.close()
            check("[FRAME] REFUSED (R-8)" in r8 and "key 0" in r8,
                  "R-8 through the index's reader: handed that unit as %s, vfc.unit_votes REFUSES on the first unresolvable key (never a silent drop): %s"
                  % (rv_["resolved_klass"], r8[:90]))
            check({r["row"].get("arm") for r in ur} == {"ensemble"} and {r["row"].get("_o2_arm") for r in ur} == {"reversed"}
                  and ue["units"][0]["unpaired"] == {"selfref": 30, "t0a": 30},
                  "5.2: arena13 enters ONLY as its (ensemble, reversed) pair; the unpaired selfref / t0a arms (30 each) are never read as orders")
            njc = [x for x in entered if x["cache"]["path"] == "experiment_results/k/kotlin_nojudge.db"][0]["table_counts"]["judge_calls"]
            check(njc["no_corpus_or_judge"] == 3 and njc["entered"] == 7 and any("without a corpus or judge 3 | ENTERED 7" in n
                                                                                  for n in notes["experiment_results/k/kotlin_nojudge.db"]),
                  "D4: matches dropped for a missing judge are COUNTED and printed (3 without a judge, 7 entered)")
            kn = [n for n in notes["experiment_results/k/kotlin_fixture.db"] if n.startswith("[COUNTS]")]
            check(kn == ["[COUNTS] judge_calls: 30 matches read of 30 readable (dropped for an unresolved label 0) | outside the subset 0 | without a corpus "
                         "or judge 0 | ENTERED 30"], "D4: a per-table [COUNTS] line is printed for every entered table: %s" % kn)
            check(abs(st[(MMLU, GROK)]["s"] - 0.75) < 1e-12 and abs(st[(MMLU, MISTRAL)]["s"] - 0.75) < 1e-12,
                  "SAME s once the certificate's transposition is applied: positional cache %.3f, transposed cache %.3f (truth 0.750)"
                  % (st[(MMLU, GROK)]["s"], st[(MMLU, MISTRAL)]["s"]))
            # withhold the transposition: treat the contestant cache as positional -> s becomes 1 - s by construction (agreements read as flips)
            cert_w = json.loads(json.dumps(cert))
            for c in cert_w["caches"]:
                if c["path"].endswith("trans.db"):
                    c["klass"] = "CERTIFIED-POSITIONAL"
                    for u in c["units"]: u["klass"] = "CERTIFIED-POSITIONAL"
            ew, _ = plan(cert_w, {"experiment_results/m/trans.db": fm["experiment_results/m/trans.db"]})
            rw, _ = extract(tmp, ew, lambda s: None, maps={})
            sw = family_stats(rw, B=50)[(MMLU, MISTRAL)]["s"]
            check(abs(sw - 0.25) < 1e-12, "OPPOSITE s when the transposition is WITHHELD: %.3f = 1 - 0.750 (the sign error the certificate exists to catch)" % sw)
            # C1 both branches on the BFCL-like fixture (12 / 0 on 57 deciding matches; the nj match excluded)
            v, l = c1_eval(recs, dict(n=57, FF=12, SS=0)); check(v == "HELD", "C1 HELD branch (57 deciding: 12 FF + 20 + 20 agreements + 5 ties; the nj match excluded): " + l)
            v, l = c1_eval(recs, BFCL_C1); check(v == "FAILED", "C1 FAILED branch: " + l)
            b = st[(BFCL, GROK)]
            check(b["s"] == 1.0 and b["support"] == "UNSUPPORTED" and b["deff"] is None and "transported MDE" in b["support_reason"],
                  "s = 1.000 -> measured DEFF UNDEFINED; UNSUPPORTED FOR C2 (%s)" % b["support_reason"])
            sv = support_of((BFCL, GROK), 57, 1.0, None, None)
            check(sv[0] == "UNSUPPORTED" and "0.352 > 0.35" in sv[1], "the registered case: 57 flips at s = 1.000 -> %s (%s)" % sv)
            DEFF_TRANSPORTED[("X", "j")] = 3.60
            try: sv2 = support_of(("X", "j"), 200, 1.0, None, None)
            finally: del DEFF_TRANSPORTED[("X", "j")]
            check(sv2[0] == "SUPPORTED", "general rule: undefined DEFF with a transported MDE <= 0.35 -> SUPPORTED (a non-BFCL family; %s)" % sv2[1])
            DEFF_TRANSPORTED[("X", "j")] = 3.60
            try: sv2b = support_of(("X", "j"), 57, 1.0, None, None)
            finally: del DEFF_TRANSPORTED[("X", "j")]
            check(sv2b[0] == "UNSUPPORTED" and "0.352 > 0.35" in sv2b[1], "general rule: undefined DEFF with a transported MDE > 0.35 -> UNSUPPORTED (%s)" % sv2b[1])
            sb58 = support_of((BFCL, GROK), 58, 1.0, None, None); sb200 = support_of((BFCL, GROK), 200, 0.8, 1.0, 0.1)
            check(sb58[0] == "UNSUPPORTED" and sb200[0] == "UNSUPPORTED" and "ruling (3)" in sb58[1] and "(SUPPORTED)" in sb200[1],
                  "support_of NEVER returns SUPPORTED for BFCL, even where its data would be supported (58 flips: %s)" % sb58[1])
            for ffb, ssb in ((58, 0), (57, 1)):
                rb = [dict(family=(BFCL, GROK), cluster=(BFCL, "t%d" % (i % 49)), p1=("Model A" if i < ffb else "Model B"), p2=("Model A" if i < ffb else "Model B"),
                           cache="b") for i in range(ffb + ssb)]
                rb += [dict(family=(MMLU, GROK), cluster=(MMLU, str(i)), p1=("Model A" if i < 300 else "Model B"), p2=("Model A" if i < 300 else "Model B"),
                            cache="m") for i in range(400)]
                sb = family_stats(rb, B=300); vb = c2_verdict(sb)
                check(sb[(BFCL, GROK)]["support"] == "UNSUPPORTED" and "PREMISE DIFFERS" in sb[(BFCL, GROK)]["support_reason"] and vb[0] == "UNDETERMINED"
                      and vb[3] and vb[2] and "decides nothing" in vb[2],
                      "BFCL at %d FF / %d SS (H1): UNSUPPORTED for C2, PREMISE DIFFERS printed, C2 PRIMARY UNDETERMINED (MMLU-Pro alone), with-BFCL reading "
                      "descriptive: %s" % (ffb, ssb, vb[2][:90]))
            # M2: the pool checks, both branches, by execution (an injected guard; the p2035 id file copied into the temp root)
            os.makedirs(os.path.join(tmp, "experiment_configs"), exist_ok=True)
            idsrc = os.path.join(ROOT, BFCL_ID_FILE); iddst = os.path.join(tmp, BFCL_ID_FILE)
            shutil.copyfile(idsrc, iddst)
            called = []
            eb = [dict(cache=dict(path="b", pools=["pool_id=p2035adddedd1becb"]), spec=dict(corpus=BFCL)),
                  dict(cache=dict(path="m", pools=["pool_id=p2dca21ab5f4ef3ae"]), spec=dict(corpus=MMLU))]
            verify_pools(eb, lambda x: None, pool_check=True, root=tmp, guard=called.append)
            check(called == ["p2dca21ab5f4ef3ae"], "pool check ADMIT branch: assert_pool_of_record invoked for p2dca (%s); p2035 re-derived over 228 ids" % called)
            def raising(x): raise SystemExit("[POOL-GUARD] stub refusal for %s" % x)
            pr1 = False
            try: verify_pools(eb, lambda x: None, pool_check=True, root=tmp, guard=raising)
            except SystemExit as e: pr1 = "[POOL-GUARD] stub refusal for p2dca21ab5f4ef3ae" in str(e)
            d = json.load(open(iddst, encoding="utf-8")); k0 = sorted(d)[0]; d[k0] = d[k0][1:]; json.dump(d, open(iddst, "w"))
            pr2 = False
            try: verify_pools(eb[:1], lambda x: None, pool_check=True, root=tmp, guard=called.append)
            except SystemExit as e: pr2 = "hashes to" in str(e)
            pr3 = False
            try: verify_pools([dict(cache=dict(path="b", pools=[]), spec=dict(corpus=BFCL))], lambda x: None, pool_check=True, root=tmp, guard=called.append)
            except SystemExit as e: pr3 = "enters without" in str(e)
            check(pr1 and pr2 and pr3, "pool check REFUSE branches: a guard refusal propagates (%s); an id file one id short refuses p2035 (%s); a BFCL cache "
                  "without p2035 in its run_meta refuses (%s)" % (pr1, pr2, pr3))
            sv3 = support_of((MATH, GROK), 500, 1.0, None, None)
            check(sv3[0] == "UNSUPPORTED" and "no transported DEFF" in sv3[1], "undefined DEFF and no transported DEFF -> UNSUPPORTED (%s)" % sv3[1])
            check(support_of((MMLU, GROK), 400, 0.6, 1.2, 2.8 * 0.5 * math.sqrt(1.2 / 400))[0] == "SUPPORTED" and
                  support_of((MMLU, GROK), 10, 0.6, 1.2, 2.8 * 0.5 * math.sqrt(1.2 / 10))[0] == "UNSUPPORTED", "measured DEFF: SUPPORTED and UNSUPPORTED branches")
            # C2: every branch of the evaluation order
            check(c2_rule({(MMLU, GROK): "FIRST-SIDED"})[0] == "UNDETERMINED", "C2 UNDETERMINED by support (one corpus)")
            check(c2_rule({(MMLU, GROK): "FIRST-SIDED", (MATH, GROK): "SECOND-SIDED"})[0] == "HELD", "C2 HELD (two corpora, both sided)")
            check(c2_rule({(MMLU, GROK): "FIRST-SIDED", (IFEVAL, GROK): "UNRESOLVED"})[0] == "FAILED", "C2 FAILED (a supported family UNRESOLVED)")
            fake = {(MMLU, GROK): dict(support="SUPPORTED", side="FIRST-SIDED", deff_undefined=False),
                    (BFCL, GROK): dict(support="UNSUPPORTED", side="FIRST-SIDED", deff_undefined=True)}
            v_, w_, d_, c_ = c2_verdict(fake)
            check(v_ == "UNDETERMINED" and c_ and "MMLU-Pro is the only corpus" in c_ and d_ and "DESCRIPTIVE, decides nothing" in d_ and "would read HELD" in d_,
                  "C2 WITHOUT BFCL is PRIMARY (UNDETERMINED: MMLU-Pro alone) while the with-BFCL reading HELD is printed DESCRIPTIVE only: %s | %s" % (c_, d_))
            fake2 = dict(fake); fake2[(MATH, GROK)] = dict(support="SUPPORTED", side="UNRESOLVED", deff_undefined=False)
            v2_, w2_, d2_, c2l_ = c2_verdict(fake2)
            check(v2_ == "FAILED" and c2l_ is None and d2_ and "decides nothing" in d2_,
                  "C2 PRIMARY FAILED on two supported corpora; BFCL's reading beside is descriptive: " + d2_)
            leak = {(MMLU, GROK): dict(support="SUPPORTED", side="FIRST-SIDED", deff_undefined=False, n=400),
                    (BFCL, GROK): dict(support="SUPPORTED", side="FIRST-SIDED", deff_undefined=False, n=58)}
            check(c2_verdict(leak)[0] == "UNDETERMINED", "second layer: even a BFCL family labelled SUPPORTED never enters C2 PRIMARY (c2_verdict excludes the corpus)")
            fake3 = {(MMLU, GROK): dict(support="SUPPORTED", side="FIRST-SIDED", deff_undefined=False),
                     (MATH, GROK): dict(support="SUPPORTED", side="SECOND-SIDED", deff_undefined=False)}
            check(c2_verdict(fake3)[0] == "HELD" and c2_verdict(fake3)[2] is None, "C2 HELD with no undefined-DEFF family: no descriptive line")
            check(st[(IFEVAL, GROK)]["side"] == "UNRESOLVED" and st[(MATH, GROK)]["side"] == "SECOND-SIDED" and st[(MMLU, GROK)]["side"] == "FIRST-SIDED",
                  "sidedness classes on the fixtures: MMLU first, MATH second, IFEval unresolved")
            # the full run: outcome written once; a second run refused
            with contextlib.redirect_stdout(io.StringIO()):
                res = analyze(tmp, fm, pool_check=False, eval_db=os.path.join(tmp, "eval_fixture.db"), expected_c1=dict(n=57, FF=12, SS=0),
                              cert_pin=vfc.script_shas()[0])
            t = res["text"]
            check("C4(a) AGREE-ORDER position shares" in t and "recorded n 8922" in t and "recorded n 10442" in t,
                  "C4(a) READ branch executed (AGREE and DISAGREE rows printed beside the record)")
            check("C4(b) POSITION-DECOMP (frontier): n 100" in t and "C4(c) POSITION-FULL (cross-tier): n 100" in t,
                  "C4(b) and C4(c) READ branches executed on the name-labelled arena13 fixture")
            check(set(res["changes"]) == {"AGREE-ORDER AGREE both-FIRST minus both-SECOND", "C4(b) POSITION-DECOMP (frontier)"} and "P6 " in t and "YES" in t,
                  "C4 sign-change detection: the constructed changes are caught and the unchanged cross-tier direction is not (%s)" % res["changes"])
            nr, ch0 = c4_lines([], tmp, os.path.join(tmp, "eval_fixture.db"))
            check(any("C4(a) AGREE-ORDER: NOT READ" in l for l in nr) and any("NOT READ (arena13.db" in l for l in nr) and ch0 == [],
                  "C4 NOT-READ branches executed (caches absent)")
            check(all(s in t for s in ("(C1)", "(C2)", "(C3)", "(C4)", "(C5)", "FAMILY TABLE", "P1 ", "P2 ", "P3 ", "P4 ", "P5 ", "P6 ", "FALSIFIER C1",
                                       "FALSIFIER C2", "FALSIFIER C4", "BFCL-FLIP-RESEED", "[POOLS]", "measured DEFF UNDEFINED", "PRIMARY, the supported families only",
                                       "DESCRIPTIVE, decides nothing", "scored on the point only", "E-COMB-CERTIFIED entered tables")),
                  "the outcome carries C1-C5, the family table, P1-P6, the three falsifier lines, the FLIP-RESEED line and the pool line")
            check(t.splitlines()[0].startswith("[POOLS]"), "the FIRST printed line lists the pools of the entered caches")
            again = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(tmp, fm, pool_check=False, cert_pin=vfc.script_shas()[0])
            except SystemExit as e: again = "WRITE-ONCE" in str(e)
            d3 = False
            try: load_cert(tmp, pin="0123456789abcdef")
            except SystemExit as e: d3 = "[CERT] REFUSED" in str(e) and "not the pinned build" in str(e)
            check(d3 and load_cert(tmp, pin=vfc.script_shas()[0])[0]["certificate"] == "HELD",
                  "D3: a certificate written by another vote_frame_cert build is REFUSED; the pinned build's is read")
            lines.append("  [INFO] VFC_PIN_LF %s pins the WRITER of the certificate read (load_cert compares it with the certificate JSON's "
                         "script_sha256_16_lf); the imported vote_frame_cert.py READER is sha256[:16] of the LF bytes %s (%s); the reader's identity is "
                         "NOT checked by load_cert or by any real run (D5, 9d3e261)"
                         % (VFC_PIN_LF, vfc.script_shas()[0], "equal" if VFC_PIN_LF == vfc.script_shas()[0] else "different"))
            cp5 = os.path.join(tmp, CERT_JSON); b5 = open(cp5, "rb").read(); d5 = json.loads(b5.decode("utf-8"))
            d5["script_sha256_16_lf"] = "0123456789abcdef"; open(cp5, "w", encoding="utf-8").write(json.dumps(d5))
            try: read5 = load_cert(tmp, pin="0123456789abcdef")[0]["certificate"] == "HELD"
            finally: open(cp5, "wb").write(b5)
            check(read5 and vfc.script_shas()[0] != "0123456789abcdef",
                  "D5: load_cert reads a certificate whose WRITER sha equals the pin although the imported reader's sha (%s) differs: the reader is not "
                  "pinned, as the INFO line states" % vfc.script_shas()[0])
            check(again, "a second run is REFUSED (write-once)")
            # refusals: a moved cache; a certificate that is not HELD; an absent certificate
            con = sqlite3.connect(os.path.join(er, "m", "pos.db")); con.execute("UPDATE verdicts SET qid = qid"); con.execute("INSERT INTO run_meta VALUES ('x','y')"); con.commit(); con.close()
            moved = False
            try: extract(tmp, entered, lambda s: None, maps={})
            except SystemExit as e: moved = "moved after certification" in str(e)
            check(moved, "a cache whose sha256_16 differs from the certificate's is REFUSED")
            cp = os.path.join(tmp, CERT_JSON); d = json.load(open(cp)); d["certificate"] = "FAILED"; os.remove(cp); json.dump(d, open(cp, "w"))
            nh = False
            try: load_cert(tmp)
            except SystemExit as e: nh = "not VOTE-FRAME-CERT HELD" in str(e)
            check(nh, "a certificate that is not HELD is REFUSED")
            os.remove(cp); ab = False
            try: load_cert(tmp)
            except SystemExit as e: ab = "absent" in str(e)
            check(ab, "an absent certificate is REFUSED")
            # predictions, falsifier and FLIP-RESEED lines: both branches of each
            good = {(MMLU, MISTRAL): dict(n=100, s=0.2, lo=0.1, hi=0.3, side="SECOND-SIDED", support="SUPPORTED"),
                    (MMLU, GROK): dict(n=100, s=0.65, lo=0.56, hi=0.74, side="FIRST-SIDED", support="SUPPORTED"),
                    (BFCL, GROK): dict(n=57, s=1.0, lo=0.2, hi=1.0, side="UNRESOLVED", support="UNSUPPORTED")}   # side not read: point only
            P = score_predictions("HELD", good, "HELD", ["x"])
            check([r for _, r, _ in P] == ["HELD"] * 5 + ["EVENT"], "P1-P6 first branch: " + " | ".join(l for _, _, l in P))
            bad = {(MMLU, MISTRAL): dict(n=100, s=0.6, lo=0.5, hi=0.7, side="UNRESOLVED", support="SUPPORTED"),
                   (MMLU, GROK): dict(n=100, s=0.3, lo=0.2, hi=0.4, side="SECOND-SIDED", support="SUPPORTED"),
                   (BFCL, GROK): dict(n=57, s=0.5, lo=0.3, hi=0.7, side="UNRESOLVED", support="SUPPORTED")}
            P = score_predictions("FAILED", bad, "FAILED", [])
            check([r for _, r, _ in P] == ["FAILED"] * 5 + ["NO EVENT"], "P1-P6 other branch: " + " | ".join(l for _, _, l in P))
            f1 = falsifier_lines("FAILED", "FAILED", ["x"]); f0 = falsifier_lines("HELD", "HELD", [])
            check(all("FIRED" in l for l in f1[:3]) and all("not fired" in l for l in f0[:3]), "falsifier lines: fired and not-fired branches")
            rl = {reseed_line("FAILED", "HELD"), reseed_line("HELD", "HELD"), reseed_line("HELD", "FAILED"), reseed_line("HELD", "UNDETERMINED")}
            check(len(rl) == 4, "BFCL-FLIP-RESEED dependency line: four distinct branches (C1 FAILED; C2 HELD / FAILED / UNDETERMINED)")
            few = [dict(family=("X", "j"), cluster=("X", str(i)), p1=("Model A" if i < 6 else "Model B"), p2=("Model A" if i < 6 else "Model B"),
                        cache="c") for i in range(10)]
            fs = family_stats(few, B=500)[("X", "j")]
            check(abs(fs["s"] - 0.6) < 1e-12 and fs["lo"] < 0.5 < fs["hi"] and fs["side"] == "UNRESOLVED",
                  "sidedness is read on the INTERVAL, not the point: s 0.600 [%.3f, %.3f] on 10 clusters -> %s" % (fs["lo"], fs["hi"], fs["side"]))
            lo, hi = clopper_pearson(57, 57); check(0.93 < lo < 0.95 and hi == 1.0, "exact binomial beside: 57 / 57 -> [%.4f, %.4f]" % (lo, hi))
    except (Exception, SystemExit) as e:      # a refusal inside the selftest is a FAIL line, not an abort
        import traceback
        lines.append("  [FAIL] exception: %r\n%s" % (e, traceback.format_exc())); ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=== %s --selftest (synthetic caches certified by vote_frame_cert under tempfile.mkdtemp(); no DB of record) ===" % TEST)
    print("\n".join(lines))
    n_chk = sum(1 for l in lines if l.lstrip().startswith(("[PASS]", "[FAIL]"))); n_info = sum(1 for l in lines if l.lstrip().startswith("[INFO]"))
    print("SELFTEST %s: %d checks, %d failed; %d INFO line(s), not checks (rr2 L1)" % ("PASS" if ok else "FAIL", n_chk, sum(1 for l in lines if "[FAIL]" in l), n_info))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="POSITION-INDEX-ALL (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.dry_run: sys.exit(dry_run())
    analyze()
