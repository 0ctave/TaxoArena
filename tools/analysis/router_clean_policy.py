"""ROUTER-CLEAN-POLICY -- the deployed union router re-read on the split of record (ZERO judge calls, zero construction).

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-09-23 (before any code or call) --
ROUTER-CLEAN-POLICY: does the deployed union router still beat the best single model when every policy is fitted on the
TRAIN side of the split of record and scored on all 6,482 EVAL questions, with an interval that carries the policy's own
variance?" (L12710-L12909 at 2bc6184; resolve by the heading). Record: docs/agents/results/ROUTER-CLEAN-POLICY.json.
This script is BUILT TO that text; where it had to read the text, the reading is stated below under READINGS.

THE DEFECT IT FIXES. tools/analysis/multicorpus_router_e2e.py (the instrument of MC-E2E / MC-SEEDS; NOT edited) builds its
own random.Random(seed) 0.30 split (L86-L90), fits every policy on that split's train (L91-L101) and only afterwards
restricts test to the clean pool (L114-L117): 4,536 of the 6,482 paeec EVAL questions sat on the policy-fitting side at
seed 42. Here TRAIN = the 15,124 union questions OUTSIDE pool paeec37aa28063c75 and EVAL = all 6,482 (the form of record,
cost_axes_ingest.py L206), with the disjointness ASSERTED AND PRINTED.

  python tools/analysis/router_clean_policy.py --selftest   # synthetic fixtures under tempfile.mkdtemp(); opens NO real DB
  python tools/analysis/router_clean_policy.py --dry-run    # 0 calls, WRITES NOTHING: guards, |TRAIN|, |EVAL|, roster, G1,
                                                            #   the 52-stratum n table, sum n^2, Kish size, planned B/seeds
  python tools/analysis/router_clean_policy.py --legacy     # G2: re-runs the MC-E2E L86-L118 construction at seed 42
                                                            #   (--clean --mathfix) and prints the record's seed-42 block
  python tools/analysis/router_clean_policy.py --run        # the test; writes the outcome file of record WRITE-ONCE

LAUNCH SEQUENCE (registration FLOW): this script (engine-coder) -> adversarial-reviewer READY (code-only) committed ->
run-operator --dry-run (0 calls, writes nothing) -> --run OUTSIDE any construction window (rule 7: it reads the union pool)
-> adversarial-reviewer on the numbers -> registrar. Run from the MAIN checkout (the DBs and the six federated trees are
untracked there). Independent pool check for the READY: python tools/analysis/pool_guard.py --pool paeec37aa28063c75

GUARDS, executed and printed in EVERY real mode (dry-run included):
  (0) WAL LAUNCH REFUSAL (ruling (d), d6b5ca8): before anything opens a DB, a NON-EMPTY -wal sidecar beside
      multicorpus_cache_v1.db or embeddings_cache.db refuses the run ("[WAL] ..."); after the POOL line each sidecar is
      printed as absent or 0 bytes.
  (1) pool_guard.assert_pool_of_record(pool_guard.UNION_POOL) is the first statement of every real mode (id file and DB
      rows hash to the id, and are equal) [after the WAL launch check (0), which opens no DB, and in --run after the
      write-once check, which opens none either]; the union DB is then opened mode=ro&immutable=1 and
      pool_guard.assert_frozen_pool(con, pool_guard.UNION_POOL) is run on the READING connection; the first printed line
      is the pool id. The scored set is checked against the pool's id file (reserved_pool_id= / scored_minus_eval=0).
  (2) |EVAL| == 6,482, |TRAIN| == 15,124, |TRAIN intersect paeec| == 0: asserted executably and printed.
  (3) Meta-Llama-3-70B-Instruct NOT in the roster and |roster| == 18: asserted and printed.
  (4) EVERY policy fit asserts, at the call, that the set of questions carrying weight is a subset of TRAIN (a set-membership
      assert in fit_policies; the number of asserts executed is printed). [2026-09-23, READY review ea09f3b D5 / D6: the
      check is an `if not ...: raise SystemExit("[G3(4)] ...")`, never an `assert`, so it survives python -O; and --run
      REFUSES unless the executed count equals 2B + 2 (1 G2 legacy fit + 1 point fit + B two-stage + B TRAIN-only).]
  (5) MATH-FIX overlay ON (the clean record of MC-E2E is the MATH-FIX clean file).
REFUSAL GATES (a failed gate raises SystemExit and writes NO outcome file; a gate is never a verdict clause):
  G1 predicted source 0.962 and predicted source+domain 0.813 over the 21,606 routed questions, to 3 dp;
  G2 the legacy construction at seed 42 (--clean --mathfix) gives deployed gain +0.0437 on n = 1,946 exactly;
  G3 the hygiene asserts (2)-(4).
  G4 [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (e)]: the two-stage variance of G (C1) or of P (C4) is 0, or
     Var(G | two-stage) = 0 for phi: every interval is degenerate, which can only mean a defect; checked inside the tee,
     before any verdict, so nothing is written.
  WAL [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (d)]: the launch refusal (0) above.
READS (all read-only): multicorpus_cache_v1.db (corpus_questions, eval_results, eval_results_mathfix, reserved_pool) with
mode=ro&immutable=1; the embedding vectors through free_tests_f4_f7.embed_matrix (the registered reader; it opens
embeddings_cache.db mode=ro, WITHOUT immutable, see READINGS); the six federated per-corpus trees
experiment_results/multicorpus/<corpus>_s42/seed_42; for a DESCRIPTIVE cross-check only, the routing files of record
experiment_results/multicorpus/union_s42_flatleaf/seed_42/validation/MAIN_union_routing_{summary.txt,queries.csv}
(NEVER the generic centroid CSV and NEVER embeddings_cache.db.queries.ground_truth_category, which is text-keyed and shared
across corpora). It never imports stack_judge.py and writes no DB.
OUTPUT: experiment_results/multicorpus/router_clean_policy_outcome.txt, WRITE-ONCE (refused if it exists; opened mode "x").

INSTRUMENT. Routing exactly as MC-E2E: flatLeaf nearest centroid over the 143 federated leaves at dim 512. Arms: best single
(argmax TRAIN accuracy) | TRUE source | TRUE (source, domain) | PRED source | PRED (source, domain) = THE DEPLOYED ARM |
PRED leaf (min_leaf 20; fallback exactly MC-E2E L108-L109) | per-question oracle | PLACEBO (C4). Argmax tie-break: the first
model in sorted-name order (numpy argmax over sorted columns = Python max() over the sorted roster = cost_axes_ingest's pick).
Policies fitted ONCE on TRAIN; scored on all 6,482. BOOTSTRAPS, all B = 2000, each with its own numpy default_rng(42):
  two-stage (DECIDING): TRAIN resampled within each of the 52 true strata, EVERY policy re-fitted (placebo included), then
      EVAL resampled within stratum and scored;
  i.i.d. (the record's form, beside): EVAL questions resampled i.i.d. over the 6,482, policy fixed;
  TRAIN-only (for R3): TRAIN resampled within stratum with every policy re-fitted, EVAL fixed;
  52-cell clustered (DESCRIPTIVE-ONLY, decides nothing): the 52 EVAL strata resampled WHOLE, policy fixed.
Deciding interval = point +- 1.96 x SE_2stage; the percentile interval, the i.i.d. and the clustered SE are printed beside.
Beside every deciding statistic: measured DEFF (var_2stage / var_iid; var_clustered / var_iid), n_eff = 6,482 / DEFF, MDE at
80% power = 2.80 x SE, and the registered Support planning numbers.

CRITERIA (verbatim bars from the registration; ONE deciding statistic each):
  C0 HELD iff best single is Qwen2.5-72B-Instruct and its EVAL accuracy and the TRUE (source, domain) accuracy equal 0.5912
     and 0.6220 to 4 dp; FAILED otherwise.
  C1 G = acc(PRED source/domain) - acc(best single); HELD iff the two-stage interval lies wholly above 0, FAILED iff wholly
     below, UNDETERMINED iff it contains 0.
  C2 PRED(source, domain) - PRED(source); C3 PRED leaf - PRED(source, domain): same form, DESCRIPTIVE-ONLY BY SUPPORT
     (the three-way reading is printed and no HELD / FAILED is recorded).
  C4 PLACEBO: the 52 TRUE labels permuted across all 21,606 questions (random.Random(42).shuffle over the sorted-qid label
     list; sizes kept), per-pseudo-stratum argmax on TRAIN scored on EVAL; FAILED iff the two-stage interval of
     P = acc(placebo) - acc(best single) lies wholly above 0; HELD otherwise.
  R3 phi = Var(G | TRAIN resampled, EVAL fixed) / Var(G | two-stage); HELD iff phi < 0.5, FAILED iff phi >= 0.5 (the point
     decides; its Monte-Carlo SE is printed).
  R4 DESCRIPTIVE: M = acc(TRUE s/d) - acc(PRED s/d) with its two-stage interval; every arm with i.i.d. and two-stage SE; per
     source; the MMLU-Pro-source subset of C1 (3,609 questions) with its two-stage interval.
PREDICTIONS P1-P7 as registered; FALSIFIER as registered (see verdict_lines).

READINGS (stated, not silent; each is for the READY to confirm or refuse):
  (a) VALIDITY TRIGGERS FIRST (the registrar's standing rule of 2026-09-23, 7da2ec5 D2). The registration makes two
      criteria preconditions of the rest: "IF C4 FAILS, every number of this test is void ... whatever C1 says", and C0
      FAILED means "the reviewer must say which is wrong before any other criterion is read". They are therefore evaluated
      FIRST as pre-empting triggers: if either fires, C1 and R3 print "UNDETERMINED (BY TRIGGER: ...)", their interval /
      point is printed but NOT scored, and the falsifier is NOT EVALUATED (the C4-void consequence is printed).
      [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (a): the two triggers are REGISTERED and their scope is wider than
      this reading. T1 (C4's two-stage interval wholly above 0, evaluated on the numbers whatever T2 says) pre-empts C1, C2,
      C3, R3 and ALL of R4: "UNDETERMINED (BY TRIGGER: C4 FAILED, the instrument manufactures gain from noise)"; C4's
      void consequence is printed. T2 (C0 FAILED) pre-empts C1, C2, C3, C4, R3 and ALL of R4: "UNDETERMINED (BY TRIGGER:
      C0 FAILED, two instruments disagree about the same object)", and the pre-emption is NOT LIFTED WITHIN THIS RUN.
      Both are named when both fire. C0 is scored in every branch; the falsifier is not evaluated when either fires.]
  (b) A prediction "X [lo, hi]" is HELD iff the observed point lies in [lo, hi] (endpoints inclusive, full precision);
      P6 is HELD iff C0 is HELD.
      [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (b): CONFIRMED, and a prediction whose criterion is pre-empted is
      UNDETERMINED (BY TRIGGER): under any trigger P1, P2, P3, P5 and P7; P4 is scored only when T1 fires alone
      (UNDETERMINED under T2); P6 is HELD iff C0 is HELD in every branch. No prediction is scored on voided numbers.]
  (c) The pool guard is the first statement of every REAL mode, not a module-level statement: at module level it would
      open multicorpus_cache_v1.db on import and in --selftest, which must open no real DB. The selftest runs the same
      guard on its fixture (db / id_file overrides) as its first fixture statement.
  (d) The registered embedding reader (free_tests_f4_f7.embed_matrix) opens embeddings_cache.db mode=ro WITHOUT
      immutable=1; it is used unchanged (immutable=1 would hide a WAL tail on a DB every construction rewrites; rule 7
      keeps constructions out of the run's window).
      [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (d): mode=ro without immutable=1 is ADMITTED for embeddings_cache.db
      PROVIDED a non-empty -wal beside it refuses the run at launch; the standing rule makes that uniform for every input
      DB whatever its open mode, so the same launch check covers multicorpus_cache_v1.db (guard (0), gate WAL).]
  (e) The legacy path (G2) fits on the legacy split's train, which contains EVAL questions BY DESIGN (it reproduces the
      defect of record); its fit asserts against that legacy train set, and nothing it computes enters a clean statistic.
  (f) A degenerate two-stage variance (0) makes phi undefined; this is a refusal (SystemExit), never a verdict.
      [RULED 2026-09-23, registrar, d6b5ca8, programme L13644-L13689 (e): CONFIRMED and registered as refusal gate G4, covering ANY
      deciding variance (G for C1, P for C4, and Var(G) for phi); the message is "[G4] ...".]
Key-scored end to end (leaderboard verifiers); no judge verdict enters, so no wrong(established) count and no tie
convention A / B arises. Denominator: the 6,482 EVAL questions of paeec37aa28063c75 in 52 fixed strata.
"""
import os, sys, io, json, random, sqlite3, hashlib, argparse, contextlib, tempfile, shutil, struct, re, csv, math; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard

TEST_ID = "ROUTER-CLEAN-POLICY"
EXCLUDED = "Meta-Llama-3-70B-Instruct"
CORPORA = ["mmlu_pro_lb", "bbh", "math", "gpqa", "musr", "ifeval"]          # MC-E2E L38, same order
ARMS = ["best single", "TRUE source", "TRUE source/domain", "PRED source", "PRED source/domain", "PRED leaf", "oracle",
        "PLACEBO"]
BS, TSRC, TDOM, PSRC, PDOM, PLEAF, ORACLE, PLAC = range(8)
OUT_PATH = os.path.join(ROOT, "experiment_results", "multicorpus", "router_clean_policy_outcome.txt")
RECORD_LEGACY_FILE = os.path.join(ROOT, "experiment_results", "multicorpus", "router_e2e_mathfix_clean.txt")
MAIN_ROUTING_DIR = os.path.join(ROOT, "experiment_results", "multicorpus", "union_s42_flatleaf", "seed_42", "validation")

# The registered numbers. None of them is a CLI knob.
REG = dict(pool=pool_guard.UNION_POOL, n_eval=6482, n_train=15124, n_routed=21606, n_strata=52, roster=18,
           g1_src="0.962", g1_dom="0.813", g2_seed=42, g2_ratio=0.3, g2_gain="+0.0437", g2_n=1946,
           c0_best="Qwen2.5-72B-Instruct", c0_bs="0.5912", c0_tdom="0.6220", B=2000, seed=42, min_leaf=20,
           placebo_seed=42, n_mmlu=3609, sum_n2=1279118, kish="197.3", leaves=143, dim=512)

# The per-stratum EVAL n table of record (profile_interval_all_union.txt L18-L69), key SOURCE/domain.
REG_STRATA_N = {
    "BBH/boolean_expressions": 75, "BBH/causal_judgement": 56, "BBH/date_understanding": 75, "BBH/disambiguation_qa": 75,
    "BBH/formal_fallacies": 75, "BBH/geometric_shapes": 75, "BBH/hyperbaton": 75, "BBH/logical_deduction_five_objects": 75,
    "BBH/logical_deduction_seven_objects": 75, "BBH/logical_deduction_three_objects": 75, "BBH/movie_recommendation": 75,
    "BBH/navigate": 75, "BBH/object_counting": 75, "BBH/penguins_in_a_table": 44, "BBH/reasoning_about_colored_objects": 75,
    "BBH/ruin_names": 75, "BBH/salient_translation_error_detection": 75, "BBH/snarks": 53, "BBH/sports_understanding": 75,
    "BBH/temporal_sequences": 75, "BBH/tracking_shuffled_objects_five_objects": 75,
    "BBH/tracking_shuffled_objects_seven_objects": 75, "BBH/tracking_shuffled_objects_three_objects": 75,
    "BBH/web_of_lies": 75, "MATH/Algebra": 92, "MATH/Counting & Probability": 37, "MATH/Geometry": 40,
    "MATH/Intermediate Algebra": 84, "MATH/Number Theory": 46, "MATH/Prealgebra": 58, "MATH/Precalculus": 41,
    "MUSR/murder_mysteries": 75, "MUSR/object_placements": 77, "MUSR/team_allocation": 75, "IFEVAL/ifeval": 162,
    "GPQA/Physics": 150, "GPQA/Chemistry": 147, "GPQA/Biology": 61, "MMLU_PRO_LB/business": 237, "MMLU_PRO_LB/law": 330,
    "MMLU_PRO_LB/psychology": 239, "MMLU_PRO_LB/biology": 215, "MMLU_PRO_LB/chemistry": 340, "MMLU_PRO_LB/history": 114,
    "MMLU_PRO_LB/other": 277, "MMLU_PRO_LB/health": 245, "MMLU_PRO_LB/economics": 253, "MMLU_PRO_LB/math": 405,
    "MMLU_PRO_LB/physics": 390, "MMLU_PRO_LB/computer science": 123, "MMLU_PRO_LB/philosophy": 150,
    "MMLU_PRO_LB/engineering": 291}

# Support section (e)-(f): the registered planning numbers, printed beside the measured ones.
PLAN = {
    "C1": dict(verdict="SCOREABLE", se_iid=0.0051, deff=1.5, deff_p=2.5, se=0.00625, se_p=0.00806, neff=4321, neff_p=2593,
               mde=1.75, mde_p=2.26, cl_deff=4.0, cl_se=0.0102, cl_neff=1620, cl_mde=2.86),
    "C2": dict(verdict="DESCRIPTIVE-ONLY", se_iid=0.0045, deff=1.5, se=0.00551, mde=1.54),
    "C3": dict(verdict="DESCRIPTIVE-ONLY", se_iid=0.0030, deff=2.0, deff_p=3.0, se=0.00424, neff=3241, mde=1.19),
    "C4": dict(verdict="SCOREABLE AS A NEGATIVE CONTROL", se=0.00625, mde=1.75),
}
# Predictions, registered intervals (fractions).
PRED = {"P1": ("C1", 0.024, 0.010, 0.036), "P2": ("C2", 0.013, 0.003, 0.025), "P3": ("C3", -0.007, -0.015, 0.002),
        "P4": ("C4", -0.003, -0.010, 0.002), "P5": ("phi", 0.15, 0.03, 0.40), "P7": ("M", 0.007, -0.003, 0.016)}
# The contrasts: name -> (arm a, arm b, subset). Gain = acc(a) - acc(b).
CONTRASTS = {"C1": (PDOM, BS, None), "C2": (PDOM, PSRC, None), "C3": (PLEAF, PDOM, None), "C4": (PLAC, BS, None),
             "M": (TDOM, PDOM, None), "ORC": (TDOM, BS, None), "C1_MMLU": (PDOM, BS, "mmlu")}


def canon(s):
    """MC-E2E L78: the DB writes MMLU-Pro rows under source MMLU_PRO; the leaderboard tree's anchors say MMLU_PRO_LB."""
    return "MMLU_PRO" if s == "MMLU_PRO_LB" else s


def key_of_record(source, domain):
    """The frozen key form SOURCE/domain used by the pool and the routing files of record (MMLU_PRO -> MMLU_PRO_LB)."""
    return "%s/%s" % ("MMLU_PRO_LB" if source == "MMLU_PRO" else source, domain)


def script_shas():
    """(LF blob sha16, CRLF blob sha16, which rendering the working tree holds). LF = `git hash-object` of the committed
    rendering; CRLF = the rendering a core.autocrlf=true checkout holds. The LF sha is the identity; CRLF sits beside it."""
    raw = open(os.path.abspath(__file__), "rb").read()
    lf = raw.replace(b"\r\n", b"\n"); crlf = lf.replace(b"\n", b"\r\n")
    blob = lambda b: hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()[:16]
    return blob(lf), blob(crlf), ("CRLF" if raw == crlf and raw != lf else "LF")


# ============================================================================================ configuration
class Cfg:
    """Where the inputs are and what the registered expectations are. real_cfg() is the only config the CLI builds."""
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    import free_tests_f4_f7 as ff
    return Cfg(pool_id=REG["pool"], db_override=None, id_override=None,
               union_db=pool_guard.db_path(REG["pool"]), emb_db=ff.EMB_DB,
               tree_dirs=[(c, os.path.join("experiment_results", "multicorpus", "%s_s42" % c, "seed_42")) for c in CORPORA],
               routing_dir=MAIN_ROUTING_DIR, record_legacy_file=RECORD_LEGACY_FILE, out_path=OUT_PATH,
               reg=dict(REG), reg_strata=dict(REG_STRATA_N), B=REG["B"], placebo_override=None)


# ============================================================================================ guards
def guard_pool(cfg):
    """Guard (1), part 1: the FIRST statement of every mode. Returns the pool id."""
    return pool_guard.assert_pool_of_record(cfg.pool_id, db=cfg.db_override, id_file=cfg.id_override)


def wal_sidecars(cfg):
    """[(db path, -wal size in bytes or None when absent)] for every input DB (ruling (d): union and embeddings)."""
    out = []
    for db in (cfg.union_db, cfg.emb_db):
        w = db + "-wal"
        out.append((db, os.path.getsize(w) if os.path.exists(w) else None))
    return out


def wal_guard(cfg):
    """Ruling (d), the standing WAL rule: a NON-EMPTY -wal beside any input DB refuses the run AT LAUNCH, before any DB is
    opened. Prints nothing, so the pool id stays the first printed line; prefix prints the sizes after it."""
    for db, size in wal_sidecars(cfg):
        if size:
            _br("WAL.REFUSED")
            raise SystemExit("[WAL] %s-wal is %d bytes: a writer is live; refusing at launch (ruling d, d6b5ca8)" % (db, size))


def open_union(cfg):
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % cfg.union_db.replace("\\", "/"), uri=True)
    got = pool_guard.assert_frozen_pool(con, cfg.pool_id)          # guard (1), part 2, on the READING connection
    return con, got


def eval_ids_of_record(cfg):
    if cfg.id_override is None:
        return pool_guard.eval_ids(cfg.pool_id)
    with open(cfg.id_override, "r", encoding="utf-8") as f:
        return frozenset(q for ids in pool_guard.judgeable(json.load(f)).values() for q in ids)


def scored_guard(cfg, scored):
    """reserved_pool_id= / scored_minus_eval= against the pool's id file (pool_guard.assert_scored_subset for the pool of
    record; the same two lines against the fixture id file in the selftest). Exits unless 0."""
    if cfg.id_override is None:
        return pool_guard.assert_scored_subset(cfg.pool_id, scored, out=sys.stdout)
    ev = eval_ids_of_record(cfg); extra = sorted(set(scored) - ev)
    print("reserved_pool_id=%s" % cfg.pool_id); print("scored_minus_eval=%d" % len(extra))
    if extra:
        raise SystemExit("[SCORED-EVAL] %d scored question(s) are not in pool %s" % (len(extra), cfg.pool_id))
    return 0


# ============================================================================================ data
def load_union(con, cfg):
    """MC-E2E load() with guard (3) and guard (5): roster by SELECT DISTINCT, then Meta-Llama absence and |roster| ASSERTED."""
    Q = {q: (s, d, t) for q, s, d, t in con.execute("SELECT question_id, source, domain, text FROM corpus_questions")}
    models = [m for (m,) in con.execute("SELECT DISTINCT model_name FROM eval_results ORDER BY model_name")]
    if models != sorted(models):
        raise SystemExit("[G3] roster ORDER BY differs from Python sorted order; the argmax tie-break would move")
    absent = EXCLUDED not in models
    print("ASSERT %s not in roster: %s | ASSERT |roster| == %d: %d -> %s"
          % (EXCLUDED, "ABSENT" if absent else "PRESENT", cfg.reg["roster"], len(models),
             "PASS" if (absent and len(models) == cfg.reg["roster"]) else "FAIL"))
    if not absent or len(models) != cfg.reg["roster"]:
        raise SystemExit("[G3(3)] roster assertion failed: %s present=%s, |roster|=%d" % (EXCLUDED, not absent, len(models)))
    print("roster (%d, sorted = the argmax tie-break order): %s" % (len(models), ", ".join(models)))
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        G[q][m] = int(c)
    n = 0; outside = 0
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix"):
        if q in G and m in G[q]:
            if G[q][m] != int(c):
                G[q][m] = int(c); n += 1
        else:
            outside += 1
    print("MATH-FIX overlay: %d corrected (question, model) cells" % n)
    print("  (mathfix rows with no eval_results cell, not overlaid, exactly as MC-E2E L51: %d)" % outside)
    pool = {q for (q,) in con.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (cfg.pool_id,))}
    return Q, models, G, pool


def federated_leaves(cfg, ff):
    """MC-E2E federated_leaves(): (leaf_id, unit-norm centroid, source, domain) over the per-corpus trees."""
    out = []
    for c, d in cfg.tree_dirs:
        for lid, mu, anchor in ff.tree_leaves(d):
            src, _, dom = anchor.partition("/")
            nrm = np.linalg.norm(mu)
            out.append(("%s:%s" % (c, lid), mu / (nrm or 1.0), src, dom))
    return out


class Data:
    pass


def _index(labels):
    keys = sorted(set(labels)); pos = {k: i for i, k in enumerate(keys)}
    return keys, np.array([pos[x] for x in labels], dtype=np.int64)


def build_data(Q, models, G, pool, leaves, vec, cfg):
    """Route every complete question exactly as MC-E2E L69-L80, then lay out arrays. TRAIN = routed \\ pool, EVAL = routed
    intersect pool; the placebo labels are the TRUE stratum labels permuted by random.Random(placebo_seed)."""
    D = Data(); D.models = list(models); m = len(models)
    qs = sorted(q for q in Q if len(G[q]) == len(models))
    qq = [q for q in qs if Q[q][2] in vec]
    X = np.stack([vec[Q[q][2]] for q in qq]); M = np.stack([l[1] for l in leaves])
    idx = np.argmax(X @ M.T, axis=1)
    D.pleaf = {q: leaves[i][0] for q, i in zip(qq, idx)}
    D.psrc = {q: leaves[i][2] for q, i in zip(qq, idx)}; D.pdom = {q: leaves[i][3] for q, i in zip(qq, idx)}
    D.src_ok = sum(1 for q in qq if canon(D.psrc[q]) == Q[q][0]) / len(qq)
    D.dom_ok = sum(1 for q in qq if canon(D.psrc[q]) == Q[q][0] and D.pdom[q] == Q[q][1]) / len(qq)
    D.n_complete = len(qs); D.n_leaves = len(leaves); D.dim = len(leaves[0][1])
    D.qq = qq; D.Q = Q; D.n = n = len(qq)
    D.qids = np.array(qq, dtype=np.int64)
    D.A = np.array([[G[q][mm] for mm in models] for q in qq], dtype=np.int64).reshape(n, m)
    D.strata_keys, D.g_tdom = _index([(Q[q][0], Q[q][1]) for q in qq])
    D.src_keys, D.g_tsrc = _index([Q[q][0] for q in qq])
    D.psrc_keys, D.g_psrc = _index([canon(D.psrc[q]) for q in qq])
    D.pdom_keys, D.g_pdom = _index([(canon(D.psrc[q]), D.pdom[q]) for q in qq])
    D.pleaf_keys, D.g_pleaf = _index([D.pleaf[q] for q in qq])
    labels = [int(x) for x in D.g_tdom]                       # sorted-qid order
    if cfg.placebo_override is not None:                       # selftest defect-injection hook; the CLI never sets it
        plac = [int(x) for x in cfg.placebo_override(D)]
    else:
        plac = labels[:]; random.Random(cfg.reg["placebo_seed"]).shuffle(plac)
    D.g_plac = np.array(plac, dtype=np.int64); D.n_plac = len(D.strata_keys)
    D.groupings = {"tsrc": (D.g_tsrc, len(D.src_keys), 1), "tdom": (D.g_tdom, len(D.strata_keys), 1),
                   "psrc": (D.g_psrc, len(D.psrc_keys), 1), "pdom": (D.g_pdom, len(D.pdom_keys), 1),
                   "pleaf": (D.g_pleaf, len(D.pleaf_keys), cfg.reg["min_leaf"]), "plac": (D.g_plac, D.n_plac, 1)}
    D.flat = {k: (g[:, None] * m + np.arange(m)[None, :]).ravel() for k, (g, _, _) in D.groupings.items()}
    D.pool_set = frozenset(pool)
    D.is_eval = np.array([q in pool for q in qq], dtype=bool)
    D.E = np.flatnonzero(D.is_eval); D.T = np.flatnonzero(~D.is_eval)
    D.train_set = frozenset(int(q) for q in D.qids[D.T]); D.eval_set = frozenset(int(q) for q in D.qids[D.E])
    K = len(D.strata_keys)
    D.strata_train = [D.T[D.g_tdom[D.T] == k] for k in range(K)]
    gE = D.g_tdom[D.E]
    D.strata_evalE = [np.flatnonzero(gE == k) for k in range(K)]          # positions WITHIN E
    D.mmlu = np.array([canon(Q[int(q)][0]) == "MMLU_PRO" for q in D.qids[D.E]], dtype=bool)
    D.srcE = np.array([Q[int(q)][0] for q in D.qids[D.E]])
    D.fit_asserts = 0
    return D


def hygiene(D, cfg):
    """Guard (2): printed and asserted. Refusal (G3) on any failure."""
    inter = D.train_set & D.pool_set
    print("|routed| = %d (complete %d) | |TRAIN| = %d (registered %d) | |EVAL| = %d (registered %d) | |pool rows| = %d"
          % (D.n, D.n_complete, len(D.train_set), cfg.reg["n_train"], len(D.eval_set), cfg.reg["n_eval"], len(D.pool_set)))
    print("ASSERT |TRAIN intersect %s| == 0: %d -> %s" % (cfg.pool_id, len(inter), "PASS" if not inter else "FAIL"))
    bad = []
    if inter: bad.append("TRAIN intersects the pool on %d ids" % len(inter))
    if len(D.eval_set) != cfg.reg["n_eval"]: bad.append("|EVAL| %d != %d" % (len(D.eval_set), cfg.reg["n_eval"]))
    if D.eval_set != D.pool_set: bad.append("EVAL != pool (%d pool ids unrouted or incomplete)" % len(D.pool_set - D.eval_set))
    if len(D.train_set) != cfg.reg["n_train"]: bad.append("|TRAIN| %d != %d" % (len(D.train_set), cfg.reg["n_train"]))
    if D.n != cfg.reg["n_routed"]: bad.append("|routed| %d != %d" % (D.n, cfg.reg["n_routed"]))
    if bad:
        raise SystemExit("[G3(2)] hygiene assertion failed: " + "; ".join(bad))


def gate_g1(D, cfg):
    s, d = "%.3f" % D.src_ok, "%.3f" % D.dom_ok
    ok = (s == cfg.reg["g1_src"] and d == cfg.reg["g1_dom"])
    print("G1: %d questions routed over %d federated leaves (dim %d) | predicted source %s | predicted source+domain %s "
          "| registered %s / %s -> %s" % (D.n, D.n_leaves, D.dim, s, d, cfg.reg["g1_src"], cfg.reg["g1_dom"],
                                         "PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit("[G1] routing accuracy not reproduced: %s / %s vs %s / %s" % (s, d, cfg.reg["g1_src"], cfg.reg["g1_dom"]))


def strata_table(D, cfg):
    """The 52-stratum table (EVAL n, TRAIN n), the sum of squares and the Kish mean stratum size; compared with the record."""
    print("\n52-STRATUM TABLE (true SOURCE/domain; EVAL n | TRAIN n | registered EVAL n):")
    rows = []
    for k, key in enumerate(D.strata_keys):
        kr = key_of_record(*key); ne = len(D.strata_evalE[k]); nt = len(D.strata_train[k])
        rows.append((kr, ne, nt)); print("  %-50s %5d %6d   %s" % (kr, ne, nt, cfg.reg_strata.get(kr, "-")))
    s2 = sum(ne * ne for _, ne, _ in rows); ne_tot = sum(ne for _, ne, _ in rows)
    table_ok = {kr: ne for kr, ne, _ in rows} == cfg.reg_strata
    print("  strata %d (registered %d) | sum n^2 = %d (registered %d) | Kish mean stratum size %.1f (registered %s) | "
          "EVAL table equals the table of record: %s"
          % (len(rows), cfg.reg["n_strata"], s2, cfg.reg["sum_n2"], s2 / max(1, ne_tot), cfg.reg["kish"],
             "MATCH" if table_ok else "MISMATCH (descriptive; the hygiene gate G3 is what refuses)"))
    return s2, ne_tot


def main_routing_readout(D, cfg):
    """DESCRIPTIVE cross-check against the routing files of record (MAIN_union_routing*, flatLeaf on the union graft; a
    DIFFERENT router object from this instrument's federated nearest centroid). True labels: per-key EVAL counts."""
    summ = os.path.join(cfg.routing_dir, "MAIN_union_routing_summary.txt")
    qcsv = os.path.join(cfg.routing_dir, "MAIN_union_routing_queries.csv")
    if not (os.path.isfile(summ) and os.path.isfile(qcsv)):
        print("MAIN_union_routing files absent at %s: cross-check NOT PRINTED (descriptive only)" % cfg.routing_dir)
        return None
    kv = dict(l.strip().split("=", 1) for l in open(summ, encoding="utf-8") if "=" in l)
    with open(qcsv, encoding="utf-8", newline="") as f:
        csv_counts = Counter(r["true_key"] for r in csv.DictReader(f))
    mine = Counter(key_of_record(*D.strata_keys[int(k)]) for k in D.g_tdom[D.E])
    e_src = np.mean([canon(D.psrc[int(q)]) == D.Q[int(q)][0] for q in D.qids[D.E]])
    e_dom = np.mean([canon(D.psrc[int(q)]) == D.Q[int(q)][0] and D.pdom[int(q)] == D.Q[int(q)][1] for q in D.qids[D.E]])
    same = bool(csv_counts == mine)
    print("ROUTING OF RECORD (descriptive; MAIN_union_routing_summary.txt, rule=%s, n=%s): top1 %s, source %s | this "
          "instrument on the %d EVAL questions: source %.4f, source+domain %.4f | per-key EVAL counts vs "
          "MAIN_union_routing_queries.csv true_key: %s"
          % (kv.get("rule", "?"), kv.get("n", "?"), kv.get("top1", "?"), kv.get("source_accuracy", "?"), len(D.E), e_src,
             e_dom, "MATCH (%d keys)" % len(mine) if same else "MISMATCH (%d keys differ)" % len(set(csv_counts) ^ set(mine)
                                                                                           | {k for k in mine if csv_counts.get(k) != mine[k]})))
    return same


# ============================================================================================ policies
class Policy:
    pass


def fit_policies(D, w, side_set, side_name):
    """Fit EVERY policy on the questions carrying weight w (integer multiplicities over D's positions). THE ASSERT AT THE CALL
    (guard 4): the support of w must be a subset of side_set (TRAIN of record for every clean fit)."""
    nz = np.flatnonzero(w)
    support = set(int(q) for q in D.qids[nz])
    if not support <= side_set:
        raise SystemExit("[G3(4)] a policy fit received %d question(s) outside %s" % (len(support - side_set), side_name))
    D.fit_asserts += 1
    m = len(D.models)
    W = D.A * w[:, None]
    P = Policy()
    P.gb = int(np.argmax(W.sum(axis=0)))                     # first max = first model in sorted-name order
    Wr = W.ravel().astype(np.float64); wf = w.astype(np.float64)
    P.pol = {}
    for k, (g, ng, mm) in D.groupings.items():
        S = np.bincount(D.flat[k], weights=Wr, minlength=ng * m).reshape(ng, m)
        mass = np.bincount(g, weights=wf, minlength=ng)
        pol = S.argmax(axis=1).astype(np.int64)
        pol[mass < max(1, mm)] = -1                         # absent group (no TRAIN mass, or a leaf below min_leaf)
        P.pol[k] = pol
    return P


def fit_clean(D, w):
    """Every clean fit: TRAIN of record, and additionally zero weight on every EVAL position (numeric form of the same)."""
    if int(w[D.E].sum()) != 0:
        raise SystemExit("[G3(4)] weight on EVAL positions")
    return fit_policies(D, w, D.train_set, "TRAIN of record")


def correctness(D, P):
    """8 x n matrix of 0/1: rows = ARMS. Fallbacks exactly MC-E2E pick() L103-L109."""
    n = D.n; gb = np.full(n, P.gb, dtype=np.int64)
    res = lambda k, fb: np.where(P.pol[k][D.groupings[k][0]] < 0, fb, P.pol[k][D.groupings[k][0]])
    tsrc = res("tsrc", gb); tdom = res("tdom", gb); psrc = res("psrc", gb)
    pdom = res("pdom", psrc)                                  # p_dom.get(key, p_src.get(src, gb))
    pdom_gb = res("pdom", gb)                                 # p_dom.get(key, gb), the leaf fallback
    pleaf = res("pleaf", pdom_gb); plac = res("plac", gb)
    r = np.arange(n); A = D.A
    return np.stack([A[r, gb], A[r, tsrc], A[r, tdom], A[r, psrc], A[r, pdom], A[r, pleaf], A.max(axis=1), A[r, plac]])


def picks_named(D, P):
    return dict(best_single=D.models[P.gb],
                tdom={key_of_record(*D.strata_keys[i]): (D.models[p] if p >= 0 else None) for i, p in enumerate(P.pol["tdom"])},
                pleaf={D.pleaf_keys[i]: (D.models[p] if p >= 0 else None) for i, p in enumerate(P.pol["pleaf"])})


def strat_counts(rng, groups, size):
    """Within-stratum resample: each group keeps its size; multiplicities returned over `size` positions."""
    w = np.zeros(size, dtype=np.int64)
    for idx in groups:
        if len(idx):
            w[idx] += np.bincount(rng.integers(0, len(idx), len(idx)), minlength=len(idx))
    return w


def score_E(CE, v, mmlu):
    tot = v.sum(); acc = CE @ v / tot
    vm = v[mmlu]; accm = (CE[:, mmlu] @ vm / vm.sum()) if vm.sum() else np.full(CE.shape[0], np.nan)
    return acc, accm


def train_full_w(D):
    w = np.zeros(D.n, dtype=np.int64); w[D.T] = 1
    return w


def run_bootstraps(D, B, seed, log=print, hook=None):
    """Point (policy fitted once on TRAIN, scored on all EVAL) and the four bootstraps, each from default_rng(seed)."""
    P0 = fit_clean(D, train_full_w(D)); C0 = correctness(D, P0); CE0 = C0[:, D.E].astype(np.float64)
    NE = len(D.E); ones = np.ones(NE, dtype=np.int64)
    point, point_m = score_E(CE0, ones, D.mmlu)
    out = dict(P0=P0, point=point, point_m=point_m)
    rng = np.random.default_rng(seed); iid = np.empty((B, 8)); iid_m = np.empty((B, 8))
    for b in range(B):
        v = np.bincount(rng.integers(0, NE, NE), minlength=NE); iid[b], iid_m[b] = score_E(CE0, v, D.mmlu)
    rng = np.random.default_rng(seed); cl = np.empty((B, 8)); K = len(D.strata_evalE)
    for b in range(B):
        v = np.zeros(NE, dtype=np.int64)
        for k in rng.integers(0, K, K): v[D.strata_evalE[k]] += 1
        cl[b] = CE0 @ v / v.sum()
    rng = np.random.default_rng(seed); two = np.empty((B, 8)); two_m = np.empty((B, 8))
    for b in range(B):
        w = strat_counts(rng, D.strata_train, D.n); P = fit_clean(D, w)
        CE = correctness(D, P)[:, D.E].astype(np.float64)
        v = strat_counts(rng, D.strata_evalE, NE); two[b], two_m[b] = score_E(CE, v, D.mmlu)
        if hook: hook("two", w, v)                            # selftest observation only; the CLI never passes one
        if log and (b + 1) % 500 == 0: log("  two-stage replicate %d / %d" % (b + 1, B))
    rng = np.random.default_rng(seed); tro = np.empty((B, 8))
    for b in range(B):
        w = strat_counts(rng, D.strata_train, D.n); P = fit_clean(D, w)
        tro[b] = correctness(D, P)[:, D.E].astype(np.float64).mean(axis=1)
        if hook: hook("tro", w, None)
        if log and (b + 1) % 500 == 0: log("  TRAIN-only replicate %d / %d" % (b + 1, B))
    out.update(iid=iid, iid_m=iid_m, cl=cl, two=two, two_m=two_m, tro=tro, B=B)
    return out


def _var(x):
    """Sample variance; EXACTLY 0 for a constant vector (np.var of identical floats can round to 1e-35 through the mean)."""
    x = np.asarray(x, dtype=np.float64)
    return 0.0 if float(np.ptp(x)) == 0.0 else float(np.var(x, ddof=1))


def _sd(x):
    return math.sqrt(_var(x))


def _ratio(a, b):
    return float(a / b) if b > 0 else float("nan")


def contrast_stats(bt, a, b, sub):
    if sub == "mmlu":
        pt = float(bt["point_m"][a] - bt["point_m"][b])
        d2 = bt["two_m"][:, a] - bt["two_m"][:, b]; di = bt["iid_m"][:, a] - bt["iid_m"][:, b]
        dc = None; dt = None
    else:
        pt = float(bt["point"][a] - bt["point"][b])
        d2 = bt["two"][:, a] - bt["two"][:, b]; di = bt["iid"][:, a] - bt["iid"][:, b]
        dc = bt["cl"][:, a] - bt["cl"][:, b]; dt = bt["tro"][:, a] - bt["tro"][:, b]
    se2 = _sd(d2); sei = _sd(di)
    c = dict(point=pt, se2=se2, lo=pt - 1.96 * se2, hi=pt + 1.96 * se2, se_iid=sei,
             pct=tuple(float(x) for x in np.percentile(d2, [2.5, 97.5])),
             se_cl=_sd(dc) if dc is not None else float("nan"), se_tro=_sd(dt) if dt is not None else float("nan"),
             var2=se2 ** 2, var_iid=sei ** 2, var_tro=(_sd(dt) ** 2 if dt is not None else float("nan")))
    c["deff2"] = _ratio(c["var2"], c["var_iid"]); c["deff_cl"] = _ratio(c["se_cl"] ** 2, c["var_iid"])
    return c, d2, dt


def phi_stats(d2, dt):
    """R3: phi = Var(G | TRAIN-only) / Var(G | two-stage), with its Monte-Carlo SE (delta method, the two variance estimates
    treated as independent; Var(s^2) ~ (m4 - s^4 (B-3)/(B-1)) / B)."""
    v2 = _var(d2); vt = _var(dt)
    if not v2 > 0:
        _br("G4.REFUSED")
        raise SystemExit("[G4] the two-stage variance of G is %r: phi is undefined; refusing (ruling e, d6b5ca8)" % v2)
    phi = vt / v2
    def rel(x):
        B = len(x); s2 = _var(x)
        if s2 <= 0: return 0.0
        m4 = float(np.mean((x - x.mean()) ** 4))
        return max(0.0, (m4 - s2 * s2 * (B - 3) / (B - 1)) / B) / (s2 * s2)
    return phi, phi * math.sqrt(rel(d2) + rel(dt)), vt, v2


def gate_g4(d2s):
    """Ruling (e), refusal gate G4: a zero two-stage variance of any DECIDING statistic (G for C1, P for C4) refuses."""
    for k in ("C1", "C4"):
        if _var(d2s[k]) == 0.0:
            _br("G4.REFUSED")
            raise SystemExit("[G4] the two-stage variance of %s is 0: every interval is degenerate; refusing (ruling e, "
                             "d6b5ca8)" % k)


# ============================================================================================ legacy (G2)
def legacy_split(D, seed, ratio):
    """MC-E2E L86-L90 verbatim over D.qq (MC-E2E's qq: sorted complete questions with a vector)."""
    Q = D.Q
    rng = random.Random(seed); strata = defaultdict(list)
    for q in D.qq: strata[(Q[q][0], Q[q][1])].append(q)
    train, test = [], []
    for k, v in sorted(strata.items()):
        v = v[:]; rng.shuffle(v); n = int(round(len(v) * ratio)); test += v[:n]; train += v[n:]
    return rng, train, test


def legacy_seed(D, cfg, with_boot, boots=200):
    """MC-E2E L86-L125 at one seed with --clean --mathfix: fit on the legacy train (which holds EVAL questions by design,
    reading (e)); restrict test to the pool; point gain; with_boot reproduces the record's 200-boot SEs with the record's
    continuing random.Random stream. Returns (lines, dep, n)."""
    seed = cfg.reg["g2_seed"]
    rng, train, test = legacy_split(D, seed, cfg.reg["g2_ratio"])
    pos = {int(q): i for i, q in enumerate(D.qids)}
    w = np.zeros(D.n, dtype=np.int64); w[[pos[q] for q in train]] = 1
    P = fit_policies(D, w, frozenset(train), "LEGACY train (seed %d; holds EVAL questions by design)" % seed)
    C = correctness(D, P)[:7]
    before = len(test); test = [q for q in test if q in D.pool_set]
    lines = ["  CLEAN: reserved side restricted to the tree's held-out pool, %d of %d kept (%.1f%%)"
             % (len(test), before, 100.0 * len(test) / max(1, before))]
    tp = np.array([pos[q] for q in test], dtype=np.int64)
    score = lambda idx: C[:, idx].sum(axis=1) / len(idx)
    o = score(tp); dep = float(o[4] - o[0]); orc = float(o[2] - o[0])
    if with_boot:
        bs = np.array([score(tp[[rng.randrange(len(tp)) for _ in range(len(tp))]]) for _ in range(boots)])
        se = bs.std(axis=0, ddof=1); se_dep = np.std(bs[:, 4] - bs[:, 0], ddof=1); se_orc = np.std(bs[:, 2] - bs[:, 0], ddof=1)
        lines.append("seed %d (reserved n=%d)" % (seed, len(tp)))
        for i, nm in enumerate(ARMS[:7]): lines.append("  %-20s %.4f +- %.4f" % (nm, o[i], se[i]))
        lines.append("  DEPLOYED gain (PRED source/domain - best single): %+.4f +- %.4f -> %s"
                     % (dep, se_dep, "REAL" if dep > 2 * se_dep else "not resolved"))
        lines.append("  oracle-metadata gain %+.4f +- %.4f | METADATA COST %+.4f" % (orc, se_orc, orc - dep))
    return lines, dep, len(tp)


def gate_g2(D, cfg):
    _, dep, n = legacy_seed(D, cfg, with_boot=False)
    ok = ("%+.4f" % dep == cfg.reg["g2_gain"] and n == cfg.reg["g2_n"])
    print("G2: legacy MC-E2E construction (seed %d, ratio %.2f, --clean --mathfix): deployed gain %+.4f on n = %d | "
          "registered %s on n = %d -> %s" % (cfg.reg["g2_seed"], cfg.reg["g2_ratio"], dep, n, cfg.reg["g2_gain"],
                                             cfg.reg["g2_n"], "PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit("[G2] the legacy code path does not reproduce the record: %+.4f / %d" % (dep, n))


_NUM = re.compile(r"[+-]?\d+\.\d+|\d+")


def compare_legacy_block(lines, path):
    """Descriptive: every number of the seed-42 block against the record file's seed-42 block (encoding-free)."""
    if not os.path.isfile(path):
        print("  record file %s absent: numeric comparison NOT PRINTED" % path); return None
    raw = open(path, "rb").read().decode("utf-8", errors="replace").splitlines()
    try:
        i = next(j for j, l in enumerate(raw) if l.startswith("seed %s " % lines[1].split()[1]))
    except StopIteration:
        print("  record file has no matching seed block"); return None
    rec = raw[i - 1:i + 10]
    a = [_NUM.findall(l) for l in lines]; b = [_NUM.findall(l) for l in rec]
    same = bool(a == b)
    print("  legacy block vs %s (numbers only, %d lines): %s" % (os.path.basename(path), len(lines),
                                                                "IDENTICAL" if same else "DIFFERENT"))
    return same


# ============================================================================================ verdicts
# Ruling (a) of d6b5ca8 (programme L13644-L13689): the two REGISTERED pre-empting triggers, their wording verbatim.
T1_WORD = "C4 FAILED, the instrument manufactures gain from noise"
T2_WORD = "C0 FAILED, two instruments disagree about the same object"
NOT_LIFTED = ("NOT LIFTED WITHIN THIS RUN: a reading requires the reviewer's written finding of which instrument is wrong AND "
              "a dated registration amendment committed before any re-read")
C4_VOID = "every number of this test is void and the instrument is defective"

_HIT = set()
ALL_BRANCHES = frozenset([
    "C0.HELD", "C0.FAILED", "TRIG.NONE", "TRIG.T1", "TRIG.T2", "TRIG.BOTH",
    "C1.HELD", "C1.FAILED", "C1.UNDETERMINED", "C1.BY_TRIGGER",
    "C2.ABOVE", "C2.BELOW", "C2.CONTAINS", "C2.BY_TRIGGER", "C3.ABOVE", "C3.BELOW", "C3.CONTAINS", "C3.BY_TRIGGER",
    "C4.HELD", "C4.FAILED", "C4.BY_TRIGGER", "R3.HELD", "R3.FAILED", "R3.BY_TRIGGER", "R4.PRINT", "R4.BY_TRIGGER",
    "P1.HELD", "P1.FAILED", "P1.BY_TRIGGER", "P2.HELD", "P2.FAILED", "P2.BY_TRIGGER", "P3.HELD", "P3.FAILED",
    "P3.BY_TRIGGER", "P4.HELD", "P4.FAILED", "P4.BY_TRIGGER", "P4.SCORED_UNDER_T1", "P5.HELD", "P5.FAILED",
    "P5.BY_TRIGGER", "P6.HELD", "P6.FAILED", "P7.HELD", "P7.FAILED", "P7.BY_TRIGGER",
    "F.NOT_EVALUATED", "F.VOID", "F.NOT_LIFTED", "F.OVERTURN", "F.REPLACE", "G4.REFUSED", "WAL.REFUSED"])


def _br(name):
    _HIT.add(name)
    return name


def _three(c):
    lo, hi = float(c["lo"]), float(c["hi"])
    return "ABOVE" if bool(lo > 0) else ("BELOW" if bool(hi < 0) else "CONTAINS")


def _pp(x):
    return "%+.2fpp" % (100 * float(x))


def support_block(name, c, n_eval):
    p = PLAN[name]
    d2 = float(c["deff2"]); dcl = float(c["deff_cl"])
    ne = (n_eval / d2) if d2 > 0 else float("nan"); necl = (n_eval / dcl) if dcl > 0 else float("nan")
    L = ["    SUPPORT (measured): SE_iid %.5f | SE_2stage %.5f -> DEFF_2stage %.3f, n_eff %.0f, MDE80 = 2.80 x SE = %s"
         % (c["se_iid"], c["se2"], d2, ne, _pp(2.80 * c["se2"])),
         "      52-cell clustered SE %.5f -> DEFF_cl %.3f, n_eff %.0f, MDE80 %s (DESCRIPTIVE-ONLY) | TRAIN-only SE %.5f"
         % (c["se_cl"], dcl, necl, _pp(2.80 * c["se_cl"]), c["se_tro"])]
    reg = "    SUPPORT (registered plan): %s; " % p["verdict"]
    reg += ", ".join("%s %s" % (k, v) for k, v in p.items() if k != "verdict")
    L.append(reg)
    return L


def verdict_lines(st):
    """Every criterion, prediction and falsifier branch, in the order ruling (a) fixes: triggers first, then the criteria
    they do not pre-empt. `st` holds plain numbers (numpy scalars welcome: every comparison is wrapped in bool(), never
    identity-tested). res values are plain words: HELD / FAILED / UNDETERMINED / DESCRIPTIVE (...) /
    UNDETERMINED (BY TRIGGER: ...)."""
    L = []; res = {}
    c0 = st["c0"]; con = st["con"]
    c0_ok = bool(c0["bs_name"] == c0["exp_name"] and "%.4f" % float(c0["bs_acc"]) == c0["exp_bs"]
                 and "%.4f" % float(c0["tdom_acc"]) == c0["exp_tdom"])
    # C0 is scored in EVERY branch (ruling (a)).
    res["C0"] = "HELD" if c0_ok else "FAILED"; _br("C0.HELD" if c0_ok else "C0.FAILED")
    L.append("C0 CROSS-INSTRUMENT REPRODUCTION: best single %s %.4f, TRUE (source, domain) %.4f | registered %s %s / %s -> %s"
             % (c0["bs_name"], float(c0["bs_acc"]), float(c0["tdom_acc"]), c0["exp_name"], c0["exp_bs"], c0["exp_tdom"],
                "HELD" if c0_ok else "FAILED"))
    c4 = con["C4"]
    t1 = bool(float(c4["lo"]) > 0)          # T1 is computed on the numbers even when T2 fires
    t2 = not c0_ok
    words = ([T1_WORD] if t1 else []) + ([T2_WORD] if t2 else [])
    trig = bool(t1 or t2)
    tag = "UNDETERMINED (BY TRIGGER: %s)" % "; ".join(words) if trig else None
    if t1 and t2:
        _br("TRIG.BOTH"); L.append("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): T1 and T2 FIRED (both named): "
                                   "T1 %s; T2 %s" % (T1_WORD, T2_WORD))
    elif t1:
        _br("TRIG.T1"); L.append("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): T1 FIRED: %s" % T1_WORD)
    elif t2:
        _br("TRIG.T2"); L.append("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): T2 FIRED: %s" % T2_WORD)
    else:
        _br("TRIG.NONE"); L.append("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): none fired (C0 HELD; C4's "
                                   "two-stage interval not wholly above 0)")
    if t2:
        _br("F.NOT_LIFTED"); L.append("  T2: " + NOT_LIFTED)
    # C1
    c1 = con["C1"]
    L.append("C1 DEPLOYED GAIN G = acc(PRED source/domain) - acc(best single) = %s | DECIDING two-stage interval "
             "[%s, %s] (point +- 1.96 x %.5f) | beside, deciding nothing: percentile [%s, %s], i.i.d. SE %.5f, 52-cell "
             "clustered SE %.5f | bar 0" % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"]), c1["se2"], _pp(c1["pct"][0]),
                                            _pp(c1["pct"][1]), c1["se_iid"], c1["se_cl"]))
    L += support_block("C1", c1, st["n_eval"])
    if trig:
        _br("C1.BY_TRIGGER"); res["C1"] = tag; L.append("  C1 -> %s; printed, NOT scored" % tag)
    else:
        r = _three(c1)
        if r == "ABOVE":
            _br("C1.HELD"); res["C1"] = "HELD"; L.append("  C1 -> HELD (the two-stage interval lies wholly above 0)")
        elif r == "BELOW":
            _br("C1.FAILED"); res["C1"] = "FAILED"; L.append("  C1 -> FAILED (the two-stage interval lies wholly below 0)")
        else:
            _br("C1.UNDETERMINED"); res["C1"] = "UNDETERMINED"
            L.append("  C1 -> UNDETERMINED (the two-stage interval contains 0)")
    # C2, C3 (DESCRIPTIVE-ONLY by support; pre-empted by either trigger)
    for nm, title in (("C2", "PRED(source, domain) - PRED(source)"), ("C3", "PRED leaf - PRED(source, domain)")):
        c = con[nm]
        L.append("%s %s = %s | two-stage interval [%s, %s] | percentile [%s, %s] | i.i.d. SE %.5f" %
                 (nm, title, _pp(c["point"]), _pp(c["lo"]), _pp(c["hi"]), _pp(c["pct"][0]), _pp(c["pct"][1]), c["se_iid"]))
        L += support_block(nm, c, st["n_eval"])
        if trig:
            _br("%s.BY_TRIGGER" % nm); res[nm] = tag; L.append("  %s -> %s; printed, NOT scored" % (nm, tag))
        else:
            r = _three(c); _br("%s.%s" % (nm, r))
            word = {"ABOVE": "lies wholly ABOVE 0", "BELOW": "lies wholly BELOW 0", "CONTAINS": "CONTAINS 0"}[r]
            L.append("  %s -> DESCRIPTIVE-ONLY BY SUPPORT: the interval %s; no HELD / FAILED is recorded" % (nm, word))
            res[nm] = "DESCRIPTIVE (%s)" % r
        if nm == "C3":
            L.append("    beside MC-LEAF's -0.9 +- 0.3pp: that SE is i.i.d. and its reserved side carries the open "
                     "[FLAG 2026-09-15]")
    # C4 (pre-empted by T2 only; T1 is its own FAILED)
    L.append("C4 PLACEBO P = acc(placebo) - acc(best single) = %s | DECIDING two-stage interval [%s, %s] | percentile "
             "[%s, %s]" % (_pp(c4["point"]), _pp(c4["lo"]), _pp(c4["hi"]), _pp(c4["pct"][0]), _pp(c4["pct"][1])))
    L += support_block("C4", c4, st["n_eval"])
    if t2:
        t2tag = "UNDETERMINED (BY TRIGGER: %s)" % T2_WORD
        _br("C4.BY_TRIGGER"); res["C4"] = t2tag
        L.append("  C4 -> %s; printed, NOT scored%s" % (t2tag, " (T1 is still NAMED: the interval lies wholly above 0)"
                                                         if t1 else ""))
    elif t1:
        _br("C4.FAILED"); res["C4"] = "FAILED"
        L.append("  C4 -> FAILED (the two-stage interval lies wholly above 0: %s)" % T1_WORD)
    else:
        _br("C4.HELD"); res["C4"] = "HELD"; L.append("  C4 -> HELD (the interval does not lie wholly above 0)")
    if t1:
        L.append("  C4 consequence: %s." % C4_VOID)
    # R3
    phi, mc = float(st["phi"]), float(st["phi_mcse"])
    L.append("R3 POLICY-VARIANCE SHARE phi = Var(G | TRAIN-only) / Var(G | two-stage) = %.5f / %.5f = %.4f "
             "(Monte-Carlo SE %.4f) | bar 0.5, the point decides" % (st["var_tro"], st["var2"], phi, mc))
    if trig:
        _br("R3.BY_TRIGGER"); res["R3"] = tag; L.append("  R3 -> %s; printed, NOT scored" % tag)
    elif bool(phi < 0.5):
        _br("R3.HELD"); res["R3"] = "HELD"; L.append("  R3 -> HELD (policy-stable: phi < 0.5)")
    else:
        _br("R3.FAILED"); res["R3"] = "FAILED"
        L.append("  R3 -> FAILED (phi >= 0.5: the gain's uncertainty is dominated by which models the policy picked)")
    # R4, ALL of it
    m = con["M"]; mm = con["C1_MMLU"]
    r4s = (" -> %s; printed, NOT read" % tag) if trig else ""
    L.append("R4 (DESCRIPTIVE) METADATA COST M = acc(TRUE s/d) - acc(PRED s/d) = %s, two-stage [%s, %s], i.i.d. SE %.5f "
             "(the record's +0.71pp is a three-seed mean on the contaminated-fit split)%s"
             % (_pp(m["point"]), _pp(m["lo"]), _pp(m["hi"]), m["se_iid"], r4s))
    L.append("R4 (DESCRIPTIVE) MMLU-Pro-source subset of C1 (n = %d, registered %d; NOT a control): G = %s, two-stage "
             "[%s, %s], i.i.d. SE %.5f%s" % (st["n_mmlu"], st["n_mmlu_reg"], _pp(mm["point"]), _pp(mm["lo"]), _pp(mm["hi"]),
                                              mm["se_iid"], r4s))
    if trig:
        _br("R4.BY_TRIGGER"); res["R4"] = tag
        L.append("R4 tables below -> %s; printed, NOT read" % tag)
    else:
        _br("R4.PRINT"); res["R4"] = "DESCRIPTIVE"
    for line in st.get("r4_lines", []): L.append(line)
    # predictions (ruling (b))
    vals = {"C1": c1["point"], "C2": con["C2"]["point"], "C3": con["C3"]["point"], "C4": c4["point"],
            "M": m["point"], "phi": phi}
    L.append("PREDICTIONS (ruling (b): HELD iff the observed point lies in the registered interval, endpoints included; "
             "UNDETERMINED (BY TRIGGER) when the criterion is pre-empted, except P4 under T1 alone and P6 always):")
    for pid in ("P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        if pid == "P6":
            ok = c0_ok; res[pid] = "HELD" if ok else "FAILED"; _br("P6.%s" % res[pid])
            L.append("  P6 C0 HELD (0.5912 / 0.6220, Qwen2.5-72B-Instruct) -> %s" % res[pid])
            continue
        what, pt, lo, hi = PRED[pid]; x = float(vals[what])
        fx = ("%.4f" % x) if what == "phi" else _pp(x)
        fr = ("%.2f [%.2f, %.2f]" % (pt, lo, hi)) if what == "phi" else ("%s [%s, %s]" % (_pp(pt), _pp(lo), _pp(hi)))
        pre = t2 if pid == "P4" else trig
        if pre:
            ptag = ("UNDETERMINED (BY TRIGGER: %s)" % T2_WORD) if pid == "P4" else tag
            _br("%s.BY_TRIGGER" % pid); res[pid] = ptag
            L.append("  %s %s predicted %s, observed %s (printed, NOT scored) -> %s" % (pid, what, fr, fx, ptag))
            continue
        ok = bool(lo <= x <= hi); res[pid] = "HELD" if ok else "FAILED"; _br("%s.%s" % (pid, res[pid]))
        if pid == "P4" and t1:
            _br("P4.SCORED_UNDER_T1")
        L.append("  %s %s predicted %s, observed %s -> %s" % (pid, what, fr, fx, res[pid]))
    # falsifier
    if trig:
        _br("F.NOT_EVALUATED"); res["F"] = "NOT EVALUATED (BY TRIGGER: %s)" % "; ".join(words)
        L.append("FALSIFIER: NOT EVALUATED (BY TRIGGER: %s)." % "; ".join(words))
        if t1:
            _br("F.VOID"); L.append("  T1: 'IF C4 FAILS, %s, whatever C1 says.'" % C4_VOID)
        if t2:
            L.append("  T2: " + NOT_LIFTED)
    elif res["C1"] == "HELD":
        _br("F.REPLACE"); res["F"] = "C1 HELD: REPLACE"
        L.append("FALSIFIER: C1 HELD -> the 'PENDING ROUTER-CLEAN-POLICY' clause is discharged the other way: +3.38pp is "
                 "REPLACED by bracket with G = %s, two-stage [%s, %s], as the number of record, and +0.71pp by R4's M = %s "
                 "[%s, %s]." % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"]), _pp(m["point"]), _pp(m["lo"]), _pp(m["hi"])))
    else:
        _br("F.OVERTURN"); res["F"] = "C1 NOT HELD: OVERTURN"
        L.append("FALSIFIER: C1 NOT HELD -> MC-E2E criterion (1) and FRAMEWORK L180's '+3.38pp mean' are OVERTURNED as "
                 "evidence of a real deployed gain on the split of record; the 'PENDING ROUTER-CLEAN-POLICY' clause is "
                 "discharged by a bracket withdrawing the gain claim.")
    L.append("NOT OVERTURNED in any branch: the routing accuracies (96.2% / 81.3%; MC-ROOT 81.58%), MC-ROUTER, "
             "ROUTER-REGRET-MMLU, the A1 bound, any judged result; C2 and C3 are DESCRIPTIVE-ONLY and overturn nothing.")
    return L, res

def r4_tables(D, bt):
    L = ["R4 (DESCRIPTIVE) every arm on the %d EVAL questions (policy fitted once on TRAIN):" % len(D.E),
         "    %-20s %8s %9s %11s" % ("arm", "acc", "SE_iid", "SE_2stage")]
    for i, nm in enumerate(ARMS):
        L.append("    %-20s %8.4f %9.5f %11.5f" % (nm, bt["point"][i], _sd(bt["iid"][:, i]), _sd(bt["two"][:, i])))
    P0 = bt["P0"]; CE0 = correctness(D, P0)[:, D.E]
    L.append("R4 (DESCRIPTIVE) per true source (point accuracies):")
    L.append("    %-14s %5s " % ("source", "n") + " ".join("%9s" % a[:9] for a in ARMS))
    for s in sorted(set(D.srcE.tolist())):
        mk = D.srcE == s
        L.append("    %-14s %5d " % (s, int(mk.sum())) + " ".join("%9.4f" % x for x in CE0[:, mk].mean(axis=1)))
    return L


# ============================================================================================ modes
def prefix(cfg, ff, pid):
    """Guards (1)-(3), (5), G1, the strata table, the descriptive routing cross-check. Common to every real mode. `pid` is
    what guard_pool(cfg) returned: every mode calls guard_pool as its FIRST statement and prefix prints it FIRST."""
    if pid != cfg.pool_id:
        raise SystemExit("[POOL-GUARD] prefix called with %r, not the guarded %s" % (pid, cfg.pool_id))
    print("POOL %s (pool_guard.assert_pool_of_record: id file and reserved_pool rows hash to it and are equal)" % pid)
    for db, size in wal_sidecars(cfg):
        if size:
            _br("WAL.REFUSED")
            raise SystemExit("[WAL] %s-wal is %d bytes (appeared after launch); refusing" % (db, size))
        print("sidecar %s-wal: %s (ruling d: a non-empty -wal refuses at launch)" % (db, "absent" if size is None else "0 bytes"))
    lf, crlf, wt = script_shas()
    print("script %s LF blob sha16 %s (git hash-object, the identity) | CRLF rendering sha16 %s | working tree holds %s"
          % (os.path.basename(__file__), lf, crlf, wt))
    con, got = open_union(cfg)
    print("pool_guard.assert_frozen_pool(con, %s) on the reading connection (mode=ro&immutable=1): %s" % (cfg.pool_id, got))
    try:
        Q, models, G, pool = load_union(con, cfg)
    finally:
        con.close()
    leaves = federated_leaves(cfg, ff)
    dim = len(leaves[0][1])
    vec = ff.embed_matrix(cfg.emb_db, [Q[q][2] for q in sorted(q for q in Q if len(G[q]) == len(models))], dim)
    D = build_data(Q, models, G, pool, leaves, vec, cfg)
    hygiene(D, cfg)
    scored_guard(cfg, D.eval_set)
    gate_g1(D, cfg)
    strata_table(D, cfg)
    main_routing_readout(D, cfg)
    return D


def mode_dry_run(cfg, ff):
    wal_guard(cfg)                                            # ruling (d): before anything opens a DB
    pid = guard_pool(cfg)                                     # FIRST DB-opening statement
    D = prefix(cfg, ff, pid)
    print("\nPLANNED: B = %d for each of the four bootstraps (two-stage DECIDING, i.i.d., TRAIN-only, 52-cell clustered), "
          "numpy default_rng(%d) each; placebo permutation random.Random(%d); min_leaf %d; G2 legacy seed %d ratio %.2f"
          % (cfg.B, cfg.reg["seed"], cfg.reg["placebo_seed"], cfg.reg["min_leaf"], cfg.reg["g2_seed"], cfg.reg["g2_ratio"]))
    print("placebo pseudo-strata: %d, sizes equal to the true strata's: %s"
          % (D.n_plac, "YES" if sorted(Counter(D.g_plac.tolist()).values()) == sorted(Counter(D.g_tdom.tolist()).values())
             else "NO"))
    print("DRY-RUN: zero calls; nothing written. Exit.")
    return D


def mode_legacy(cfg, ff):
    wal_guard(cfg)                                            # ruling (d): before anything opens a DB
    pid = guard_pool(cfg)                                     # FIRST DB-opening statement
    D = prefix(cfg, ff, pid)
    lines, dep, n = legacy_seed(D, cfg, with_boot=True)
    print("\nLEGACY (MC-E2E L86-L125 at seed %d, --clean --mathfix; fitted on the legacy train BY DESIGN):" % cfg.reg["g2_seed"])
    for l in lines: print(l)
    compare_legacy_block(lines, cfg.record_legacy_file)
    ok = ("%+.4f" % dep == cfg.reg["g2_gain"] and n == cfg.reg["g2_n"])
    print("G2: %+.4f on n = %d vs registered %s on n = %d -> %s" % (dep, n, cfg.reg["g2_gain"], cfg.reg["g2_n"],
                                                                    "PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit("[G2] the legacy code path does not reproduce the record")
    print("LEGACY: zero calls; nothing written.")
    return D


class _Tee(io.TextIOBase):
    def __init__(self, a):
        self.a = a; self.buf = []
    def write(self, s):
        self.a.write(s); self.buf.append(s); return len(s)
    def flush(self):
        self.a.flush()


def mode_run(cfg, ff):
    wal_guard(cfg)                                            # ruling (d): before anything opens a DB
    if os.path.exists(cfg.out_path):                          # write-once, before any DB is opened
        raise SystemExit("[WRITE-ONCE] %s exists; an outcome file of record is never overwritten" % cfg.out_path)
    pid = guard_pool(cfg)                                     # FIRST DB-opening statement
    tee = _Tee(sys.stdout)
    with contextlib.redirect_stdout(tee):
        D = prefix(cfg, ff, pid)
        print("%s outcome (zero calls). Registration: docs/judge_v2_program.md L12710-L12909 (2bc6184)." % TEST_ID)
        gate_g2(D, cfg)
        print("\nFITS AND BOOTSTRAPS (B = %d each):" % cfg.B)
        bt = run_bootstraps(D, cfg.B, cfg.reg["seed"])
        expect = 2 * cfg.B + 2
        if D.fit_asserts != expect:
            raise SystemExit("[G3(4)] fit-call count %d != 2B+2 = %d" % (D.fit_asserts, expect))
        print("fit-call TRAIN-subset checks executed and CHECKED: %d == 2B+2 (1 G2 legacy fit against its own train + 1 point "
              "fit + %d two-stage + %d TRAIN-only against the TRAIN of record)" % (D.fit_asserts, cfg.B, cfg.B))
        nm = picks_named(D, bt["P0"])
        print("best single on TRAIN: %s" % nm["best_single"])
        con = {}; d2s = {}; dtc = None
        for k, (a, b, sub) in CONTRASTS.items():
            con[k], d2s[k], dt = contrast_stats(bt, a, b, sub)
            if k == "C1": dtc = dt
        gate_g4(d2s)
        phi, mc, vt, v2 = phi_stats(d2s["C1"], dtc)
        st = dict(c0=dict(bs_name=nm["best_single"], bs_acc=bt["point"][BS], tdom_acc=bt["point"][TDOM],
                          exp_name=cfg.reg["c0_best"], exp_bs=cfg.reg["c0_bs"], exp_tdom=cfg.reg["c0_tdom"]),
                  con=con, phi=phi, phi_mcse=mc, var_tro=vt, var2=v2, n_eval=len(D.E), n_mmlu=int(D.mmlu.sum()),
                  n_mmlu_reg=cfg.reg["n_mmlu"], r4_lines=r4_tables(D, bt))
        print("oracle-metadata gain acc(TRUE s/d) - acc(best single) = %s, two-stage [%s, %s] (the C0 contrast; descriptive)"
              % (_pp(con["ORC"]["point"]), _pp(con["ORC"]["lo"]), _pp(con["ORC"]["hi"])))
        print("\n=== VERDICTS ===")
        lines, res = verdict_lines(st)
        for l in lines: print(l)
        print("\nSUMMARY: " + " | ".join("%s %s" % (k, v) for k, v in res.items()))
        print("Denominator: the %d EVAL questions of %s in %d fixed strata; policies on %d TRAIN questions. Key-scored: no "
              "judge verdict, no wrong(established), tie conventions A/B n/a." % (len(D.E), cfg.pool_id,
                                                                                   len(D.strata_keys), len(D.T)))
    text = "".join(tee.buf)
    os.makedirs(os.path.dirname(cfg.out_path), exist_ok=True)
    try:
        with open(cfg.out_path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        raise SystemExit("[WRITE-ONCE] %s appeared during the run; nothing written" % cfg.out_path)
    print("WROTE %s (write-once)" % cfg.out_path)
    return D, st, res


# ============================================================================================ selftest
class _Checks:
    def __init__(self): self.n = 0; self.sections = Counter()
    def __call__(self, cond, msg, sec):
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED [%s]: %s" % (sec, msg))
        self.n += 1; self.sections[sec] += 1


def _write_fixture(tmp, models, rows, pool_ids, leaves_by_corpus, qvec, mathfix=(), pool_id=None):
    """rows: list of (qid, source, domain, text, {model: 0/1}). leaves_by_corpus: corpus -> [(anchor, [(leaf_id, vec)])].
    Returns a Cfg whose every path lives under tmp."""
    os.makedirs(tmp, exist_ok=True)
    dbp = os.path.join(tmp, "union.db"); embp = os.path.join(tmp, "emb.db")
    con = sqlite3.connect(dbp)
    con.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT, domain TEXT, text TEXT)")
    con.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, is_correct INTEGER)")
    con.execute("CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER)")
    con.execute("CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER)")
    ids_by_key = defaultdict(list)
    for q, s, d, t, cor in rows:
        con.execute("INSERT INTO corpus_questions VALUES (?,?,?,?)", (q, s, d, t))
        for mm, c in cor.items(): con.execute("INSERT INTO eval_results VALUES (?,?,?)", (q, mm, c))
        if q in pool_ids: ids_by_key[key_of_record(s, d)].append(q)
    for q, mm, c in mathfix: con.execute("INSERT INTO eval_results_mathfix VALUES (?,?,?)", (q, mm, c))
    pid = pool_guard.compute_pool_id(ids_by_key) if pool_id is None else pool_id
    for k, ids in ids_by_key.items():
        for q in ids: con.execute("INSERT INTO reserved_pool VALUES (?,?,?)", (pid, k, q))
    con.commit(); con.close()
    idf = os.path.join(tmp, "pool_ids.json")
    with open(idf, "w", encoding="utf-8") as f: json.dump(ids_by_key, f)
    e = sqlite3.connect(embp); e.execute("CREATE TABLE embeddings (query TEXT, vector BLOB)")
    for t, v in qvec.items():
        e.execute("INSERT INTO embeddings VALUES (?,?)", (t, struct.pack(">%df" % len(v), *[float(x) for x in v])))
    e.commit(); e.close()
    tree_dirs = []
    for c, anchors in leaves_by_corpus.items():
        d = os.path.join(tmp, "trees", c); os.makedirs(d, exist_ok=True)
        nodes = [{"id": "root", "depth": 0, "label": "root", "childIds": [], "vmfMu": [0.0]}]
        for ai, (anchor, lvs) in enumerate(anchors):
            aid = "a%d" % ai; nodes[0]["childIds"].append(aid)
            nodes.append({"id": aid, "depth": 1, "label": anchor, "childIds": [l for l, _ in lvs], "vmfMu": [0.0]})
            for lid, v in lvs: nodes.append({"id": lid, "depth": 2, "label": lid, "childIds": [], "vmfMu": list(map(float, v))})
        with open(os.path.join(d, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"nodes": [{"id": "old"}]}) + "\n" + json.dumps({"nodes": nodes}) + "\n")
        tree_dirs.append((c, d))
    rd = os.path.join(tmp, "routing"); os.makedirs(rd, exist_ok=True)
    return Cfg(pool_id=pid, db_override=dbp, id_override=idf, union_db=dbp, emb_db=embp, tree_dirs=tree_dirs,
               routing_dir=rd, record_legacy_file=os.path.join(tmp, "record_legacy.txt"),
               out_path=os.path.join(tmp, "out", "outcome.txt"), reg=dict(REG), reg_strata={}, B=200,
               placebo_override=None)


def _hand_fixture(tmp):
    """The 3-stratum hand fixture of the selftest (values computed by hand in the comments of selftest())."""
    models = ["mA", "mB", "mC"]
    e = {1: [1, 0, 0, 0], 2: [0, 1, 0, 0], 3: [0, 0, 1, 0], 4: [0, 0, 0, 1]}
    spec = [  # qid, source, domain, eval?, leaf(1..4), (mA, mB, mC)
        (1, "SRC1", "d1", 0, 1, (1, 1, 0)), (2, "SRC1", "d1", 0, 1, (1, 0, 0)), (3, "SRC1", "d1", 0, 1, (1, 1, 1)),
        (4, "SRC1", "d1", 0, 1, (0, 0, 0)), (5, "SRC1", "d1", 1, 1, (0, 1, 0)), (6, "SRC1", "d1", 1, 2, (1, 1, 0)),
        (7, "SRC1", "d2", 0, 2, (0, 1, 1)), (8, "SRC1", "d2", 0, 2, (1, 1, 0)), (9, "SRC1", "d2", 0, 2, (0, 1, 1)),
        (10, "SRC1", "d2", 0, 2, (0, 0, 0)), (11, "SRC1", "d2", 1, 2, (0, 1, 1)), (12, "SRC1", "d2", 1, 2, (0, 0, 1)),
        (13, "SRC2", "d3", 0, 3, (0, 0, 1)), (14, "SRC2", "d3", 0, 3, (0, 1, 1)), (15, "SRC2", "d3", 0, 3, (0, 1, 0)),
        (16, "SRC2", "d3", 0, 4, (0, 0, 1)), (17, "SRC2", "d3", 0, 4, (1, 0, 1)),
        (18, "SRC2", "d3", 1, 3, (1, 0, 1)), (19, "SRC2", "d3", 1, 4, (0, 1, 0)), (20, "SRC2", "d3", 1, 3, (1, 0, 0))]
    rows = [(q, s, d, "text-%d" % q, dict(zip(models, cor))) for q, s, d, ev, lf, cor in spec]
    pool = {q for q, s, d, ev, lf, cor in spec if ev}
    qvec = {"text-%d" % q: e[lf] for q, s, d, ev, lf, cor in spec}
    leaves = {"c1": [("SRC1/d1", [("L1", e[1])]), ("SRC1/d2", [("L2", e[2])])],
              "c2": [("SRC2/d3", [("L3", e[3]), ("L4", e[4])])]}
    cfg = _write_fixture(tmp, models, rows, pool, leaves, qvec)
    cfg.reg.update(n_eval=7, n_train=13, n_routed=20, roster=3, g1_src="1.000", g1_dom="0.950", min_leaf=3,
                   c0_best="mB", c0_bs="0.5714", c0_tdom="0.4286", n_mmlu=0, n_strata=3)
    return cfg, spec


def _synthetic_D(cfg, K_sizes, gen, models, seed=7, misroute=0):
    """In-memory Data for the statistical checks. gen(k, side, rng) -> correctness row. Routing is perfect (pred = true)
    unless misroute = m > 0: then every m-th question is placed on the NEXT stratum's leaf (pred != true)."""
    rng = random.Random(seed); Q = {}; G = defaultdict(dict); pool = set(); leaves = []; vec = {}; q = 1
    dim = len(K_sizes)
    for k, (nt, ne) in enumerate(K_sizes):
        u = np.zeros(dim); u[k] = 1.0
        leaves.append(("c:L%d" % k, u, "S%d" % k, "d%d" % k))
        for side, cnt in (("train", nt), ("eval", ne)):
            for _ in range(cnt):
                Q[q] = ("S%d" % k, "d%d" % k, "t%d" % q); vec["t%d" % q] = u
                if misroute and q % misroute == 1:
                    u2 = np.zeros(dim); u2[(k + 1) % len(K_sizes)] = 1.0; vec["t%d" % q] = u2
                for mm, c in zip(models, gen(k, side, rng)): G[q][mm] = int(c)
                if side == "eval": pool.add(q)
                q += 1
    return build_data(Q, models, G, pool, leaves, vec, cfg), Q, G, pool, leaves, vec


def selftest():
    import free_tests_f4_f7 as ff
    chk = _Checks()
    tmp = tempfile.mkdtemp(prefix="rcp_selftest_")
    real_connect = sqlite3.connect
    opened = []

    def guarded_connect(path, *a, **k):
        p = str(path)
        plain = p[5:].split("?")[0] if p.startswith("file:") else p
        if not os.path.abspath(plain).replace("\\", "/").lower().startswith(os.path.abspath(tmp).replace("\\", "/").lower()):
            raise RuntimeError("SELFTEST opened a non-fixture DB: %s" % p)
        opened.append(plain)
        return real_connect(path, *a, **k)
    sqlite3.connect = guarded_connect
    old_hit = set(_HIT); _HIT.clear()
    try:
        # ---------------------------------------------------------------- S0 static: every declared branch has a _br literal
        src = open(os.path.abspath(__file__), encoding="utf-8").read()
        code = src[:src.index("\ndef selftest(")]
        lits = set()
        for line in code.splitlines():
            if "_br(" in line:
                lits |= set(re.findall(r'"([A-Z][A-Z0-9]*\.[A-Z][A-Z0-9_]*)"', line))
        templates = {'_br("%s.BY_TRIGGER" % nm)': {"C2.BY_TRIGGER", "C3.BY_TRIGGER"},
                     '_br("%s.%s" % (nm, r))': {"%s.%s" % (a, b) for a in ("C2", "C3") for b in ("ABOVE", "BELOW", "CONTAINS")},
                     '_br("P6.%s" % res[pid])': {"P6.HELD", "P6.FAILED"},
                     '_br("%s.BY_TRIGGER" % pid)': {"%s.BY_TRIGGER" % a for a in ("P1", "P2", "P3", "P4", "P5", "P7")},
                     '_br("%s.%s" % (pid, res[pid]))': {"%s.%s" % (a, b) for a in ("P1", "P2", "P3", "P4", "P5", "P7")
                                                         for b in ("HELD", "FAILED")}}
        dyn = set()
        for t, names in templates.items():
            chk(t in code, "dynamic branch site %s present" % t, "S0"); dyn |= names
        chk((lits | dyn) == set(ALL_BRANCHES), "declared branches vs source: only declared %s, only in source %s"
            % (sorted(set(ALL_BRANCHES) - lits - dyn), sorted((lits | dyn) - set(ALL_BRANCHES))), "S0")

        # ---------------------------------------------------------------- S1 hand fixture, end to end through the DB layer
        cfg, spec = _hand_fixture(os.path.join(tmp, "hand"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            D = prefix(cfg, ff, guard_pool(cfg))                  # guard (1) first, on the fixture (db / id_file overrides)
        out = buf.getvalue()
        chk(out.splitlines()[0].startswith("POOL %s" % cfg.pool_id), "first printed line is the pool id", "S1")
        chk("ASSERT |TRAIN intersect %s| == 0: 0 -> PASS" % cfg.pool_id in out, "disjointness print", "S1")
        chk("ASSERT %s not in roster: ABSENT" % EXCLUDED in out, "Meta-Llama print", "S1")
        chk("reserved_pool_id=%s\nscored_minus_eval=0" % cfg.pool_id in out, "scored_minus_eval print", "S1")
        chk("-> PASS" in out.split("G1:")[1].splitlines()[0], "G1 on the fixture", "S1")
        chk(len(D.train_set) == 13 and len(D.eval_set) == 7, "sides 13 / 7", "S1")
        # Hand values. TRAIN totals mA 5, mB 7, mC 7 -> tie mB/mC -> gb = mB (sorted-name tie-break).
        P = fit_clean(D, train_full_w(D))
        chk(D.models[P.gb] == "mB", "gb = mB by the sorted-name tie-break", "S1")
        nmd = picks_named(D, P)
        # S1 TRAIN mA 3 mB 2 mC 1 -> mA, although EVAL S1 says mB (mA 1, mB 2): TRAIN-ONLY fitting.
        chk(nmd["tdom"] == {"SRC1/d1": "mA", "SRC1/d2": "mB", "SRC2/d3": "mC"}, "TRUE s/d picks %s" % nmd["tdom"], "S1")
        # L3 TRAIN (q13-15): mA 0, mB 2, mC 2 -> tie -> mB; L4 has 2 TRAIN < min_leaf 3 -> absent (fallback p_dom = mC).
        chk(nmd["pleaf"] == {"c1:L1": "mA", "c1:L2": "mB", "c2:L3": "mB", "c2:L4": None}, "leaf picks %s" % nmd["pleaf"], "S1")
        C = correctness(D, P)[:, D.E]
        acc = C.sum(axis=1)
        # EVAL (q5, q6, q11, q12, q18, q19, q20): bs 4, TRUE src 4, TRUE s/d 3, PRED src 4, PRED s/d 3, PRED leaf 2,
        # oracle 7, all over 7.
        chk(acc[:7].tolist() == [4, 4, 3, 4, 3, 2, 7], "hand arm sums %s" % acc.tolist(), "S1")
        chk(abs(D.src_ok - 1.0) < 1e-12 and abs(D.dom_ok - 0.95) < 1e-12, "routing 20/20 and 19/20", "S1")
        # EVAL-side argmax in SRC1/d1 would be mB; the policy is mA: TRAIN-only fitting by construction.
        e_s1 = [i for i, q in enumerate(D.qids[D.E]) if D.Q[int(q)][1] == "d1"]
        chk(int(np.argmax(D.A[D.E][e_s1].sum(axis=0))) == 1 and nmd["tdom"]["SRC1/d1"] == "mA", "EVAL argmax differs", "S1")
        # The fit assert fires on any weight outside TRAIN (guard 4), and on EVAL weight in fit_clean.
        w_bad = train_full_w(D); w_bad[D.E[0]] = 1
        try:
            fit_policies(D, w_bad, D.train_set, "TRAIN"); fired = False
        except SystemExit as ex:
            fired = "[G3(4)]" in str(ex)
        chk(fired, "fit_policies refuses a weight on an EVAL question", "S1")
        try:
            fit_clean(D, w_bad); fired = False
        except SystemExit as ex:
            fired = str(ex) == "[G3(4)] weight on EVAL positions"
        chk(fired, "fit_clean's numeric check refuses a weight on an EVAL position (before the set check)", "S1")
        # The SET assert is live on its own: with the numeric EVAL-weight assert satisfied, a TRAIN set short by one id
        # (a registry mismatch) must still refuse, naming the TRAIN of record.
        import copy
        Dt = copy.copy(D); Dt.train_set = D.train_set - {int(D.qids[D.T[0]])}
        try:
            fit_clean(Dt, train_full_w(Dt)); fired = False
        except SystemExit as ex:
            fired = "outside TRAIN of record" in str(ex)
        chk(fired, "the set-membership assert fires by itself against the TRAIN of record", "S1")
        # The hygiene intersection check refuses BY ITSELF (every count consistent, one pool id inside TRAIN).
        Dh = copy.copy(D); Dh.train_set = D.train_set | {int(D.qids[D.E[0]])}
        ch = Cfg(**cfg.__dict__); ch.reg = dict(cfg.reg); ch.reg["n_train"] = len(Dh.train_set)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                hygiene(Dh, ch)
            fired = False
        except SystemExit as ex:
            fired = "TRAIN intersects the pool on 1 ids" in str(ex) and "|TRAIN|" not in str(ex)
        chk(fired, "hygiene refuses on the intersection alone", "S1")
        # Two-stage replicate by hand: w = TRAIN with q13 x3, q14 x0, q15 x0; v = EVAL with q5 x2, q6 x0.
        pos = {int(q): i for i, q in enumerate(D.qids)}; posE = {int(q): i for i, q in enumerate(D.qids[D.E])}
        w = train_full_w(D); w[pos[13]] = 3; w[pos[14]] = 0; w[pos[15]] = 0
        Pw = fit_clean(D, w)
        # totals mA 5, mB 5, mC 8 -> gb = mC; L3 = q13 x3 -> mC.
        chk(D.models[Pw.gb] == "mC" and picks_named(D, Pw)["pleaf"]["c2:L3"] == "mC", "hand refit", "S1")
        v = np.ones(len(D.E), dtype=np.int64); v[posE[5]] = 2; v[posE[6]] = 0
        a2, _ = score_E(correctness(D, Pw)[:, D.E].astype(float), v, D.mmlu)
        # bs mC: q5 0 x2, q11 1, q12 1, q18 1, q19 0, q20 0 = 3/7; PRED s/d: q5 mA 0 x2, q11 1, q12 0, q18 1 = 2/7.
        chk(abs(a2[BS] - 3 / 7) < 1e-12 and abs(a2[PDOM] - 2 / 7) < 1e-12 and abs((a2[PDOM] - a2[BS]) + 1 / 7) < 1e-12,
            "hand two-stage replicate G = -1/7", "S1")
        # Within-stratum resampling keeps every stratum's size on each side and never crosses sides.
        rng = np.random.default_rng(3)
        for _ in range(50):
            w = strat_counts(rng, D.strata_train, D.n); vv = strat_counts(rng, D.strata_evalE, len(D.E))
            ok = all(int(w[ix].sum()) == len(ix) for ix in D.strata_train) and int(w[D.E].sum()) == 0
            ok = ok and all(int(vv[ix].sum()) == len(ix) for ix in D.strata_evalE)
            chk(ok, "within-stratum sizes kept, no mass across sides", "S1")
        # Placebo: exactly random.Random(42).shuffle of the sorted-qid label list; sizes kept.
        lab = [int(x) for x in D.g_tdom]; exp = lab[:]; random.Random(42).shuffle(exp)
        chk(D.g_plac.tolist() == exp and sorted(D.g_plac.tolist()) == sorted(lab), "placebo permutation", "S1")
        chk(D.qq == sorted(D.qq), "sorted-qid order", "S1")

        # ---------------------------------------------------------------- S1b fallbacks when a PREDICTED cell has no TRAIN
        # SRC1/d1 TRAIN 3 (mA right), SRC1/d2 TRAIN 3 (mB right), SRC2/d3 TRAIN 6 (mC right) -> gb = mC; p_src(SRC1): mA 3,
        # mB 3 -> mA (tie-break). Leaf L9 carries anchor SRC1/d9, which no TRAIN question reaches. EVAL q100 (SRC1/d1,
        # correct only for mA) routes to L9: PRED s/d = p_dom.get((SRC1, d9), p_src(SRC1)) = mA -> 1 (a gb fallback would give
        # mC -> 0); PRED leaf = p_leaf.get(L9, p_dom.get((SRC1, d9), gb)) = gb = mC -> 0 (a p_src fallback would give 1).
        u = {i: np.eye(4)[i] for i in range(4)}
        Qb = {}; Gb = defaultdict(dict); qv = {}; q = 1
        for k, (sb, dom, nt, right) in enumerate([("SRC1", "d1", 3, 0), ("SRC1", "d2", 3, 1), ("SRC2", "d3", 6, 2)]):
            for _ in range(nt):
                Qb[q] = (sb, dom, "b%d" % q); qv["b%d" % q] = u[k]
                for j, mm in enumerate(["mA", "mB", "mC"]): Gb[q][mm] = int(j == right)
                q += 1
        Qb[100] = ("SRC1", "d1", "b100"); qv["b100"] = u[3]; Gb[100] = {"mA": 1, "mB": 0, "mC": 0}
        Qb[101] = ("SRC2", "d3", "b101"); qv["b101"] = u[2]; Gb[101] = {"mA": 0, "mB": 0, "mC": 1}
        lvb = [("c:L1", u[0], "SRC1", "d1"), ("c:L2", u[1], "SRC1", "d2"), ("c:L3", u[2], "SRC2", "d3"),
               ("c:L9", u[3], "SRC1", "d9")]
        cfgB = Cfg(**cfg.__dict__); cfgB.reg = dict(cfg.reg); cfgB.reg["min_leaf"] = 1
        DB = build_data(Qb, ["mA", "mB", "mC"], Gb, {100, 101}, lvb, qv, cfgB)
        PB = fit_clean(DB, train_full_w(DB)); CB = correctness(DB, PB)
        i100 = int(np.flatnonzero(DB.qids == 100)[0])
        chk(DB.models[PB.gb] == "mC" and CB[PDOM, i100] == 1 and CB[PLEAF, i100] == 0 and CB[BS, i100] == 0,
            "fallbacks: PRED s/d -> p_src, PRED leaf -> p_dom-or-gb (%s)" % CB[:, i100].tolist(), "S1b")
        # MATH-FIX overlay (guard 5), and the record's own load() reading the same fixture identically.
        cfgX, _ = _hand_fixture(os.path.join(tmp, "mathfix"))
        con = real_connect(cfgX.union_db)
        con.execute("INSERT INTO eval_results_mathfix VALUES (5, 'mB', 0)")      # flips q5 mB 1 -> 0
        con.execute("INSERT INTO eval_results_mathfix VALUES (6, 'mA', 1)")      # equal to the ingested value: not counted
        con.execute("INSERT INTO eval_results_mathfix VALUES (999, 'mA', 1)")    # no eval_results cell: not overlaid
        con.commit(); con.close()
        bx = io.StringIO()
        with contextlib.redirect_stdout(bx):
            con = open_union(cfgX)[0]; QX, mX, GX, _ = load_union(con, cfgX); con.close()
        chk(GX[5]["mB"] == 0 and GX[6]["mA"] == 1 and 999 not in GX, "MATH-FIX overlay applied", "S1b")
        chk("MATH-FIX overlay: 1 corrected" in bx.getvalue() and "MC-E2E L51: 1)" in bx.getvalue(), "overlay counts", "S1b")
        import multicorpus_router_e2e as mre0
        mre0.MATHFIX = True
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                Qr, mr, Gr = mre0.load(cfgX.union_db)
        finally:
            mre0.MATHFIX = False
        chk(mr == mX and {k: dict(v) for k, v in Gr.items()} == {k: dict(v) for k, v in GX.items()},
            "load_union reads exactly what MC-E2E load() reads", "S1b")

        # ---------------------------------------------------------------- S2 legacy path == the record's own code (MC-E2E)
        import multicorpus_router_e2e as mre
        cfg.reg.update(g2_ratio=0.3)
        lines, dep, n = legacy_seed(D, cfg, with_boot=True, boots=200)
        mre.MATHFIX = True; mre.CLEANPOOL = set(D.pool_set)
        fx_leaves = federated_leaves(cfg, ff)

        class _FF:
            EMB_DB = cfg.emb_db
            embed_matrix = staticmethod(ff.embed_matrix)
        saved = (mre.federated_leaves, mre.ff)
        mre.federated_leaves = lambda: fx_leaves; mre.ff = _FF
        b2 = io.StringIO()
        try:
            with contextlib.redirect_stdout(b2):
                mre.main(cfg.union_db, [42], 200, 0.3, cfg.reg["min_leaf"])
        finally:
            mre.federated_leaves, mre.ff = saved; mre.MATHFIX = False; mre.CLEANPOOL = None
        rec = b2.getvalue().splitlines()
        i = next(j for j, l in enumerate(rec) if l.startswith("seed 42 "))
        rec_block = rec[i - 1:i + 10]
        chk([_NUM.findall(l) for l in lines] == [_NUM.findall(l) for l in rec_block],
            "legacy block equals multicorpus_router_e2e.main on the fixture:\n%s\n---\n%s" % ("\n".join(lines), "\n".join(rec_block)), "S2")
        # compare_legacy_block against a written 'record file' (the MC-E2E output) -> IDENTICAL; then a doctored one.
        with open(cfg.record_legacy_file, "w", encoding="cp1252") as f:
            f.write("\n".join(l.replace("+-", chr(0xB1)) for l in rec) + "\n")
        b3 = io.StringIO()
        with contextlib.redirect_stdout(b3):
            same = compare_legacy_block(lines, cfg.record_legacy_file)
        chk(same is not None and bool(same), "legacy comparison IDENTICAL (cp1252 record)", "S2")
        with open(cfg.record_legacy_file, "w", encoding="utf-8") as f:
            f.write("\n".join(rec).replace("DEPLOYED gain (PRED source/domain - best single): ",
                                           "DEPLOYED gain (PRED source/domain - best single): 9") + "\n")
        with contextlib.redirect_stdout(io.StringIO()):
            same = compare_legacy_block(lines, cfg.record_legacy_file)
        chk(same is not None and not bool(same), "legacy comparison DIFFERENT on a doctored record", "S2")
        # G2 gate: PASS at the fixture's own values, FAIL (SystemExit, nothing written) otherwise.
        cfg.reg.update(g2_gain="%+.4f" % dep, g2_n=n)
        with contextlib.redirect_stdout(io.StringIO()):
            gate_g2(D, cfg)
        chk(True, "G2 passes at the fixture's values", "S2")

        # ---------------------------------------------------------------- S3 statistics against analytic values
        cfgS = Cfg(**{k: v for k, v in cfg.__dict__.items()}); cfgS.reg = dict(cfg.reg); cfgS.reg["min_leaf"] = 1
        # Stratum 0: mB right on all TRAIN, mA wrong -> p_dom S0 = mB for every TRAIN resample; S1, S2: mA right on all
        # TRAIN -> gb = mA always. EVAL S0: independent Bernoulli; G's two-stage variance is then EXACTLY the stratified
        # EVAL bootstrap variance n0 * s2_pop(d) / N^2 (policy fixed in every replicate), and TRAIN-only variance is 0.
        def gen(k, side, rng):
            if side == "train": return (0, 1, 0) if k == 0 else (1, 0, 0)
            return (int(rng.random() < 0.1), int(rng.random() < 0.9), int(rng.random() < 0.5))
        DS = _synthetic_D(cfgS, [(40, 120), (60, 90), (60, 90)], gen, ["mA", "mB", "mC"])[0]
        with contextlib.redirect_stdout(io.StringIO()):
            bt = run_bootstraps(DS, 2000, 42, log=None)
        c1, d2, dt = contrast_stats(bt, PDOM, BS, None)
        E0 = DS.strata_evalE[0]; A_E = DS.A[DS.E]
        d0 = (A_E[E0, 1] - A_E[E0, 0]).astype(float); N = len(DS.E)
        se_an = math.sqrt(len(E0) * np.var(d0) / N ** 2)
        chk(abs(c1["se2"] / se_an - 1) < 0.08, "two-stage SE %.5f vs analytic %.5f" % (c1["se2"], se_an), "S3")
        se_iid_an = math.sqrt(float(np.var(np.where(DS.g_tdom[DS.E] == 0, A_E[:, 1] - A_E[:, 0], 0))) / N)
        chk(abs(c1["se_iid"] / se_iid_an - 1) < 0.08 and se_iid_an > 1.5 * se_an,
            "i.i.d. SE %.5f vs analytic %.5f (and well above the stratified %.5f)" % (c1["se_iid"], se_iid_an, se_an), "S3")
        chk(float(np.ptp(dt)) == 0.0 and _var(dt) == 0.0, "TRAIN-only variance exactly 0 when the policy cannot move", "S3")
        phi, mc, vt, v2 = phi_stats(d2, dt)
        chk(phi == 0.0 and mc == 0.0, "phi = 0 exactly", "S3")
        chk(abs(c1["point"] - float(d0.sum()) / N) < 1e-12, "point G = sum d / N", "S3")
        # i.i.d. SE (unstratified) >= stratified one here; clustered SE finite; DEFF ratios computed.
        chk(c1["se_iid"] > 0 and c1["se_cl"] > 0 and c1["deff2"] > 0, "iid / clustered SEs positive", "S3")
        # A policy that CAN move: TRAIN S0 mA/mB near-tied -> TRAIN-only variance > 0 and phi in (0, 1].
        def gen2(k, side, rng):
            if side == "train" and k == 0: return (int(rng.random() < 0.5), int(rng.random() < 0.5), 0)
            return gen(k, side, rng)
        DS2 = _synthetic_D(cfgS, [(40, 120), (60, 90), (60, 90)], gen2, ["mA", "mB", "mC"])[0]
        with contextlib.redirect_stdout(io.StringIO()):
            bt2 = run_bootstraps(DS2, 400, 42, log=None)
        _, d2b, dtb = contrast_stats(bt2, PDOM, BS, None)
        phib = phi_stats(d2b, dtb)[0]
        chk(0.0 < phib <= 1.5, "phi > 0 when the policy moves (%.3f)" % phib, "S3")
        # Degenerate two-stage variance -> refusal, never a verdict.
        try:
            phi_stats(np.zeros(10), np.zeros(10)); fired = False
        except SystemExit as ex:
            fired = "[G4]" in str(ex)
        chk(fired, "phi refusal on zero two-stage variance is G4", "S3")
        try:
            gate_g4({"C1": np.array([0.1, 0.2]), "C4": np.zeros(5)}); fired = False
        except SystemExit as ex:
            fired = "[G4]" in str(ex) and "C4" in str(ex)
        chk(fired, "G4 refuses a zero C4 two-stage variance", "S3")
        gate_g4({"C1": np.array([0.1, 0.2]), "C4": np.array([0.0, 0.1])})
        chk(True, "G4 admits non-zero variances", "S3")
        # D7: with MIS-ROUTES (pred cell != true cell) and TRAIN heterogeneity, every replicate's weights keep each TRUE
        # stratum's size on each side; the true groups are rebuilt HERE from Q and the pool, independently of D.strata_*.
        def gen4(k, side, rng):
            return (int(rng.random() < 0.3 + 0.2 * k), int(rng.random() < 0.6 - 0.1 * k), int(rng.random() < 0.5))
        DM, QM, _, poolM, _, _ = _synthetic_D(cfgS, [(30, 20), (50, 25), (40, 35)], gen4, ["mA", "mB", "mC"], misroute=4)
        chk(DM.dom_ok < 0.9, "the stratification fixture is mis-routed (%.3f)" % DM.dom_ok, "S3")
        pos_true = defaultdict(lambda: {"train": [], "eval": []}); e_rank = {}
        for i, q in enumerate(DM.qids.tolist()):
            if q in poolM: e_rank[i] = len(e_rank)
        for i, q in enumerate(DM.qids.tolist()):
            key = QM[q][:2]
            if q in poolM: pos_true[key]["eval"].append(e_rank[i])
            else: pos_true[key]["train"].append(i)
        seen = Counter()

        def hook(kind, w, v):
            seen[kind] += 1
            ok = all(int(w[g["train"]].sum()) == len(g["train"]) for g in pos_true.values())
            ok = ok and int(w[[i for i in e_rank]].sum()) == 0
            if v is not None:
                ok = ok and all(int(v[g["eval"]].sum()) == len(g["eval"]) for g in pos_true.values())
            chk(ok, "%s replicate keeps every TRUE stratum's size on each side" % kind, "S3")
        with contextlib.redirect_stdout(io.StringIO()):
            run_bootstraps(DM, 25, 42, log=None, hook=hook)
        chk(seen["two"] == 25 and seen["tro"] == 25, "the hook saw every replicate", "S3")
        # Placebo on a NO-SIGNAL fixture (all strata alike) is not above 0; a LEAK (placebo := true labels) on a signal
        # fixture manufactures a gain -> C4 FAILED branch reachable from data, not only from synthetic stats.
        def gen3(k, side, rng):
            if k == 0: return (int(rng.random() < 0.1), int(rng.random() < 0.9), 0)
            return (int(rng.random() < 0.8), int(rng.random() < 0.2), 0)
        DL = _synthetic_D(cfgS, [(150, 150), (150, 150), (150, 150)], gen3, ["mA", "mB", "mC"])[0]
        with contextlib.redirect_stdout(io.StringIO()):
            btL = run_bootstraps(DL, 300, 42, log=None)
        c4, _, _ = contrast_stats(btL, PLAC, BS, None)
        chk(not bool(c4["lo"] > 0), "placebo on permuted labels not above 0 (lo %.4f)" % c4["lo"], "S3")
        cfgL = Cfg(**{k: v for k, v in cfgS.__dict__.items()}); cfgL.placebo_override = lambda D_: D_.g_tdom
        DLk = _synthetic_D(cfgL, [(150, 150), (150, 150), (150, 150)], gen3, ["mA", "mB", "mC"])[0]
        with contextlib.redirect_stdout(io.StringIO()):
            btK = run_bootstraps(DLk, 300, 42, log=None)
        c4k, _, _ = contrast_stats(btK, PLAC, BS, None)
        chk(bool(c4k["lo"] > 0), "leaked placebo manufactures gain (lo %.4f): C4 would FAIL" % c4k["lo"], "S3")
        # Reproducibility: same seed, same replicates.
        with contextlib.redirect_stdout(io.StringIO()):
            btL2 = run_bootstraps(DL, 300, 42, log=None)
        chk(np.array_equal(btL["two"], btL2["two"]) and np.array_equal(btL["tro"], btL2["tro"]), "seeded replicates", "S3")

        # ---------------------------------------------------------------- S4 every verdict / prediction / falsifier branch
        def mk(pt, lo, hi, **kw):
            c = dict(point=np.float64(pt), lo=np.float64(lo), hi=np.float64(hi), se2=np.float64(0.006), se_iid=0.005,
                     se_cl=0.01, se_tro=0.002, pct=(np.float64(lo - 1.0), np.float64(hi + 1.0)), deff2=np.float64(1.44),
                     deff_cl=np.float64(4.0))
            c.update(kw); return c
        def st_of(c0ok=True, c1=(0.024, 0.012, 0.036), c2=(0.01, 0.002, 0.02), c3=(-0.007, -0.015, 0.001),
                  c4=(-0.003, -0.01, 0.004), m=(0.007, -0.002, 0.016), phi=0.15):
            return dict(c0=dict(bs_name="Qwen2.5-72B-Instruct", bs_acc=np.float64(0.59123 if c0ok else 0.5), tdom_acc=0.62204,
                                exp_name="Qwen2.5-72B-Instruct", exp_bs="0.5912", exp_tdom="0.6220"),
                        con=dict(C1=mk(*c1), C2=mk(*c2), C3=mk(*c3), C4=mk(*c4), M=mk(*m), C1_MMLU=mk(0.01, 0.0, 0.02)),
                        phi=np.float64(phi), phi_mcse=np.float64(0.005), var_tro=0.1, var2=0.5, n_eval=6482,
                        n_mmlu=3609, n_mmlu_reg=3609, r4_lines=["R4 table line"])
        # The ruled wording, written out LITERALLY here (not via the module constants), so a wording mutant is caught.
        W1 = "C4 FAILED, the instrument manufactures gain from noise"
        W2 = "C0 FAILED, two instruments disagree about the same object"
        U1 = "UNDETERMINED (BY TRIGGER: %s)" % W1
        U2 = "UNDETERMINED (BY TRIGGER: %s)" % W2
        U12 = "UNDETERMINED (BY TRIGGER: %s; %s)" % (W1, W2)
        NL = ("NOT LIFTED WITHIN THIS RUN: a reading requires the reviewer's written finding of which instrument is wrong "
              "AND a dated registration amendment committed before any re-read")
        VOID = "every number of this test is void and the instrument is defective"
        HELD7 = {"P%d" % i: "HELD" for i in range(1, 8)}
        scenarios = [
            ("all held", st_of(), dict(C0="HELD", C1="HELD", C2="DESCRIPTIVE (ABOVE)", C3="DESCRIPTIVE (CONTAINS)",
                                       C4="HELD", R3="HELD", R4="DESCRIPTIVE", F="C1 HELD: REPLACE", **HELD7)),
            ("c1 below", st_of(c1=(-0.03, -0.04, -0.02), c2=(-0.02, -0.03, -0.01), c3=(0.02, 0.01, 0.03), phi=0.7,
                               m=(0.05, 0.04, 0.06), c4=(0.003, -0.001, 0.007)),
             dict(C0="HELD", C1="FAILED", C2="DESCRIPTIVE (BELOW)", C3="DESCRIPTIVE (ABOVE)", C4="HELD", R3="FAILED",
                  R4="DESCRIPTIVE", F="C1 NOT HELD: OVERTURN", P1="FAILED", P2="FAILED", P3="FAILED", P4="FAILED",
                  P5="FAILED", P6="HELD", P7="FAILED")),
            ("c1 contains", st_of(c1=(0.005, -0.007, 0.017), c2=(0.001, -0.01, 0.012), c3=(-0.02, -0.03, -0.01), phi=0.5),
             dict(C1="UNDETERMINED", C2="DESCRIPTIVE (CONTAINS)", C3="DESCRIPTIVE (BELOW)", R3="FAILED",
                  F="C1 NOT HELD: OVERTURN")),
            # D7: an endpoint EXACTLY on 0: C1 lo == 0 -> CONTAINS -> UNDETERMINED; C4 lo == 0 -> HELD (no trigger).
            ("zero edges", st_of(c1=(0.01, 0.0, 0.02), c4=(0.01, 0.0, 0.02), c2=(0.01, 0.0, 0.02)),
             dict(C0="HELD", C1="UNDETERMINED", C2="DESCRIPTIVE (CONTAINS)", C4="HELD", R3="HELD", F="C1 NOT HELD: OVERTURN")),
            ("T1 only", st_of(c4=(0.02, 0.01, 0.03), c3=(-0.02, -0.03, -0.01)),
             dict(C0="HELD", C1=U1, C2=U1, C3=U1, C4="FAILED", R3=U1, R4=U1, P1=U1, P2=U1, P3=U1, P4="FAILED", P5=U1,
                  P6="HELD", P7=U1, F="NOT EVALUATED (BY TRIGGER: %s)" % W1)),
            ("T1 only, P4 held", st_of(c4=(0.001, 0.0005, 0.0015)),
             dict(C0="HELD", C1=U1, C4="FAILED", P4="HELD", P6="HELD", P1=U1)),
            ("T2 only", st_of(c0ok=False, c1=(-0.03, -0.04, -0.02)),
             dict(C0="FAILED", C1=U2, C2=U2, C3=U2, C4=U2, R3=U2, R4=U2, P1=U2, P2=U2, P3=U2, P4=U2, P5=U2, P6="FAILED",
                  P7=U2, F="NOT EVALUATED (BY TRIGGER: %s)" % W2)),
            ("both", st_of(c0ok=False, c4=(0.02, 0.01, 0.03)),
             dict(C0="FAILED", C1=U12, C2=U12, C3=U12, C4=U2, R3=U12, R4=U12, P1=U12, P2=U12, P3=U12, P4=U2, P5=U12,
                  P6="FAILED", P7=U12, F="NOT EVALUATED (BY TRIGGER: %s; %s)" % (W1, W2))),
            ("edges lo", st_of(c1=(0.010, 0.001, 0.02), c2=(0.003, 0.0, 0.01), c3=(-0.015, -0.02, 0.0), c4=(-0.010, -0.02, 0.0),
                               m=(-0.003, -0.01, 0.0), phi=0.03),
             dict(P1="HELD", P2="HELD", P3="HELD", P4="HELD", P5="HELD", P7="HELD")),
            ("edges hi", st_of(c1=(0.036, 0.02, 0.05), c2=(0.025, 0.0, 0.03), c3=(0.002, -0.01, 0.01), c4=(0.002, -0.01, 0.01),
                               m=(0.016, 0.0, 0.03), phi=0.40),
             dict(P1="HELD", P2="HELD", P3="HELD", P4="HELD", P5="HELD", P7="HELD")),
        ]
        texts = {}
        for name, st, want in scenarios:
            L, res = verdict_lines(st); texts[name] = "\n".join(L)
            for k, v in want.items():
                chk(res[k] == v, "%s: %s = %r, want %r" % (name, k, res[k], v), "S4")
        t1, t2, tb = texts["T1 only"], texts["T2 only"], texts["both"]
        chk("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): T1 FIRED: " + W1 in t1, "T1 named", "S4")
        chk("VALIDITY TRIGGERS (evaluated FIRST; ruling (a), d6b5ca8): T2 FIRED: " + W2 in t2, "T2 named", "S4")
        chk("T1 and T2 FIRED (both named): T1 %s; T2 %s" % (W1, W2) in tb, "both named", "S4")
        for nm in ("C1", "C2", "C3", "R3"):
            chk("  %s -> %s; printed, NOT scored" % (nm, U1) in t1, "T1 wording on %s" % nm, "S4")
            chk("  %s -> %s; printed, NOT scored" % (nm, U2) in t2, "T2 wording on %s" % nm, "S4")
            chk("  %s -> %s; printed, NOT scored" % (nm, U12) in tb, "both wording on %s" % nm, "S4")
        chk("  C4 -> %s; printed, NOT scored" % U2 in t2 and "  C4 -> FAILED" not in t2, "C4 pre-empted by T2", "S4")
        chk("  C4 -> %s; printed, NOT scored (T1 is still NAMED: the interval lies wholly above 0)" % U2 in tb, "C4 both", "S4")
        chk("  C4 -> FAILED (the two-stage interval lies wholly above 0: %s)" % W1 in t1, "C4 FAILED under T1", "S4")
        chk("R4 tables below -> %s; printed, NOT read" % U1 in t1 and "R4 tables below -> %s; printed, NOT read" % U2 in t2,
            "R4 tables pre-empted", "S4")
        chk(NL in t2 and NL in tb and NL not in t1 and NL not in texts["all held"], "NOT LIFTED printed under T2 only", "S4")
        chk(VOID in t1 and VOID in tb and VOID not in t2, "C4 void consequence under T1 only", "S4")
        chk("FALSIFIER: NOT EVALUATED (BY TRIGGER: %s)." % W1 in t1 and "FALSIFIER: NOT EVALUATED (BY TRIGGER: %s)." % W2
            in t2, "falsifier not evaluated", "S4")
        for t in (t1, t2, tb):
            chk("DESCRIPTIVE-ONLY BY SUPPORT" not in t and "FALSIFIER: C1" not in t and "are OVERTURNED as" not in t
                and "VOID (C4 FAILED)" not in t, "no reading under a trigger", "S4")
        chk("C1 -> HELD" not in t1 and "C1 -> FAILED" not in t2, "no second verdict", "S4")
        chk("C0 CROSS-INSTRUMENT" in t1 and "-> HELD" in t1.splitlines()[0] and "-> FAILED" in t2.splitlines()[0],
            "C0 scored in every branch", "S4")
        chk("DESCRIPTIVE-ONLY BY SUPPORT" in texts["all held"] and "C2 -> HELD" not in texts["all held"], "C2 chip", "S4")
        chk("SUPPORT (measured)" in texts["all held"] and "SUPPORT (registered plan)" in texts["all held"], "support", "S4")
        # numpy.bool_ / numpy.float64 inputs: verdicts identical to plain floats (no identity test anywhere).
        L1, r1 = verdict_lines(st_of()); stp = st_of()
        for k in stp["con"]:
            stp["con"][k] = {kk: (float(vv) if isinstance(vv, np.floating) else vv) for kk, vv in stp["con"][k].items()}
        L2, r2 = verdict_lines(stp)
        chk(r1 == r2 and L1 == L2, "numpy scalars and floats read identically", "S4")

        # ---------------------------------------------------------------- S5 modes, gates, write-once on the hand fixture
        cfg.B = 50
        cfg.reg.update(c0_best="mB", c0_bs="0.5714", c0_tdom="0.4286")
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            mode_dry_run(cfg, ff)
        chk(not os.path.exists(cfg.out_path) and "DRY-RUN: zero calls; nothing written" in b.getvalue(), "dry-run writes nothing", "S5")
        chk("PLANNED: B = 50" in b.getvalue(), "dry-run plan print", "S5")
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            mode_legacy(cfg, ff)
        chk("G2: " in b.getvalue() and "-> PASS" in b.getvalue() and not os.path.exists(cfg.out_path), "legacy mode", "S5")
        # G1 failure -> SystemExit, no file.
        cG = Cfg(**cfg.__dict__); cG.reg = dict(cfg.reg); cG.reg["g1_dom"] = "0.951"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode_run(cG, ff)
            fired = False
        except SystemExit as ex:
            fired = "[G1]" in str(ex)
        chk(fired and not os.path.exists(cfg.out_path), "G1 refusal writes nothing", "S5")
        cG.reg = dict(cfg.reg); cG.reg["g2_gain"] = "+0.9999"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode_run(cG, ff)
            fired = False
        except SystemExit as ex:
            fired = "[G2]" in str(ex)
        chk(fired and not os.path.exists(cfg.out_path), "G2 refusal writes nothing", "S5")
        cG.reg = dict(cfg.reg); cG.reg["n_train"] = 14
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode_run(cG, ff)
            fired = False
        except SystemExit as ex:
            fired = "[G3(2)]" in str(ex)
        chk(fired and not os.path.exists(cfg.out_path), "G3 hygiene refusal writes nothing", "S5")
        # The run itself (degenerate fixture: phi may be undefined -> use a non-degenerate one below).
        # Meta-Llama present -> G3(3) refusal.
        cfgM, _ = _hand_fixture(os.path.join(tmp, "meta"))
        con = real_connect(cfgM.union_db); con.execute("INSERT INTO eval_results VALUES (1, ?, 1)", (EXCLUDED,)); con.commit(); con.close()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                prefix(cfgM, ff, guard_pool(cfgM))
            fired = False
        except SystemExit as ex:
            fired = "[G3(3)]" in str(ex)
        chk(fired, "Meta-Llama present -> refusal", "S5")
        # A non-member scored id -> scored_minus_eval refusal (fixture and the pool of record's id file, JSON only).
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                scored_guard(cfg, set(D.eval_set) | {999999})
            fired = False
        except SystemExit as ex:
            fired = "[SCORED-EVAL]" in str(ex)
        chk(fired, "scored_minus_eval refusal (fixture id file)", "S5")
        rc = Cfg(pool_id=REG["pool"], id_override=None)
        real_ids = sorted(pool_guard.eval_ids(REG["pool"]))
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            scored_guard(rc, set(real_ids))
        chk(b.getvalue() == "reserved_pool_id=%s\nscored_minus_eval=0\n" % REG["pool"] and len(real_ids) == REG["n_eval"],
            "pool-of-record branch of scored_guard (id file only)", "S5")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                scored_guard(rc, {-5})
            fired = False
        except SystemExit as ex:
            fired = "[SCORED-EVAL]" in str(ex)
        chk(fired, "pool-of-record scored refusal", "S5")
        # MAIN_union_routing readout: MATCH and MISMATCH branches.
        with open(os.path.join(cfg.routing_dir, "MAIN_union_routing_summary.txt"), "w", encoding="utf-8") as f:
            f.write("rule=flatLeaf\nn=7\ntop1=0.857\nsource_accuracy=1.0\n")
        keys = [key_of_record(*D.strata_keys[int(k)]) for k in D.g_tdom[D.E]]
        with open(os.path.join(cfg.routing_dir, "MAIN_union_routing_queries.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("true_key,true_source\n" + "".join("%s,%s\n" % (k, k.split("/")[0]) for k in keys))
        with contextlib.redirect_stdout(io.StringIO()):
            chk(main_routing_readout(D, cfg) is True, "routing readout MATCH", "S5")
        with open(os.path.join(cfg.routing_dir, "MAIN_union_routing_queries.csv"), "a", encoding="utf-8", newline="") as f:
            f.write("SRC9/x,SRC9\n")
        with contextlib.redirect_stdout(io.StringIO()):
            chk(main_routing_readout(D, cfg) is False, "routing readout MISMATCH", "S5")
        # Full --run on a larger fixture routed through the DB layer (non-degenerate bootstrap), then write-once.
        rngf = random.Random(11); models = ["mA", "mB", "mC"]
        rowsF = []; poolF = set(); qvF = {}; q = 1
        base = {0: np.array([1.0, 0, 0, 0]), 1: np.array([0, 1.0, 0, 0]), 2: np.array([0, 0, 1.0, 0])}
        pr = {0: (0.3, 0.7, 0.5), 1: (0.6, 0.4, 0.5), 2: (0.5, 0.5, 0.6)}
        for k in range(3):
            for i in range(60):
                ev = i % 3 == 0; rowsF.append((q, "SRC%d" % (k // 2), "d%d" % k, "tf-%d" % q,
                                               {mm: int(rngf.random() < p) for mm, p in zip(models, pr[k])}))
                if ev: poolF.add(q)
                v = base[k] + (1.2 * base[(k + 1) % 3] if i % 10 == 1 else 0)          # mis-route to the next cell
                if k == 2 and i % 10 == 2: v = base[2] + 0.05 * base[0]                  # lands on L3 (below min_leaf)
                qvF["tf-%d" % q] = v; q += 1
        leavesF = {"cA": [("SRC0/d0", [("L0", base[0])]), ("SRC0/d1", [("L1", base[1])])],
                   "cB": [("SRC1/d2", [("L2", base[2]), ("L3", base[2] + 0.01 * base[0])])]}
        cfgF = _write_fixture(os.path.join(tmp, "full"), models, rowsF, poolF, leavesF, qvF)
        # Fill the fixture's expectations from its own data, through the same functions, then run.
        cfgF.reg.update(n_eval=60, n_train=120, n_routed=180, roster=3, min_leaf=5, n_mmlu=0)
        con = real_connect(cfgF.union_db); QF = {qq: (s, d, t) for qq, s, d, t in con.execute(
            "SELECT question_id, source, domain, text FROM corpus_questions")}
        GF = defaultdict(dict)
        for qq, mm, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"): GF[qq][mm] = c
        con.close()
        lvF = federated_leaves(cfgF, ff); vcF = ff.embed_matrix(cfgF.emb_db, [QF[x][2] for x in sorted(QF)], 4)
        DF = build_data(QF, models, GF, poolF, lvF, vcF, cfgF)
        with contextlib.redirect_stdout(io.StringIO()):
            _, depF, nF = legacy_seed(DF, cfgF, with_boot=False)
        PF = fit_clean(DF, train_full_w(DF)); aF = correctness(DF, PF)[:, DF.E].mean(axis=1)
        cfgF.reg.update(g1_src="%.3f" % DF.src_ok, g1_dom="%.3f" % DF.dom_ok, g2_gain="%+.4f" % depF, g2_n=nF,
                        c0_best=DF.models[PF.gb], c0_bs="%.4f" % aF[BS], c0_tdom="%.4f" % aF[TDOM])
        cfgF.B = 200
        chk(DF.dom_ok < 1.0, "the full fixture has mis-routes (PRED != TRUE)", "S5")
        # S2b: the legacy path equals the record's OWN CODE (multicorpus_router_e2e.main, unmodified, fed this fixture's
        # DB, leaves and vectors) at the three seeds of record, on a fixture with mis-routes and a leaf below min_leaf.
        import multicorpus_router_e2e as mre
        lvF2 = federated_leaves(cfgF, ff)

        class _FF2:
            EMB_DB = cfgF.emb_db
            embed_matrix = staticmethod(ff.embed_matrix)
        saved = (mre.federated_leaves, mre.ff)
        mre.federated_leaves = lambda: lvF2; mre.ff = _FF2; mre.MATHFIX = True; mre.CLEANPOOL = set(poolF)
        try:
            for sd in (42, 137, 2048):
                cS = Cfg(**cfgF.__dict__); cS.reg = dict(cfgF.reg); cS.reg["g2_seed"] = sd
                ln, dp, nn = legacy_seed(DF, cS, with_boot=True, boots=200)
                bb = io.StringIO()
                with contextlib.redirect_stdout(bb):
                    mre.main(cfgF.union_db, [sd], 200, 0.3, cfgF.reg["min_leaf"])
                rr = bb.getvalue().splitlines(); j = next(t for t, l in enumerate(rr) if l.startswith("seed %d " % sd))
                chk(nn >= 10 and [_NUM.findall(l) for l in ln] == [_NUM.findall(l) for l in rr[j - 1:j + 10]],
                    "seed %d: legacy block (n=%d) equals multicorpus_router_e2e.main:\n%s\n---\n%s"
                    % (sd, nn, "\n".join(ln), "\n".join(rr[j - 1:j + 10])), "S2b")
                chk(len(set(_NUM.findall(" ".join(ln[2:9])))) > 3, "seed %d: the compared block is not degenerate" % sd, "S2b")
        finally:
            mre.federated_leaves, mre.ff = saved; mre.MATHFIX = False; mre.CLEANPOOL = None
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            _, stF, resF = mode_run(cfgF, ff)
        chk(os.path.isfile(cfgF.out_path), "outcome written", "S5")
        body = open(cfgF.out_path, encoding="utf-8").read()
        chk(body.splitlines()[0].startswith("POOL %s" % cfgF.pool_id), "outcome: the pool id is its first line", "S5")
        for tag in ("ASSERT |TRAIN intersect", "scored_minus_eval=0", "G1:", "G2:", "C0 CROSS-INSTRUMENT", "C1 DEPLOYED GAIN",
                    "C2 PRED", "C3 PRED", "C4 PLACEBO", "R3 POLICY-VARIANCE", "R4 (DESCRIPTIVE)", "PREDICTIONS", "FALSIFIER",
                    "SUPPORT (measured)", "fit-call TRAIN-subset checks executed and CHECKED: %d == 2B+2" % (2 * cfgF.B + 2),
                    "LF blob sha16", "sidecar %s-wal: absent" % cfgF.union_db, "sidecar %s-wal: absent" % cfgF.emb_db):
            chk(tag in body, "outcome carries %r" % tag, "S5")
        chk(resF["C0"] == "HELD", "full fixture C0 HELD at its own values", "S5")
        chk(body.splitlines()[1].startswith("sidecar "), "sidecars printed right after the POOL line", "S5")
        before = open(cfgF.out_path, "rb").read()
        b2x = io.StringIO()
        try:
            with contextlib.redirect_stdout(b2x):
                mode_run(cfgF, ff)
            fired = False
        except SystemExit as ex:
            fired = "exists; an outcome file of record is never overwritten" in str(ex)
        chk(fired and open(cfgF.out_path, "rb").read() == before, "second --run refused; file unchanged", "S5")
        chk("FITS AND BOOTSTRAPS" not in b2x.getvalue() and "G1:" not in b2x.getvalue(), "refused before any work", "S5")
        # Ruling (d), WAL: a NON-EMPTY -wal beside EITHER input DB refuses every mode at launch, prints nothing, writes nothing.
        for dbp in (cfg.union_db, cfg.emb_db):
            with open(dbp + "-wal", "wb") as f:
                f.write(b"\0")
            for fn in (mode_run, mode_dry_run, mode_legacy):
                bw = io.StringIO()
                try:
                    with contextlib.redirect_stdout(bw):
                        fn(cfg, ff)
                    fired = False
                except SystemExit as ex:
                    fired = str(ex).startswith("[WAL] %s-wal is 1 bytes: a writer is live; refusing at launch" % dbp)
                chk(fired and bw.getvalue() == "" and not os.path.exists(cfg.out_path),
                    "%s refuses on a non-empty %s-wal, silent, nothing written" % (fn.__name__, os.path.basename(dbp)), "S5")
            # a sidecar that appears AFTER launch is refused by prefix too
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    prefix(cfg, ff, cfg.pool_id)
                fired = False
            except SystemExit as ex:
                fired = "[WAL]" in str(ex) and "appeared after launch" in str(ex)
            chk(fired, "prefix refuses a sidecar that appeared after launch (%s)" % os.path.basename(dbp), "S5")
            os.remove(dbp + "-wal")
        open(cfg.union_db + "-wal", "wb").close()                 # EMPTY sidecar: admitted, and its size printed
        bw = io.StringIO()
        with contextlib.redirect_stdout(bw):
            mode_dry_run(cfg, ff)
        chk("sidecar %s-wal: 0 bytes" % cfg.union_db in bw.getvalue() and "sidecar %s-wal: absent" % cfg.emb_db in bw.getvalue()
            and bw.getvalue().splitlines()[0].startswith("POOL "), "empty sidecar admitted and printed; POOL still first", "S5")
        os.remove(cfg.union_db + "-wal")

        def fill(cX, poolX, n_e, n_t, B):
            """Fixture expectations from the fixture's own data through the same functions (so G1-G3 pass)."""
            cX.reg.update(n_eval=n_e, n_train=n_t, n_routed=n_e + n_t, roster=3, min_leaf=5, n_mmlu=0)
            cn = real_connect(cX.union_db)
            QX = {qq: (s_, d_, t_) for qq, s_, d_, t_ in cn.execute("SELECT question_id, source, domain, text FROM corpus_questions")}
            GX = defaultdict(dict)
            for qq, mm, c in cn.execute("SELECT question_id, model_name, is_correct FROM eval_results"): GX[qq][mm] = c
            cn.close()
            lvX = federated_leaves(cX, ff); vcX = ff.embed_matrix(cX.emb_db, [QX[x][2] for x in sorted(QX)], 4)
            DX = build_data(QX, models, GX, poolX, lvX, vcX, cX)
            with contextlib.redirect_stdout(io.StringIO()):
                _, dX, nX = legacy_seed(DX, cX, with_boot=False)
            PX = fit_clean(DX, train_full_w(DX)); aX = correctness(DX, PX)[:, DX.E].mean(axis=1)
            cX.reg.update(g1_src="%.3f" % DX.src_ok, g1_dom="%.3f" % DX.dom_ok, g2_gain="%+.4f" % dX, g2_n=nX,
                          c0_best=DX.models[PX.gb], c0_bs="%.4f" % aX[BS], c0_tdom="%.4f" % aX[TDOM])
            cX.B = B
        # Ruling (e), G4 through mode_run: every model identical on every question -> G and P are 0 in every replicate.
        rngz = random.Random(5); rowsZ = []; poolZ = set(); qvZ = {}; q = 1
        for k in range(3):
            for i in range(30):
                bit = int(rngz.random() < 0.5)
                rowsZ.append((q, "SRC%d" % (k // 2), "d%d" % k, "tz-%d" % q, {mm: bit for mm in models}))
                if i % 3 == 0: poolZ.add(q)
                qvZ["tz-%d" % q] = base[k]; q += 1
        leavesZ = {"cA": [("SRC0/d0", [("L0", base[0])]), ("SRC0/d1", [("L1", base[1])])],
                   "cB": [("SRC1/d2", [("L2", base[2])])]}
        cfgZ = _write_fixture(os.path.join(tmp, "zero"), models, rowsZ, poolZ, leavesZ, qvZ)
        fill(cfgZ, poolZ, 30, 60, 40)
        bz = io.StringIO()
        try:
            with contextlib.redirect_stdout(bz):
                mode_run(cfgZ, ff)
            fired = False
        except SystemExit as ex:
            fired = str(ex).startswith("[G4] the two-stage variance of C1 is 0")
        chk(fired and not os.path.exists(cfgZ.out_path) and "=== VERDICTS ===" not in bz.getvalue(),
            "G4 refuses a zero-variance run before any verdict; no file", "S5")
        # D6: the run CHECKS the fit-call count (2B + 2); a bootstrap that ran one replicate short is refused.
        cD = Cfg(**cfgF.__dict__); cD.reg = dict(cfgF.reg); cD.out_path = os.path.join(tmp, "out_d6", "outcome.txt")
        orig_rb = globals()["run_bootstraps"]
        globals()["run_bootstraps"] = lambda D_, B_, seed_, log=print, hook=None: orig_rb(D_, B_ - 1, seed_, log=None)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode_run(cD, ff)
            fired = False
        except SystemExit as ex:
            fired = "[G3(4)] fit-call count %d != 2B+2 = %d" % (2 * cD.B, 2 * cD.B + 2) in str(ex)
        finally:
            globals()["run_bootstraps"] = orig_rb
        chk(fired and not os.path.exists(cD.out_path), "fit-call count is CHECKED (2B+2); a short run is refused", "S5")
        import ast
        n_assert = sum(isinstance(nd, ast.Assert) for nd in ast.walk(ast.parse(src)))
        chk(n_assert == 0, "no assert statement anywhere in the file (python -O safe): %d found" % n_assert, "S5")
        # The mode-x open itself refuses a file that appears between the check and the write.
        chk("open(cfg.out_path, \"x\"" in src, "outcome opened with mode x", "S5")
        chk("import stack_judge" not in src.replace('"import stack_judge"', "") and "stack_judge" not in sys.modules,
            "stack_judge never imported", "S5")
        chk(all(os.path.abspath(p).lower().startswith(os.path.abspath(tmp).lower()) for p in opened) and opened,
            "every DB opened lives under the fixture dir (%d opens)" % len(opened), "S5")
        # Every declared branch (verdicts, predictions, falsifier, triggers, G4, WAL) was EXECUTED above, and nothing else.
        missing = set(ALL_BRANCHES) - _HIT
        chk(not missing, "branches never executed: %s" % sorted(missing), "BR")
        chk(not (_HIT - set(ALL_BRANCHES)), "undeclared branches executed: %s" % sorted(_HIT - set(ALL_BRANCHES)), "BR")
    finally:
        sqlite3.connect = real_connect
        hit = set(_HIT); _HIT.clear(); _HIT.update(old_hit)
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST OK: %d checks (%s); %d of %d registered branches executed; fixtures under a tempfile.mkdtemp() dir, "
          "removed; no real DB opened (real NON-DB reads: the paeec id file and reserved_pools.json via pool_guard, and "
          "source files read by transitive imports)" % (chk.n, ", ".join("%s %d" % kv for kv in sorted(chk.sections.items())),
                                          len(hit & ALL_BRANCHES), len(ALL_BRANCHES)))
    return chk.n


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=TEST_ID)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true")
    g.add_argument("--legacy", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); sys.exit(0)
    import free_tests_f4_f7 as _ff
    cfg = real_cfg()
    if a.dry_run: mode_dry_run(cfg, _ff)
    elif a.legacy: mode_legacy(cfg, _ff)
    else: mode_run(cfg, _ff)
