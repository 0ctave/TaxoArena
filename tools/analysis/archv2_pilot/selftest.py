"""archv2_pilot.selftest: SYNTHETIC ONLY (no DB of record is opened; no call is posted: a fake call_full).

    python tools/analysis/archv2_pilot/selftest.py [--part stage1|supply|all]
    python -O tools/analysis/archv2_pilot/selftest.py [--part ...]

No assert anywhere: every check is an explicit comparison printed PASS / FAIL and counted; every guard under test refuses
by raise SystemExit, so the -O run executes the same branches.

FIXTURE. data_v2.gates._fixture (the E-D fixture: two tiny source DBs with the schemas of record, NEW files in a temporary
directory) plus: 14 MMLU-Pro categories (the real anchor names) with 12..38 questions each, answered by the 12 ARENA12
models and two extra models (roster 16 = ARENA12 + the fixture's mA / mB + 2 extras; Meta-Llama QUARANTINED), preds
correlated with a per-model strength that the model output states ("quality=<s>", which the fake judge reads), one extra
model shown REVERSED options on 8 questions per category (MIXED orderings), grok-reasoning-v0 references on two of every
three questions (so some matches are excluded per match), and 40 cross-corpus twins in the union corpus (so a count without the
corpus_version filter double-counts). Then E-D's own ingest -> split (DEV seed) -> gen_view / eval_view.

PARTS: the frozen-instrument lf16; the stream seed rule; the stage-1 draw (identity with design.choose_strata, one per
group, write-once, verify and its refusals); the supply JSON (parsed by archv2_g22_sim.supply_from; the 7-anchor file
makes choose_strata return exactly the registered 7); the scheduler's identity with design.schedule_stratum; the plan
(anchors inside the 7, the trim applied with ARENA12 pairs kept, the predicted exclusions accepted by the loader); the
launch (posting day, pilot before run, no --go posts nothing, the pilot guard, the ledger); the analysis (C0 on a partial
cache, then complete: C1 written before the key, the readings); every print branch; and the MUTANTS:
  cv_filter_dropped   the corpus_version filter dropped            -> REFUSED (ids not distinct)
  trim_arena12        ARENA12 pairs admitted to the trim           -> REFUSED (NEVER trimmed)
  cap_off             the trim skipped                              -> REFUSED (> the cap)
  anchors_from_14     the pilot draws from the 14, not the 7        -> REFUSED (C0 (g))
  a 14-anchor stage-1 file                                          -> REFUSED (the registered 7)
  the rubric sha missing / wrong                                    -> REFUSED
  unseal_early        the key read before C1 is written             -> REFUSED
  refit_pair          C1's nominal on a refit pair                  -> REFUSED
  the cap exceeded at the ledger (ceiling, match rule, day cap)     -> REFUSED
[AMENDED 2026-09-25 (0761cfa, k = 37), insertion only: the fixture adds ONE ACTIVE model "zz-dropped-1" with EMPTY
outputs, dropped by the fixture Config's DEV drop list (roster 16 = 17 ACTIVE - 1; registry 18). ADDED refusals: a dropped
model missing / not ACTIVE; a roster sha mismatch; a dropped model in ARENA12; a scheduled row naming a non-roster model;
the trim engaged (t > 0, C0 (h)) and the schedule bound; an EMPTY output on a scheduled cell (the drop list removed); a
printed M bar that is not round(exact_M, 4). The trim is exercised as a unit (it can no longer pass make_plan: C0 (h)).
ADDED units: the exact M bar at k 37 (2.052941 / 2.0529), the C1b bars at k 37 (0.3556 / 1.0878), the K8 boundary at 666
pairs (14 THIN, 13 not), the raw-output counter (empty, 39 and 40 characters), the arx_0314 disclosure, the Kotlin
BANNED_MODELS list = the 9 + Meta-Llama.]
[RE-PINNED 2026-09-25, insertion only (the author's pre-decided fallback; record pending): the fixture's rubric slot is
the slot of record, GENERIC_RUBRIC (pilot.load_generic_rubric, record mode), so every launch / analysis below judges the
system turn of record. ADDED: the slot's sha, length and import; payload.build_system = STACK-NORUBRIC's measured
combination (and stack_norubric.py's source carries that formula); refusals of any other text in record mode, a wrong
--rubric-sha256 witness, the artefact arguments in a record run, the INDUCE-RUBRIC-1 path in record mode (disclosure
only); MUTANT norubric_off; the slot line printed in the outcome. K2: the pins are MAIN b653b0a's (induction.py 147e6874,
a layer-identity pin), each also = main's actual blob; the INDUCE-RUBRIC-1 mode is retired. K10 (c) (the INDUCE-1
positive label / population) is replaced by the disclosure-only refusal.]
[ADDED 2026-09-25 after the pilot-12 transport incident, insertion only: the fixture sets rejudge_reasoning's endpoint /
key to FIXTURE values (https://fixture.invalid, never posted to: every launch injects a fake call_full) so that every
launch executes the transport preflight; part_transport: load_transport from a data root's .env (rr.ROOT restored, no
value printed), the preflight's refusals (endpoint / key / deployment None or empty, http, no host, no .env), MUTANT
load_env_skipped refused by the preflight with the journal, the store, the manifest and the ledger UNTOUCHED and 0 posts;
the retired store refused in record mode; prior journals counted on the journal side (a new store reconciles against a
ledger that carries a retired store's rows; without them the launch refuses AHEAD; a wrong prior sha refuses).]
[ADDED 2026-09-25, L7' (READY 1f58df5 L7': after the run, before --analyze), insertion only: part_l7_units (F3: the
ruling's 8-case table, the exact M unrounded, K7, P3b FAILED iff the falsifier fires; F2: measured_deff / deff_lines /
support_lines, every branch; G1: P5 on journal + prior at the 8,000 boundary; F4: the record's text verbatim, both
system-turn branches; MUTANTS p3b_inverted, p3_no_undetermined, deff_inverted); part_l7_outcome (the fixture outcome: the
DEFF recomputed from the two record files; the INERTNESS of C1 under the DEFF code, leg A deff_off vs leg B with the
execution witness; F3 / F4 / F8 / G1 lines; P3 UNDETERMINED in the partial-cache and the C0 (d)-void branches; the
CODE IDENTITY disclosure: an analysis lf16 and a store script_blob that differ from each other, and --analyze still reads
the store; MUTANTS deff_question_draws, p5_journal_only); part_transport_probe (G2, the reviewer's probe: (a) data_root
honours TAXOARENA_DATA_ROOT, (b) a --run launch with the endpoint None is refused with store / journal / ledger
byte-identical; MUTANTS T3 and T2 killed).]
[ADDED 2026-09-25, D-4 (delta READY 3 0c10ea2), insertion only: the falsifier NOT READ without a C1 reading (units:
K7, C0 FAILED with and without words; end to end: the forced-zero K7 world, the partial cache, the C0 (d)-void branch);
MUTANT falsifier_not_fired_no_reading killed; branch FALSIFIER.NOT_READ.]
[ADDED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239), insertion only:
part_pool (also alone: --part pool): a pooled pilot + run at workers 4 equal to the workers-1 launch slot for slot; the
labels ' w=4', journal v2, ledger == journal; EC5 (the no-go launch prints the preflight, the [POOL] line and max_inflight,
posts nothing, creates nothing; the line names a journal created at workers 1 and the refusal to come); a pooled --run on
a journal created at workers 1 refused before any post; the rate control at workers 1 (a RateConfig makes the single
poster pooled; refused on a workers-1 journal); I5 the TRANSPORT PREFLIGHT first at workers 4 (nothing written, 0 posts)
with MUTANTS preflight_after_pool and preflight_skipped_pooled killed. K2 re-pinned: the record table is b653b0a's with
judge_v2/writer.py moved and judge_v2/pool.py added (8 pins; the live table is judge_v2.writer._pins()); MAIN-B653B0A is
retired. --main-ref REF (SELFTEST-ONLY, printed): K2's main-blob lookups resolve against REF in this process -- the
pre-merge simulation of a branch whose judge_v2 is not yet main's (on the unmerged branch K2 refuses writer.py and
pool.py by design, and every launch with it).]
"""
import hashlib
import json
import math
import os
import random
import re
import shutil
import sys
import tempfile

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "archv2_pilot"
    import archv2_pilot  # noqa: F401

import numpy as np  # noqa: E402

from . import common as C  # noqa: E402
from . import stage1 as S1  # noqa: E402
from . import supply as SU  # noqa: E402
from archv2_arena import design, report  # noqa: E402
from archv2_arena.streams import Streams  # noqa: E402
from data_v2 import gates as dv2gates, ingest as dv2ingest, split as dv2split  # noqa: E402
from data_v2 import views as dv2views  # noqa: E402
import rubric_p8  # noqa: E402

# The pilot's modules import judge_v2 (whose _base pins the data_v2 blobs): loaded only by the "all" part, so the stage-1
# and supply selftests run without judge_v2 (re-pin 2026-09-24: main's data_v2 moved at 093ab1e).
PL = A = OC = ACC = JI = P = None
FIXTURE = {}


def _load_pilot():
    global PL, A, OC, ACC, JI, P
    from . import accounting as _acc, analysis as _a, outcome as _oc, pilot as _pl
    from judge_v2 import induction as _ji, payload as _p
    PL, A, OC, ACC, JI, P = _pl, _a, _oc, _acc, _ji, _p

CATS = ["biology", "business", "chemistry", "computer science", "economics", "engineering", "health", "history", "law",
        "math", "other", "philosophy", "physics", "psychology"]
EXTRAS = ["zz-extra-1", "zz-extra-2"]
MIXER = "zz-extra-1"
VARIANT_MODEL = "zz-extra-2"
DROPPED_DEV = "zz-dropped-1"        # [0761cfa] the fixture's DEV drop list (ACTIVE, empty outputs)
DEV_SEED = "DEV-archv2-pilot-selftest"
U_TEXT = "A quarantined-only fixture question that no active model answered and no corpus row carries?"
TODAY = "2026-09-25"


class Checks:
    def __init__(self, out):
        self.out, self.n, self.fails = out, 0, []

    def check(self, name, ok, detail=""):
        self.n += 1
        ok = bool(ok)
        self.out("[SELFTEST-PILOT] %s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + str(detail)[:300]) if detail else ""))
        if not ok:
            self.fails.append(name)
        return ok

    def refused(self, name, fn, must=()):
        try:
            fn()
        except SystemExit as e:
            msg = str(e)
            return self.check(name + " -> REFUSED", all(s in msg for s in must), msg[:220])
        return self.check(name + " -> REFUSED", False, "no refusal")


def _rmtree(p):
    def onerr(fn, path, _exc):
        try:
            os.chmod(path, 0o666)
            fn(path)
        except OSError:
            pass
    shutil.rmtree(p, onerror=onerr)


def _mutant(mod, name):
    class _M:
        def __enter__(self):
            mod.MUTANT = name

        def __exit__(self, *a):
            mod.MUTANT = None
    return _M()


def _scratch(path):
    """THE ONE read-write open in this selftest, on the fixture's own LEGACY-schema source DBs (never a v2 corpus, view or
    verdict DB): the rule of data_v2.ro.open_scratch_rw restated (an existing file under the system temporary directory,
    anything else REFUSED), then the unwrapped connect (archv2_arena.ro.REAL_CONNECT)."""
    from archv2_arena import ro as aro
    tmp = os.path.realpath(tempfile.gettempdir())
    rp = os.path.realpath(path)
    if not (os.path.isfile(rp) and os.path.commonpath([tmp, rp]) == tmp):
        raise SystemExit("[SELFTEST-PILOT] _scratch refuses %s: only an existing file under %s" % (path, tmp))
    return aro.REAL_CONNECT(rp)


# ── the fixture ─────────────────────────────────────────────────────────────────────────────

def build_fixture(tmp):
    data_root = os.path.join(tmp, "data")
    build = os.path.join(tmp, "build")
    os.mkdir(data_root)
    os.mkdir(build)
    dv2gates._fixture(data_root)
    rng = random.Random(20260925)
    models = sorted(rubric_p8.ARENA12) + EXTRAS
    strength = {m: k + 1 for k, m in enumerate(models)}
    cw = _scratch(os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db"))
    c0 = _scratch(os.path.join(data_root, "experiment_results", "judge_solve", "grok-reasoning.db"))
    twins = []
    qid = 20000
    for ci, cat in enumerate(CATS):
        for k in range(12 + 2 * ci):
            qid += 1
            text = "Fixture question %d on %s: which of the listed options holds?" % (qid, cat)
            opts = ["%s option %d letter %s" % (cat, qid, x) for x in "ABCD"]
            gt = rng.choice("ABCD")
            cur = cw.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?,?,?,?,?)",
                             (text, cat, "", json.dumps(opts), gt))
            cw.execute("INSERT INTO eval_question_link VALUES (?,?,?,0)", (qid, cur.lastrowid, text))
            for mo in models:
                p_ok = 0.25 + 0.045 * strength[mo]
                pred = gt if rng.random() < p_ok else rng.choice([x for x in "ABCD" if x != gt])
                o, pr, g = opts, pred, gt
                if mo == MIXER and k < 8:
                    o = list(reversed(opts))
                    pr = "ABCD"[3 - "ABCD".index(pred)]
                    g = "ABCD"[3 - "ABCD".index(gt)]
                if mo == VARIANT_MODEL and k in (3, 4):
                    # another OPTION SET (a fifth option): another variant of the same item (the K8 mask's case)
                    o = opts + ["%s option %d letter E" % (cat, qid)]
                out = "Worked reasoning, quality=%d, for fixture question %d. Final answer (%s)." % (strength[mo], qid, pr)
                cw.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
                           (qid, mo, cat, text, json.dumps(o), g, pr, out, int(pr == g)))
            if k % 3 != 2:
                c0.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?)", (qid, gt, gt, 1, "solve %d" % qid, 10, 1.0,
                                                                            1757400000.0))
            if len(twins) < 40 and k % 5 == 1:
                twins.append((6000000 + qid, "MMLU_PRO", qid, "mmlu_pro_" + cat, cat, text, json.dumps(opts), gt,
                              "MC_LETTER", 0))
    cw.commit()
    cw.close()
    c0.commit()
    c0.close()
    # [0761cfa] ONE ACTIVE model with EMPTY outputs on every question, DROPPED by the fixture's DEV drop list (the real 9
    # are six text-less and three mixed-format); its own rng, so the rows above are unchanged
    cw = _scratch(os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db"))
    rd = random.Random(37)
    rows = cw.execute("SELECT question_id, category, question_text, options_json, gt_answer FROM eval_results WHERE"
                      " model_name=? ORDER BY question_id", (models[0],)).fetchall()
    for qid_, cat, text, oj, g in rows:
        cw.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
                   (qid_, DROPPED_DEV, cat, text, oj, g, rd.choice("ABCD"), "", 0))
    cw.commit()
    cw.close()
    # CK-CLOSE-v2 U: a QUARANTINED-ONLY item (only Meta-Llama answered it; no corpus row): the split excludes it and it
    # appears in NO view (views.build_view skips it)
    cw = _scratch(os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db"))
    cw.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
               (99999, "Meta-Llama-3-70B-Instruct", "law", U_TEXT, json.dumps(["u1", "u2"]), "A", "A", "u out", 1))
    cw.commit()
    cw.close()
    u = _scratch(os.path.join(data_root, "multicorpus_cache_v1.db"))
    for r in twins:
        u.execute("INSERT INTO corpus_questions VALUES (?,?,?,?,?,?,?,?,?,?)", r)
    u.commit()
    u.close()
    quiet = lambda s: None  # noqa: E731
    repo = os.path.join(tmp, "repo")
    paths = [dv2ingest.build_corpus(cv, build, out=quiet, data_root=data_root, repo_root=repo)["path"]
             for cv in ("mmlu-pro-v2", "mc6-2026-09-11")]
    FIXTURE["corpus_paths"] = list(paths)
    sp = dv2split.build_split(paths, build, "DEV-archv2-pilot-selftest", out=quiet)
    gv = dv2views.build_view("gen", paths, sp["path"], build, out=quiet)
    ev = dv2views.build_view("eval", paths, sp["path"], build, out=quiet)
    return gv["path"], ev["path"]


def fixture_roster():
    return sorted(list(rubric_p8.ARENA12) + ["mA", "mB"] + EXTRAS)


def fixture_cfg(**kw):
    # the former DEV pin mode "f5bbbda" is retired (re-pin 2026-09-24): the fixture runs under the record pin mode
    # [0761cfa] active_n 17 (the 16 + DROPPED_DEV), the DEV drop list, the fixture roster's sha, the exact bar at k 16
    base = dict(roster_n=16, active_n=17, dropped=(DROPPED_DEV,), roster_sha256=C.sha256_text("\n".join(fixture_roster())),
                rungs=(12, 14, 16), bar_M=round(PL.exact_M(16, 12), 4), B_outer=24, B_inner=16, B_rungs=8,
                n_integrated=3, registry_total=18)
    base.update(kw)
    return PL.Config(**base)


def fake_call_factory():
    n = {"calls": 0}
    rx = re.compile(r"quality=(\d+)")

    def call(system, user):
        n["calls"] += 1
        q = rx.findall(user)
        h = int(hashlib.sha256((system + user).encode("utf-8")).hexdigest()[:8], 16) / 2.0 ** 32
        p = 1.0 / (1.0 + math.exp(-0.6 * (int(q[0]) - int(q[1])))) if len(q) >= 2 else 0.5
        w = "Model A" if h < 0.9 * p else ("Model B" if h < 0.9 else "TIE")
        return (json.dumps({"winner": w, "confidence": 0.8, "reasoning": "fixture"}), "azure:fixture-judge", 12, 0.01,
                "stop", {"_response_id": "fx-%d" % n["calls"]})
    call.n = n
    return call


# ── parts ───────────────────────────────────────────────────────────────────────────────────

def part_basics(ck):
    ck.check("the frozen instrument is the chain's (instrument_lf16 %s)" % C.FROZEN_INSTRUMENT_LF16,
             C.check_instrument() == C.FROZEN_INSTRUMENT_LF16)
    st = Streams(S1.MASTER)
    want = int.from_bytes(hashlib.sha256(("%s|%s" % (S1.MASTER, S1.STREAM)).encode("utf-8")).digest()[:8], "big")
    ck.check("the stream seed is sha256(master|name)[:8] big-endian", st.seed(S1.STREAM) == want, want)
    ck.check("the stage-1 master is the RE-DRAW's (5b89159), the first draw's kept for disclosure only",
             S1.MASTER == "ARCHV2-STAGE1-ANCHORS-2:e2623b4b69e664a9f222abc8b1121dc19d92cceb" and
             S1.REGISTRATION == "ARCH-V2-STAGE1-ANCHOR-DRAW-2" and S1.MASTER_1.endswith("229687736d52902c3741e48ebc83be62efed488c"))
    ck.refused("the first draw's master is never reused", lambda: S1.draw({c: 1 for c in CATS}, S1.MASTER_1), ("never reused",))
    ck.check("the split of record pins (5a3e756): view e35b7518..., pools pv2_41dbd3dbcd399df0 / pv2_1575de61bb20e977",
             C.EVAL_VIEW_SHA256.startswith("e35b7518") and C.POOL_MMLU == "pv2_41dbd3dbcd399df0" and
             C.POOL_UNION == "pv2_1575de61bb20e977" and C.SPLIT_SEED.endswith("2929bd46aa271d883050bfe735f96e621ed55fd2"))
    from archv2_arena import ro as aro
    m = aro.REAL_CONNECT(":memory:")
    m.execute("CREATE TABLE pool (pool_id TEXT, scope TEXT, n_components INTEGER, n_items_by_scope TEXT)")
    m.execute("INSERT INTO pool VALUES ('pA', 'all corpora + mc6-2026-09-11', 5, '{\"all corpora\": 9, \"mc6-2026-09-11\": 9}')")
    m.execute("INSERT INTO pool VALUES ('pB', 'mmlu-pro-v2', 3, '{\"mmlu-pro-v2\": 4}')")
    a1, b1 = C.pool_of(m, "mc6-2026-09-11"), C.pool_of(m, "mmlu-pro-v2")
    m2 = aro.REAL_CONNECT(":memory:")
    m2.execute("CREATE TABLE pool (pool_id TEXT, scope TEXT, n_components INTEGER, n_items INTEGER)")
    m2.execute("INSERT INTO pool VALUES ('pC', 'mmlu-pro-v2', 3, 7)")
    c1 = C.pool_of(m2, "mmlu-pro-v2")
    ck.check("pool_of reads the merged-scope n_items_by_scope schema (093ab1e) and the older n_items schema",
             a1["pool_id"] == "pA" and a1["n_items"] == 9 and b1["n_items"] == 4 and c1["n_items"] == 7, (a1, b1, c1))
    m.close()
    m2.close()


def part_u_excluded(ck, gen_path, ev_path):
    """CK-CLOSE-v2 U (data_v2 093ab1e): the quarantined-only fixture item is in NEITHER view."""
    from data_v2 import common as dv2c
    iid = dv2c.item_id_of_key(dv2c.KeyCache().stem(U_TEXT))
    ce = dv2views.open_eval("arena", ev_path)
    cg = dv2views.open_generation("construct", gen_path)
    try:
        ne = ce.execute("SELECT COUNT(*) FROM item WHERE item_id=?", (iid,)).fetchone()[0]
        ng = cg.execute("SELECT COUNT(*) FROM item WHERE item_id=?", (iid,)).fetchone()[0]
        nse = ce.execute("SELECT COUNT(*) FROM side WHERE item_id=?", (iid,)).fetchone()[0]
    finally:
        ce.close()
        cg.close()
    from archv2_arena import ro as aro
    nc = 0
    for cp in FIXTURE.get("corpus_paths", []):
        cc = aro.open_ro(cp)
        try:
            nc += cc.execute("SELECT COUNT(*) FROM item WHERE item_id=?", (iid,)).fetchone()[0]
        finally:
            cc.close()
    ck.check("the U-excluded (quarantined-only) item IS in the corpus (%d) and appears in no view (eval %d, gen %d, eval"
             " side %d)" % (nc, ne, ng, nse), nc >= 1 and ne == ng == nse == 0)


def part_stage1(ck, ev_path, tmp):
    conn, sha, _m = C.open_view("arena", ev_path, None, lambda s: None)
    try:
        pool = C.pool_of(conn, C.CV_MMLU)
        anchor_of, counts, _raw = C.anchor_of_items(conn, C.CV_MMLU, pool)
        with _mutant(C, "cv_filter_dropped"):
            ck.refused("MUTANT cv_filter_dropped: the per-anchor counts without corpus_version",
                       lambda: C.anchor_of_items(conn, C.CV_MMLU, pool), ("corpus_version",))
        ck.refused("the pool of record is required in a record read", lambda: C.pool_of(conn, C.CV_MMLU, C.POOL_MMLU),
                   ("pool of record",))
    finally:
        conn.close()
    ck.check("the fixture pool has the 14 anchors, ids distinct, total = the pool row", len(counts) == 14 and
             sum(counts.values()) == pool["n_items"], counts)
    chosen, groups, st = S1.draw(counts)
    rng = np.random.Generator(np.random.PCG64(Streams(S1.MASTER).seed(S1.STREAM)))
    names = sorted(counts, key=lambda k: (-counts[k], k))
    manual = sorted(names[int(rng.choice(g))] for g in np.array_split(np.arange(14), 7))
    ck.check("the draw equals design.choose_strata's procedure computed by hand (sort, 7 groups, one per group)",
             chosen == manual, (chosen, manual))
    ck.check("one anchor per group of 2, 7 in all", all(len(set(g) & set(chosen)) == 1 for g in groups) and
             len(chosen) == 7 and all(len(g) == 2 for g in groups))
    rec = S1.make_record(counts, chosen, groups, st, ev_path, sha, pool, record=False)
    p = os.path.join(tmp, "stage1.json")
    C.write_once_json(p, rec)
    ck.refused("the stage-1 record is write-once", lambda: C.write_once_json(p, rec), ("exists",))
    ck.check("verify reads back the 7 (DEV record)", S1.verify(p, counts=counts, view_sha=sha, record=False) == chosen)
    ck.check("the record pins the RUNNER (the CLI blob / lf16, the package lf16, the instrument lf16) and the split",
             rec["runner"]["archv2_stage1_anchor_draw.py"].startswith("blob:") and
             rec["runner"]["frozen instrument_lf16"] == C.FROZEN_INSTRUMENT_LF16 and rec["split_of_record"] == C.SPLIT_LABEL)
    ck.refused("a DEV record is refused where a record draw is required", lambda: S1.verify(p, record=True),
               ("not of record",))
    bad = dict(rec, anchors=sorted(counts))
    ck.refused("MUTANT wrong anchor source: a stage-1 file carrying the 14", lambda: S1.verify(bad, record=False),
               ("carries 14 anchors",))
    t = dict(rec, counts=dict(rec["counts"], biology=rec["counts"]["biology"] + 1))
    ck.refused("tampered counts", lambda: S1.verify(t, record=False), ("digest",))
    t2 = dict(rec, anchors=sorted(set(counts) - set(chosen))[:7])
    ck.refused("anchors that do not reproduce", lambda: S1.verify(t2, record=False), ("reproduce",))
    ck.refused("another eval_view", lambda: S1.verify(p, view_sha="0" * 64, record=False), ("drawn on eval_view",))
    # READY a254a1d LOW-1: the meta-seed guard of common.open_view is defence in depth (the pinned bytes already fix the
    # seed, so it cannot fire on the record path); a MUTANT makes the fixture view's sha "the pinned sha" to execute it
    saved = C.EVAL_VIEW_SHA256
    try:
        C.EVAL_VIEW_SHA256 = sha
        ck.refused("MUTANT a view with the pinned sha but another meta seed (defence in depth)",
                   lambda: C.open_view("arena", ev_path, sha, lambda s: None), ("meta seed",))
    finally:
        C.EVAL_VIEW_SHA256 = saved
    # READY a254a1d LOW-3: the draw CLI appends a refusal's text to its --transcript, then re-raises
    import archv2_stage1_anchor_draw as DRAW
    tp = os.path.join(tmp, "draw_refused_transcript.txt")
    ck.refused("the draw CLI refuses a record draw under another master",
               lambda: DRAW.main(["--dry-run", "--eval-view", ev_path, "--master", "DEV-not-the-master",
                                  "--transcript", tp]), ("registered master",))
    txt = open(tp, encoding="utf-8").read() if os.path.isfile(tp) else ""
    ck.check("LOW-3: the refusal's text is IN the transcript", "REFUSED:" in txt and "registered master" in txt, txt[:200])
    tp2 = os.path.join(tmp, "draw_dev_transcript.txt")
    DRAW.main(["--dry-run", "--dev", "--master", "DEV-archv2-stage1", "--eval-view", ev_path, "--transcript", tp2])
    txt2 = open(tp2, encoding="utf-8").read()
    ck.check("LOW-3: a run that does not refuse writes no REFUSED line", "REFUSED:" not in txt2 and
             "STAGE-1 ANCHORS" in txt2, txt2[-200:])
    return p, counts, chosen


def part_supply(ck, ev_path, tmp, s1path, chosen):
    conn, sha, _m = C.open_view("arena", ev_path, None, lambda s: None)
    try:
        sup_i, man = SU.build(conn, "items", record=False, out=lambda s: None)
        sup_j, _ = SU.build(conn, "judgeable", record=False, out=lambda s: None)
        sup7, _ = SU.build(conn, "judgeable", record=False, only_anchors=s1path, out=lambda s: None)
        ck.refused("--count is required (no default)", lambda: SU.build(conn, None, record=False), ("does not choose",))
        with _mutant(C, "cv_filter_dropped"):
            ck.refused("MUTANT cv_filter_dropped in the supply builder", lambda: SU.build(conn, "items", record=False,
                                                                                         out=lambda s: None),
                       ("corpus_version",))
    finally:
        conn.close()
    ck.check("supply: mmlu 14 anchors and union strata; judgeable <= items", len(sup_i["mmlu"]) == 14 and sup_i["union"]
             and all(sup_j["mmlu"][a] <= sup_i["mmlu"][a] for a in sup_i["mmlu"]))
    path = os.path.join(tmp, "supply.json")
    report.write_once(path, C.canonical_json(sup_j))
    import sqlite3
    from archv2_arena import ro as aro
    import archv2_g22_sim as sim            # its import installs the archv2 global connect guard for the process
    sqlite3.connect = aro.REAL_CONNECT      # restored: the fixture's writer opens its own new store below

    class _Args:
        supply_json = path
    got, label = sim.supply_from(_Args(), None, None)
    ck.check("archv2_g22_sim.supply_from parses the file unchanged", got == sup_j, label)
    ck.check("the 7-anchor supply carries exactly the registered 7", sorted(sup7) == ["mmlu"] and
             sorted(sup7["mmlu"]) == chosen)
    picked = design.choose_strata(sup7["mmlu"], 7, np.random.default_rng(1))
    ck.check("with the 7-anchor supply, design.choose_strata(supply, 7) returns exactly the registered 7 (D1-stage1)",
             sorted(picked) == chosen, picked)


def part_scheduler_identity(ck):
    rng0 = np.random.default_rng(5)
    Q, M = 9, 6
    Parr = rng0.choice(np.array(["opt:a", "opt:b", "opt:c", ""]), size=(Q, M))
    Varr = np.full((Q, M), "v", dtype="<U2")
    a, ea = PL.schedule_anchor(Parr, Varr, 2, np.random.default_rng(11))
    b, eb = design.schedule_stratum(list(range(Q)), list(range(M)), Parr, 2, np.random.default_rng(11))
    ck.check("the scheduler equals design.schedule_stratum when every question is judgeable (rng call for rng call)",
             a == b and ea == eb, (len(a), len(b), ea, eb))
    Varr2 = Varr.copy()
    Varr2[0, 0] = "w"
    c, _ = PL.schedule_anchor(Parr, Varr2, 2, np.random.default_rng(11))
    ck.check("a question answered under two variants is never scheduled for that pair",
             not any(q == 0 and 0 in (i, j) for i, j, q in c))


def part_plan(ck, ev_path, s1path, rubric, chosen):
    quiet = lambda s: None  # noqa: E731
    # [0761cfa] the plan of the fixture runs at t = 0 (C0 (h)); the TRIM RULE stays a fail-closed guard, exercised as a
    # unit on the untrimmed schedule and, through make_plan, as a C0 (h) refusal
    cfg = fixture_cfg()
    lines = []
    plan = PL.make_plan(cfg, ev_path, s1path, lines.append)
    total = len(plan.before)
    cap = total - 25
    ck.check("the pilot anchors are 2 of the registered 7", len(plan.anchors) == 2 and set(plan.anchors) <= set(chosen),
             plan.anchors)
    ck.check("C0 (h) the fixture plan: t = 0, after = before, before <= 2 x N x C(16,2) = %d; the line printed" %
             (2 * cfg.N * 120), plan.t == 0 and plan.kept == plan.before and total <= 2 * cfg.N * 120 and
             any("C0 (h) SCHEDULE BOUND" in x and "trim not engaged (t = 0)" in x for x in lines), (plan.t, total))
    ck.check("the plan prints the roster rule (16 = 17 ACTIVE - 1 dropped) and the dropped sha; digests carry dropped_sha",
             any("16 = 17 ACTIVE - 1 dropped" in x for x in lines) and
             any("dropped (1): %s | dropped_sha %s" % (DROPPED_DEV, C.sha256_text(DROPPED_DEV)) in x for x in lines) and
             plan.digests["dropped_sha"] == C.sha256_text(DROPPED_DEV) and plan.dropped == [DROPPED_DEV] and
             DROPPED_DEV not in plan.roster and plan.digests["roster_sha"] == cfg.roster_sha256, plan.digests)
    ck.check("C0 (b) the raw outputs of the scheduled cells are read (no EMPTY; the dropped model's empties never read)",
             sum(v["empty"] for v in plan.raw_counts.values()) == 0 and set(plan.raw_counts) <= set(plan.roster) and
             sum(v["cells"] for v in plan.raw_counts.values()) > 0 and
             not any(k[1] == DROPPED_DEV for k in plan.free["LEN"]), len(plan.free["LEN"]))
    cfg_t = fixture_cfg(cap_matches=cap)
    kept, removed, t = PL.trim(cfg_t, Streams(cfg_t.master), plan.before, quiet)
    arena = set(cfg.arena12)
    arena_pairs = {PL.pair_key(m) for m in plan.before if PL.pair_key(m)[1] in arena and PL.pair_key(m)[2] in arena}
    ck.check("the TRIM unit (a cap below the schedule): t >= 1, equal per anchor, total <= cap, every ARENA12 pair kept",
             t >= 1 and len(kept) <= cap and arena_pairs <= {PL.pair_key(m) for m in kept} and
             len({k[0] for k in removed}) == 2 and len(removed) == 2 * t, (total, cap, t, len(kept)))
    ck.refused("C0 (h) the trim engaged through make_plan (a cap below the schedule)",
               lambda: PL.make_plan(cfg_t, ev_path, s1path, quiet), ("C0 (h) FAILS", "trim engaged"))
    ck.check("the schedule reproduces (same digests on a second plan)",
             PL.make_plan(cfg, ev_path, s1path, quiet).digests == plan.digests)
    ck.check("the fixture schedules excluded matches (MIXED referenced) and exhausted pairs",
             len(plan.expected) > 0 and sum(s["exhausted_pairs"] for s in plan.stats.values()) > 0,
             (len(plan.expected), {a: s["exhausted_pairs"] for a, s in plan.stats.items()}))
    loaded, order_ids = PL.load_plan(plan, quiet)
    ck.check("the loader accepts the predicted exclusions (realised == expected) and loads the rest",
             set(loaded.manifest["excluded"]) == set(plan.expected) and len(order_ids) == len(plan.kept) - len(plan.expected))
    with _mutant(PL, "trim_arena12"):
        ck.refused("MUTANT trim_arena12: ARENA12 pairs admitted to the trim",
                   lambda: PL.make_plan(cfg_t, ev_path, s1path, quiet), ("NEVER trimmed",))
    with _mutant(PL, "cap_off"):
        ck.refused("MUTANT cap_off: the schedule over the cap", lambda: PL.make_plan(cfg_t, ev_path, s1path, quiet),
                   ("> the cap",))
    with _mutant(PL, "anchors_from_14"):
        ck.refused("MUTANT anchors_from_14: the pilot's anchors drawn from the 14",
                   lambda: PL.make_plan(cfg, ev_path, s1path, quiet), ("C0 (g) FAILS",))
    ck.refused("ARENA12 not inside the roster (C0 (b))", lambda: PL.make_plan(
        fixture_cfg(arena12=tuple(sorted(cfg.arena12))[:11] + ("no-such-model",)), ev_path, s1path,
        quiet), ("ARENA12",))
    # [0761cfa] re-texted for k 37: a registered size of 37 on the fixture's 16-model roster
    ck.refused("a roster of the wrong size (37 required, the fixture's 16)", lambda: PL.make_plan(
        fixture_cfg(roster_n=37), ev_path, s1path, quiet), ("not 37",))
    ck.refused("[0761cfa] the ACTIVE count is not active_n (46 required, the fixture's 17)", lambda: PL.make_plan(
        fixture_cfg(active_n=46), ev_path, s1path, quiet), ("ACTIVE models, not 46",))
    ck.refused("[0761cfa] a dropped model MISSING from the registry", lambda: PL.make_plan(
        fixture_cfg(dropped=("zz-no-such-model",)), ev_path, s1path, quiet), ("not in the", "registry has changed"))
    ck.refused("[0761cfa] a dropped model NOT ACTIVE (the quarantined Meta-Llama in the drop list)", lambda: PL.make_plan(
        fixture_cfg(dropped=(cfg.quarantined,)), ev_path, s1path, quiet), ("not ACTIVE",))
    ck.refused("[0761cfa] a dropped model in ARENA12", lambda: PL.make_plan(
        fixture_cfg(dropped=("arx_0314",)), ev_path, s1path, quiet), ("among the dropped",))
    ck.refused("[0761cfa] a roster sha mismatch", lambda: PL.make_plan(
        fixture_cfg(roster_sha256="0" * 64), ev_path, s1path, quiet), ("roster sha256-text", "not the registered"))
    r17 = sorted(fixture_roster() + [DROPPED_DEV])
    ck.refused("[0761cfa] an EMPTY output on a scheduled cell (the drop list removed: the empty model is scheduled)",
               lambda: PL.make_plan(fixture_cfg(dropped=(), roster_n=17, roster_sha256=C.sha256_text("\n".join(r17)),
                                                rungs=(12, 14, 17), bar_M=round(PL.exact_M(17, 12), 4)),
                                    ev_path, s1path, quiet), ("EMPTY raw output", DROPPED_DEV))
    ck.refused("[0761cfa] a scheduled row naming a model outside the roster", lambda: PL.require_inside(
        plan.kept[:3] + [dict(plan.kept[0], model_b=DROPPED_DEV)], plan.roster, "scheduled"),
        ("1 scheduled row(s) name a model outside",))
    ck.check("[0761cfa] outside_roster counts dict and tuple rows (0 on the plan, 2 on two foreign rows)",
             PL.outside_roster(plan.kept, plan.roster) == 0 and
             PL.outside_roster([(DROPPED_DEV, plan.roster[0]), ("x", "y"), (plan.roster[0], plan.roster[1])],
                               plan.roster) == 2)
    ck.refused("[0761cfa] C0 (h) t > 0 (the unit)", lambda: PL.check_c0h(cfg, plan.stats, len(plan.roster), 1, quiet),
               ("C0 (h) FAILS", "t = 1 > 0"))
    over = {a: dict(s, matches_before_trim=cfg.N * 120 + 1) for a, s in plan.stats.items()}
    ck.refused("[0761cfa] C0 (h) the bound: an anchor above N x C(16,2) = 240", lambda: PL.check_c0h(
        cfg, over, len(plan.roster), 0, quiet), ("C0 (h) FAILS", "exceed N x C(16,2) = 240"))
    ck.check("[0761cfa] schedule_bound at k 37 on 2 anchors: 1,332 per anchor, 2,664 in all (C0 (h))",
             PL.schedule_bound(PL.Config(), 37, 2) == (1332, 2664))
    rows, n, hits = PL.scan_payloads(loaded, rubric, order_ids, quiet)
    ck.check("the dry-run builds and scans 100%% of the payloads (%d = 2 x %d), 0 hits" % (n, len(order_ids)),
             n == 2 * len(order_ids) and not hits)
    return cfg, plan, loaded, order_ids, PL.payload_anchor(rows)


def part_k37_units(ck):
    """[0761cfa] the amendment's constants and units (no DB)."""
    import zlib
    ck.check("[0761cfa] Config: roster_n 37, active_n 46, registry 47, rungs (12, 20, 28, 37), the 9 dropped, the shas",
             PL.Config().roster_n == 37 and PL.Config().active_n == 46 and PL.Config().registry_total == 47 and
             PL.Config().rungs == (12, 20, 28, 37) and len(PL.DROPPED_BANNED) == 9 and
             PL.Config().roster_sha256 == "3a3204cc35cf600495506e6e1f545ab379707b26c16371df78ce654837846f91" and
             C.sha256_text("\n".join(PL.DROPPED_BANNED)) ==
             "36e10ea298adf62d78bd88f0ba5caaa5146507644d4cd55238c11040c9ce29b4" == PL.DROPPED_SHA256)
    ck.check("[0761cfa] ARENA12 and the 9 dropped are disjoint; the quarantined model is not in the 9",
             not (set(rubric_p8.ARENA12) & set(PL.DROPPED_BANNED)) and PL.QUARANTINED not in PL.DROPPED_BANNED)
    kt = os.path.join(C.ROOT, "src", "main", "kotlin", "taxonomy", "dataset", "EvalIngestValidator.kt")
    with open(kt, encoding="utf-8") as f:
        src = f.read().replace("\r\n", "\n")
    blk = src[src.index("BANNED_MODELS: Map<String, String> = mapOf("):]
    blk = blk[:blk.index("\n    )")]
    names = re.findall(r'^\s+"([^"]+)" to', blk, flags=re.M)
    ck.check("[0761cfa] the Kotlin EvalIngestValidator.BANNED_MODELS keys = the 9 dropped + %s (%d keys)" % (
        PL.QUARANTINED, len(names)), sorted(names) == sorted(PL.DROPPED_BANNED + (PL.QUARANTINED,)), names)
    m37 = PL.exact_M(37, 12)
    ck.check("[0761cfa] THE EXACT M at k 37: ln(666/66) / ln(37/12) = 2.052941; the printed bar 2.0529 = round(it, 4)",
             abs(m37 - 2.052941) < 5e-7 and round(m37, 4) == PL.Config().bar_M == 2.0529 and
             A.exact_M is PL.exact_M and PL.exact_bar_M(PL.Config(), 37) == m37, m37)
    ck.refused("[0761cfa] a printed M bar that is not round(exact_M, 4) (the superseded 2.05 at k 37)",
               lambda: PL.exact_bar_M(PL.Config(bar_M=2.05), 37), ("is not round(exact_M(37, 12), 4)",))
    w, l = A.c1_readings(1.5, 1.2, 2.05292, 1.06, m37)
    ck.check("[0761cfa] an upper end in [2.0529, 2.052941) reads 'M EXCLUDED' against the exact bar; the line prints"
             " 'M bar 2.0529 (exact, registered)'", w == ["P EXCLUDED", "M EXCLUDED"] and
             any("M bar 2.0529 (exact, registered)" in x for x in l), (w, l))
    w2, _ = A.c1_readings(1.5, 1.2, 2.05295, 1.06, m37)
    ck.check("[0761cfa] an upper end 2.05295 >= the exact M does not read 'M EXCLUDED'", w2 == ["P EXCLUDED"], w2)
    cfg = PL.Config()
    P_bar, M_bar, ph, plo = A.bars(cfg, 37)
    ck.check("[0761cfa] C1b bars at k 37: P = 0.1078 x (37/12)^1.06 = 0.3556, M = 0.1078 x 666/66 = 1.0878",
             round(P_bar, 4) == 0.3556 and round(M_bar, 4) == 1.0878 and (ph, plo) == (666, 66), (P_bar, M_bar))
    ck.check("[0761cfa] the planning constants 0.23 / 0.29 / 0.82 / 0.99; the memo bars are gone",
             (A.PLANNING_SE, A.PLANNING_SE_INFL, A.PLANNING_MDE, A.P_M_SEPARATION) == (0.23, 0.29, 0.82, 0.99) and
             not hasattr(A, "MEMO_BARS"))
    sl = A.support_lines(0.19, 0.29, {"a": {"q_used": 10, "matches": 20, "kish_m": 2.0}}, {"a": (3, 2)})
    ck.check("[0761cfa] the support line prints the planning constants from the constants (0.19 / 0.23 / 0.29 / 0.82)",
             any("(planning 0.19)" in x and "(planning 0.23; 0.29" in x and "(planning 0.82)" in x for x in sl), sl)
    thin = PL.mask_thin_lines({"a": {"mask": {"exhausted_masked": 24, "exhausted_unmasked": 10}, "pairs": 666},
                               "b": {"mask": {"exhausted_masked": 23, "exhausted_unmasked": 10}, "pairs": 666}})
    ck.check("[0761cfa] K8 at 666 pairs: 14 exhausted by the mask is THIN (> 13.32), 13 is not",
             "thins the target design" in thin[0] and "(14 of 666 pairs" in thin[0] and "does not thin" in thin[1] and
             "(13 of 666 pairs" in thin[1], thin)
    # C2's raw-output counter: an empty output, whitespace only, 39 and 40 characters, 39 two-byte code points
    blobs = {"q1": "", "q2": "   \n ", "q3": "x" * 39, "q4": "  " + "y" * 40 + " ", "q5": "\u00e9" * 39}
    LEN = {(q, "m1"): PL.raw_output_len(zlib.compress(t.encode("utf-8"))) for q, t in blobs.items()}
    ck.check("[0761cfa] raw_output_len: code points after strip (0, 0, 39, 40, 39)",
             [LEN[(q, "m1")] for q in sorted(blobs)] == [0, 0, 39, 40, 39], LEN)
    LEN.update({(q, "m2"): 100 for q in blobs})
    ms = [{"item_id": q, "model_a": "m1", "model_b": "m2"} for q in sorted(blobs)] + [
        {"item_id": "q3", "model_a": "m2", "model_b": "m1"}]
    rc = PL.raw_output_counts({"LEN": LEN}, ms, ["m1", "m2"])
    ck.check("[0761cfa] raw_output_counts over the scheduled CELLS (a repeated cell counted once): m1 empty 2, short 4"
             " (39 counts, 40 does not), short non-empty 2, of 5 cells; m2 0 / 0 of 5",
             rc["m1"] == {"cells": 5, "empty": 2, "short": 4, "short_nonempty": 2} and
             rc["m2"] == {"cells": 5, "empty": 0, "short": 0, "short_nonempty": 0}, rc)

    class _P:
        raw_counts = {"arx_0314": {"cells": 10, "empty": 0, "short": 3, "short_nonempty": 3}, "m2": rc["m2"]}
    rl = OC.raw_output_lines(_P())
    ck.check("[0761cfa] C2's per-model EMPTY / SHORT table and the arx_0314 line",
             any("all models: 0 / 3 / 3 / 15" in x for x in rl) and
             any(x.startswith("  arx_0314 (DISCLOSED; ARENA12): empty 0, short 3 (30.0%)") for x in rl), rl)
    dl = A.disclosure_lines(_P.raw_counts, {12: (2, 10), 20: None, 37: (3, 40)}, "beside C1")
    ck.check("[0761cfa] the arx_0314 DISCLOSURE: counts over its scheduled cells, its called-edge share per rung, the"
             " pair weights (k 12: 11 of 66, k 37: 36 of 666)", any("beside C1" in x and "k 12: 11 of 66 pairs, k 37:"
                                                                     " 36 of 666 pairs" in x for x in dl) and
             any("EMPTY 0, SHORT (< 40, empty included) 3" in x for x in dl) and
             any("rung k 12: called edges naming arx_0314 2 of 10 (0.2000)" in x for x in dl) and
             any("rung k 20: arx_0314 not in this rung's roster" in x for x in dl), dl)
    dl2 = A.disclosure_lines({}, {12: (0, 0)}, "beside C1b")
    ck.check("[0761cfa] the disclosure when arx_0314 has no scheduled cell / no called edge",
             any("has no scheduled cell" in x for x in dl2) and any("no called edge" in x for x in dl2), dl2)
    ed = [{"anchor": "a", "a": "arx_0314", "b": "m2", "p": 0.999, "m": 3.0, "s": 0.1, "agree": 0.0, "right": False},
          {"anchor": "a", "a": "m3", "b": "m2", "p": 0.999, "m": 3.0, "s": 0.1, "agree": 0.0, "right": False},
          {"anchor": "a", "a": "m3", "b": "arx_0314", "p": 0.5, "m": 0.0, "s": 1.0, "agree": 0.0, "right": False}]
    sh = A.called_share(ed, PL.Config().frozen_pair, "arx_0314")
    ck.check("[0761cfa] called_share on three edges (two clear, one coin flip): (called naming arx_0314, called) = (1, 2)",
             sh == (1, 2) and A.called_share([], PL.Config().frozen_pair, "arx_0314") == (0, 0), sh)


def part_generic_slot(ck):
    """[2026-09-25] the rubric slot of record: GENERIC_RUBRIC by sha (the author's pre-decided fallback)."""
    import rubric_value_contrast as rvc
    from judge_v2._base import prompt_v2, rj
    rub, of_rec = PL.load_generic_rubric(record=True)
    ck.check("GENERIC slot: the text is rubric_value_contrast.GENERIC_RUBRIC (imported), sha256-text 67f843eb..., 81"
             " characters, corpus type mcq, no artefact", rub.rubric is rvc.GENERIC_RUBRIC and
             rub.rubric_sha256 == PL.GENERIC_RUBRIC_SHA256 ==
             "67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc" and
             hashlib.sha256(rvc.GENERIC_RUBRIC.encode("utf-8")).hexdigest() == PL.GENERIC_RUBRIC_SHA256 and
             len(rub.rubric) == 81 and rub.corpus_type == "mcq" and rub.artefact_id == "" and
             of_rec == PL.RUBRIC_SLOT_OF_RECORD, (rub.rubric_sha256, len(rub.rubric), of_rec))
    want = (prompt_v2.v2_system_template().replace("$systemPrompt", rvc.GENERIC_SYSTEM)
            .replace("$rubric", rvc.GENERIC_RUBRIC) + "\n\n" + rj.SCHEMA_INSTRUCTION)
    ck.check("GENERIC slot: payload.build_system = STACK-NORUBRIC's measured system turn (v2 template, GENERIC_SYSTEM,"
             " GENERIC_RUBRIC, SCHEMA_INSTRUCTION), byte for byte", P.build_system(rub) == want ==
             PL.stack_norubric_system() and P.FIXED_SYSTEM_PERSONA is rvc.GENERIC_SYSTEM and
             PL.persona_sha() == "3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9")
    with open(os.path.join(C.ANALYSIS, "stack_norubric.py"), encoding="utf-8") as f:
        src = f.read()
    ck.check("GENERIC slot: stack_norubric.py's source carries the formula restated (tmpl = v2_system_template(); nor ="
             " tmpl.replace($systemPrompt, persona).replace($rubric, GENERIC_RUBRIC) + SCHEMA_INSTRUCTION; persona ="
             " GENERIC_SYSTEM under --sp generic; both imported from rubric_value_contrast)",
             "tmpl = prompt_v2.v2_system_template()" in src and
             'persona = GENERIC_SYSTEM if SP_MODE == "generic" else sp' in src and
             'nor = tmpl.replace("$systemPrompt", persona).replace("$rubric", GENERIC_RUBRIC) + "\\n\\n" +'
             ' rj.SCHEMA_INSTRUCTION' in src and "GENERIC_SYSTEM = rvc.GENERIC_SYSTEM" in src and
             "GENERIC_RUBRIC = rvc.GENERIC_RUBRIC" in src)
    ck.check("GENERIC slot: rubric_value_contrast.py is blob 9e1541a7 (provenance, printed)", PL.rvc_blob() == PL.RVC_BLOB,
             PL.rvc_blob())
    sl = PL.rubric_slot_lines(rub)
    ck.check("GENERIC slot: the printed line (C0 header and outcome)", sl[0] == "  rubric slot: GENERIC_RUBRIC (author's"
             " pre-decided fallback 2026-09-25; INDUCE-RUBRIC-1/-2/-3 NOT ADOPTED)" and
             "= STACK-NORUBRIC's measured combination: True" in sl[1] and PL.GENERIC_RUBRIC_SHA256 in sl[1], sl)
    ck.refused("GENERIC slot: any other text in record mode (one trailing space)", lambda: PL.load_generic_rubric(
        record=True, text=rvc.GENERIC_RUBRIC + " "), ("not GENERIC_RUBRIC's",))
    ck.refused("GENERIC slot: an induced-looking rubric text in record mode", lambda: PL.load_generic_rubric(
        record=True, text="Prefer the response whose final answer is correct."), ("not GENERIC_RUBRIC's",))
    r2, o2 = PL.load_generic_rubric(record=False, text="DEV rubric text for the fixture")
    ck.check("GENERIC slot: a DEV call admits another text and labels it NOT OF RECORD",
             o2 == "DEV rubric text, NOT OF RECORD" and r2.rubric_sha256 != PL.GENERIC_RUBRIC_SHA256)
    ck.check("GENERIC slot: the --rubric-sha256 witness equal to the slot's sha is admitted",
             PL.load_generic_rubric(record=True, rubric_sha256=PL.GENERIC_RUBRIC_SHA256)[0].rubric_sha256 ==
             PL.GENERIC_RUBRIC_SHA256)
    ck.refused("GENERIC slot: a wrong --rubric-sha256 witness", lambda: PL.load_generic_rubric(
        record=True, rubric_sha256="0" * 64), ("--rubric-sha256",))
    ck.refused("GENERIC slot: --rubric-artefact in a record run", lambda: PL.check_rubric_args(
        PL.Config(), "rubric.json", None), ("--rubric-artefact",))
    ck.refused("GENERIC slot: --rubric-artefact-sha256 in a record run", lambda: PL.check_rubric_args(
        PL.Config(), None, "0" * 64), ("--rubric-artefact",))
    ck.check("GENERIC slot: no artefact argument in a record run is admitted; a DEV run admits them",
             PL.check_rubric_args(PL.Config(), None, None) is None and
             PL.check_rubric_args(fixture_cfg(), "x.json", "0" * 64) is None)
    real = P.build_system
    try:
        P.build_system = lambda r: real(r) + " "
        ck.refused("GENERIC slot: a system turn that is not STACK-NORUBRIC's (build_system patched)",
                   lambda: PL.load_generic_rubric(record=True), ("STACK-NORUBRIC",))
        PL.MUTANT_RUBRIC = "norubric_off"
        ck.check("MUTANT norubric_off: the identity check skipped -> the patched system turn is ADMITTED (killed by the"
                 " check above)", PL.load_generic_rubric(record=True)[0].rubric_sha256 == PL.GENERIC_RUBRIC_SHA256)
    finally:
        P.build_system = real
        PL.MUTANT_RUBRIC = None
    return rub


def part_rubric(ck, gen_path, tmp):
    """The INDUCE-RUBRIC-1 path (DISCLOSURE ONLY since 2026-09-25): its DEV-mode refusals kept; record mode refuses."""
    art = JI.induce("mcq", JI.StubInducer(), gen_path, seed=DEV_SEED, out=lambda s: None)
    p = os.path.join(tmp, "rubric.json")
    JI.write_artefact(art, p)
    rub, _o = PL.load_rubric(p, art["artefact_sha256"], art["rubric_sha256"], record=False)
    ck.check("the rubric slot loads by artefact_sha256 AND rubric_sha256", rub.rubric_sha256 == art["rubric_sha256"])
    ck.refused("MUTANT the rubric sha missing", lambda: PL.load_rubric(p, art["artefact_sha256"], None, record=False),
               ("--rubric-sha256 is required",))
    ck.refused("the artefact sha missing", lambda: PL.load_rubric(p, None, art["rubric_sha256"], record=False),
               ("--rubric-artefact-sha256 is required",))
    ck.refused("a wrong rubric sha", lambda: PL.load_rubric(p, art["artefact_sha256"], "0" * 64, record=False),
               ("not the named",))
    ck.refused("a wrong artefact sha", lambda: PL.load_rubric(p, "0" * 64, art["rubric_sha256"], record=False),
               ("pinned",))
    ck.refused("a STUB / DEV artefact in a record run (2026-09-25: the INDUCE-RUBRIC-1 path is disclosure only)",
               lambda: PL.load_rubric(p, art["artefact_sha256"], art["rubric_sha256"], record=True),
               ("DISCLOSURE ONLY",))
    return part_generic_slot(ck)


def part_accounting(ck, tmp):
    d = os.path.join(tmp, "ledger_acc")
    os.mkdir(d)
    q = lambda s: None  # noqa: E731
    n = ACC.guard_day(PL.REGISTRATION, 100, 0, d, day=TODAY, out=q)
    ck.check("the day guard passes a small launch and prints the three numbers", not n["breaches"])
    ck.refused("MUTANT the cap exceeded: 7,990 posted + 24", lambda: ACC.guard_day(PL.REGISTRATION, 24, 7990, d, day=TODAY,
                                                                                  out=q), ("(i)",))
    ACC.append(PL.REGISTRATION, "fixture", 7000, d, day="2026-09-26")
    ck.refused("the ceiling counts the LEDGER when it exceeds the store", lambda: ACC.guard_day(
        PL.REGISTRATION, 1200, 0, d, day=TODAY, out=q), ("(i)",))
    ACC.append("OTHER-TEST", "fixture", 13990, d, day=TODAY)
    ck.refused("the posting-day cap 14,000", lambda: ACC.guard_day(PL.REGISTRATION, 20, 7000, d, day=TODAY, out=q),
               ("(iii)",))
    ck.refused("an unknown test", lambda: ACC.guard_day("NO-SUCH", 1, 0, d, out=q), ("unknown",))


def part_launch_and_analyze(ck, tmp, ev_path, s1path, cfg, plan, loaded, order_ids, rubric, anchor):
    q = lambda s: None  # noqa: E731
    store = os.path.join(tmp, "pilot.db")
    led = os.path.join(tmp, "ledger")
    os.mkdir(led)
    call = fake_call_factory()
    P.configure_rr()
    exp = {"payload_anchor": anchor, "order_sha": plan.digests["order_sha"]}
    ck.refused("a posting day before 2026-09-25", lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, call,
                                                                     "pilot", exp, "blob:x", go=True, today="2026-09-24",
                                                                     out=q), ("before 2026-09-25",))
    ck.refused("the run before the pilot", lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, call, "run",
                                                             exp, "blob:x", go=True, today=TODAY, out=q), ("pilot 12",))
    r0 = PL.launch(plan, loaded, order_ids, rubric, store, led, call, "pilot", exp, "blob:x", go=False, today=TODAY, out=q)
    ck.check("without --go nothing is posted and no store is created", r0["posted"] == 0 and call.n["calls"] == 0 and
             not os.path.exists(store))
    ck.refused("a payload anchor other than the dry-run's", lambda: PL.launch(
        plan, loaded, order_ids, rubric, store, led, call, "pilot", dict(exp, payload_anchor="0" * 64), "blob:x", go=True,
        today=TODAY, out=q), ("differs from the dry-run",))
    r1 = PL.launch(plan, loaded, order_ids, rubric, store, led, call, "pilot", exp, "blob:x", go=True, today=TODAY, out=q)
    a1, v1, e1 = PL.store_counts(store)
    ck.check("the pilot posts exactly the first 12 matches (24 calls), the guard PASSES, the ledger row is appended",
             r1["posted"] == 24 and a1 == 24 and v1 == 24 and r1["guard"]["pass"] and
             ACC.atl.ledger_calls(PL.REGISTRATION, led) == 24, (r1, a1, v1))
    g_bad = PL.pilot_guard(store, order_ids[1:13])
    ck.check("the pilot guard FAILS on a foreign row (another id set)", not g_bad["pass"] and g_bad["foreign_rows"] > 0)
    ck.refused("a second pilot after a PASS", lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, call, "pilot",
                                                                exp, "blob:x", go=True, today=TODAY, out=q),
               ("already PASSED",))
    r_ng = PL.launch(plan, loaded, order_ids, rubric, store, led, call, "run", exp, "blob:x", go=False, today=TODAY, out=q)
    ck.check("a run without --go posts nothing, opens nothing writable and reports the pending count",
             r_ng["posted"] == 0 and r_ng["planned"] == 2 * len(order_ids) - 24 and PL.store_counts(store)[0] == 24 and
             call.n["calls"] == 24, (r_ng["planned"], call.n["calls"]))
    res_p = OC.analyze(cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "outcome.txt"), expect=exp, echo=False)
    ck.check("the analysis of an INCOMPLETE cache writes _PARTIAL with C0 FAIL and no reading",
             not res_p["c0"] and res_p["path"].endswith("_PARTIAL.txt") and os.path.exists(res_p["path"]))
    r2 = PL.launch(plan, loaded, order_ids, rubric, store, led, call, "run", exp, "blob:x", go=True, today=TODAY, out=q)
    a2, v2, _e2 = PL.store_counts(store)
    ck.check("the run posts every remaining slot; attempts == verdicts == 2 x loaded; the ledgers agree",
             a2 == v2 == 2 * len(order_ids) and ACC.atl.ledger_calls(PL.REGISTRATION, led) == a2 and
             r2["posted"] == a2 - 24, (a2, v2, len(order_ids)))
    r3 = PL.launch(plan, loaded, order_ids, rubric, store, led, call, "run", exp, "blob:x", go=True, today=TODAY, out=q)
    ck.check("a relaunch of a complete run posts nothing", r3["posted"] == 0)
    with _mutant(A, "refit_pair"):
        ck.refused("MUTANT refit_pair: C1's nominal on a refit pair", lambda: OC.analyze(
            cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "o_refit.txt"), expect=exp, echo=False),
            ("FROZEN",))
    with _mutant(A, "unseal_early"):
        ck.refused("MUTANT unseal_early: the key read before C1 is written", lambda: OC.analyze(
            cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "o_early.txt"), expect=exp, echo=False),
            ("SEALED",))
    out = os.path.join(tmp, "outcome_full.txt")
    res = OC.analyze(cfg, ev_path, s1path, store, rubric, led, out, expect=exp, echo=False)
    with open(out, encoding="utf-8") as f:
        txt = f.read()
    with open(res["c1_path"], encoding="utf-8") as f:
        c1 = f.read()
    for ln in txt.splitlines():
        ck.out("[FIXTURE-OUTCOME] " + ln)
    ck.check("[2026-09-25] the outcome prints the rubric slot line, and C0 (c) names GENERIC_RUBRIC's sha and main"
             " b653b0a's pins", "  rubric slot: GENERIC_RUBRIC (author's pre-decided fallback 2026-09-25;"
             " INDUCE-RUBRIC-1/-2/-3 NOT ADOPTED)" in txt.splitlines() and
             any(ln.startswith("  (c) PASS") and PL.GENERIC_RUBRIC_SHA256 in ln and "main b653b0a's" in ln
                 for ln in txt.splitlines()))
    ck.check("C0 PASSES on the complete fixture cache; C1 is written first and holds no C3 line",
             res["c0"] and A.C1_MARK in c1 and "C3 BOTH" not in c1 and "C3 BOTH" in txt, res.get("words"))
    ck.check("C1's reading is one of the registered words and the frozen-pair label is on the C1 lines",
             bool(res["words"]) and all(w in ("P EXCLUDED", "M EXCLUDED", "UNRESOLVED AT THIS n") or
                                         w.startswith("UNDETERMINED") for w in res["words"]) and
             all(A.FROZEN_LABEL in ln for ln in txt.splitlines() if ln.startswith("  anchor ") and "nominal k" in ln),
             (res["beta"], res["interval"]))
    ck.check("per-replicate records written (c1_boot %d replicates) with a manifest" % cfg.B_outer,
             any(n == "c1_boot" and k == cfg.B_outer for n, _p, k, _s in res["records"]) and
             os.path.exists(out + ".records.manifest.txt"))
    ck.refused("the outcome is write-once", lambda: OC.analyze(cfg, ev_path, s1path, store, rubric, led, out, expect=exp,
                                                               echo=False), ("write-once",))
    ck.check("K4 the witness line: key-material loads before C1 = 0; C1's file holds no leak-scan line of part 2",
             "key-material loads in this analysis before C1: 0" in c1 and "(d) part 2" not in c1 and "(d) part 2 PASS" in txt)
    ck.check("K5 P2b is scored on the MATCHED level; C1b prints the key-blind level first with 'no bar'",
             res["level_scored"] == res["matched_hi"] and txt.index("C1b KEY-BLIND") < txt.index("C1b KEY-INFORMED") and
             "definition differs from L12; no bar" in txt)
    ck.check("K1 C0 (f) reads the journal: ledger == journal invocations", "(f) PASS: journal invocations" in txt)
    with _mutant(OC, "load_early"):
        ck.refused("MUTANT load_early: the loader's key material read before C1", lambda: OC.analyze(
            cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "o_load.txt"), expect=exp, echo=False),
            ("K4",))
    part_l7_outcome(ck, tmp, ev_path, s1path, cfg, rubric, exp, store, led, out, res, txt, c1, res_p["path"])
    return res


def _fresh_launch_env(tmp, name):
    store = os.path.join(tmp, name + ".db")
    led = os.path.join(tmp, name + "_ledger")
    os.mkdir(led)
    return store, led


def part_k1_journal(ck, tmp, plan, loaded, order_ids, rubric, exp):
    """K1: the write-ahead journal, in process (the reviewer's probes run as subprocesses beside this selftest)."""
    q = lambda s: None  # noqa: E731
    # (1) Ctrl-C after the 5th post returned: ledger == journal == posts
    store, led = _fresh_launch_env(tmp, "k1_kbint")
    base = fake_call_factory()
    posts = {"n": 0}

    def kb(system, user):
        posts["n"] += 1
        r = base(system, user)
        if posts["n"] == 5:
            raise KeyboardInterrupt("selftest: Ctrl-C after the post returned")
        return r
    try:
        PL.launch(plan, loaded, order_ids, rubric, store, led, kb, "pilot", exp, "blob:x", go=True, today=TODAY, out=q)
        ck.check("K1 the KeyboardInterrupt propagated", False)
    except KeyboardInterrupt:
        pass
    js = ACC.read_journal(PL.journal_path(store))
    ck.check("K1 after Ctrl-C at post 5: ledger == journal == posts == 5 (the finally ledgers every post)",
             ACC.atl.ledger_calls(PL.REGISTRATION, led) == js["invocations"] == posts["n"] == 5,
             (ACC.atl.ledger_calls(PL.REGISTRATION, led), js, posts["n"]))
    r = PL.launch(plan, loaded, order_ids, rubric, store, led, kb, "pilot", exp, "blob:x", go=True, today=TODAY, out=q)
    js = ACC.read_journal(PL.journal_path(store))
    ck.check("K1 the relaunched pilot PASSES and ledger == journal == posts (the interrupted slot re-posted)",
             r["guard"]["pass"] and ACC.atl.ledger_calls(PL.REGISTRATION, led) == js["invocations"] == posts["n"],
             (js["invocations"], posts["n"]))
    # (2) a hard kill simulated: a PENDING invocation committed, then nothing (no reply, no ledger row)
    j = ACC.Journal.open(PL.journal_path(store))
    j.pending("killed launch", order_ids[20], 1, "0" * 64, TODAY)
    j.close()
    ck.refused("K1 a launch while the ledger is behind the journal is never silent (the no-go path reports; the go path"
               " reconciles)", lambda: ACC.check_equal(PL.REGISTRATION, ACC.read_journal(PL.journal_path(store))
                                                       ["invocations"], led, "probe"), ("must be EQUAL",))
    r = PL.launch(plan, loaded, order_ids, rubric, store, led, base, "run", exp, "blob:x", go=True, today=TODAY, out=q)
    js = ACC.read_journal(PL.journal_path(store))
    ck.check("K1 the relaunch after a kill: the orphan resolved and disclosed, the ledger reconciled, ledger == journal",
             js["by_outcome"].get("ORPHAN") == 1 and not js["unresolved"] and
             ACC.atl.ledger_calls(PL.REGISTRATION, led) == js["invocations"], js)
    ck.check("K1 the journal counts every post: invocations == the fake's posts + the 1 orphan (which never posted)",
             js["invocations"] == base.n["calls"] + 1, (js["invocations"], base.n["calls"]))
    # (3) the cap trigger acts BEFORE the post
    jp = os.path.join(tmp, "cap_journal.db")
    jc = ACC.Journal.open(jp, cap=3, create=True)
    fake = fake_call_factory()
    # [ARCHV2-SELFTEST-CLOCK-FIX 2026-09-26] the fixture clock: without clock= wrap_call reads accounting.local_day()
    # and raises DAY ROLLOVER on any date but TODAY (148 of 282 checks executed on 2026-09-26)
    call = ACC.wrap_call(fake, jc, {"s": [("m", 1)]}, {"n": 0}, "cap", TODAY, lambda s, u: "s", clock=lambda: TODAY)
    for _ in range(3):
        call("x", "y")
    ck.refused("K1 the 4th invocation beyond a cap of 3 is refused BEFORE the post",
               lambda: call("x", "y"), ("BEFORE any post",))
    ck.check("K1 ... and no 4th post happened", fake.n["calls"] == 3)
    jc.close()
    ck.refused("K1 a journal cap above the author's hard 8,000", lambda: ACC.Journal.open(os.path.join(tmp, "j9.db"),
                                                                                          cap=8001, create=True), ("8000",))
    # (4) a ledger AHEAD of the journal refuses
    d = os.path.join(tmp, "ahead")
    os.mkdir(d)
    ja = ACC.Journal.open(os.path.join(tmp, "ahead_journal.db"), create=True)
    ACC.append(PL.REGISTRATION, "stray", 3, d, day=TODAY)
    ck.refused("K1 a ledger ahead of the journal is never reconciled downward", lambda: ACC.reconcile(
        PL.REGISTRATION, ja, d, q), ("AHEAD",))
    ja.close()
    # (5) MUTANT journal_after_post: the Ctrl-C probe leaves the ledger ahead of the journal -> the next launch refuses
    store2, led2 = _fresh_launch_env(tmp, "k1_mut")
    posts2 = {"n": 0}

    def kb2(system, user):
        posts2["n"] += 1
        r = base(system, user)
        if posts2["n"] == 3:
            raise KeyboardInterrupt("selftest")
        return r
    with _mutant(ACC, "journal_after_post"):
        try:
            PL.launch(plan, loaded, order_ids, rubric, store2, led2, kb2, "pilot", exp, "blob:x", go=True, today=TODAY,
                      out=q)
        except KeyboardInterrupt:
            pass
    ck.refused("MUTANT journal_after_post (the row written after the post): the next launch REFUSES (ledger 3 > journal 2)",
               lambda: PL.launch(plan, loaded, order_ids, rubric, store2, led2, base, "pilot", exp, "blob:x", go=True,
                                 today=TODAY, out=q), ("AHEAD",))
    part_rollover(ck, tmp, plan, loaded, order_ids, rubric, exp)
    part_transport(ck, tmp, plan, loaded, order_ids, rubric, exp)


FIXTURE_ENDPOINT = "https://fixture.invalid/models/chat/completions?api-version=2024-05-01-preview"
FIXTURE_KEY = "fixture-key-NEVER-PRINTED-7f3a"


def _set_transport(endpoint, key):
    PL.rr.AZURE_ENDPOINT, PL.rr.AZURE_KEY = endpoint, key


def part_transport(ck, tmp, plan, loaded, order_ids, rubric, exp):
    """[2026-09-25 incident] the transport: load_env from the data root, the preflight, MUTANT load_env_skipped."""
    rr = PL.rr
    saved = (rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.JUDGE_MODEL, rr.ROOT, rr.TOKEN)
    lines = []
    try:
        droot = os.path.join(tmp, "data_root")
        os.mkdir(droot)
        with open(os.path.join(droot, ".env"), "x", encoding="utf-8") as f:
            f.write("AZURE_AI_ENDPOINT=https://grok-fixture.services.example.com/\nAZURE_GROK_API_KEY=%s\n" % FIXTURE_KEY)
        _set_transport(None, None)
        root_before = rr.ROOT
        envp = PL.load_transport(droot, out=lines.append)
        ck.check("TRANSPORT load_transport reads <data root>/.env through rr.load_env: endpoint and key set, rr.ROOT restored",
                 envp == os.path.join(droot, ".env") and rr.AZURE_ENDPOINT ==
                 "https://grok-fixture.services.example.com/models/chat/completions?api-version=2024-05-01-preview" and
                 rr.AZURE_KEY == FIXTURE_KEY and rr.ROOT == root_before, (envp, rr.ROOT))
        ln = PL.transport_preflight(out=lines.append)
        ck.check("TRANSPORT PREFLIGHT OK prints the host and the deployment only (no key, no path of the URL)",
                 ln == "TRANSPORT PREFLIGHT: OK (endpoint host=grok-fixture.services.example.com, deployment=%s)"
                 % rr.JUDGE_MODEL and all(FIXTURE_KEY not in x and "api-version" not in x for x in lines), lines)
        ck.refused("TRANSPORT no .env at the data root", lambda: PL.load_transport(os.path.join(tmp, "nowhere"),
                                                                                    out=lines.append), ("no .env",))
        for name, ep, key, dep, must in (
                ("the endpoint None (load_env never called: the incident)", None, FIXTURE_KEY, None, "endpoint (AZURE_ENDPOINT) is None"),
                ("the endpoint empty", "  ", FIXTURE_KEY, None, "endpoint (AZURE_ENDPOINT) is empty"),
                ("the key None", FIXTURE_ENDPOINT, None, None, "key (AZURE_KEY) is None"),
                ("the key empty", FIXTURE_ENDPOINT, "", None, "key (AZURE_KEY) is empty"),
                ("the deployment empty", FIXTURE_ENDPOINT, FIXTURE_KEY, "", "deployment (JUDGE_MODEL) is empty"),
                ("an http endpoint", "http://fixture.invalid/x", FIXTURE_KEY, None, "https URL"),
                ("an endpoint with no host", "https:///models", FIXTURE_KEY, None, "https URL"),
                ("the literal 'None' URL", "None", FIXTURE_KEY, None, "https URL")):
            _set_transport(ep, key)
            dep0 = rr.JUDGE_MODEL
            if dep is not None:
                rr.JUDGE_MODEL = dep
            try:
                ck.refused("TRANSPORT PREFLIGHT: %s" % name, lambda: PL.transport_preflight(out=lines.append),
                           ("TRANSPORT PREFLIGHT: REFUSED", must))
            finally:
                rr.JUDGE_MODEL = dep0
        ck.check("TRANSPORT the key is never printed (every line above)", all(FIXTURE_KEY not in x for x in lines))
        # MUTANT load_env_skipped: the CLI's sequence (load_transport, then the launch's preflight) with fresh globals
        _set_transport(None, None)
        store, led = _fresh_launch_env(tmp, "transport_mut")
        fk = fake_call_factory()
        with _MutT():
            PL.load_transport(droot, out=lines.append)
            ck.refused("MUTANT load_env_skipped: the launch (--go) is refused by the TRANSPORT PREFLIGHT",
                       lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "pilot", exp, "blob:x", go=True,
                                         today=TODAY, out=q_), ("TRANSPORT PREFLIGHT: REFUSED", "is None"))
            ck.refused("MUTANT load_env_skipped: the no-go launch (the dry-run's launch path) is refused too",
                       lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "pilot", exp, "blob:x",
                                         go=False, today=TODAY, out=q_), ("TRANSPORT PREFLIGHT: REFUSED",))
        ck.check("MUTANT load_env_skipped: 0 posts, and NOTHING written: no journal, no store, no launch manifest, no"
                 " ledger file", fk.n["calls"] == 0 and not os.path.exists(PL.journal_path(store)) and
                 not os.path.exists(store) and not os.path.exists(store + ".launch.json") and os.listdir(led) == [],
                 os.listdir(led))
        _set_transport(FIXTURE_ENDPOINT, FIXTURE_KEY)
        # the retired store
        ck.refused("STORE the retired pilot_k46_verdicts.db in a record run", lambda: PL.check_store_path(
            PL.Config(), os.path.join(tmp, "pilot_k46_verdicts.db")), ("RETIRED", "pilot_k46_incident_2026-09-25",
                                                                       "pilot_k46_verdicts_run2.db"))
        ck.check("STORE the run2 store is admitted in a record run; a DEV run admits any name",
                 PL.check_store_path(PL.Config(), "x/pilot_k46_verdicts_run2.db") and
                 PL.check_store_path(fixture_cfg(), "x/pilot_k46_verdicts.db"))
        ck.check("STORE the CLI's default store is run2", __import__("archv2_pilot_k46").DEFAULT_STORE.replace(
            "\\", "/").endswith("experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db"))
        ck.check("PRIOR the record's prior journal is the incident's (sha256 995087c3...)", PL.PRIOR_JOURNALS == (
            (os.path.join("experiment_results", "archv2", "pilot_k46", "pilot_k46_verdicts.db.invocations.db"),
             "995087c316036df717471c909f94bc19c088485676b4610ff1a085e2eea80375"),))
        # prior journals: a retired store's 3 booked invocations on TODAY, ledgered
        store_o, led_p = _fresh_launch_env(tmp, "prior")
        jo = ACC.Journal.open(PL.journal_path(store_o), create=True)
        for i in range(3):
            s_ = jo.pending("retired launch", order_ids[i], 1, "0" * 64, TODAY)
            jo.resolve(s_, "RAISED", "ValueError: unknown url type: 'None'")
        jo.close()
        ACC.append(PL.REGISTRATION, "retired launch", 3, led_p, day=TODAY)
        prior = [(PL.journal_path(store_o), C.dv2ro.file_sha256(PL.journal_path(store_o)))]
        store_n = os.path.join(os.path.dirname(store_o), "new_store.db")
        ck.refused("PRIOR without the prior journal: the new store's launch refuses (ledger AHEAD of the journal)",
                   lambda: PL.launch(plan, loaded, order_ids, rubric, store_n, led_p, fake_call_factory(), "pilot", exp,
                                     "blob:x", go=True, today=TODAY, out=q_), ("AHEAD",))
        ck.refused("PRIOR a prior journal with a wrong sha256", lambda: PL.launch(
            plan, loaded, order_ids, rubric, os.path.join(os.path.dirname(store_o), "new_store_b.db"), led_p,
            fake_call_factory(), "pilot", exp, "blob:x", go=True, today=TODAY, out=q_,
            prior_journals=[(prior[0][0], "0" * 64)]), ("not the pinned",))
        store_c = os.path.join(os.path.dirname(store_o), "new_store_c.db")
        fk2 = fake_call_factory()
        r = PL.launch(plan, loaded, order_ids, rubric, store_c, led_p, fk2, "pilot", exp, "blob:x", go=True, today=TODAY,
                      out=q_, prior_journals=prior)
        js = ACC.read_journal(PL.journal_path(store_c))
        rows = ACC.test_day_rows(PL.REGISTRATION, led_p)
        ck.check("PRIOR with the prior journal: the new store's pilot PASSES; ledger %d == new journal %d + prior 3; no"
                 " catch-up row" % (rows.get(TODAY, 0), js["invocations"]),
                 r["guard"]["pass"] and rows == {TODAY: js["invocations"] + 3} and js["invocations"] == fk2.n["calls"] and
                 not any("reconciled after crash" in str(x.get("launch", "")) for f in ACC.atl.ledger_files(led_p)
                         for x in ACC.atl._rows(f)), (rows, js))
    finally:
        rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.JUDGE_MODEL, rr.ROOT, rr.TOKEN = saved
        PL.MUTANT_TRANSPORT = None


def q_(s):
    return None


class _MutT:
    def __enter__(self):
        PL.MUTANT_TRANSPORT = "load_env_skipped"

    def __exit__(self, *a):
        PL.MUTANT_TRANSPORT = None


NEXT_DAY = "2026-09-26"


def _rollover_clock(n_before):
    """SELFTEST clock: TODAY for the first n_before reads, NEXT_DAY after (local midnight crossed mid-launch)."""
    t = {"n": 0}

    def clock():
        t["n"] += 1
        return TODAY if t["n"] <= n_before else NEXT_DAY
    return clock


def part_rollover(ck, tmp, plan, loaded, order_ids, rubric, exp):
    """[2026-09-25] a launch crossing local midnight: a clean stop before the first post of the new day; journal and ledger
    agree per day; the relaunch on the new day reconciles with no catch-up row and resumes. MUTANT rollover_off."""
    q = lambda s: None  # noqa: E731
    store, led = _fresh_launch_env(tmp, "rollover")
    fk = fake_call_factory()
    ck.refused("ROLLOVER: the local date rolls over after the 7th post -> the launch stops cleanly BEFORE the 8th post",
               lambda: PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "pilot", exp, "blob:x", go=True,
                                 today=TODAY, out=q, clock=_rollover_clock(7)), ("DAY ROLLOVER", TODAY, NEXT_DAY))
    js = ACC.read_journal(PL.journal_path(store))
    rows = ACC.test_day_rows(PL.REGISTRATION, led)
    ck.check("ROLLOVER: 7 posted; the journal holds 7 invocations, all on %s, none unresolved; the ledger holds 7 on %s and"
             " none on %s; no pilot guard file" % (TODAY, TODAY, NEXT_DAY),
             fk.n["calls"] == 7 and js["invocations"] == 7 and js["per_day"] == {TODAY: 7} and not js["unresolved"] and
             rows == {TODAY: 7} and not os.path.exists(store + ".pilot_guard.json"), (fk.n["calls"], js, rows))
    r = PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "pilot", exp, "blob:x", go=True, today=NEXT_DAY, out=q)
    js2 = ACC.read_journal(PL.journal_path(store))
    rows2 = ACC.test_day_rows(PL.REGISTRATION, led)
    n2 = 2 * len(order_ids[:PL.Config().pilot_n]) - 7
    ck.check("ROLLOVER: the relaunch on %s is admitted (no double count, no catch-up row), resumes the %d pending pilot"
             " slots and PASSES; ledger per day == journal per day ({%s: 7, %s: %d})" % (NEXT_DAY, n2, TODAY, NEXT_DAY, n2),
             r["guard"]["pass"] and r["posted"] == n2 and js2["per_day"] == {TODAY: 7, NEXT_DAY: n2} == rows2 and
             not any("reconciled after crash" in str(x.get("launch", "")) for f in ACC.atl.ledger_files(led)
                     for x in ACC.atl._rows(f)), (r.get("posted"), js2["per_day"], rows2))
    store_m, led_m = _fresh_launch_env(tmp, "rollover_mut")
    fk_m = fake_call_factory()
    with _mutant(ACC, "rollover_off"):
        r_m = PL.launch(plan, loaded, order_ids, rubric, store_m, led_m, fk_m, "pilot", exp, "blob:x", go=True,
                        today=TODAY, out=q, clock=_rollover_clock(7))
    js_m = ACC.read_journal(PL.journal_path(store_m))
    ck.check("MUTANT rollover_off: the launch posts past midnight (all %d, %d of them after the rollover, booked to %s) ->"
             " killed by the ROLLOVER refusal above" % (2 * PL.Config().pilot_n, 2 * PL.Config().pilot_n - 7, TODAY),
             r_m["posted"] == fk_m.n["calls"] == 2 * PL.Config().pilot_n and js_m["per_day"] == {TODAY: fk_m.n["calls"]},
             (r_m.get("posted"), js_m["per_day"]))


def part_k3_guard(ck, tmp, plan, loaded, order_ids, rubric, exp):
    q = lambda s: None  # noqa: E731
    for mut in (None, "guard_errored_fails"):
        store, led = _fresh_launch_env(tmp, "k3_%s" % (mut or "ok"))
        base = fake_call_factory()
        k = {"n": 0}

        def flaky(system, user):
            k["n"] += 1
            if k["n"] == 3:
                raise RuntimeError("selftest: HTTP 429 retries exhausted")
            return base(system, user)
        with _mutant(PL, mut) if mut else _mutant(PL, None):
            try:
                PL.launch(plan, loaded, order_ids, rubric, store, led, flaky, "pilot", exp, "blob:x", go=True, today=TODAY,
                          out=q)
                first = "returned"
            except SystemExit as e:
                first = str(e)
            ok2 = True
            try:
                r = PL.launch(plan, loaded, order_ids, rubric, store, led, flaky, "pilot", exp, "blob:x", go=True,
                              today=TODAY, out=q)
                g = r["guard"]
            except SystemExit:
                ok2, g = False, None
        files = sorted(f for f in os.listdir(tmp) if f.startswith(os.path.basename(store) + ".pilot_guard_FAILED."))
        if mut is None:
            ck.check("K3 one transport error in the pilot 12: launch 1 FAILS the guard, FAILED file .1 written",
                     "guard FAILED" in first and files == [os.path.basename(store) + ".pilot_guard_FAILED.1.json"],
                     (first[:120], files))
            ck.check("K3 the relaunch fills the slot and the guard PASSES (errored 1 counted and printed)",
                     ok2 and g["pass"] and g["errored_attempts"] == 1, g)
            ck.check("K3 the FAILED file name is a counter", PL.failed_guard_path(store).endswith("_FAILED.2.json"))
        else:
            ck.check("MUTANT guard_errored_fails (errored must be 0): the relaunch can never PASS -> killed", not ok2)


def part_k2_pins(ck):
    # re-pin 2026-09-25: the record pins are MAIN b653b0a's judge_v2 (06a17be's with induction.py 147e6874)
    ok, bad = PL.judge_pins_ok(PL.Config())
    ck.check("K2 on this checkout (= main's judge_v2 at b653b0a) the record pin mode PASSES", ok, bad)
    mains_real = {k: PL.main_blob(k) for k in PL.expected_pins(PL.Config())}
    ok2, bad2 = PL.judge_pins_ok(PL.Config(), main_blob_fn=lambda r: (
        PL.INDUCE_INDUCTION_BLOB_06A17BE if r == "judge_v2/induction.py" else mains_real[r]))
    ck.check("K2 the guard: main's actual induction.py must equal the pin (main = 06a17be's f4d65f59 -> REFUSED, and"
             " only that key)", not ok2 and set(bad2) == {"main:judge_v2/induction.py"}, bad2)
    ok2b, bad2b = PL.judge_pins_ok(PL.Config(), main_blob_fn=lambda r: (
        PL.JUDGE_V2_F5BBBDA[r] if r == "judge_v2/_base.py" else mains_real[r]))
    ck.check("K2 generalised: main's actual _base.py must equal the pin too (main = f5bbbda's f88fefa7 -> REFUSED)",
             not ok2b and set(bad2b) == {"main:judge_v2/_base.py"}, bad2b)
    ok2c, bad2c = PL.judge_pins_ok(PL.Config(), main_blob_fn=lambda r: None)
    ck.check("K2 main unreadable (git fails) -> REFUSED on all seven", not ok2c and
             set(bad2c) == {"main:" + k for k in PL.expected_pins(PL.Config())}, bad2c)
    live = PL.W._pins()      # [JV2-PARALLEL-POSTING] the live table (pin_table() + pool.py)
    old_base = dict(live, **{"judge_v2/_base.py": PL.JUDGE_V2_F5BBBDA["judge_v2/_base.py"]})
    ok3, bad3 = PL.judge_pins_ok(PL.Config(), table_fn=lambda: old_base)
    ck.check("K2 MUTANT a live _base.py at f5bbbda's blob -> REFUSED", not ok3 and set(bad3) == {"judge_v2/_base.py"}, bad3)
    old_ind = dict(live, **{"judge_v2/induction.py": PL.INDUCE_INDUCTION_BLOB_06A17BE})
    ok4, bad4 = PL.judge_pins_ok(PL.Config(), table_fn=lambda: old_ind)
    ck.check("K2 MUTANT a live induction.py at 06a17be's f4d65f59 (the INDUCE-RUBRIC-1 D1 blob) -> REFUSED",
             not ok4 and set(bad4) == {"judge_v2/induction.py"}, bad4)
    old_ind2 = dict(live, **{"judge_v2/induction.py": PL.INDUCE_INDUCTION_BLOB_23E56E7})
    ok5, bad5 = PL.judge_pins_ok(PL.Config(), table_fn=lambda: old_ind2)
    ck.check("K2 MUTANT a live induction.py at 23e56e7's 0de6153f -> REFUSED", not ok5 and "judge_v2/induction.py" in bad5,
             bad5)
    # [JV2-PARALLEL-POSTING re-pin] the record table is b653b0a's with writer.py moved and pool.py added (8 pins)
    ck.check("K2 the record pins differ from f5bbbda's in exactly _base.py, induction.py and writer.py (+ pool.py new)",
             {k for k, v in PL.expected_pins(PL.Config()).items() if PL.JUDGE_V2_F5BBBDA.get(k) != v} ==
             {"judge_v2/_base.py", "judge_v2/induction.py", "judge_v2/writer.py", "judge_v2/pool.py"})
    ck.check("K2 the record pins differ from main b653b0a's in exactly writer.py (6db4ab32 -> %s) and pool.py (new, %s)"
             % (PL.WRITER_BLOB_JV2PP[5:13], PL.POOL_BLOB_JV2PP[5:13]),
             {k for k, v in PL.expected_pins(PL.Config()).items() if PL.JUDGE_V2_MAIN_B653B0A.get(k) != v} ==
             {"judge_v2/writer.py", "judge_v2/pool.py"} and PL.expected_pins(PL.Config())["judge_v2/induction.py"] ==
             "blob:147e6874926b65393037cdcacd0e29aa308651ef" and
             PL.JUDGE_V2_MAIN_B653B0A["judge_v2/writer.py"] == "blob:6db4ab3207a24aa61a1d4ea43ca6f2da2c68e547")
    ck.check("K2 the live writer.py and pool.py are the re-pinned blobs (judge_v2.writer._pins())",
             PL.W._pins()["judge_v2/writer.py"] == PL.WRITER_BLOB_JV2PP and
             PL.W._pins()["judge_v2/pool.py"] == PL.POOL_BLOB_JV2PP)
    ck.check("K2 every record pin is MAIN's actual blob (git rev-parse main:tools/analysis/<f>)",
             mains_real == PL.expected_pins(PL.Config()), {k: v for k, v in mains_real.items()
                                                            if v != PL.expected_pins(PL.Config())[k]})
    ck.check("K2 the fixture runs under the record pin mode", fixture_cfg().judge_pins == "JV2-PARALLEL-POSTING" ==
             PL.Config().judge_pins)
    ck.refused("K2 the retired pin mode MAIN-B653B0A (the K46 run's)", lambda: PL.expected_pins(
        fixture_cfg(judge_pins="MAIN-B653B0A")), ("pin mode",))
    ck.refused("K2 an unknown pin mode", lambda: PL.expected_pins(fixture_cfg(judge_pins="whatever")), ("pin mode",))
    ck.refused("K2 the retired DEV pin mode f5bbbda", lambda: PL.expected_pins(fixture_cfg(judge_pins="f5bbbda")),
               ("pin mode",))
    ck.refused("K2 the retired pin mode INDUCE-RUBRIC-1 (06a17be's table)", lambda: PL.expected_pins(
        fixture_cfg(judge_pins="INDUCE-RUBRIC-1")), ("pin mode",))


def part_k9_k10(ck, tmp, ev_path, s1path, gen_path):
    q = lambda s: None  # noqa: E731
    ck.refused("K9 a record launch with a ledger directory other than the main checkout's",
               lambda: PL.check_ledger_dir(tmp, PL.Config(), q), ("MAIN checkout",))
    ck.check("K9 a DEV run prints and admits a temporary ledger directory", bool(PL.check_ledger_dir(tmp, fixture_cfg(), q)))
    ck.check("K9 the main checkout is located", PL.main_ledger_dir() is not None, PL.main_ledger_dir())
    # READY a254a1d LOW-4 / MEDIUM-1 (re-pin 2026-09-24): the stage-1 pins are FILLED; the record-mode refusals and the
    # LF normalisation are exercised (the committed record is a JSON file, not a DB; read-only)
    ck.refused("a record run on a stage-1 file other than the record (sha256-lf mismatch)", lambda: PL.check_stage1_file(
        s1path, PL.Config()), ("is sha256-lf", "not the record's"))
    rec_path = os.path.join(C.ROOT, PL.STAGE1_RECORD_REL)
    with open(rec_path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    ck.check("the committed stage-1 record passes in record mode, whatever its checkout EOL (this one: %s)"
             % ("CRLF" if b"\r\n" in raw else "LF"), PL.check_stage1_file(rec_path, PL.Config()) == PL.STAGE1_RECORD_SHA256)
    p_lf, p_crlf, p_bad = (os.path.join(tmp, n) for n in ("s1_rec_lf.json", "s1_rec_crlf.json", "s1_rec_bad.json"))
    for p, data in ((p_lf, lf), (p_crlf, lf.replace(b"\n", b"\r\n")), (p_bad, lf.replace(b'"math"', b'"math" '))):
        with open(p, "xb") as f:
            f.write(data)
    ck.check("MEDIUM-1: the LF and the CRLF renderings of the record both pass (sha256-lf and blob)",
             PL.check_stage1_file(p_lf, PL.Config()) == PL.check_stage1_file(p_crlf, PL.Config()) ==
             PL.STAGE1_RECORD_SHA256)
    ck.check("MEDIUM-1 witness: the CRLF rendering's RAW sha256 is not the pin (a raw-bytes check would have refused)",
             C.dv2ro.file_sha256(p_crlf) != PL.STAGE1_RECORD_SHA256 and C.dv2ro.file_sha256(p_lf) == PL.STAGE1_RECORD_SHA256)
    ck.refused("MUTANT a byte-changed stage-1 record", lambda: PL.check_stage1_file(p_bad, PL.Config()),
               ("is sha256-lf", "not the record's"))
    ck.check("the record reproduces (stage1.verify, record mode) and carries the 7 anchors of record",
             tuple(S1.verify(p_crlf, record=True)) == PL.STAGE1_ANCHORS_OF_RECORD ==
             ("chemistry", "computer science", "economics", "health", "math", "other", "philosophy"))
    saved = PL.STAGE1_RECORD_SHA256
    try:
        PL.STAGE1_RECORD_SHA256 = None
        ck.refused("MUTANT the stage-1 pin unset: a record run refuses", lambda: PL.check_stage1_file(
            p_lf, PL.Config()), ("not pinned yet",))
    finally:
        PL.STAGE1_RECORD_SHA256 = saved
    saved_b = PL.STAGE1_RECORD_BLOB
    try:
        PL.STAGE1_RECORD_BLOB = "blob:" + "0" * 40
        ck.refused("MUTANT a wrong blob pin beside a matching sha256-lf", lambda: PL.check_stage1_file(
            p_lf, PL.Config()), ("not the record's blob:",))
    finally:
        PL.STAGE1_RECORD_BLOB = saved_b
    ck.check("a DEV run admits a non-record stage-1 file (sha256-lf returned, no refusal)",
             PL.check_stage1_file(s1path, fixture_cfg()) == PL.file_sha256_lf(s1path))
    ck.check("the pilot's stage-1 default points at the RE-DRAW's output path",
             PL.default_stage1_record().replace("\\", "/").endswith(
                 "experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json"))
    ck.refused("K10 (f) the registry total", lambda: PL.make_plan(fixture_cfg(registry_total=47), ev_path, s1path, q),
               ("registry carries",))
    art = JI.induce("mcq", JI.StubInducer(), gen_path, seed=DEV_SEED, out=q)
    art["of_record"] = "REGISTERED ARCH-V2-INDUCE-RUBRIC-1 (attempt 1 of record)"
    body = {k: v for k, v in art.items() if k != "artefact_sha256"}
    art["artefact_sha256"] = C.sha256_text(json.dumps(body, sort_keys=True, ensure_ascii=True))
    p = os.path.join(tmp, "rubric_reg.json")
    JI.write_artefact(art, p)
    # [2026-09-25] K10 (c) (the INDUCE-1 positive label and population) is superseded: the whole INDUCE-RUBRIC-1 path is
    # DISCLOSURE ONLY, so even a REGISTERED-labelled artefact is refused in record mode before K10 (c) is reached
    ck.refused("K10 (c) superseded: a REGISTERED ARCH-V2-INDUCE-RUBRIC-1 artefact in a record run (disclosure only)",
               lambda: PL.load_rubric(p, art["artefact_sha256"], art["rubric_sha256"], record=True),
               ("DISCLOSURE ONLY",))
    ck.check("K10 (b) the persona sha is the pinned GENERIC_SYSTEM text sha",
             PL.persona_sha() == "3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9")
    ck.check("K10 (g) b1's sign printed beside IDENTIFIED", "sign -" in A.ident_word(5.0, None, -1.2) and
             "sign +" in A.ident_word(5.0, None, 2.0))


def part_rulings_units(ck, plan):
    """K5 / K6 / K7 / K8 units and their mutants."""
    cfg = PL.Config()
    m37 = PL.exact_M(37, 12)            # [0761cfa] every comparison against the exact M
    # K7
    w, _ = A.c1_readings(1.9, 1.5, 2.0, cfg.bar_P, m37, n_inf=1)
    ck.check("K7 one non-finite replicate -> UNDETERMINED (1 non-finite replicates), no exclusion read",
             w == ["UNDETERMINED (1 non-finite replicates)"], w)
    with _mutant(A, "drop_nonfinite"):
        w2, _ = A.c1_readings(1.9, 1.5, 2.0, cfg.bar_P, m37, n_inf=1)
    ck.check("MUTANT drop_nonfinite reads 'M EXCLUDED' on the same data -> killed by the check above", "M EXCLUDED" in w2)
    # [0761cfa] the K7 2.05 / 2.0484 edge test is REPLACED: the M bar is exact (2.0529 at k 37); the edge branch is retired
    w3, l3 = A.c1_readings(1.9, 1.5, 2.0529, cfg.bar_P, m37, n_inf=0)
    ck.check("K7 at the exact bar: an upper end 2.0529 (< 2.052941) reads 'M EXCLUDED'; no edge message; 'M bar 2.0529"
             " (exact, registered)'", "M EXCLUDED" in w3 and len(l3) == 1 and "M bar 2.0529 (exact, registered)" in l3[0]
             and report.HITS.get("C1.M_EDGE", 0) == 0, l3)
    # K6
    u, wv, sed = A.level_intervals(1.0, 0.1, cfg.level_cv)
    ck.check("K6 the widened interval uses sqrt(SE_boot^2 + (0.133 x level)^2 / 2)",
             abs(sed - math.sqrt(0.01 + 0.133 ** 2 / 2)) < 1e-12 and (wv[1] - wv[0]) > (u[1] - u[0]))
    with _mutant(A, "unwidened_only"):
        u2, w2v, _ = A.level_intervals(1.0, 0.1, cfg.level_cv)
    ck.check("MUTANT unwidened_only gives equal intervals -> killed by the check above", (w2v[1] - w2v[0]) == (u2[1] - u2[0]))
    # K5
    P_bar, M_bar, _ph, _pl = A.bars(cfg, 37)
    lines, lvl = A.c1b_lines(cfg, 37, 3.0, 0.1, 0.2, 0.02, 1.9, 1.8, 1.5, 2.1, {12: (0.1, 0.12, 66, 60, 2)})
    ck.check("K5 only the MATCHED level is compared with the L12 bars; the key-blind line says 'no bar'",
             lvl == 0.2 and any("definition differs from L12; no bar" in x for x in lines) and
             any("MATCHED level lies BELOW" in x for x in lines) and any("= 0.3556; M = L12 x 666/66 = 1.0878" in x
                                                                          for x in lines) and
             not any("memo" in x for x in lines), lines)
    with _mutant(A, "bars_on_keyblind"):
        _l2, lvl2 = A.c1b_lines(cfg, 37, 3.0, 0.1, 0.2, 0.02, 1.9, 1.8, 1.5, 2.1, {})
    ck.check("MUTANT bars_on_keyblind compares the key-blind level -> killed", lvl2 == 3.0)
    ck.check("K5 the projections: matched and mixed printed with their difference",
             any("beta_matched" in x for x in lines) and any("MIXED projection" in x for x in lines))
    # K8
    thin = PL.mask_thin_lines({"a": {"mask": {"exhausted_masked": 40, "exhausted_unmasked": 10}, "pairs": 666},
                               "b": {"mask": {"exhausted_masked": 40, "exhausted_unmasked": 30}, "pairs": 666}})
    ck.check("K8 > 2% of an anchor's pairs exhausted BY THE MASK prints the thinning line (a: 30), <= 2% does not (b: 10)",
             "thins the target design" in thin[0] and "anchor a" in thin[0] and "does not thin" in thin[1], thin)
    lost = sum(s["mask"]["lost_cells"] for s in plan.stats.values())
    ck.check("K8 the fixture's mask loses (pair, question) cells (a model answered another variant)", lost > 0,
             {a: s["mask"] for a, s in plan.stats.items()})
    Parr = np.array([["opt:a", "opt:b"], ["opt:a", "opt:a"]], dtype=str)
    Varr = np.array([["v", "w"], ["v", "v"]], dtype=str)
    mk = PL.mask_stats(Parr, Varr, ["m1", "m2"], 2)
    ck.check("K8 the unit: 1 cell lost, the pair exhausted with the mask and not without it",
             mk["lost_cells"] == 1 and mk["exhausted_masked"] == 1 and mk["exhausted_unmasked"] == 1 - 0 and
             mk["lost_by_model"] == {"m1": 1, "m2": 1}, mk)
    with _mutant(PL, "mask_off_count"):
        mk2 = PL.mask_stats(Parr, Varr, ["m1", "m2"], 2)
    ck.check("MUTANT mask_off_count reports 0 lost cells -> killed by the unit", mk2["lost_cells"] == 0)


def part_forced_zero(ck, tmp, ev_path, s1path, cfg, plan, loaded, order_ids, rubric, exp):
    """K7 proved by EXECUTION: a judge that answers TIE on every order gives a zero nominal at every rung, so C1 and
    beta_matched read UNDETERMINED end to end."""
    q = lambda s: None  # noqa: E731
    store, led = _fresh_launch_env(tmp, "zero")
    n = {"c": 0}

    def tie(system, user):
        n["c"] += 1
        return (json.dumps({"winner": "TIE", "confidence": 0.5, "reasoning": "fixture"}), "azure:fixture-judge", 5, 0.01,
                "stop", {"_response_id": "tie-%d" % n["c"]})
    PL.launch(plan, loaded, order_ids, rubric, store, led, tie, "pilot", exp, "blob:x", go=True, today=TODAY, out=q)
    PL.launch(plan, loaded, order_ids, rubric, store, led, tie, "run", exp, "blob:x", go=True, today=TODAY, out=q)
    res = OC.analyze(cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "zero_outcome.txt"), expect=exp, echo=False)
    ck.check("K7 the forced-zero world: C1 reads UNDETERMINED, and so does beta_matched",
             res["c0"] and res["words"][0].startswith("UNDETERMINED") and res["matched_words"][0].startswith("UNDETERMINED"),
             (res["words"], res["matched_words"], res["beta"], res["n_inf"]))
    with open(res["path"], encoding="utf-8") as f:
        ztxt = f.read().splitlines()
    ck.check("D-4 K7 end to end: the falsifier is NOT READ (no C1 reading: K7 fired ...), no planning consequence, no"
             " 'NOT FIRED' / 'FIRED' line; P3a / P3b UNDETERMINED",
             any(x.startswith("  FALSIFIER NOT READ (no C1 reading: K7 fired (UNDETERMINED") for x in ztxt) and
             not any("FALSIFIER NOT FIRED" in x or "FALSIFIER FIRED" in x or "planning on the M / X columns stands" in x
                     for x in ztxt) and any(x.startswith("    P3a UNDETERMINED") for x in ztxt) and
             any(x.startswith("    P3b UNDETERMINED") for x in ztxt), [x for x in ztxt if "FALSIFIER" in x or "P3" in x])


def part_branches(ck):
    need = set()

    def cov(tag):
        need.add(tag)
    cfg = PL.Config()
    m37 = PL.exact_M(37, 12)
    for beta, lo, hi in ((1.9, 1.5, 2.0), (1.9, 1.5, 2.3), (1.9, 0.9, 2.3), (1.0, 0.5, 1.5), (float("nan"), 0, 1)):  # noqa
        A.c1_readings(beta, lo, hi, cfg.bar_P, m37)
    w, _ = A.c1_readings(1.9, 1.5, 2.0, cfg.bar_P, m37)
    ck.check("both exclusions can hold at once (the interval inside (1.06, 2.0529))", w == ["P EXCLUDED", "M EXCLUDED"], w)
    w, _ = A.c1_readings(1.9, 0.9, 2.3, cfg.bar_P, m37)
    ck.check("neither exclusion -> UNRESOLVED AT THIS n", w == ["UNRESOLVED AT THIS n"], w)
    st = {"a": {"q_used": 10, "matches": 20, "kish_m": 2.0}}
    A.support_lines(0.1, 0.2, st, {"a": (3, 2)})
    A.support_lines(0.5, 0.6, st, {"a": (3, 2)})
    for lv in (0.2, 0.6, 3.0):
        A.c1b_lines(cfg, 37, lv, 0.1, lv, 0.1, 1.9, 1.8, 1.5, 2.3, {})
    A.c3_status_line(1.0, 0)
    A.c3_status_line(20.0, 20)
    A.ident_word(5.0, None)
    A.ident_word(1.0, None)
    pl1 = A.predictions_lines(True, 1.9, 0.9, ["P EXCLUDED"], 2120, 2120, 0.001, 5328, cfg)
    pl2 = A.predictions_lines(False, 3.0, 5.0, ["M EXCLUDED"], 5000, 4100, 0.5, 9000, cfg)
    pl3 = A.predictions_lines(True, 1.9, 0.9, ["P EXCLUDED"], 2120, 2000, 0.001, 5328, cfg)
    ck.check("[0761cfa] P2b [0.6, 1.3] point 0.9 on nu_2(37); P3a 0.79 / P3b 0.13; P4 [1,540, 2,664] with after = before"
             " (a trimmed schedule NOT HELD) [L7': P3a / P3b by the ruling of 2026-09-25 (p3_lines); pl2's C0 FAILED ->"
             " both UNDETERMINED]", any("P2b HELD" in x and "nu_2(37)" in x and "[0.6, 1.3] (point 0.9" in x
                                        for x in pl1) and any("P3a HELD" in x and "forecast 0.79" in x for x in pl1)
             and any("P3b UNDETERMINED" in x and "0.13" in x for x in pl2) and any("P4 HELD" in x and "[1,540, 2,664]" in x
                                                                          for x in pl1) and
             any("P4 NOT HELD" in x for x in pl3) and any("P4 NOT HELD" in x for x in pl2), (pl1, pl2, pl3))
    for lv, held in ((0.59, False), (0.6, True), (1.3, True), (1.31, False)):
        pl = A.predictions_lines(True, 1.9, lv, [], 2120, 2120, 0.0, 0, cfg)
        ck.check("[0761cfa] P2b boundary: level %.2f -> %s" % (lv, "HELD" if held else "NOT HELD"),
                 any(("P2b HELD" if held else "P2b NOT HELD") in x for x in pl), pl)
    for b, held in ((1539, False), (1540, True), (2664, True), (2665, False)):
        pl = A.predictions_lines(True, 1.9, 0.9, [], b, b, 0.0, 0, cfg)
        ck.check("[0761cfa] P4 boundary: %d filtered matches -> %s" % (b, "HELD" if held else "NOT HELD"),
                 any(("P4 HELD" if held else "P4 NOT HELD") in x for x in pl), pl)
    A.falsifier_lines(["M EXCLUDED"])
    A.falsifier_lines(["P EXCLUDED"])
    for t in ("C1.P_EXCLUDED", "C1.P_NOT_EXCLUDED", "C1.M_EXCLUDED", "C1.M_NOT_EXCLUDED", "C1.UNRESOLVED",
              "C1.UNDETERMINED_NONFINITE", "K8.THIN", "K8.NOT_THIN", "C0.d2.PASS", "SUPPORT.SCOREABLE", "SUPPORT.NOT_SCOREABLE", "C1B.BELOW_P", "C1B.BETWEEN",
              "C1B.ABOVE_M", "C3.STATUS_UNDETERMINED", "C3.STATUS_OVERRIDDEN", "C3.IDENTIFIED", "C3.NOT_IDENTIFIED",
              "FALSIFIER.FIRED", "FALSIFIER.NOT_FIRED", "C0.UNDETERMINED_BY_VALIDITY", "TRIM.APPLIED", "TRIM.NOT_NEEDED",
              "PILOT.GUARD_PASS", "PILOT.GUARD_FAIL", "KEY.UNSEALED", "STAGE1.VERIFIED", "C0.a.PASS", "C0.b.PASS",
              "C0.c.PASS", "C0.d.PASS", "C0.e.PASS", "C0.f.PASS", "C0.g.PASS", "C0.complete.PASS", "C0.complete.FAIL",
              "C0.h.PASS", "DISCLOSURE.COUNTS", "DISCLOSURE.ABSENT",
              # [L7'] the new print branches
              "PRED.P3a.UNDETERMINED", "PRED.P3b.UNDETERMINED", "SUPPORT.DEFF_MEASURED", "SUPPORT.DEFF_UNDEFINED",
              "SUPPORT.DEFF_ABSENT", "F4.SYSTEM_EQUAL", "F4.SYSTEM_DIFFERS", "C0.D2_VOID", "FALSIFIER.NOT_READ"):
        cov(t)
    for p in ("P1", "P2", "P2b", "P3a", "P3b", "P4", "P5"):
        cov("PRED.%s.HELD" % p)
        cov("PRED.%s.NOT_HELD" % p)
    missing = sorted(t for t in need if report.HITS.get(t, 0) == 0)
    ck.check("EVERY registered print branch executed (%d branches)" % len(need), not missing, missing)
    ck.check("the readings are python bools, never numpy identity tests", isinstance(bool(np.float64(2.0) > 1.06), bool))


# ── [L7' 2026-09-25] the pre-analyze delta: F2 (the measured DEFF), F3 (P3 by the ruling), G1 (P5 + prior), F4, F8,
# the code-identity disclosure, G2 (the reviewer's transport probe, mutants T2 / T3) ──────────────────────────────────

F4_RECORD_TEXT = ("system turn byte-identical to STACK-NORUBRIC's measured norubric arm (944 of 944 rows, sys_sha"
                  " d0c524bbd66b5a5e); the user turn is E-J's; 1,846 of 2,664 matches (69.3%) carry no reference, a"
                  " branch STACK-NORUBRIC never measured; GENERIC_SYSTEM + GENERIC_RUBRIC on E-J's layer is UNMEASURED.")

# the ruling's table: (c0_pass, words) -> (P3a, P3b)
P3_TABLE = (
    (True, ["P EXCLUDED"], "HELD", "HELD"),
    (True, ["M EXCLUDED"], "FAILED", "FAILED"),
    (True, ["P EXCLUDED", "M EXCLUDED"], "HELD", "FAILED"),
    (True, ["UNRESOLVED AT THIS n"], "FAILED", "HELD"),
    (True, ["UNDETERMINED (1 non-finite replicates)"], "UNDETERMINED", "UNDETERMINED"),
    (False, ["P EXCLUDED"], "UNDETERMINED", "UNDETERMINED"),
    (False, ["M EXCLUDED"], "UNDETERMINED", "UNDETERMINED"),
    (False, [], "UNDETERMINED", "UNDETERMINED"),
)


def _p3_scores(c0, words):
    got = {}
    for ln in A.p3_lines(c0, words):
        m = re.match(r"\s+(P3[ab]) (HELD|FAILED|UNDETERMINED):", ln)
        if m:
            got[m.group(1)] = m.group(2)
    return got.get("P3a"), got.get("P3b")


def _p3_table_ok():
    bad = []
    for c0, words, want_a, want_b in P3_TABLE:
        got = _p3_scores(c0, words)
        if got != (want_a, want_b):
            bad.append((c0, words, got, (want_a, want_b)))
    return not bad, bad


def part_l7_units(ck):
    """[L7'] F3 (every branch of the ruling, the exact bar, the falsifier's equivalence), F2 (measured_deff / deff_lines
    / support_lines, all branches), G1 (P5 on journal + prior), F4 (the verbatim text, both system-turn branches); and
    the mutants p3b_inverted, p3_no_undetermined, deff_inverted."""
    cfg = PL.Config()
    m37 = PL.exact_M(37, 12)
    ok, bad = _p3_table_ok()
    ck.check("F3 the ruling's table, 8 cases: P3a HELD iff 'P EXCLUDED' (UNRESOLVED -> FAILED); P3b HELD iff NOT 'M"
             " EXCLUDED'; both UNDETERMINED when C0 FAILED or K7 fired", ok, bad)
    for c0, words, _a, want_b in P3_TABLE:
        if c0 and not words[0].startswith("UNDETERMINED"):
            fired = any("FALSIFIER FIRED" in x for x in A.falsifier_lines(words))
            ck.check("F3 P3b FAILED iff the FALSIFIER fires: %s" % " + ".join(words), (want_b == "FAILED") == fired,
                     (want_b, fired))
    # the exact bar, end to end through c1_readings (compared unrounded): 2.0529 < 2.052941 -> M EXCLUDED -> P3b FAILED
    for hi, want_b in ((2.0529, "FAILED"), (2.05295, "HELD"), (m37, "HELD")):
        w, _l = A.c1_readings(1.9, 1.5, hi, cfg.bar_P, m37)
        ck.check("F3 at the exact M (unrounded): upper %.6f -> C1 %s -> P3b %s" % (hi, w, want_b),
                 _p3_scores(True, w)[1] == want_b, (w, _p3_scores(True, w)))
    w, _l = A.c1_readings(1.9, 1.5, 2.0, cfg.bar_P, m37, n_inf=2)
    ck.check("F3 K7 through c1_readings (2 non-finite replicates) -> P3a / P3b UNDETERMINED",
             _p3_scores(True, w) == ("UNDETERMINED", "UNDETERMINED"), (w, _p3_scores(True, w)))
    pl = A.predictions_lines(True, 1.9, 0.9, ["UNRESOLVED AT THIS n"], 2120, 2120, 0.0, 10, cfg)
    ck.check("F3 predictions_lines carries the ruling's lines (no 'NOT HELD' for P3; the forecasts 0.79 / 0.87 printed)",
             any(x.startswith("    P3a FAILED:") and "forecast 0.79" in x for x in pl) and
             any(x.startswith("    P3b HELD:") and "forecast 0.87" in x for x in pl) and
             not any(x.startswith("    P3") and "NOT HELD" in x for x in pl), pl)
    with _mutant(A, "p3b_inverted"):
        ok_m, _b = _p3_table_ok()
    ck.check("MUTANT p3b_inverted (the pre-L7' P3b, HELD on 'M EXCLUDED') -> killed by the table", not ok_m)
    with _mutant(A, "p3_no_undetermined"):
        ok_m2, _b2 = _p3_table_ok()
    ck.check("MUTANT p3_no_undetermined (P3 scored when C1 gives no reading) -> killed by the table", not ok_m2)

    # [D-4] the falsifier without a reading: NOT READ, no planning consequence
    def fals_ok():
        cases = ((True, ["UNDETERMINED (1 non-finite replicates)"], "K7 fired (UNDETERMINED (1 non-finite replicates))"),
                 (False, ["M EXCLUDED"], "C0 FAILED (UNDETERMINED BY VALIDITY)"),
                 (False, [], "C0 FAILED (UNDETERMINED BY VALIDITY)"))
        bad = []
        for c0, words, why in cases:
            fl = A.falsifier_lines(words, c0_pass=c0)
            if fl != ["  FALSIFIER NOT READ (no C1 reading: %s); no planning consequence is stated" % why]:
                bad.append((c0, words, fl))
        for words, fired in ((["M EXCLUDED"], True), (["P EXCLUDED"], False), (["UNRESOLVED AT THIS n"], False)):
            fl = A.falsifier_lines(words, c0_pass=True)
            if not (len(fl) == 1 and fl[0].startswith("  FALSIFIER FIRED" if fired else "  FALSIFIER NOT FIRED")):
                bad.append((True, words, fl))
        return not bad, bad
    ok_f, bad_f = fals_ok()
    ck.check("D-4 the falsifier without a C1 reading (K7; C0 FAILED, even with 'M EXCLUDED' in the words; no words) is"
             " NOT READ with the reason and no planning consequence; with a reading FIRED iff 'M EXCLUDED'", ok_f, bad_f)
    with _mutant(A, "falsifier_not_fired_no_reading"):
        ok_fm, _bf = fals_ok()
    ck.check("MUTANT falsifier_not_fired_no_reading (the pre-D-4 'NOT FIRED ... planning stands' without a reading) ->"
             " killed", not ok_fm)
    # F2 units
    d = A.measured_deff([1.0, 2.0, 3.0, float("nan")], [1.0, 1.5, 2.0, float("inf"), float("nan")], 100)
    ck.check("F2 measured_deff: Var_q 1 / Var_m 0.25 = DEFF 4; n 100 -> n_eff 25; non-finite counted (1 / 2), never used",
             abs(d["deff"] - 4.0) < 1e-12 and abs(d["n_eff"] - 25.0) < 1e-12 and (d["inf_q"], d["inf_m"]) == (1, 2) and
             (d["finite_q"], d["finite_m"]) == (3, 3), d)
    with _mutant(A, "deff_inverted"):
        d_m = A.measured_deff([1.0, 2.0, 3.0], [1.0, 1.5, 2.0], 100)
    ck.check("MUTANT deff_inverted (Var_m / Var_q) -> killed by the unit (0.25 != 4)", abs(d_m["deff"] - 4.0) > 1e-6,
             d_m)
    d_u1 = A.measured_deff([1.0, 2.0], [1.0, float("nan")], 50)
    d_u2 = A.measured_deff([1.0, 2.0], [1.0, 1.0, 1.0], 50)
    ck.check("F2 DEFF undefined: fewer than 2 finite match-level replicates, or Var_m 0 -> deff / n_eff None",
             d_u1["deff"] is None and d_u1["n_eff"] is None and d_u2["deff"] is None, (d_u1, d_u2))
    dl = A.deff_lines(d, 0.25, "matches")
    ck.check("F2 deff_lines: DEFF 4.000, n 100, n_eff 25.0, MDE 2.80 x 0.25 = 0.700 and x 1.25 = 0.875, 'DECIDES NOTHING'",
             "DECIDES NOTHING" in dl[0] and "DEFF = 4.000" in dl[1] and "n = 100 matches" in dl[1] and
             "n_eff = n / DEFF = 25.0" in dl[1] and "= 0.700" in dl[1] and "= 0.875" in dl[1], dl)
    dlu = A.deff_lines(d_u1, 0.25, "matches")
    ck.check("F2 deff_lines, undefined branch: printed, n named, no n_eff", "DEFF undefined" in dlu[1] and
             "n = 50 matches" in dlu[1], dlu)
    st = {"a": {"q_used": 10, "matches": 20, "kish_m": 2.0}}
    s0 = A.support_lines(0.1, 0.2, st, {"a": (3, 2)})
    s1 = A.support_lines(0.1, 0.2, st, {"a": (3, 2)}, deff=d)
    ck.check("F2 support_lines: the 'DEFF: not applicable' line and the n_eff(questions) label are KEPT and bracketed; the"
             " measured lines follow when given, 'not computed' otherwise; the SCOREABLE line is unchanged",
             any(x.startswith("    DEFF: not applicable") and "[L7' 2026-09-25" in x for x in s1) and
             any("n_eff(questions) 10 [L7' 2026-09-25" in x for x in s1) and any("DEFF = 4.000" in x for x in s1) and
             any("MEASURED DEFF: not computed" in x for x in s0) and s0[-1] == s1[-1] and "SCOREABLE" in s1[-1],
             (s0, s1))
    # G1 units
    p_ok = A.predictions_lines(True, 1.9, 0.9, [], 2120, 2120, 0.0, 5352, cfg, prior=24)
    p_over = A.predictions_lines(True, 1.9, 0.9, [], 2120, 2120, 0.0, 7980 + 24, cfg, prior=24)
    p_mut = A.predictions_lines(True, 1.9, 0.9, [], 2120, 2120, 0.0, 7980, cfg)
    ck.check("G1 P5 prints posted = journal + prior (5,352 = 5,328 + 24); journal 7,980 + prior 24 = 8,004 > 8,000 -> NOT"
             " HELD, where the journal alone (the pre-L7' count) would read HELD",
             any("P5 HELD" in x and "posted 5352 (invocations: journal 5328 + prior (retired stores) 24" in x
                 for x in p_ok) and any("P5 NOT HELD" in x and "posted 8004" in x for x in p_over) and
             any("P5 HELD" in x and "posted 7980 <=" in x for x in p_mut), (p_ok[-1], p_over[-1], p_mut[-1]))
    # F4 units
    ck.check("F4 the disclosure text is the record's, verbatim (READY 286a1b0 F4 / programme L16931 bracket)",
             A.F4_TEXT == F4_RECORD_TEXT, A.F4_TEXT)
    f_eq = A.f4_disclosure_lines({"ONE": 818, "NONE": 1846}, A.F4_NORUBRIC_SYS16 + "0" * 48, "beside C1")
    f_ne = A.f4_disclosure_lines({"ONE": 1}, "f" * 64, "beside C1b")
    ck.check("F4 lines: the verbatim text beside C1 / C1b; this analysis's count (1,846 of 2,664 = 69.3%); the system turn"
             " EQUAL / DIFFERS branches; 'SYSTEM TURN ONLY'", F4_RECORD_TEXT in f_eq[0] and "beside C1)" in f_eq[0] and
             "reference NONE on 1846 of 2664 scheduled matches (69.3%" in f_eq[1] and ": EQUAL." in f_eq[1] and
             "SYSTEM TURN ONLY" in f_eq[1] and "beside C1b" in f_ne[0] and ": DIFFERS." in f_ne[1] and
             "reference NONE on 0 of 1" in f_ne[1], (f_eq, f_ne))


def _read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def part_l7_outcome(ck, tmp, ev_path, s1path, cfg, rubric, exp, store, led, out, res, txt, c1, partial_path):
    """[L7'] the fixture outcome end to end: F2 printed from the records (recomputed), the INERTNESS of C1 under the DEFF
    code (leg A deff_off vs leg B, with the execution witness), F3 / F4 / F8 / G1 lines, the C0-failure branches' P3
    lines (partial cache; C0 (d) part 2 void), the code-identity disclosure (the store's script_blob and the analysis's
    lf16 DIFFER, and the analysis still reads), and the mutants deff_question_draws and p5_journal_only."""
    lines = txt.splitlines()
    # F2 from the records: recompute DEFF from c1_boot and deff_match_boot
    rec_q = [r for n, p, k, s in res["records"] if n == "c1_boot" for r in _read_jsonl(p)]
    rec_m = [r for n, p, k, s in res["records"] if n == "deff_match_boot" for r in _read_jsonl(p)]
    bq = np.array([r["beta"] for r in rec_q if r["beta"] is not None and np.isfinite(r["beta"])], dtype=float)
    bm = np.array([r["beta"] for r in rec_m if r["beta"] is not None and np.isfinite(r["beta"])], dtype=float)
    d = res["deff"]
    ck.check("F2 the match-level records (deff_match_boot, %d = B replicates) are written; DEFF recomputed from the two"
             " record files = the printed one (%s)" % (len(rec_m), d and d["deff"]),
             len(rec_m) == cfg.B_outer and d is not None and d["deff"] is not None and bm.size > 1 and
             abs(d["deff"] - float(bq.var(ddof=1)) / float(bm.var(ddof=1))) < 1e-9 and
             any(("DEFF = %.3f" % d["deff"]) in x for x in lines), d)
    n_board = [x for x in lines if "(b) [F8] board rows naming a model outside the roster: 0 of" in x]
    ck.check("F2 n = the usable dual-order matches on the board (= the F8 board count), n_eff = n / DEFF",
             bool(n_board) and ("0 of %d " % d["n"]) in n_board[0] and abs(d["n_eff"] - d["n"] / d["deff"]) < 1e-9,
             (n_board, d))
    units = {}
    for x in lines:
        m = re.search(r"the match-level resample's units; ([^)]*)\)", x)
        if m:
            units = {a: int(v) for a, v in re.findall(r"([a-z ]+?) (\d+)(?:, |$)", m.group(1))}
    per_anchor = {m.group(1): int(m.group(2)) for m in (re.match(r"    anchor (.+?): questions judged \d+, matches (\d+),", x)
                                                         for x in lines) if m}
    ck.check("F2 the match-level resample's units per anchor = the board's usable matches per anchor (the support"
             " line's 'matches'), not its questions; n = their sum", bool(units) and units == per_anchor and
             sum(units.values()) == d["n"], (units, per_anchor, d["n"]))
    ck.check("F2 the match-level stream 'deff/mboot' and its inner streams are in the stream log; C1's 'boot' too",
             any("deff/mboot" in x for x in open(out + ".streams.tsv", encoding="utf-8")) and
             any(x.startswith("deff/rep0000/k") for x in open(out + ".streams.tsv", encoding="utf-8")))
    # INERTNESS of C1 under the DEFF code: leg A (deff_off) vs leg B (the build); witness: leg B executed the new code
    out_a = os.path.join(tmp, "outcome_deff_off.txt")
    with _mutant(OC, "deff_off"):
        res_a = OC.analyze(cfg, ev_path, s1path, store, rubric, led, out_a, expect=exp, echo=False)
    pa = dict((n, s) for n, _p, _k, s in res_a["records"])
    pb = dict((n, s) for n, _p, _k, s in res["records"])
    ck.check("F2 INERTNESS: C1 is identical with the match-level bootstrap OFF (leg A) and ON (leg B): beta-hat, the"
             " interval, the words, n_inf and the c1_boot / c1_integrated / c1b_matched_boot record shas",
             res_a["beta"] == res["beta"] and res_a["interval"] == res["interval"] and res_a["words"] == res["words"] and
             res_a["n_inf"] == res["n_inf"] and res_a["beta_matched"] == res["beta_matched"] and
             all(pa[k] == pb[k] for k in ("c1_boot", "c1_integrated", "c1b_matched_boot")),
             (res_a["beta"], res["beta"], res_a["interval"], res["interval"]))
    ck.check("F2 INERTNESS witness: leg B EXECUTED the new code (deff_match_boot records, a measured DEFF), leg A did not",
             "deff_match_boot" in pb and "deff_match_boot" not in pa and res_a["deff"] is None and res["deff"] is not None)
    out_q = os.path.join(tmp, "outcome_deff_q.txt")
    with _mutant(OC, "deff_question_draws"):
        res_q = OC.analyze(cfg, ev_path, s1path, store, rubric, led, out_q, expect=exp, echo=False)
    ck.check("MUTANT deff_question_draws (the denominator from C1's own question draws: DEFF 1) -> killed: the build's"
             " match-level variance differs from the question-clustered one", res_q["deff"]["deff"] == 1.0 and
             res["deff"]["deff"] != 1.0, (res_q["deff"], res["deff"]))
    # F3 / F4 / F8 / G1 in the outcome of record
    p3 = [x for x in lines if x.startswith("    P3a ") or x.startswith("    P3b ")]
    ck.check("F3 the outcome scores P3a / P3b by the ruling (2 lines, HELD / FAILED, the reading printed)",
             len(p3) == 2 and all(re.match(r"    P3[ab] (HELD|FAILED): C1 reads ", x) for x in p3) and
             _p3_scores(True, res["words"]) == tuple(re.match(r"    P3[ab] (\w+)", x).group(1) for x in p3), p3)
    ck.check("F4 the disclosure is printed verbatim beside C1 (in the C1 file) and beside C1b (in the outcome)",
             sum(1 for x in lines if F4_RECORD_TEXT in x) == 2 and
             sum(1 for x in c1.splitlines() if F4_RECORD_TEXT in x and "beside C1)" in x) == 1 and
             any(F4_RECORD_TEXT in x and "beside C1b" in x for x in lines))
    ck.check("F4 the fixture's system turn is the slot of record's (= STACK-NORUBRIC's d0c524bbd66b5a5e: EQUAL)",
             any("STACK-NORUBRIC's norubric sys_sha d0c524bbd66b5a5e: EQUAL" in x for x in lines))
    ck.check("F8 C0 (b): the board rows (before C1) and the LOADED specs (after C1) are counted separately, both 0",
             any("(b) [F8] board rows naming a model outside the roster: 0 of" in x for x in c1.splitlines()) and
             any("(b) [F8] LOADED specs naming a model outside the roster: 0 of" in x for x in lines) and
             not any("(b) [F8] LOADED specs" in x for x in c1.splitlines()))
    ck.check("G1 the outcome's P5 prints journal + prior (DEV: prior 0)", any(
        "P5 " in x and "(invocations: journal" in x and "+ prior (retired stores) 0" in x for x in lines))
    # the C0-failure branches print P3 UNDETERMINED: the partial cache ...
    with open(partial_path, encoding="utf-8") as f:
        ptxt = f.read()
    ck.check("F3 C0 FAILED (the partial cache): P3a / P3b UNDETERMINED printed",
             "P3a UNDETERMINED: C1 gives no reading (C0 FAILED" in ptxt and "P3b UNDETERMINED" in ptxt)
    ck.check("D-4 C0 FAILED (the partial cache): 'FALSIFIER NOT READ (no C1 reading: C0 FAILED ...)', no planning"
             " consequence", "FALSIFIER NOT READ (no C1 reading: C0 FAILED (UNDETERMINED BY VALIDITY))" in ptxt and
             "FALSIFIER NOT FIRED" not in ptxt and "planning on the M / X columns stands" not in ptxt)
    # ... and C0 (d) part 2 void (the rebuilt payloads' leak scan forced to report a hit)
    real_scan = PL.scan_payloads

    def scan_hit(*a, **k):
        rows, n, hits = real_scan(*a, **k)
        return rows, n, {"forced": 1}
    PL.scan_payloads = scan_hit
    try:
        res_v = OC.analyze(cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "outcome_void.txt"), expect=exp,
                           echo=False)
    finally:
        PL.scan_payloads = real_scan
    with open(res_v["path"], encoding="utf-8") as f:
        vtxt = f.read()
    ck.check("F3 C0 (d) part 2 VOID after C1: P3a / P3b UNDETERMINED printed; no P5 / no C3", res_v.get("void") and
             "P3a UNDETERMINED" in vtxt and "P3b UNDETERMINED" in vtxt and "C3 BOTH" not in vtxt, res_v)
    ck.check("D-4 C0 (d) part 2 VOID: the falsifier NOT READ (C0 FAILED), no planning consequence",
             "FALSIFIER NOT READ (no C1 reading: C0 FAILED" in vtxt and "FALSIFIER NOT FIRED" not in vtxt and
             "FALSIFIER FIRED" not in vtxt)
    # the code identity: a different analysis lf16 and the store's script_blob 'blob:x' -> DIFFERS, and the store is READ
    real_lf = C.package_lf16
    real_prior = PL.prior_journals_state
    C.package_lf16 = lambda: "0" * 16
    PL.prior_journals_state = lambda cfg_, ledger_dir, prior_journals=None: {
        "invocations": 3, "per_day": {TODAY: 3}, "paths": ["selftest-prior"]}
    ACC.append(PL.REGISTRATION, "selftest retired store", 3, led, day=TODAY)
    try:
        out_p = os.path.join(tmp, "outcome_prior.txt")
        res_p = OC.analyze(cfg, ev_path, s1path, store, rubric, led, out_p, expect=exp, echo=False)
        with _mutant(OC, "p5_journal_only"):
            res_pm = OC.analyze(cfg, ev_path, s1path, store, rubric, led, os.path.join(tmp, "outcome_prior_m.txt"),
                                expect=exp, echo=False)
    finally:
        C.package_lf16 = real_lf
        PL.prior_journals_state = real_prior
    with open(out_p, encoding="utf-8") as f:
        prt = f.read().splitlines()
    with open(res_pm["path"], encoding="utf-8") as f:
        prm = f.read().splitlines()
    inv = ACC.read_journal(PL.journal_path(store))["invocations"]
    ck.check("CODE IDENTITY: the analysis's lf16 DIFFERS from the posting build's and the store's script_blob is 'blob:x';"
             " --analyze READS the store (C0 PASS, a reading): it never compares the recipe identity",
             res_p["c0"] and bool(res_p["words"]) and any("DIFFERS from the posting build's" in x and "blob:x" in x
                                                          for x in prt))
    ck.check("G1 end to end with a prior of 3 booked on the ledger: C0 (f) PASSES on journal + prior, and P5 prints"
             " posted %d = journal %d + prior 3" % (inv + 3, inv),
             any(x.startswith("  (f) PASS") and "+ prior (retired stores) 3" in x for x in prt) and
             any("P5 " in x and "posted %d (invocations: journal %d + prior (retired stores) 3" % (inv + 3, inv) in x
                 for x in prt), [x for x in prt if "P5 " in x or x.startswith("  (f)")])
    ck.check("MUTANT p5_journal_only (the pre-L7' P5 count) -> killed: P5 prints the journal only (%d)" % inv,
             not any("posted %d (invocations" % (inv + 3) in x for x in prm) and
             any("P5 " in x and ("posted %d <=" % inv) in x for x in prm), [x for x in prm if "P5 " in x])


def part_transport_probe(ck, tmp, plan, loaded, order_ids, rubric, exp):
    """[L7' G2] the reviewer's transport probe (READY 1f58df5 claim 2b / 2c; scratchpad k37/mrepo2/probe_transport.py),
    in the selftest: (a) data_root honours TAXOARENA_DATA_ROOT and load_transport() (no root argument) reads THAT .env;
    (b) a --run launch with the endpoint None (load_env skipped in the run's process) is REFUSED by the preflight with the
    store, the journal and the ledger byte-identical and 0 posts. MUTANT T2 (the preflight skipped in mode run) and
    MUTANT T3 (data_root ignores TAXOARENA_DATA_ROOT and falls back to a checkout root) are each KILLED."""
    rr = PL.rr
    saved = (rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.ROOT, rr.TOKEN)
    env0 = os.environ.get("TAXOARENA_DATA_ROOT")
    real_pf, real_dr = PL.transport_preflight, PL.data_root

    def h(p):
        if not os.path.exists(p):
            return None
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    try:
        droot = os.path.join(tmp, "probe_data_root")
        os.mkdir(droot)
        with open(os.path.join(droot, ".env"), "x", encoding="utf-8") as f:
            f.write("AZURE_AI_ENDPOINT=https://probe-fixture.services.example.com/\nAZURE_GROK_API_KEY=%s\n" % FIXTURE_KEY)
        noenv = os.path.join(tmp, "probe_checkout_root")         # a checkout root WITHOUT .env (the worktree's case)
        os.mkdir(noenv)
        os.environ["TAXOARENA_DATA_ROOT"] = droot

        def probe_a():
            _set_transport(None, None)
            try:
                envp = PL.load_transport(out=q_)
            except SystemExit:
                return False
            return (PL.data_root() == droot and envp == os.path.join(droot, ".env") and
                    str(rr.AZURE_ENDPOINT).startswith("https://probe-fixture.services.example.com/"))
        ok_a = probe_a()
        ck.check("G2 probe (a): data_root honours TAXOARENA_DATA_ROOT; load_transport() reads that .env", ok_a)
        PL.data_root = lambda: noenv                                     # MUTANT T3
        try:
            ok_t3 = probe_a()
        finally:
            PL.data_root = real_dr
        ck.check("MUTANT T3 (data_root ignores TAXOARENA_DATA_ROOT) -> killed by probe (a)", ok_a and not ok_t3)
        _set_transport(FIXTURE_ENDPOINT, FIXTURE_KEY)
        store, led = _fresh_launch_env(tmp, "probe_tr")
        fk = fake_call_factory()
        r = PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "pilot", exp, "blob:x", go=True, today=TODAY,
                      out=q_)
        n_pilot = fk.n["calls"]

        def snap():
            return (h(store), h(PL.journal_path(store)), tuple(sorted((f, h(os.path.join(led, f)))
                                                                     for f in os.listdir(led))))

        def probe_b():
            before, n0 = snap(), fk.n["calls"]
            _set_transport(None, FIXTURE_KEY)                           # load_env skipped in the --run process
            try:
                PL.launch(plan, loaded, order_ids, rubric, store, led, fk, "run", exp, "blob:x", go=True, today=TODAY,
                          out=q_)
                res = "NOT REFUSED"
            except SystemExit as e:
                res = "REFUSED: " + str(e)
            finally:
                _set_transport(FIXTURE_ENDPOINT, FIXTURE_KEY)
            return "TRANSPORT PREFLIGHT: REFUSED" in res and snap() == before and fk.n["calls"] == n0, res
        ok_b, res_b = probe_b()
        ck.check("G2 probe (b): the pilot PASSED (%d posts); a --run with the endpoint None is REFUSED by the TRANSPORT"
                 " PREFLIGHT, store / journal / ledger byte-identical, 0 posts" % n_pilot,
                 r["guard"]["pass"] and ok_b, res_b[:200])
        PL.transport_preflight = lambda out=print: None                  # MUTANT T2: the preflight skipped (mode run)
        try:
            ok_t2, res_t2 = probe_b()
        finally:
            PL.transport_preflight = real_pf
        ck.check("MUTANT T2 (the preflight skipped in mode run) -> killed by probe (b): NOT refused, %d fake posts" % (
            fk.n["calls"] - n_pilot), ok_b and not ok_t2 and fk.n["calls"] > n_pilot, res_t2[:120])
    finally:
        PL.transport_preflight, PL.data_root = real_pf, real_dr
        rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.ROOT, rr.TOKEN = saved
        if env0 is None:
            os.environ.pop("TAXOARENA_DATA_ROOT", None)
        else:
            os.environ["TAXOARENA_DATA_ROOT"] = env0


def part_pool(ck, tmp, plan, loaded, order_ids, rubric, exp):
    """[JV2-PARALLEL-POSTING, registered bf9d80b; I5 and EC5 at the driver] launch(..., workers=N): a pooled pilot + run
    equal to the sequential one; the no-go launch prints the [POOL] line with max_inflight and posts nothing; a pooled
    launch on a journal created at workers 1 is refused before any post; the TRANSPORT PREFLIGHT runs FIRST at workers 4
    (before the journal, the store, the ledger and the pool); MUTANTS preflight_after_pool, preflight_skipped_pooled."""
    from judge_v2 import pool as POOL
    lines = []
    s1, l1 = _fresh_launch_env(tmp, "pool_w1")
    f1 = fake_call_factory()
    PL.launch(plan, loaded, order_ids, rubric, s1, l1, f1, "pilot", exp, "blob:x", go=True, today=TODAY, out=q_)
    PL.launch(plan, loaded, order_ids, rubric, s1, l1, f1, "run", exp, "blob:x", go=True, today=TODAY, out=q_)
    s4, l4 = _fresh_launch_env(tmp, "pool_w4")
    f4 = fake_call_factory()
    r4p = PL.launch(plan, loaded, order_ids, rubric, s4, l4, f4, "pilot", exp, "blob:x", go=True, today=TODAY,
                    out=lines.append, workers=4)
    r4r = PL.launch(plan, loaded, order_ids, rubric, s4, l4, f4, "run", exp, "blob:x", go=True, today=TODAY,
                    out=lines.append, workers=4)

    def votes(p):
        c = PL.open_store_ro(p)
        try:
            return sorted(c.execute("SELECT match_id, presentation_order, vote, payload_sha256 FROM verdict").fetchall())
        finally:
            c.close()
    ck.check("POOL workers 4: the pilot 12 PASSES its guard and the run completes; the verdicts equal the workers-1"
             " launch's slot for slot", r4p["guard"]["pass"] and PL.store_counts(s4)[1] == 2 * len(order_ids) and
             votes(s4) == votes(s1) and r4p["posted"] + r4r["posted"] == f4.n["calls"] == f1.n["calls"],
             (r4p["posted"], r4r["posted"], f4.n["calls"], f1.n["calls"]))
    rows = ACC.atl._rows(ACC.atl.day_ledger_path(l4, TODAY))
    ck.check("POOL workers 4: the labels carry ' w=4', the journal is v2 (max_inflight %d), ledger == journal" %
             POOL.MAX_INFLIGHT, all(r["launch"].endswith(" w=4") for r in rows) and
             ACC.journal_max_inflight(PL.journal_path(s4)) == POOL.MAX_INFLIGHT and
             ACC.atl.ledger_calls(PL.REGISTRATION, l4) == ACC.read_journal(PL.journal_path(s4))["invocations"],
             [r["launch"] for r in rows])
    ck.check("POOL workers 4 prints the writer's pipelined [POOL] line; workers 1 prints the sequential one",
             any(x.startswith("[POOL] workers 4 (pipelined path; journal max_inflight %d" % POOL.MAX_INFLIGHT)
                 for x in lines))
    # EC5: no --go: the [POOL] line with the journal's max_inflight; nothing posted, nothing created
    s5, l5 = _fresh_launch_env(tmp, "pool_nogo")
    f5 = fake_call_factory()
    ng = []
    PL.launch(plan, loaded, order_ids, rubric, s5, l5, f5, "pilot", exp, "blob:x", go=False, today=TODAY, out=ng.append,
              workers=4)
    ck.check("POOL EC5 a launch without --go prints the preflight, the [POOL] line and max_inflight, and posts nothing",
             any(x.startswith("TRANSPORT PREFLIGHT: OK") for x in ng) and
             "  [POOL] workers 4 (pipelined path); journal max_inflight %d (a new journal; journal v2); registered"
             " maximum %d -> OK" % (POOL.MAX_INFLIGHT, POOL.MAX_INFLIGHT) in ng and f5.n["calls"] == 0 and
             not os.path.exists(s5) and not os.path.exists(PL.journal_path(s5)) and os.listdir(l5) == [],
             [x for x in ng if "POOL" in x])
    ng1 = []
    PL.launch(plan, loaded, order_ids, rubric, s1, l1, f1, "run", exp, "blob:x", go=False, today=TODAY, out=ng1.append,
              workers=4)
    ck.check("POOL EC5 the no-go line names a journal created at workers 1 and the refusal to come",
             "  [POOL] workers 4 (pipelined path); journal max_inflight 1 (created at workers 1); registered maximum %d ->"
             " REFUSED at the launch (workers > max_inflight)" % POOL.MAX_INFLIGHT in ng1, [x for x in ng1 if "POOL" in x])
    # a pooled relaunch on the workers-1 journal: refused before any post (journal v1: max_inflight 1)
    s6, l6 = _fresh_launch_env(tmp, "pool_v1")
    f6 = fake_call_factory()
    PL.launch(plan, loaded, order_ids, rubric, s6, l6, f6, "pilot", exp, "blob:x", go=True, today=TODAY, out=q_)
    n6 = f6.n["calls"]
    ck.refused("POOL a pooled --run on a journal created at workers 1", lambda: PL.launch(
        plan, loaded, order_ids, rubric, s6, l6, f6, "run", exp, "blob:x", go=True, today=TODAY, out=q_, workers=4),
        ("max_inflight 1", "REFUSED before any post"))
    ck.check("POOL ... with 0 posts and ledger == journal", f6.n["calls"] == n6 and ACC.atl.ledger_calls(
        PL.REGISTRATION, l6) == ACC.read_journal(PL.journal_path(s6))["invocations"])
    # the coordinator's rate control at workers 1: a rate configuration makes a single poster POOLED (journal v2, bound 1)
    s7, l7 = _fresh_launch_env(tmp, "pool_rate1")
    f7 = fake_call_factory()
    l7lines = []
    PL.launch(plan, loaded, order_ids, rubric, s7, l7, f7, "pilot", exp, "blob:x", go=True, today=TODAY,
              out=l7lines.append, rate=POOL.RateConfig(max_rpm=20))
    rows7 = ACC.atl._rows(ACC.atl.day_ledger_path(l7, TODAY))
    ck.check("POOL workers 1 WITH a rate configuration: the pooled path at bound 1 (journal v2, label ' w=1', the [RATE]"
             " config line), the pilot guard PASSES", any(x.startswith("[POOL] workers 1 (pipelined path") for x in l7lines)
             and any(x.startswith("[RATE] config: max_rpm 20") for x in l7lines) and all(r["launch"].endswith(" w=1") for r
                                                                                        in rows7) and
             ACC.journal_max_inflight(PL.journal_path(s7)) == POOL.MAX_INFLIGHT and PL.pilot_guard(s7, order_ids[
                 :plan.cfg.pilot_n])["pass"], [x for x in l7lines if x.startswith(("[POOL]", "[RATE]"))][:3])
    ck.refused("POOL a rate-controlled (pooled) --run at workers 1 on a journal created at workers 1", lambda: PL.launch(
        plan, loaded, order_ids, rubric, s6, l6, f6, "run", exp, "blob:x", go=True, today=TODAY, out=q_,
        rate=POOL.RateConfig()), ("POOLED launch", "REFUSED before any post"))
    # I5: the preflight FIRST at workers 4
    saved = (PL.rr.AZURE_ENDPOINT, PL.rr.AZURE_KEY)

    def bad_launch(name):
        s, led = _fresh_launch_env(tmp, name)
        fk = fake_call_factory()
        _set_transport(None, FIXTURE_KEY)
        try:
            try:
                PL.launch(plan, loaded, order_ids, rubric, s, led, fk, "pilot", exp, "blob:x", go=True, today=TODAY,
                          out=q_, workers=4)
                msg = None
            except SystemExit as e:
                msg = str(e)
        finally:
            _set_transport(*saved)
        untouched = (not os.path.exists(s) and not os.path.exists(PL.journal_path(s)) and
                     not os.path.exists(s + ".launch.json") and os.listdir(led) == [])
        return msg, untouched, fk.n["calls"]
    msg, untouched, n = bad_launch("pool_pf")
    ck.check("POOL I5 workers 4 with the endpoint None: REFUSED by the TRANSPORT PREFLIGHT before the journal, the store,"
             " the manifest, the ledger and the pool; 0 posts", msg is not None and "TRANSPORT PREFLIGHT: REFUSED" in msg
             and untouched and n == 0, msg)
    for m in ("preflight_after_pool", "preflight_skipped_pooled"):
        PL.MUTANT_POOL = m
        try:
            msg, untouched, n = bad_launch("pool_pf_" + m)
        finally:
            PL.MUTANT_POOL = None
        ck.check("POOL I5 MUTANT %s: the journal / store / ledger written or a post made before (or without) the"
                 " preflight -> killed" % m, not (msg is not None and "TRANSPORT PREFLIGHT: REFUSED" in msg and untouched
                                                  and n == 0), (msg or "no refusal")[:120])


def premerge_main_ref(ref, out=print):
    """SELFTEST-ONLY [JV2-PARALLEL-POSTING]: resolve K2's `main:` lookups against `ref` (e.g. HEAD) in THIS process, to
    exercise the record's pin table on a branch before its merge. Printed; pilot.py itself is not changed."""
    import subprocess

    def mb(rel):
        r = subprocess.run(["git", "rev-parse", "%s:tools/analysis/%s" % (ref, rel)], capture_output=True, text=True,
                           cwd=C.ROOT, timeout=60)
        return ("blob:" + r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
    PL.main_blob = mb
    PL.judge_pins_ok.__defaults__ = (mb, None)
    out("[SELFTEST-PILOT] PRE-MERGE SIMULATION: K2's main-blob lookups resolve against %r in this process (the record's"
        " K2 reads main; a launch of record never runs under this flag)" % ref)


def selftest(out=print, part="all", main_ref=None):
    ck = Checks(out)
    tmp = tempfile.mkdtemp(prefix="archv2_pilot_selftest_")
    try:
        out("[SELFTEST-PILOT] python %s, -O %s; fixture under %s; no DB of record; no call" % (
            sys.version.split()[0], not __debug__, tmp))
        part_basics(ck)
        gen_path, ev_path = build_fixture(tmp)
        part_u_excluded(ck, gen_path, ev_path)
        s1path, _counts, chosen = part_stage1(ck, ev_path, tmp)
        if part in ("supply", "all"):
            part_supply(ck, ev_path, tmp, s1path, chosen)
        if part in ("all", "pool"):
            _load_pilot()
            if main_ref:
                premerge_main_ref(main_ref, out)
            _saved_transport = (PL.rr.AZURE_ENDPOINT, PL.rr.AZURE_KEY)
            # [2026-09-25] FIXTURE transport values (never posted to: every launch below injects a fake call_full), so
            # every launch executes the transport preflight
            _set_transport(FIXTURE_ENDPOINT, FIXTURE_KEY)
            ck.check("the registered pilot master; the registered Config is of record, a fixture Config is DEV",
                     PL.MASTER.endswith("5e406fce61daf51e0cf9b1963ab6e58606bda320") and PL.Config().record() and
                     not fixture_cfg().record())
            part_scheduler_identity(ck)
            part_k37_units(ck)
            rub = part_rubric(ck, gen_path, tmp)
            P.configure_rr()
            cfg, plan, loaded, order_ids, anchor = part_plan(ck, ev_path, s1path, rub, chosen)
            if part == "pool":
                exp = {"payload_anchor": anchor, "order_sha": plan.digests["order_sha"]}
                part_pool(ck, tmp, plan, loaded, order_ids, rub, exp)
                return _finish(ck, out)
            part_accounting(ck, tmp)
            part_launch_and_analyze(ck, tmp, ev_path, s1path, cfg, plan, loaded, order_ids, rub, anchor)
            exp = {"payload_anchor": anchor, "order_sha": plan.digests["order_sha"]}
            part_k1_journal(ck, tmp, plan, loaded, order_ids, rub, exp)
            part_k3_guard(ck, tmp, plan, loaded, order_ids, rub, exp)
            part_k2_pins(ck)
            part_k9_k10(ck, tmp, ev_path, s1path, gen_path)
            part_rulings_units(ck, plan)
            part_l7_units(ck)
            part_transport_probe(ck, tmp, plan, loaded, order_ids, rub, exp)
            part_forced_zero(ck, tmp, ev_path, s1path, cfg, plan, loaded, order_ids, rub, exp)
            part_pool(ck, tmp, plan, loaded, order_ids, rub, exp)
            part_branches(ck)
    finally:
        C.MUTANT = None
        if PL is not None:
            PL.MUTANT_TRANSPORT = None
            if "_saved_transport" in locals():
                _set_transport(*_saved_transport)
        for mod in (PL, A, OC, ACC):
            if mod is not None:
                mod.MUTANT = None
        _rmtree(tmp)
    return _finish(ck, out)


def _finish(ck, out):
    out("[SELFTEST-PILOT] %d checks, %d failed%s" % (ck.n, len(ck.fails), (": " + "; ".join(ck.fails)) if ck.fails else ""))
    return 1 if ck.fails else 0


def main(argv=None):
    argv = list(argv or [])
    part = argv[argv.index("--part") + 1] if "--part" in argv else "all"
    if part not in ("stage1", "supply", "all", "pool"):
        raise SystemExit("--part stage1|supply|all|pool")
    main_ref = argv[argv.index("--main-ref") + 1] if "--main-ref" in argv else None
    return selftest(print, part, main_ref)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
