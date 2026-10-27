"""K46-KEY-READ (RP04) -- the zero-call key read of the ARCH-V2-PILOT-K46 verdict store, by reference class (ZERO judge calls).

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-09-27 (before any code or call) — K46-KEY-READ:
on the content-closed v2 split, how often does the judge recipe as ARCH-V2-PILOT-K46 posted it pick the key-correct side of a
key-decidable match, separately for matches WITH a reference (ONE) and WITHOUT (NONE), and is ONE's accuracy at least 0.80?
(zero-call; the first content-closed key-based fidelity reading of that recipe; plan R-C)" (L21616-L21644 as of a357ef0;
resolve by the heading, the last bracket wins). BINDING RULING: docs/reviews/RULING_w0_seal_k46_reuse.md (c5a8cb6) R2, section
2 row RP04, section 3, W4-W9. This script is BUILT TO that text; its readings are listed under READINGS for the READY.

  python tools/analysis/k46_key_read.py --selftest    # synthetic store + sealed view under tempfile; opens NO DB of record
  python tools/analysis/k46_key_read.py --dry-run     # 0 calls, WRITES NOTHING, prints NO accuracy: pins, shas, the identity
                                                      #   gate (counts of record), classes, stems, components, preconditions
  python tools/analysis/k46_key_read.py --run         # the key read; write-once outcome

LAUNCH SEQUENCE: registration a357ef0 -> this script (engine-coder) -> the data-steward's census (key-decidable n per class x
anchor x v0-correct) bracketed in BEFORE the read, with the verdict line re-derived in the same pre-read bracket -> the
registrar's parameters below set by a delta of this script -> adversarial-reviewer READY -> run-operator --dry-run -> --run in
a W1 rule-7 window (W12) -> adversarial-reviewer on the numbers -> registrar; the stage-1 KEY-SEEN clause S1 then names this
outcome's commit (ruling R2). Run from the MAIN checkout; TAXOARENA_DATA_ROOT may point the inputs elsewhere.

PRECONDITIONS THAT REFUSE --run WHILE UNSET (PRECONDITIONS below; none is chosen here):
  census_bracket  the programme line / commit of the steward's census and the re-derived verdict line (registration Support
                  (a) and (f): "bracketed in BEFORE the read"; "the line is fixed BEFORE the read and never after").
  interval_form   C1's interval form. The registration fixes the cluster unit (CK-CLOSE components, B >= 2,000) and not the
                  interval: "normal" (point +- 1.96 x the component-clustered SE), "percentile" (2.5 / 97.5), or "both_agree"
                  (the BFCL-JUDGED-PILOT precedent, programme L11230 (d): normal of record, percentile beside, UNDETERMINED
                  when they disagree about the bar). AMBIGUITY K1.
  beta_len        the registration prints "beta_len DESCRIPTIVE with the DISAGREE comparator +0.32/1k" beside C1, but defines
                  no estimand, and the ruling's RP04 column list (section 2: store schedule / match_status; view is_correct,
                  reference.correct; "anything not listed is refused") admits no length column (verdict body_zlib and
                  response output_zlib are not listed). Only "STRUCK" (a registrar bracket striking it before the read) is
                  implemented; anything else refuses. AMBIGUITY K2 (unreachable as ruled).

[DELTA 2026-09-27, the engine-coder, after READY review e451753 and ruling R4 (programme L21831-L21846, 3fdc5d2); insertion
only] D1: the key SELECTs filter IN SQL with bound parameters: response rows only for (model IN the scheduled contestants,
seen_ck IN the scheduled variants); reference rows only for the ONE variants at the pinned vintage; the rows fetched are
printed and the selftest asserts them against an independent in-scope count on a fixture carrying out-of-scope rows (a
second unscheduled variant, a model outside the roster, a NONE reference, another vintage). R4 (ii): census_bracket,
interval_form (K1) and beta_len (K2) are NOT settable from the record and stay None (REPORTED; D3 / D4 / K2 / D5 brackets are
owed, not ruled). D6: beta_len is ("STRUCK", <the striking bracket>) and the outcome cites THAT bracket, never the census's.
[DELTA 2026-09-29 w0-delta3, the engine-coder, after delta-2 READY b2ad5ef C34-3; insertion only] PRECONDITIONS set from the
registrar's record of 2026-09-29 (e09e551): census_bracket = steward 5572465 with Support re-derived (ruling 8); interval_form
= "both_agree" (ruling 6); beta_len = ("STRUCK", e09e551 ruling 7). The selftest's "all None" check is retargeted to these
values (missing_preconditions finds none). LOW: the verdict print adds "CENSUS CHECK: the read's key-decidable ONE n / components
vs the census 544 / 160: EQUAL | MISMATCH" (flagged, deciding nothing; branches CENSUS.EQUAL / CENSUS.MISMATCH executed).
D7: --run refuses unless OMP / MKL / OPENBLAS are "1". D8: the identity gate asserts run_ids == ("ARCH-V2-PILOT-K46-run1",).
D2: the reviewer's K1-K5 are killed (C2 sign vs the naive per-class accuracies; the v0 split vs the fixture truth; every
identity row perturbed in turn refuses; a wrong-vintage reference refuses; ARENA12 vs a hand count).

GUARDS, executed and printed in every real mode:
  (1) the first printed line is the pool id pv2_41dbd3dbcd399df0.
  (2) the store experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db is opened by data_v2.ro.open_ro with
      expect_sha256 44724d25...27793 (sha256-bytes; mode=ro&immutable=1 after the -wal / -journal refusal), schema_id checked,
      re-hashed after the read; never written, never relaunched. The eval_view (sha256-bytes e35b7518...) is opened ONLY by
      data_v2.views.open_eval("arena") (as K46's --analyze did, outcome.py L201), re-hashed after the read.
  (3) KEY TRIPWIRE: store columns body_zlib / raw_text are never admitted; view columns output_zlib / gt_raw / answer_text /
      pred are never admitted; response.is_correct and reference.correct stay SEALED in --dry-run and until the identity gate
      has passed and the preconditions are set.
  (4) IDENTITY GATE (a FAILED PRECONDITION, refused before any accuracy is computed): scheduled 2,664; order verdicts 5,328,
      finish_reason stop and response_model grok-4-1-fast-non-reasoning on all 5,328; usable 2,661 (A 1,039 / B 1,022 /
      TIE 600); INVALID 3, all NONE; reference class scheduled ONE 818 / NONE 1,846 (usable NONE 1,843); ARENA12 263 usable of
      264; variants 566 (health 161 / math 405); the store sha.
  (5) THE KEY OF A MATCH SIDE is the is_correct of the response the judge was SHOWN, joined by (corpus_version mmlu-pro-v2,
      model = the contestant, seen_ck = the scheduled variant_id): exactly the loader's rule (judge_v2.loader L316-L324);
      a side with zero or several rows is REFUSED AND COUNTED (expected 0), never a (model, item) lookup where the last row
      wins (ruling section 3).
  (6) reference.correct is read ONLY for the ONE matches, by the scheduled reference_row_id "ref:<variant>|<vintage>|<key>"
      (vintage grok-reasoning-v0 asserted).
  (7) write-once outcome (mode "x") and a write-once read marker (refused if present).

INSTRUMENT. Key-decidable = exactly one side key-correct (W7). CONVENTION A (DECIDES): TIE / INVALID / NON_TERMINATED /
CONTENT_FILTER on a key-decidable match count WRONG and stay in the denominator; CONVENTION B (beside): committed verdicts
(A / B) only. Bootstraps, B = 2,000, each from numpy default_rng(42): CK-CLOSE component-clustered (DECIDES; components from
the view's side table of the variant's item, twins clustered, never dropped); stem-clustered (beside); i.i.d. over matches
(the DEFF denominator). Measured DEFF = var_component / var_iid, n_eff = n / DEFF, MDE80 = 2.80 x SE_component (K46's DEFF of
beta-hat 1.0785 is a different estimand and is never transported here).

CRITERIA (registered): C1 (THE criterion; convention A; the INTERVAL decides, the point decides nothing): ONE-class
key-decidable accuracy: HELD iff the component-clustered 95% lower bound >= 0.80; FAILED iff the upper bound < 0.80;
UNDETERMINED otherwise. C2 ONE - NONE (convention A): DESCRIPTIVE, a between-item contrast, a planning input only; it never
confirms or withdraws PAIR-NOREF. PRINTED BESIDE as registered (NONE accuracy; convention B for both classes; ONE split by
reference.correct; the difficulty-balance table; the ARENA12 sub-board with its [P-FAM] comparators; the p2dca-family
comparators with their [P-FAM] brackets verbatim; no r8 number). PREDICTIONS P1-P6 and FALSIFIER F1 as registered.

READINGS (stated, not silent):
  (a) "through the 86e88d2 unseal path" is read as: the same opener (open_eval("arena"), sha pinned) and the same column
      (response.is_correct, corpus_version named) as 86e88d2's unseal_key; its (model, item) lookup is NOT used, because the
      registration's HYGIENE and the ruling (section 3) bind the join to the shown response (guard 5).
  (b) The component-clustered bootstrap resamples the components of the class's key-decidable matches with replacement,
      unstratified (the registration names no stratum); C2 resamples the components of ONE and NONE key-decidable matches
      jointly.
  (c) A prediction "X [lo, hi]" is HELD iff the observed point lies in [lo, hi], endpoints inclusive. P5 is scored on the
      realised key-decidable ONE n; P6 on the measured component DEFF of C1.
  (d) The difficulty-balance table counts key-decidable matches per class x anchor x v0-correct; v0-correct is
      reference.correct and exists only for ONE (the ruling admits reference.correct on the ONE variants only); NONE rows
      print "not read".
  (e) The ARENA12 sub-board is the key-decidable matches whose two contestants are both in rubric_p8.ARENA12, read under
      both conventions; DESCRIPTIVE.
No model-edge count is computed, so no wrong(established) count arises (stated). Denominator: the key-decidable matches of
the 2,664 scheduled on 566 variants (health 161, math 405), printed per class, with its CK-CLOSE component count.
OUTPUT: experiment_results/archv2/k46_key_read/k46_key_read_outcome.txt (aggregates only, W11; write-once) and the marker
k46_key_read.READ_STARTED.
"""
import os, sys, io, json, math, argparse, tempfile, shutil, hashlib, stat, re, contextlib
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import v2_reader_guards as G
from data_v2 import ro as dv2ro
from data_v2 import views as dv2views

TEST_ID = "K46-KEY-READ"
PROG = "docs/judge_v2_program.md L21616-L21644 (as of a357ef0)"
RULING = "docs/reviews/RULING_w0_seal_k46_reuse.md (c5a8cb6)"
SPLIT_LABEL = "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
STORE_REL = os.path.join("experiment_results", "archv2", "pilot_k46", "pilot_k46_verdicts_run2.db")
STORE_SHA = "44724d25aa8653b49cef5ea85e99016f4e27f1c99819edc62073416eeec27793"
EVAL_REL = os.path.join("data_v2", SPLIT_LABEL, "eval_view_REG.db")
EVAL_SHA = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"
POOL, CV = "pv2_41dbd3dbcd399df0", "mmlu-pro-v2"
VINTAGE = "grok-reasoning-v0"
OUT_DIR = os.path.join(ROOT, "experiment_results", "archv2", "k46_key_read")
STORE_FORBIDDEN = ("body_zlib", "raw_text")
VIEW_FORBIDDEN = ("output_zlib", "gt_raw", "answer_text", "pred")
INTERVAL_FORMS = ("normal", "percentile", "both_agree")
# READY_w0_delta2 (b2ad5ef) C34-3: set from the registrar's record of 2026-09-29 (e09e551; rulings 6, 7, 8) and the steward's
# census 5572465 (docs/reviews/STEWARD_w0_counts.md section 3). Values, not choices of this script.
PRECONDITIONS = dict(
    census_bracket=("steward 5572465 (docs/reviews/STEWARD_w0_counts.md section 3: ONE 544 key-decidable in 160 CK-CLOSE"
                    " components, Kish m 4.934); Support (a)-(g) re-derived BEFORE the read in the registrar's record of"
                    " 2026-09-29 (e09e551), ruling 8"),
    interval_form="both_agree",                                                           # ruling 6 (K1)
    beta_len=("STRUCK", "the registrar's record of 2026-09-29 (e09e551), ruling 7 (K2: beta_len STRUCK before the read)"))
IDENTITY = dict(scheduled=2664, order_verdicts=5328, finish_stop=5328, response_model="grok-4-1-fast-non-reasoning",
                usable=2661, A=1039, B=1022, TIE=600, INVALID=3, invalid_none=3, one_sched=818, none_sched=1846,
                none_usable=1843, arena12_usable=263, arena12_sched=264, variants=566, anchors={"health": 161, "math": 405},
                run_ids=("ARCH-V2-PILOT-K46-run1",))  # D8: archv2_pilot_k46_outcome.txt L2 ("run ARCH-V2-PILOT-K46-run1")
REG = dict(B=2000, seed=42, bar=0.80, stems_one=174, stems_none=392)
RECIPE_LABEL = ("the recipe as posted by ARCH-V2-PILOT-K46: system turn d0c524bb... (= STACK-NORUBRIC's norubric system turn),"
                " GENERIC_RUBRIC 67f843eb..., E-J user turn, grok-4-1-fast-non-reasoning, dual order with TIE on flip; ONE ="
                " the cached grok-reasoning-v0 solve; NONE = no reference, while the system turn states that one exists (K5)")
POPULATION = ("2 of 14 anchors (health, math); 566 judged variants; k 37; N = 2; the filter on; the key-decidable subset;"
              " reference class fixed per item")
PFAM_LINES = (
    "ARENA12 comparators 0.848 / 0.916 [P-FAM (c) 2026-09-27: 0.848 / 0.916 are p2dca-family quantities — planning only"
    " (RULING_w0_p2dca_family.md)]",
    "0.852 (convention A, 4,507 matches) and 0.865 (a selection maximum) [P-FAM (c) 2026-09-27: 0.852 / 0.865 are"
    " p2dca-family quantities — planning only (RULING_w0_p2dca_family.md)]",
    "PAIR-NOREF 0.864 / 0.738 and CONSENSUS-FIT 0.922 / 0.657 / 0.226 [P-FAM 2026-09-27: p2dca judged family — history,"
    " not evidence (docs/reviews/RULING_w0_p2dca_family.md)]",
    "DISAGREE comparator +0.32/1k [P-FAM]; no r8 number (H3, R2 LRT) is printed",
    "comparators are printed beside, never pooled and never deciding (P-FAM use (3))")
# C34-2 / ruling 8 (registrar's record 2026-09-29, e09e551, "K46-KEY-READ SUPPORT RE-DERIVED AT THE CENSUS"; fixed BEFORE the
# read): PLAN is computed by plan_from_census from the steward's census (5572465): n = 544 key-decidable ONE matches in 160
# CK-CLOSE components, DEFF = Kish m-bar 4.934 DECLARED as the rho = 1 upper bound (cluster sizes only). The registered pilot
# (2.0 / 390) is printed beside as PLAN_PILOT. P6 stays scored on the post-read (measured) DEFF.
CENSUS = dict(n=544, components=160, kish=4.934, p=0.86, bar=0.80,
              source="census 5572465; Support re-derived in the registrar's record of 2026-09-29 (e09e551), ruling 8")


def plan_from_census(n, deff, p, bar):
    """Rule (f): SE = sqrt(p(1-p)/n) x sqrt(DEFF); MDE80 = 2.80 x SE; HELD is DESCRIPTIVE-ONLY when |p - bar| < MDE, else
    SCOREABLE; break-even DEFF = (|p - bar| / (2.80 x SE_iid))^2; the FAILED branch is scoreable against a true ONE <= bar - MDE."""
    se_iid = math.sqrt(p * (1.0 - p) / n)
    se = se_iid * math.sqrt(deff)
    mde = 2.80 * se
    gap = abs(p - bar)
    held = "DESCRIPTIVE-ONLY" if gap < mde else "SCOREABLE"
    be = (gap / (2.80 * se_iid)) ** 2
    return dict(deff=deff, n=n, n_eff=n / deff, se=se, mde=mde, breakeven=be, failed_below=bar - mde,
                verdict="%s for the HELD prediction at the census (%.2f lies %.3f from the bar %s MDE %.4f; break-even DEFF %.3f); "
                        "the FAILED branch is SCOREABLE against a true ONE <= %.4f"
                        % (held, p, gap, "<" if gap < mde else ">=", mde, be, bar - mde))


PLAN = plan_from_census(CENSUS["n"], CENSUS["kish"], CENSUS["p"], CENSUS["bar"])
PLAN_PILOT = dict(deff=2.0, n=390, n_eff=195, se=0.02485, mde=0.0696,
                  verdict="DESCRIPTIVE-ONLY for the HELD prediction at the declared pilot (break-even DEFF 1.487); the FAILED branch"
                          " is SCOREABLE against a true ONE <= 0.730")
PRED = dict(P1=(0.82, 0.90, 0.86), P2=(0.70, 0.80, 0.75), P3=(0.08, 0.15, 0.11), P4=(0.03, 0.12, None), P5=(330, 450, None),
            P6=(1.2, 2.5, None))
MUTANT = None
EVENTS = []
READ_COUNTS = {}    # D1: rows fetched by the last read_keys (response, reference)
BRANCH_NAMES = ("CENSUS.EQUAL", "CENSUS.MISMATCH", "GATE.PASS", "GATE.REFUSED", "FORM.normal", "FORM.percentile", "FORM.both_agree", "C1.HELD", "C1.FAILED",
                "C1.UNDETERMINED", "C1.UNDET_FORMS_DISAGREE", "BETA.STRUCK", "P1.HELD", "P1.FAILED", "P2.HELD", "P2.FAILED",
                "P3.HELD", "P3.FAILED", "P4.HELD", "P4.FAILED", "P5.HELD", "P5.FAILED", "P6.HELD", "P6.FAILED", "F1.FIRED",
                "F1.NOT_FIRED")
BR = G.Branches(BRANCH_NAMES)


def ev(x):
    EVENTS.append(x)


class Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    import rubric_p8
    return Cfg(store_path=os.path.join(DATA_ROOT, STORE_REL), store_sha=STORE_SHA, eval_path=os.path.join(DATA_ROOT, EVAL_REL),
               eval_sha=EVAL_SHA, pool=POOL, cv=CV, identity=dict(IDENTITY), reg=dict(REG), pre=dict(PRECONDITIONS),
               arena12=frozenset(rubric_p8.ARENA12), out=os.path.join(OUT_DIR, "k46_key_read_outcome.txt"),
               mark=os.path.join(OUT_DIR, "k46_key_read.READ_STARTED"))


def missing_preconditions(cfg):
    bad = []
    if not cfg.pre.get("census_bracket"):
        bad.append("census_bracket (the steward's census and the re-derived verdict line, bracketed in BEFORE the read)")
    if cfg.pre.get("interval_form") not in INTERVAL_FORMS:
        bad.append("interval_form (AMBIGUITY K1: C1's interval form, %s)" % (INTERVAL_FORMS,))
    bl = cfg.pre.get("beta_len")
    if not (isinstance(bl, tuple) and len(bl) == 2 and bl[0] == "STRUCK" and bool(bl[1])):
        bad.append("beta_len (AMBIGUITY K2: no estimand registered and no admitted length column; only 'STRUCK' by a registrar"
                   " bracket is implemented, as ('STRUCK', <the striking bracket>))")
    return bad


# ============================================================================================ reading
def open_store(cfg, say):
    before = G.sha256_file(cfg.store_path)
    say("  store %s | sha256-bytes BEFORE %s (%s) | sidecars: %s" % (cfg.store_path, before, "= the pinned sha" if before ==
                                                                      cfg.store_sha else "NOT the pinned %s" % cfg.store_sha,
                                                                      G.sidecar_line(cfg.store_path)))
    if before != cfg.store_sha:
        raise SystemExit("[PIN] store sha256-bytes %s != the pinned %s" % (before, cfg.store_sha))
    c = dv2ro.open_ro(cfg.store_path, expect_sha256=cfg.store_sha)
    sid = c.execute("SELECT value FROM run_meta WHERE key='schema_id'").fetchone()
    if sid is None or sid[0] != dv2ro.RUN_SCHEMA_ID:
        c.close()
        raise SystemExit("[STORE] %s is not a v2 verdict run DB (schema_id %r)" % (cfg.store_path, sid))
    ev("open:store")
    return G.KeyTripwire(c, STORE_FORBIDDEN, key=(), label="store"), before


def open_view(cfg, say):
    before = G.sha256_file(cfg.eval_path)
    say("  eval_view %s | sha256-bytes BEFORE %s (%s) | sidecars: %s" % (cfg.eval_path, before, "= the pinned sha" if before ==
                                                                          cfg.eval_sha else "NOT the pinned %s" % cfg.eval_sha,
                                                                          G.sidecar_line(cfg.eval_path)))
    if before != cfg.eval_sha:
        raise SystemExit("[PIN] eval_view sha256-bytes %s != the pinned %s" % (before, cfg.eval_sha))
    c = dv2views.open_eval("arena", cfg.eval_path, cfg.eval_sha)
    ev("open:view")
    return G.KeyTripwire(c, VIEW_FORBIDDEN, key=("is_correct", "correct"), label="eval_view(arena)"), before


def after(path, before, label, say):
    if MUTANT == "no_rehash":
        return True
    a = G.sha256_file(path)
    say("  %s sha256-bytes AFTER %s (%s)" % (label, a, "EQUAL to before" if a == before else "DIFFERS from before %s" % before))
    return a == before


def read_store(tw):
    run_ids = sorted({r for (r,) in tw.execute("SELECT DISTINCT run_id FROM schedule")})
    sched = tw.execute("SELECT run_id, match_id, presentation_order, draw_index, variant_id, stem_key, component_id, contestant_a,"
                       " contestant_b, reference_row_id, reference_vintage FROM schedule").fetchall()
    verd = tw.execute("SELECT run_id, match_id, presentation_order, draw_index, vote, finish_reason, response_model FROM"
                      " verdict").fetchall()
    status = tw.execute("SELECT run_id, match_id, draw_index, combined FROM match_status").fetchall()
    M = {}
    for r in sched:
        k = (r[0], r[1], r[3])
        m = M.setdefault(k, dict(run_id=r[0], match_id=r[1], draw=r[3], variant=r[4], stem=r[5], comp_s=r[6], a=r[7], b=r[8],
                                 ref=r[9], vintage=r[10], orders=set()))
        if (m["variant"], m["a"], m["b"], m["ref"]) != (r[4], r[7], r[8], r[9]):
            raise SystemExit("[STORE] match %s: its two order slots disagree on variant / contestants / reference" % (k,))
        m["orders"].add(r[2])
    for rid, mid, dr, comb in status:
        M[(rid, mid, dr)]["combined"] = comb
    return run_ids, M, verd


def view_structure(tw, cv):
    var_item = dict(tw.execute("SELECT variant_id, item_id FROM variant WHERE corpus_version=?", (cv,)).fetchall())
    side = {i: (c, d) for i, c, d in tw.execute("SELECT item_id, component_id, stratum_domain FROM side")}
    return var_item, side


def attach_structure(M, var_item, side):
    bad = 0
    for m in M.values():
        it = var_item.get(m["variant"])
        if it is None or it not in side:
            raise SystemExit("[VIEW] variant %s has no EVAL item in the view" % m["variant"])
        m["item"] = it; m["comp"] = side[it][0]; m["anchor"] = side[it][1].strip().lower()
        if m["comp_s"] is not None and m["comp_s"] != m["comp"]:
            bad += 1
        m["klass"] = "ONE" if m["ref"] is not None else "NONE"
    if bad:
        raise SystemExit("[VIEW] %d matches: the schedule's component_id differs from the view's side table" % bad)


def identity_gate(cfg, run_ids, M, verd, say, refuse=True):
    I = cfg.identity
    comb = Counter(m.get("combined", "PENDING") for m in M.values())
    usable = sum(comb[k] for k in ("A", "B", "TIE"))
    one_s = sum(1 for m in M.values() if m["klass"] == "ONE"); none_s = len(M) - one_s
    none_u = sum(1 for m in M.values() if m["klass"] == "NONE" and m.get("combined") in ("A", "B", "TIE"))
    inv_none = sum(1 for m in M.values() if m.get("combined") == "INVALID" and m["klass"] == "NONE")
    a12 = [m for m in M.values() if m["a"] in cfg.arena12 and m["b"] in cfg.arena12]
    a12u = sum(1 for m in a12 if m.get("combined") in ("A", "B", "TIE"))
    variants = {m["variant"]: m["anchor"] for m in M.values()}
    anc = Counter(variants.values())
    fr = Counter(v[5] for v in verd); rm = Counter(v[6] for v in verd)
    rows = [("scheduled matches", len(M), I["scheduled"]), ("order verdicts", len(verd), I["order_verdicts"]),
            ("finish_reason stop", fr.get("stop", 0), I["finish_stop"]),
            ("response_model %s" % I["response_model"], rm.get(I["response_model"], 0), I["order_verdicts"]),
            ("usable (A / B / TIE)", usable, I["usable"]), ("  A", comb["A"], I["A"]), ("  B", comb["B"], I["B"]),
            ("  TIE", comb["TIE"], I["TIE"]), ("INVALID", comb["INVALID"], I["INVALID"]), ("  INVALID with NONE", inv_none, I["invalid_none"]),
            ("NON_TERMINATED + CONTENT_FILTER + PENDING", comb["NON_TERMINATED"] + comb["CONTENT_FILTER"] + comb["PENDING"], 0),
            ("reference class ONE (scheduled)", one_s, I["one_sched"]), ("reference class NONE (scheduled)", none_s, I["none_sched"]),
            ("NONE usable", none_u, I["none_usable"]), ("ARENA12 scheduled", len(a12), I["arena12_sched"]),
            ("ARENA12 usable", a12u, I["arena12_usable"]), ("variants", len(variants), I["variants"])]
    rows += [("variants in %s" % a, anc.get(a, 0), n) for a, n in sorted(I["anchors"].items())]
    rows += [("variants outside health / math", sum(v for a, v in anc.items() if a not in I["anchors"]), 0),
             ("matches with both order slots", sum(1 for m in M.values() if m["orders"] == {1, 2}), I["scheduled"])]
    say("IDENTITY GATE (a FAILED PRECONDITION on any mismatch; evaluated before any key is read):")
    say("  run_id(s) in the schedule: %s (registered %s)" % (run_ids, list(I["run_ids"])))
    ok = tuple(run_ids) == tuple(I["run_ids"])                 # D8
    if not ok:
        say("  run_id MISMATCH")
    for name, got, want in rows:
        hit = got == want
        ok &= hit
        say("  %-44s %6d  (registered %6d)  %s" % (name, got, want, "OK" if hit else "MISMATCH"))
    say("  store sha256-bytes = the pinned %s: checked at the open" % cfg.store_sha[:16])
    if MUTANT == "gate_off":
        ok = True
    if not ok:
        BR.hit("GATE.REFUSED")
        if refuse:
            raise SystemExit("[IDENTITY-GATE] the store is not the object of record: refused before any accuracy")
        say("  -> IDENTITY GATE: FAIL (dry-run: printed, not refused)")
        return False
    BR.hit("GATE.PASS")
    say("  -> IDENTITY GATE: PASS")
    return True


def structure_lines(M, say):
    stems = defaultdict(set)
    for m in M.values():
        stems[m["stem"]].add(m["klass"])
    one_only = sum(1 for v in stems.values() if v == {"ONE"}); none_only = sum(1 for v in stems.values() if v == {"NONE"})
    mixed = sum(1 for v in stems.values() if len(v) > 1)
    comps = defaultdict(set)
    for m in M.values():
        comps[m["klass"]].add(m["comp"])
    say("  stems: %d; ONE-only %d (R-C 174), NONE-only %d (R-C 392), mixed %d | CK-CLOSE components carrying ONE matches %d, NONE"
        " matches %d | matches per ONE stem %.2f" % (len(stems), one_only, none_only, mixed, len(comps["ONE"]), len(comps["NONE"]),
                                                     sum(1 for m in M.values() if m["klass"] == "ONE") / max(1, one_only)))
    return one_only, none_only, mixed


def read_keys(tw, cv, M, vintage):
    """THE KEY READ. Side key = the is_correct of the shown response: (cv, model = contestant, seen_ck = variant); zero or
    several rows -> the side is refused and counted. reference.correct for ONE matches only."""
    need = set()
    for m in M.values():
        need.add((m["a"], m["variant"])); need.add((m["b"], m["variant"]))
    rows = defaultdict(list)
    fetched = dict(response=0, reference=0)
    items = {m["item"] for m in M.values()}
    if MUTANT == "model_item_join":
        byitem = {}
        vi = {m["variant"]: m["item"] for m in M.values()}
        for mo, sc, it, c in tw.execute("SELECT model, seen_ck, item_id, is_correct FROM response WHERE corpus_version=?", (cv,)):
            byitem[(mo, it)] = int(c)                                   # the last row wins (the defect)
        for mo, v in need:
            if (mo, vi[v]) in byitem:
                rows[(mo, v)] = [byitem[(mo, vi[v])]]
    else:
        # D1 (READY e451753; ruling R4 (i)): only the scheduled contestants' rows on the scheduled variants reach the process
        mods = sorted({mo for mo, _ in need}); vars_ = sorted({v for _, v in need})
        if MUTANT == "sql_unfiltered":
            got = tw.execute("SELECT model, seen_ck, item_id, is_correct FROM response WHERE corpus_version=?", (cv,)).fetchall()
        else:
            got = []
            for s0 in range(0, len(vars_), 500):
                ch = vars_[s0:s0 + 500]
                got.extend(tw.execute("SELECT model, seen_ck, item_id, is_correct FROM response WHERE corpus_version=? AND model IN (%s)"
                                      " AND seen_ck IN (%s)" % (",".join("?" * len(mods)), ",".join("?" * len(ch))), [cv] + mods + ch))
        fetched["response"] = len(got)
        for mo, sc, it, c in got:
            if (mo, sc) in need:
                rows[(mo, sc)].append(int(c))
    key = {}
    refused = Counter()
    for k in need:
        v = rows.get(k, [])
        if len(v) == 1 or (MUTANT == "multi_side_used" and v):
            key[k] = v[0]
        else:
            refused["zero rows" if not v else "several rows"] += 1
    refs = {}
    want = {m["ref"] for m in M.values() if m["klass"] == "ONE"}
    parsed = {}
    for r in want:
        if not r.startswith("ref:"):
            raise SystemExit("[REF] reference_row_id %r is not ref:<variant>|<vintage>|<key>" % r)
        v, vt, sk = r[4:].split("|", 2)
        if vt != vintage:
            raise SystemExit("[REF] reference vintage %r is not %s" % (vt, vintage))
        parsed[(v, vt, sk)] = r
    one_vars = sorted({v for (v, _vt, _sk) in parsed})
    got = []
    for s0 in range(0, max(1, len(one_vars)), 500):
        ch = one_vars[s0:s0 + 500]
        if not ch:
            break
        got.extend(tw.execute("SELECT variant_id, vintage, source_key, correct FROM reference WHERE corpus_version=? AND vintage=?"
                              " AND variant_id IN (%s)" % ",".join("?" * len(ch)), [cv, vintage] + ch))
    fetched["reference"] = len(got)
    for v, vt, sk, c in got:
        if (v, vt, sk) in parsed:
            refs[parsed[(v, vt, sk)]] = None if c is None else int(c)
    missing_ref = len(want - set(refs))
    READ_COUNTS.clear(); READ_COUNTS.update(fetched)
    return key, refused, refs, missing_ref


def classify(M, key, refs):
    """Per match: kd (key-decidable), key_side ('A' / 'B'), right_A (convention A), committed, right_B, v0."""
    out = []
    for m in sorted(M.values(), key=lambda x: (x["run_id"], x["match_id"], x["draw"])):
        ka, kb = key.get((m["a"], m["variant"])), key.get((m["b"], m["variant"]))
        r = dict(m=m, klass=m["klass"], comp=m["comp"], stem=m["stem"], anchor=m["anchor"],
                 v0=refs.get(m["ref"]) if m["klass"] == "ONE" else None,
                 a12=None)
        if MUTANT == "class_swap":
            r["klass"] = "NONE" if m["klass"] == "ONE" else "ONE"
        if ka is None or kb is None:
            r["kd"] = False; r["refused_side"] = True
        else:
            r["refused_side"] = False
            r["kd"] = (ka + kb == 1)
        if r["kd"]:
            side = "A" if ka == 1 else "B"
            comb = m.get("combined")
            r["committed"] = comb in ("A", "B")
            if MUTANT == "tie_right" and comb == "TIE":
                r["right_A"] = 1
            else:
                r["right_A"] = int(comb == side)
            r["right_B"] = int(comb == side) if r["committed"] else None
            r["drop_A"] = MUTANT == "conv_a_drops_invalid" and comb in ("INVALID", "NON_TERMINATED", "CONTENT_FILTER")
        out.append(r)
    return out


# ============================================================================================ statistics
def boot_acc(rows, conv, unit, B, seed):
    """-> (point, replicate array) for the accuracy over rows (conv 'A' or 'B') resampling `unit` ('comp', 'stem', 'iid')."""
    if conv == "A":
        rows = [r for r in rows if not r.get("drop_A")]
        y = np.array([r["right_A"] for r in rows], dtype=np.float64)
    else:
        rows = [r for r in rows if r["committed"]]
        y = np.array([r["right_B"] for r in rows], dtype=np.float64)
    n = len(rows)
    if n == 0:
        return float("nan"), np.full(B, np.nan), 0, 0
    if unit == "iid":
        g = np.arange(n)
    else:
        keys = sorted(set(r[unit] for r in rows)); pos = {k: i for i, k in enumerate(keys)}
        g = np.array([pos[r[unit]] for r in rows], dtype=np.int64)
    ng = int(g.max()) + 1
    s = np.bincount(g, weights=y, minlength=ng); c = np.bincount(g, minlength=ng).astype(np.float64)
    rng = np.random.default_rng(seed)
    reps = np.empty(B)
    for b in range(B):
        w = np.bincount(rng.integers(0, ng, ng), minlength=ng)
        reps[b] = (w @ s) / (w @ c)
    return float(y.mean()), reps, n, ng


def boot_diff(rows_one, rows_none, B, seed):
    """C2: ONE - NONE (convention A), components of both classes resampled jointly."""
    rows = [("ONE", r) for r in rows_one] + [("NONE", r) for r in rows_none]
    keys = sorted(set(r["comp"] for _, r in rows)); pos = {k: i for i, k in enumerate(keys)}
    ng = len(keys)
    s = {k: np.zeros(ng) for k in ("ONE", "NONE")}; c = {k: np.zeros(ng) for k in ("ONE", "NONE")}
    for k, r in rows:
        s[k][pos[r["comp"]]] += r["right_A"]; c[k][pos[r["comp"]]] += 1
    pt = s["ONE"].sum() / c["ONE"].sum() - s["NONE"].sum() / c["NONE"].sum()
    rng = np.random.default_rng(seed)
    reps = np.empty(B)
    for b in range(B):
        w = np.bincount(rng.integers(0, ng, ng), minlength=ng)
        reps[b] = (w @ s["ONE"]) / (w @ c["ONE"]) - (w @ s["NONE"]) / (w @ c["NONE"])
    return float(pt), reps


def _sd(x):
    x = np.asarray(x, dtype=np.float64); x = x[np.isfinite(x)]
    return float(np.std(x, ddof=1)) if x.size > 1 and float(np.ptp(x)) > 0 else 0.0


def intervals(pt, reps):
    se = _sd(reps)
    pc = tuple(float(v) for v in np.nanpercentile(reps, [2.5, 97.5]))
    return dict(point=pt, se=se, n_lo=pt - 1.96 * se, n_hi=pt + 1.96 * se, p_lo=pc[0], p_hi=pc[1])


def c1_word(iv, form, bar):
    """HELD iff lower >= bar; FAILED iff upper < bar; UNDETERMINED otherwise; both_agree: the two forms must agree."""
    ge = (lambda a, b: a > b) if MUTANT == "bar_strict" else (lambda a, b: a >= b)
    def one(lo, hi):
        if G.as_bool(ge(lo, bar)):
            return "HELD"
        if G.as_bool(hi < bar):
            return "FAILED"
        return "UNDETERMINED"
    if form == "normal":
        BR.hit("FORM.normal"); return one(iv["n_lo"], iv["n_hi"]), None
    if form == "percentile":
        BR.hit("FORM.percentile"); return one(iv["p_lo"], iv["p_hi"]), None
    BR.hit("FORM.both_agree")
    a, b = one(iv["n_lo"], iv["n_hi"]), one(iv["p_lo"], iv["p_hi"])
    return (a, None) if a == b else ("UNDETERMINED", (a, b))


def in_range(x, lo, hi):
    return G.as_bool(x == x and lo <= x <= hi)


def verdict_lines(st):
    L = []
    say = L.append
    one, form = st["ONE_A"], st["form"]
    say("")
    say("=== VERDICTS ===")
    say("RECIPE (W5, verbatim): " + RECIPE_LABEL)
    say("POPULATION (W6): " + POPULATION)
    ivd = st["ONE_A_iv"]
    say("C1 ONE-class key-decidable accuracy (convention A) = %.4f on %d key-decidable ONE matches in %d CK-CLOSE components |"
        " component-clustered (DECIDING unit; B %d) normal [%.4f, %.4f] (SE %.4f), percentile [%.4f, %.4f] | interval form of"
        " record: %s | bar 0.80" % (one[0], one[1], one[2], st["B"], ivd["n_lo"], ivd["n_hi"], ivd["se"], ivd["p_lo"], ivd["p_hi"], form))
    ivs = st["ONE_A_stem"]
    say("    beside: stem-clustered normal [%.4f, %.4f] (SE %.4f), percentile [%.4f, %.4f]; i.i.d. SE %.4f"
        % (ivs["n_lo"], ivs["n_hi"], ivs["se"], ivs["p_lo"], ivs["p_hi"], st["ONE_A_iid_se"]))
    d = st["deff"]
    say("    SUPPORT (measured): SE_component %.4f | SE_iid %.4f -> DEFF %.3f, n_eff %.0f, MDE80 = 2.80 x SE = %.4f"
        % (ivd["se"], st["ONE_A_iid_se"], d, st["n_eff"], 2.80 * ivd["se"]))
    say("    SUPPORT (plan of record, at the census; ruling 8): DEFF %.3f (Kish m-bar, DECLARED rho = 1 upper bound), n %d in %d "
        "components, n_eff %.1f, SE %.5f, MDE80 %.4f; %s" % (PLAN["deff"], PLAN["n"], CENSUS["components"], PLAN["n_eff"], PLAN["se"],
                                                            PLAN["mde"], PLAN["verdict"]))
    say("    beside (the registered pilot, deciding nothing): DEFF %.1f, n %d, n_eff %d, SE %.5f, MDE80 %.4f; %s"
        % (PLAN_PILOT["deff"], PLAN_PILOT["n"], PLAN_PILOT["n_eff"], PLAN_PILOT["se"], PLAN_PILOT["mde"], PLAN_PILOT["verdict"]))
    same = G.as_bool(one[1] == CENSUS["n"] and one[2] == CENSUS["components"])            # C34-3 LOW: flagged, deciding nothing
    BR.hit("CENSUS.EQUAL" if same else "CENSUS.MISMATCH")
    say("    CENSUS CHECK: the read's key-decidable ONE n %d in %d components vs the census %d in %d: %s" % (
        one[1], one[2], CENSUS["n"], CENSUS["components"], "EQUAL" if same else
        "MISMATCH (the plan of record was derived at the census; a READY defect to report to the registrar)"))
    w, dis = c1_word(ivd, form, REG["bar"])
    if dis is not None:
        BR.hit("C1.UNDET_FORMS_DISAGREE")
        say("  C1 -> UNDETERMINED (the normal form reads %s and the percentile form %s: they disagree about the bar)" % dis)
    else:
        BR.hit("C1." + w)
        say("  C1 -> %s (HELD iff the lower bound >= 0.80; FAILED iff the upper bound < 0.80)" % w)
    c2 = st["C2"]
    say("C2 ONE - NONE (convention A; DESCRIPTIVE, a between-item contrast, a planning input only; it never confirms or withdraws"
        " PAIR-NOREF) = %+.4f | component-clustered normal [%+.4f, %+.4f], percentile [%+.4f, %+.4f]" % (
            c2["point"], c2["n_lo"], c2["n_hi"], c2["p_lo"], c2["p_hi"]))
    say("PRINTED BESIDE (declared; deciding nothing):")
    for name in ("NONE_A", "ONE_B", "NONE_B"):
        iv = st[name + "_iv"]; x = st[name]
        say("  %-7s accuracy %.4f on %d matches (%d components) | component-clustered normal [%.4f, %.4f], percentile [%.4f, %.4f]"
            % (name, x[0], x[1], x[2], iv["n_lo"], iv["n_hi"], iv["p_lo"], iv["p_hi"]))
    for v0, x in sorted(st["one_by_v0"].items(), key=lambda kv: str(kv[0])):
        say("  ONE split by the reference's own key-correctness (reference.correct = %s): convention A %.4f on %d, convention B"
            " %.4f on %d" % (v0, x[0], x[1], x[2], x[3]))
    say("  DIFFICULTY-BALANCE TABLE (key-decidable matches per class x anchor x v0-correct; v0 read for ONE only):")
    for k, n in sorted(st["balance"].items(), key=lambda kv: tuple(str(z) for z in kv[0])):
        say("    %-5s %-8s v0-correct %-9s %5d" % (k[0], k[1], "not read" if k[0] == "NONE" else k[2], n))
    a = st["a12"]
    say("  ARENA12 sub-board (both contestants in ARENA12; DESCRIPTIVE): convention A %.4f on %d key-decidable, convention B"
        " %.4f on %d" % (a[0], a[1], a[2], a[3]))
    for l in PFAM_LINES:
        say("    " + l)
    BR.hit("BETA.STRUCK")
    say("  beta_len: NOT COMPUTED (struck before the read by the registrar's bracket %r; AMBIGUITY K2)" % st["beta_bracket"])
    say("PREDICTIONS (HELD iff the observed point lies in the registered interval, endpoints included):")
    for p, x, what in (("P1", one[0], "ONE(A)"), ("P2", st["NONE_A"][0], "NONE(A)"), ("P3", c2["point"], "ONE - NONE (A), scored descriptively"),
                       ("P4", st["ONE_B"][0] - one[0], "B - A for ONE"), ("P5", st["ONE_A"][1], "the key-decidable ONE n"),
                       ("P6", d, "the measured component DEFF of C1")):
        lo, hi, c = PRED[p]
        ww = "HELD" if in_range(x, lo, hi) else "FAILED"
        BR.hit("%s.%s" % (p, ww))
        say("  %s %s predicted %s[%s, %s], observed %s -> %s" % (p, what, ("%s " % c) if c is not None else "", lo, hi,
                                                                 ("%.4f" % x) if isinstance(x, float) else x, ww))
    say("  (registered: C1 HELD 0.45 / UNDETERMINED 0.45 / FAILED 0.10; realised: %s)" % ("UNDETERMINED" if dis else w))
    say("FALSIFIER (H4):")
    if (dis is None and w == "FAILED"):
        BR.hit("F1.FIRED")
        say("  F1 FIRED (C1 FAILED): the planning use of the p2dca-family referenced fidelity (0.852 at board scale; P-FAM use"
            " (3)) is WITHDRAWN as a figure for the recipe as K46 posted it; RP19 / RP20 / any v2 board are re-priced before any"
            " paid call. C2 withdraws nothing.")
    else:
        BR.hit("F1.NOT_FIRED")
        say("  F1 NOT FIRED (C1 %s); nothing is promoted (a content-closed outcome may withdraw a planning prior, never promote"
            " it)" % ("UNDETERMINED" if dis else w))
    return L, ("UNDETERMINED" if dis else w)


# ============================================================================================ the mode
def header(cfg, say):
    say("POOL %s (%s; %s; the first line of every mode)" % (cfg.pool, TEST_ID, cfg.cv))
    say("%s | registration %s | ruling %s" % (TEST_ID, PROG, RULING))
    for f in (os.path.abspath(__file__), G.__file__):
        say("  " + G.identity_line(f))
    say("  MUTANT %r (must be None in every real mode)" % MUTANT)
    say("  WORDS (W1): the store's split is 'content-closed under CK-CLOSE-v2 (residual disclosed: 1,142 P pairs in the"
        " 15-19-token band covering 422 EVAL items, 1,096 of the pairs BBH; O 20)'. Never 'STACK-v2 fidelity'; never 'the v2"
        " recipe's fidelity' in general (B7 item 6).")
    say("PRECONDITIONS (None REFUSES --run):")
    for k in ("census_bracket", "interval_form", "beta_len"):
        say("  %-15s %r" % (k, cfg.pre.get(k)))
    miss = missing_preconditions(cfg)
    say("  -> %s" % ("ALL SET" if not miss else "%d UNSET: %s" % (len(miss), "; ".join(miss))))
    return miss


def write_outcome(path, text):
    if MUTANT == "write_w":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return path
    return G.write_once(path, text)


def mode(cfg, dry):
    lines = []
    def say(s):
        lines.append(s); print(s, flush=True)
    miss = header(cfg, say)
    if not dry:
        if miss:
            raise SystemExit("[PRECONDITION] --run refused: %s" % "; ".join(miss))
        for p in (cfg.out, cfg.mark):
            if os.path.exists(p):
                raise SystemExit("[WRITE-ONCE] %s exists; refused before any read" % p)
    st_tw, s_before = open_store(cfg, say)
    run_ids, M, verd = read_store(st_tw)
    st_tw.close()
    ok_s = after(cfg.store_path, s_before, "store", say)
    vw, v_before = open_view(cfg, say)
    var_item, side = view_structure(vw, cfg.cv)
    attach_structure(M, var_item, side)
    gate = identity_gate(cfg, run_ids, M, verd, say, refuse=not dry)
    structure_lines(M, say)
    if dry:
        if MUTANT == "dry_reads_key":
            vw.execute("SELECT is_correct FROM response LIMIT 1")
        vw.close()
        after(cfg.eval_path, v_before, "eval_view", say)
        say("PLANNED: B = %d, default_rng(%d), component-clustered (deciding) / stem-clustered / i.i.d.; outputs %s, %s (write-once)"
            % (cfg.reg["B"], cfg.reg["seed"], cfg.out, cfg.mark))
        say("DRY-RUN: identity gate %s; no key column was selected (view statements %d, all key-free); no accuracy printed."
            % ("PASS" if gate else "FAIL", len(vw.log)))
        return None
    ev("gate")
    if MUTANT != "marker_off":
        G.read_marker(cfg.mark, "K46-KEY-READ: the key read started\n")
    vw.unseal("K46-KEY-READ: identity gate passed; preconditions set (census %s)" % cfg.pre["census_bracket"])
    ev("key")
    key, refused, refs, missing_ref = read_keys(vw, cfg.cv, M, VINTAGE)
    vw.close()
    ok_v = after(cfg.eval_path, v_before, "eval_view", say)
    say("KEY JOIN (the shown response: model = contestant, seen_ck = the scheduled variant): %d sides joined; refused %s (expected"
        " 0); ONE references read %d, missing %d; rows fetched (filtered in SQL): response %d, reference %d"
        % (len(key), dict(refused) or 0, len(refs), missing_ref, READ_COUNTS.get("response", 0), READ_COUNTS.get("reference", 0)))
    rows = classify(M, key, refs)
    n_ref_side = sum(1 for r in rows if r["refused_side"])
    kd = [r for r in rows if r["kd"]]
    say("  matches with a refused side (not key-decidable, counted): %d | key-decidable %d of %d scheduled" % (n_ref_side, len(kd), len(rows)))
    B, seed = cfg.reg["B"], cfg.reg["seed"]
    one = [r for r in kd if r["klass"] == "ONE"]; none = [r for r in kd if r["klass"] == "NONE"]
    st = dict(B=B, form=cfg.pre["interval_form"], beta_bracket=cfg.pre["beta_len"][1])   # D6: the STRIKING bracket
    for name, rr, conv in (("ONE_A", one, "A"), ("NONE_A", none, "A"), ("ONE_B", one, "B"), ("NONE_B", none, "B")):
        unit = "comp" if MUTANT != "stem_decides" or name != "ONE_A" else "stem"
        pt, reps, n, ng = boot_acc(rr, conv, unit, B, seed)
        st[name] = (pt, n, ng); st[name + "_iv"] = intervals(pt, reps)
    pt, reps, n, ng = boot_acc(one, "A", "stem", B, seed); st["ONE_A_stem"] = intervals(pt, reps)
    pt, reps, n, ng = boot_acc(one, "A", "iid", B, seed); st["ONE_A_iid_se"] = _sd(reps)
    vc = st["ONE_A_iv"]["se"] ** 2; vi = st["ONE_A_iid_se"] ** 2
    st["deff"] = (vc / vi) if vi > 0 else float("nan")
    if MUTANT == "deff_inverse" and vc > 0:
        st["deff"] = vi / vc
    st["n_eff"] = st["ONE_A"][1] / st["deff"] if st["deff"] == st["deff"] and st["deff"] > 0 else float("nan")
    pt, reps = boot_diff(one, none, B, seed); st["C2"] = intervals(pt, reps)
    byv = {}
    for v0 in sorted(set(r["v0"] for r in one), key=str):
        sub = [r for r in one if r["v0"] == v0]
        a = [r["right_A"] for r in sub]; b = [r["right_B"] for r in sub if r["committed"]]
        byv[v0] = (float(np.mean(a)) if a else float("nan"), len(a), float(np.mean(b)) if b else float("nan"), len(b))
    st["one_by_v0"] = byv
    st["balance"] = Counter((r["klass"], r["anchor"], r["v0"] if r["klass"] == "ONE" else None) for r in kd)
    a12 = [r for r in kd if r["m"]["a"] in cfg.arena12 and r["m"]["b"] in cfg.arena12]
    a12b = [r for r in a12 if r["committed"]]
    st["a12"] = (float(np.mean([r["right_A"] for r in a12])) if a12 else float("nan"), len(a12),
                 float(np.mean([r["right_B"] for r in a12b])) if a12b else float("nan"), len(a12b))
    L, word = verdict_lines(st)
    for l in L:
        say(l)
    if not (ok_s and ok_v):
        write_outcome(cfg.out.replace(".txt", "_VOID.txt"), "\n".join(lines) + "\n[VOID] a sha differs after the read\n")
        raise SystemExit("[PIN] a sha differs after the read: written to _VOID, not to the file of record")
    write_outcome(cfg.out, "\n".join(lines) + "\n")
    print("OUTCOME written write-once: %s" % cfg.out)
    return dict(st=st, word=word, rows=rows, refused=refused, text="\n".join(lines), fetched=dict(READ_COUNTS))


# ============================================================================================ selftest
def _mk_fixture(tmp, name, spec_mut=None):
    """A synthetic verdict store (the real DDL of data_v2.verdicts) and a sealed synthetic eval view."""
    from data_v2 import verdicts as dv2v
    d = os.path.join(tmp, name); os.makedirs(d)
    rs = np.random.RandomState(5)
    models = ["m%02d" % i for i in range(8)]
    arena = frozenset(models[:4])
    items = []
    for anchor, n in (("health", 30), ("math", 50)):
        for j in range(n):
            iid = "i:%s%03d" % (anchor[0], j)
            comp = "c:%s%03d" % (anchor[0], j // 2 * 2)             # twins: pairs of items share a component
            klass = "ONE" if (j // 2) % 3 == 0 else "NONE"          # twins share a component and a class
            items.append(dict(id=iid, var="v:" + iid[2:], comp=comp, anchor=anchor, klass=klass, stem="s:" + iid[2:]))
    # the view
    vp = os.path.join(d, "eval.db")
    c = dv2ro.create_new(vp)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT INTO meta VALUES ('view_kind', 'eval')")
    c.execute("CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT, side TEXT, stratum_source TEXT, stratum_domain TEXT, corpora TEXT)")
    c.execute("CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, PRIMARY KEY (corpus_version, variant_id))")
    c.execute("CREATE TABLE response (corpus_version TEXT, response_id TEXT, model TEXT, legacy_qid INTEGER, seen_ck TEXT,"
              " item_id TEXT, is_correct INTEGER, output_zlib BLOB, gt_raw TEXT, pred TEXT, PRIMARY KEY (corpus_version, response_id))")
    c.execute("CREATE TABLE reference (corpus_version TEXT, variant_id TEXT, vintage TEXT, source_key TEXT, item_id TEXT, correct"
              " INTEGER, PRIMARY KEY (corpus_version, variant_id, vintage, source_key))")
    truth = {}
    v0truth = {}
    k = 0
    for it in items:
        c.execute("INSERT INTO side VALUES (?,?,?,?,?,?)", (it["id"], it["comp"], "EVAL", "MMLU_PRO", it["anchor"].title(), "mmlu"))
        c.execute("INSERT INTO variant VALUES (?,?,?)", ("mmlu", it["var"], it["id"]))
        for mo in models:
            k += 1
            v = int(rs.rand() < 0.5)
            truth[(mo, it["var"])] = v
            c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, mo, k, it["var"], it["id"], v, b"z", "g", "p"))
        # a SECOND variant of the same item for model m00 with the opposite key (the (model, item) last-wins trap)
        k += 1
        c.execute("INSERT INTO variant VALUES (?,?,?)", ("mmlu", it["var"] + "b", it["id"]))
        c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, "m00", k, it["var"] + "b", it["id"],
                                                                       1 - truth[("m00", it["var"])], b"z", "g", "p"))
        if it["klass"] == "ONE":
            v0truth[it["var"]] = int(rs.rand() < 0.8)
            c.execute("INSERT INTO reference VALUES (?,?,?,?,?,?)", ("mmlu", it["var"], VINTAGE, "sk", it["id"], v0truth[it["var"]]))
    # D1 out-of-scope rows: a model outside the roster on a scheduled variant; a NONE variant's reference; another vintage
    k += 1
    c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, "zz_out", k, items[1]["var"], items[1]["id"], 1, b"z", "g", "p"))
    none_it = next(it for it in items if it["klass"] == "NONE")
    one_it = next(it for it in items if it["klass"] == "ONE")
    c.execute("INSERT INTO reference VALUES (?,?,?,?,?,?)", ("mmlu", none_it["var"], VINTAGE, "sk", none_it["id"], 1))
    c.execute("INSERT INTO reference VALUES (?,?,?,?,?,?)", ("mmlu", one_it["var"], "other-vintage", "sk", one_it["id"], 0))
    # one multi-response side (model m07, first ONE item): two rows on the same variant -> refused and counted
    multi_item = items[0]
    k += 1
    c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, "m07", k, multi_item["var"], multi_item["id"], 1, b"z", "g", "p"))
    c.commit()
    vsha = dv2ro.seal(c, vp, "selftest eval view")["sha256_bytes"]
    # the store
    sp = os.path.join(d, "store.db")
    s = dv2ro.create_new(sp)
    s.executescript(dv2v.DDL)
    s.execute("INSERT INTO run_meta VALUES ('schema_id', ?)", (dv2ro.RUN_SCHEMA_ID,))
    matches = []
    mid = 0
    for it in items:
        for rep_ in range(3):
            a, b = rs.choice(len(models), 2, replace=False)
            if it is items[0] and rep_ == 0:
                a, b = 7, 1                                     # the multi-response side (m07 on items[0]) is scheduled
            mid += 1
            matches.append(dict(mid="M%04d" % mid, it=it, a=models[a], b=models[b]))
    for m in matches:
        it = m["it"]
        ref = ("ref:%s|%s|sk" % (it["var"], VINTAGE)) if it["klass"] == "ONE" else None
        for order in (1, 2):
            first, second = (m["a"], m["b"]) if order == 1 else (m["b"], m["a"])
            s.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                "RUN", m["mid"], order, 0, it["var"], it["stem"], it["comp"], m["a"], m["b"], first, second, "h1", "h2", ref,
                VINTAGE if ref else None, None))
    votes = []
    for m in matches:
        it = m["it"]
        ka, kb = truth[(m["a"], it["var"])], truth[(m["b"], it["var"])]
        r = rs.rand()
        if r < 0.03:
            comb = ("INVALID", "INVALID")
        elif r < 0.25:
            comb = ("A", "B")                                      # a flip -> TIE
        else:
            good = "A" if ka >= kb else "B"
            pick = good if rs.rand() < (0.85 if it["klass"] == "ONE" else 0.7) else ("B" if good == "A" else "A")
            comb = (pick, pick)
        m["comb"] = "INVALID" if comb[0] == "INVALID" else ("TIE" if comb[0] != comb[1] else comb[0])
        for order, vc in ((1, comb[0]), (2, comb[1])):
            if vc in ("A", "B"):
                shown_first = m["a"] if order == 1 else m["b"]
                target = m["a"] if vc == "A" else m["b"]
                vote = "FIRST" if target == shown_first else "SECOND"
            else:
                vote = vc
            ref = ("ref:%s|%s|sk" % (it["var"], VINTAGE)) if it["klass"] == "ONE" else None
            s.execute("INSERT INTO verdict (run_id, match_id, presentation_order, draw_index, vote, raw_text, parse_version, payload_sha256,"
                      " body_zlib, body_codec, judge_requested, provider, response_model, finish_reason, max_tokens, temperature_sent,"
                      " temperature_label, content_filter, n_attempts, prompt_template_blob, script_blob, combiner_blob,"
                      " reference_row_id, reference_vintage, stem_key, pool_id, created_at) VALUES"
                      " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                          "RUN", m["mid"], order, 0, vote, "raw", "p1", "ps", b"z", "zlib", "j", "prov", IDENTITY["response_model"], "stop",
                          8192, None, "omitted", 0, 1, "pt", "sb", "cb", ref, VINTAGE if ref else None, it["stem"], "pv", "t"))
    s.commit()
    s.close()
    os.chmod(sp, stat.S_IREAD)
    ssha = G.sha256_file(sp)
    comb = Counter(m["comb"] for m in matches)
    one_s = sum(1 for m in matches if m["it"]["klass"] == "ONE")
    ident = dict(scheduled=len(matches), order_verdicts=2 * len(matches), finish_stop=2 * len(matches),
                 response_model=IDENTITY["response_model"], usable=comb["A"] + comb["B"] + comb["TIE"], A=comb["A"], B=comb["B"],
                 TIE=comb["TIE"], INVALID=comb["INVALID"],
                 invalid_none=sum(1 for m in matches if m["comb"] == "INVALID" and m["it"]["klass"] == "NONE"),
                 one_sched=one_s, none_sched=len(matches) - one_s,
                 none_usable=sum(1 for m in matches if m["it"]["klass"] == "NONE" and m["comb"] != "INVALID"),
                 arena12_sched=sum(1 for m in matches if m["a"] in arena and m["b"] in arena),
                 arena12_usable=sum(1 for m in matches if m["a"] in arena and m["b"] in arena and m["comb"] != "INVALID"),
                 variants=len(items), anchors={"health": 30, "math": 50}, run_ids=("RUN",))
    out = os.path.join(d, "out")
    cfg = Cfg(store_path=sp, store_sha=ssha, eval_path=vp, eval_sha=vsha, pool="pv_m", cv="mmlu", identity=ident,
              reg=dict(REG, B=300), pre=dict(census_bracket="SELFTEST", interval_form="normal", beta_len=("STRUCK", "SELFTEST-BETA-BRACKET")),
              arena12=arena, out=os.path.join(out, "o.txt"), mark=os.path.join(out, "o.READ_STARTED"))
    return cfg, dict(matches=matches, truth=truth, items=items, multi=(("m07", multi_item["var"])), arena=arena, v0=v0truth, models=models)


def _naive(fx):
    """INDEPENDENT recomputation of C1's point (convention A and B) and the class counts, from the fixture's own truth."""
    res = defaultdict(lambda: [0, 0, 0, 0])
    multi = fx["multi"]
    for m in fx["matches"]:
        it = m["it"]
        if (m["a"], it["var"]) == multi or (m["b"], it["var"]) == multi:
            continue
        ka, kb = fx["truth"][(m["a"], it["var"])], fx["truth"][(m["b"], it["var"])]
        if ka + kb != 1:
            continue
        side = "A" if ka == 1 else "B"
        r = res[it["klass"]]
        r[0] += int(m["comb"] == side); r[1] += 1
        if m["comb"] in ("A", "B"):
            r[2] += int(m["comb"] == side); r[3] += 1
    out = {k: (v[0] / v[1], v[1], v[2] / v[3], v[3]) for k, v in res.items()}
    # ARENA12 (both contestants in the arena set) and the ONE split by v0, by hand
    a = [0, 0, 0, 0]
    byv = defaultdict(lambda: [0, 0, 0, 0])
    for m in fx["matches"]:
        it = m["it"]
        if (m["a"], it["var"]) == multi or (m["b"], it["var"]) == multi:
            continue
        ka, kb = fx["truth"][(m["a"], it["var"])], fx["truth"][(m["b"], it["var"])]
        if ka + kb != 1:
            continue
        side = "A" if ka == 1 else "B"
        for acc, cond in ((a, m["a"] in fx["arena"] and m["b"] in fx["arena"]), (byv[fx["v0"].get(it["var"])], it["klass"] == "ONE")):
            if cond:
                acc[0] += int(m["comb"] == side); acc[1] += 1
                if m["comb"] in ("A", "B"):
                    acc[2] += int(m["comb"] == side); acc[3] += 1
    out["A12"] = (a[0] / a[1], a[1], a[2] / a[3], a[3])
    out["V0"] = {k: (v[0] / v[1], v[1], v[2] / v[3] if v[3] else float("nan"), v[3]) for k, v in byv.items() if v[1] > 0}
    return out


def selftest():
    global MUTANT
    import time
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="k46kr_selftest_")
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok))); print("  [%s] %s" % ("PASS" if ok else "FAIL", name), flush=True)
    counter = [0]
    def fx(**pre):
        counter[0] += 1
        c, f = _mk_fixture(tmp, "f%d" % counter[0])
        c.pre.update(pre)
        return c, f
    try:
        cfg, F = fx()
        with contextlib.redirect_stdout(io.StringIO()) as so:
            r = mode(cfg, True)
        txt = so.getvalue()
        check("dry-run: returns None, writes nothing, identity gate PASS", r is None and not os.path.exists(cfg.out) and
              not os.path.exists(cfg.mark) and "IDENTITY GATE: PASS" in txt)
        check("dry-run: no accuracy printed and no key column selected", "accuracy" not in txt.split("PLANNED")[0].lower()
              and "no key column was selected" in txt)
        check("dry-run: first line is the pool id", txt.startswith("POOL pv_m"))
        check("C34-3: the three preconditions carry the e09e551 values (census 5572465 / ruling 8; both_agree / ruling 6; beta_len"
              " STRUCK / ruling 7) and missing_preconditions finds none",
              PRECONDITIONS["census_bracket"].startswith("steward 5572465 (") and "e09e551" in PRECONDITIONS["census_bracket"]
              and PRECONDITIONS["interval_form"] == "both_agree" and PRECONDITIONS["beta_len"][0] == "STRUCK"
              and "e09e551" in PRECONDITIONS["beta_len"][1] and "ruling 7" in PRECONDITIONS["beta_len"][1]
              and missing_preconditions(Cfg(pre=dict(PRECONDITIONS))) == [] and set(PRECONDITIONS) == {"census_bracket", "interval_form", "beta_len"})
        cfg0, _ = fx(census_bracket=None, interval_form=None, beta_len=None)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg0, False)
            check("run refuses with the preconditions unset", False)
        except SystemExit as e:
            check("run refuses with the preconditions unset", "[PRECONDITION]" in str(e) and all(k in str(e) for k in ("census_bracket", "interval_form", "beta_len")))
        cfgb2, _ = fx(beta_len="STRUCK")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfgb2, False)
            check("D6: a bare 'STRUCK' without the striking bracket refuses", False)
        except SystemExit as e:
            check("D6: a bare 'STRUCK' without the striking bracket refuses", "beta_len" in str(e))
        cfgb, _ = fx(beta_len="some estimand")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfgb, False)
            check("run refuses a beta_len other than STRUCK", False)
        except SystemExit as e:
            check("run refuses a beta_len other than STRUCK", "beta_len" in str(e))
        # a wrong identity number refuses before the key
        cfgg, _ = fx(); cfgg.identity = dict(cfgg.identity, A=cfgg.identity["A"] + 1)
        EVENTS.clear()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfgg, False)
            check("identity gate refuses a mismatch", False)
        except SystemExit as e:
            check("identity gate refuses a mismatch BEFORE any key read", "[IDENTITY-GATE]" in str(e) and "key" not in EVENTS
                  and not os.path.exists(cfgg.mark))
        # the run
        EVENTS.clear()
        with contextlib.redirect_stdout(io.StringIO()):
            R = mode(cfg, False)
        nv = _naive(F)
        st = R["st"]
        check("C1 point (A) and n equal the independent recomputation (%.4f on %d)" % nv["ONE"][:2],
              abs(st["ONE_A"][0] - nv["ONE"][0]) < 1e-12 and st["ONE_A"][1] == nv["ONE"][1])
        check("convention B (ONE, NONE) and NONE(A) equal the independent recomputation",
              abs(st["ONE_B"][0] - nv["ONE"][2]) < 1e-12 and st["ONE_B"][1] == nv["ONE"][3] and abs(st["NONE_A"][0] - nv["NONE"][0]) < 1e-12
              and abs(st["NONE_B"][0] - nv["NONE"][2]) < 1e-12)
        check("the multi-response side is refused and counted (1 side)", R["refused"].get("several rows", 0) == 1)
        # --- READY e451753 D1 and D2 (K1, K2, K5, D6): value-asserting checks against the fixture's own truth
        sched_vars = {m["it"]["var"] for m in F["matches"]}
        sched_models = {x for m in F["matches"] for x in (m["a"], m["b"])}
        in_resp = sum(1 for (mo, v) in F["truth"] if v in sched_vars and mo in sched_models) + 1       # + the multi row of m07
        one_vars = {m["it"]["var"] for m in F["matches"] if m["it"]["klass"] == "ONE"}
        check("D1: response rows fetched = in-scope rows (%d; the unscheduled second variants and zz_out never fetched)" % in_resp,
              R["fetched"]["response"] == in_resp)
        check("D1: reference rows fetched = the ONE variants at the pinned vintage (%d; the NONE and other-vintage rows never fetched)"
              % len(one_vars), R["fetched"]["reference"] == len(one_vars))
        check("K1: C2 = ONE(A) - NONE(A) from the naive per-class accuracies (%+.6f)" % (nv["ONE"][0] - nv["NONE"][0]),
              abs(st["C2"]["point"] - (nv["ONE"][0] - nv["NONE"][0])) < 1e-12)
        check("K2: the ONE split by v0 equals the fixture truth (%s)" % {k: v[1] for k, v in nv["V0"].items()},
              sorted(st["one_by_v0"]) == sorted(nv["V0"]) and all(abs(st["one_by_v0"][k][0] - nv["V0"][k][0]) < 1e-12 and
                                                                  st["one_by_v0"][k][1] == nv["V0"][k][1] for k in nv["V0"]))
        check("K5: ARENA12 sub-board equals the hand count (A %.4f on %d; B %.4f on %d)" % nv["A12"],
              abs(st["a12"][0] - nv["A12"][0]) < 1e-12 and st["a12"][1] == nv["A12"][1] and abs(st["a12"][2] - nv["A12"][2]) < 1e-12)
        check("D6: the beta_len line cites the STRIKING bracket, not the census's",
              "struck before the read by the registrar's bracket 'SELFTEST-BETA-BRACKET'" in R["text"])
        # K3 / D8: every identity row perturbed in turn refuses (the gate is evaluated on the store's own counts)
        cfgi, _ = fx()
        with contextlib.redirect_stdout(io.StringIO()):
            stw, _sb = open_store(cfgi, lambda s_: None); rids, M_, verd_ = read_store(stw); stw.close()
            vw_, _vb = open_view(cfgi, lambda s_: None); vi_, sd_ = view_structure(vw_, cfgi.cv); vw_.close()
            attach_structure(M_, vi_, sd_)
        refused_all, n_rows = True, 0
        for key_ in sorted(cfgi.identity):
            val = cfgi.identity[key_]
            if key_ == "response_model":
                continue
            bad = dict(cfgi.identity)
            if key_ == "anchors":
                bad[key_] = dict(val, health=val["health"] + 1)
            elif key_ == "run_ids":
                bad[key_] = ("ARCH-V2-PILOT-K46-run1",)
            else:
                bad[key_] = val + 1
            n_rows += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    identity_gate(Cfg(identity=bad, arena12=cfgi.arena12, store_sha=cfgi.store_sha), rids, M_, verd_, lambda s_: None)
                refused_all = False
            except SystemExit as e:
                refused_all = refused_all and "[IDENTITY-GATE]" in str(e)
        check("K3 / D8: each of the %d identity rows perturbed in turn refuses (incl. INVALID with NONE and run_ids)" % n_rows, refused_all and n_rows >= 17)
        # K4: a wrong-vintage reference id refuses
        with contextlib.redirect_stdout(io.StringIO()):
            vw2, _ = open_view(cfgi, lambda s_: None)
        vw2.unseal("selftest K4")
        try:
            read_keys(vw2, cfgi.cv, {("R", "M", 0): dict(a="m00", b="m01", variant=F["items"][0]["var"], item=F["items"][0]["id"],
                                                        ref="ref:%s|other-vintage|sk" % F["items"][0]["var"], klass="ONE")}, VINTAGE)
            check("K4: a wrong-vintage reference refuses", False)
        except SystemExit as e:
            check("K4: a wrong-vintage reference refuses", "[REF]" in str(e) and "vintage" in str(e))
        finally:
            vw2.close()
        check("order: identity gate before the key read", EVENTS.index("gate") < EVENTS.index("key"))
        check("DEFF = var_component / var_iid (recomputed)", abs(st["deff"] - (st["ONE_A_iv"]["se"] / st["ONE_A_iid_se"]) ** 2) < 1e-9)
        check("the component interval decides (it differs from the stem interval)", st["ONE_A_iv"]["se"] != st["ONE_A_stem"]["se"])
        check("outcome: first line pool id; recipe label and population verbatim; P-FAM lines present",
              R["text"].startswith("POOL pv_m") and RECIPE_LABEL in R["text"] and POPULATION in R["text"] and all(l in R["text"] for l in PFAM_LINES))
        check("outcome file written once, and the marker", os.path.exists(cfg.out) and os.path.exists(cfg.mark))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mode(cfg, False)
            check("re-run refused", False)
        except SystemExit as e:
            check("re-run refused", "[WRITE-ONCE]" in str(e) or "[B1]" in str(e))
        # interval forms on synthetic intervals; bar boundary
        iv = dict(n_lo=0.80, n_hi=0.9, p_lo=0.79, p_hi=0.88)
        check("form normal: lower == 0.80 -> HELD", c1_word(iv, "normal", 0.8)[0] == "HELD")
        check("form percentile: 0.79 -> UNDETERMINED", c1_word(iv, "percentile", 0.8)[0] == "UNDETERMINED")
        check("form both_agree: disagreement -> UNDETERMINED", c1_word(iv, "both_agree", 0.8) == ("UNDETERMINED", ("HELD", "UNDETERMINED")))
        check("upper < 0.80 -> FAILED; upper == 0.80 is not FAILED", c1_word(dict(n_lo=0.7, n_hi=0.799, p_lo=0, p_hi=0), "normal", 0.8)[0] == "FAILED"
              and c1_word(dict(n_lo=0.7, n_hi=0.80, p_lo=0, p_hi=0), "normal", 0.8)[0] == "UNDETERMINED")
        # branch coverage via verdict_lines on synthetic stats
        base_iv = lambda lo, hi, plo, phi, pt: dict(point=pt, se=0.02, n_lo=lo, n_hi=hi, p_lo=plo, p_hi=phi)
        def st_of(one_pt, lo, hi, plo, phi, form, none_pt, b_pt, n, deff, c2):
            return dict(B=2000, form=form, beta_bracket="X", ONE_A=(one_pt, n, 100), ONE_A_iv=base_iv(lo, hi, plo, phi, one_pt),
                        ONE_A_stem=base_iv(lo, hi, plo, phi, one_pt), ONE_A_iid_se=0.015, deff=deff, n_eff=n / deff,
                        C2=base_iv(c2 - 0.02, c2 + 0.02, c2 - 0.02, c2 + 0.02, c2), NONE_A=(none_pt, 500, 200),
                        NONE_A_iv=base_iv(0.7, 0.8, 0.7, 0.8, none_pt), ONE_B=(b_pt, n - 20, 90), ONE_B_iv=base_iv(0.8, 0.9, 0.8, 0.9, b_pt),
                        NONE_B=(0.8, 400, 180), NONE_B_iv=base_iv(0.75, 0.85, 0.75, 0.85, 0.8), one_by_v0={1: (0.9, 300, 0.95, 280), 0: (0.5, 90, 0.6, 80)},
                        balance=Counter({("ONE", "health", 1): 10, ("NONE", "math", None): 20}), a12=(0.85, 100, 0.9, 90))
        for s_ in (st_of(0.86, 0.81, 0.91, 0.81, 0.91, "normal", 0.75, 0.93, 390, 1.5, 0.11),
                   st_of(0.70, 0.65, 0.75, 0.65, 0.75, "percentile", 0.60, 0.72, 200, 3.0, 0.20),
                   st_of(0.82, 0.78, 0.86, 0.78, 0.86, "normal", 0.75, 0.93, 390, 1.5, 0.11),
                   st_of(0.82, 0.80, 0.86, 0.79, 0.86, "both_agree", 0.75, 0.93, 390, 1.5, 0.11)):
            with contextlib.redirect_stdout(io.StringIO()):
                verdict_lines(s_)
        # C34-2 / ruling 8: the plan of record at the census, by value (the registrar's record 2026-09-29 numbers)
        check("PLAN at the census: n 544, DEFF 4.934, n_eff %.1f == 110.3, SE %.5f == 0.03305, MDE80 %.4f == 0.0925, break-even "
              "%.3f == 2.075, FAILED below %.4f == 0.7075" % (PLAN["n_eff"], PLAN["se"], PLAN["mde"], PLAN["breakeven"], PLAN["failed_below"]),
              PLAN["n"] == 544 and PLAN["deff"] == 4.934 and round(PLAN["n_eff"], 1) == 110.3 and round(PLAN["se"], 5) == 0.03305
              and round(PLAN["mde"], 4) == 0.0925 and round(PLAN["breakeven"], 3) == 2.075 and round(PLAN["failed_below"], 4) == 0.7075
              and PLAN["verdict"].startswith("DESCRIPTIVE-ONLY for the HELD prediction at the census"))
        pp = plan_from_census(390, 2.0, 0.86, 0.80)
        check("plan_from_census reproduces the registered pilot (390 / 2.0): SE %.5f, MDE %.4f, break-even %.3f, FAILED below %.3f"
              % (pp["se"], pp["mde"], pp["breakeven"], pp["failed_below"]),
              round(pp["se"], 5) == 0.02485 and round(pp["mde"], 4) == 0.0696 and round(pp["breakeven"], 3) == 1.487
              and round(pp["failed_below"], 3) == 0.730 and pp["n_eff"] == 195 and pp["verdict"].startswith("DESCRIPTIVE-ONLY"))
        ps = plan_from_census(544, 1.0, 0.86, 0.80)
        check("plan_from_census SCOREABLE branch (DEFF 1: MDE %.4f < gap 0.060)" % ps["mde"], ps["verdict"].startswith("SCOREABLE"))
        with contextlib.redirect_stdout(io.StringIO()):
            vt = "\n".join(verdict_lines(st_of(0.86, 0.81, 0.91, 0.81, 0.91, "normal", 0.75, 0.93, 544, 4.934, 0.11))[0])
        check("C34-3 census check: n 544 in 100 components (the fixture) prints MISMATCH",
              "CENSUS CHECK: the read's key-decidable ONE n 544 in 100 components vs the census 544 in 160: MISMATCH" in vt)
        s_eq = st_of(0.86, 0.81, 0.91, 0.81, 0.91, "normal", 0.75, 0.93, 544, 4.934, 0.11)
        s_eq["ONE_A"] = (0.86, 544, 160)
        s_n = dict(s_eq, ONE_A=(0.86, 543, 160))
        with contextlib.redirect_stdout(io.StringIO()):
            vt_eq, vt_n = ("\n".join(verdict_lines(x)[0]) for x in (s_eq, s_n))
        check("C34-3 census check: 544 in 160 prints EQUAL; 543 in 160 prints MISMATCH",
              "vs the census 544 in 160: EQUAL" in vt_eq and "ONE n 543 in 160 components vs the census 544 in 160: MISMATCH" in vt_n)
        check("verdict print: the census plan of record and the pilot beside, by value",
              "SUPPORT (plan of record, at the census; ruling 8): DEFF 4.934 (Kish m-bar, DECLARED rho = 1 upper bound), n 544 in 160 "
              "components, n_eff 110.3, SE 0.03305, MDE80 0.0925; DESCRIPTIVE-ONLY" in vt
              and "beside (the registered pilot, deciding nothing): DEFF 2.0, n 390, n_eff 195, SE 0.02485, MDE80 0.0696" in vt
              and vt.index("plan of record, at the census") < vt.index("the registered pilot, deciding nothing"))
        # mutants
        def m_point():
            c, f = fx(); R_ = mode(c, False); nv_ = _naive(f)
            return not (abs(R_["st"]["ONE_A"][0] - nv_["ONE"][0]) < 1e-12 and R_["st"]["ONE_A"][1] == nv_["ONE"][1]
                        and abs(R_["st"]["NONE_A"][0] - nv_["NONE"][0]) < 1e-12)
        def m_refused():
            c, f = fx(); R_ = mode(c, False)
            return R_["refused"].get("several rows", 0) != 1
        def m_gate():
            c, f = fx(); c.identity = dict(c.identity, A=c.identity["A"] + 1); mode(c, False)
            return True                                               # admitted a wrong store: observed
        def m_stem():
            c, f = fx(); R_ = mode(c, False)
            return R_["st"]["ONE_A_iv"]["se"] == R_["st"]["ONE_A_stem"]["se"]
        def m_deff():
            c, f = fx(); R_ = mode(c, False); s2 = R_["st"]
            return abs(s2["deff"] - (s2["ONE_A_iv"]["se"] / s2["ONE_A_iid_se"]) ** 2) > 1e-9
        def m_rehash():
            c, f = fx(); R_ = mode(c, False)
            return "store sha256-bytes AFTER" not in R_["text"]
        def m_bar():
            return c1_word(dict(n_lo=0.80, n_hi=0.9, p_lo=0, p_hi=0), "normal", 0.8)[0] != "HELD"
        def m_marker():
            c, f = fx(); mode(c, False); os.remove(c.out); mode(c, False)
            return True
        def m_write():
            p = os.path.join(tmp, "w%d.txt" % counter[0]); counter[0] += 1
            write_outcome(p, "a"); write_outcome(p, "b")
            return True
        def m_dry():
            c, f = fx(); mode(c, True)
            return False
        def m_sqlscope():
            c, f = fx(); R_ = mode(c, False)
            return R_["fetched"]["response"] != in_resp
        MUTS = [("sql_unfiltered", m_sqlscope, None), ("model_item_join", m_point, None), ("conv_a_drops_invalid", m_point, None), ("tie_right", m_point, None),
                ("class_swap", m_point, None), ("multi_side_used", m_refused, None), ("gate_off", m_gate, None),
                ("stem_decides", m_stem, None), ("deff_inverse", m_deff, None), ("no_rehash", m_rehash, None),
                ("bar_strict", m_bar, None), ("marker_off", m_marker, None), ("write_w", m_write, None),
                ("dry_reads_key", m_dry, "[KEY-TRIPWIRE]")]
        for name, fn, expect in MUTS:
            MUTANT = name
            msg = ""
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    k = bool(fn())
            except SystemExit as e:
                msg = str(e); k = bool(expect) and expect in msg
            finally:
                MUTANT = None
            check("MUTANT %-22s killed%s" % (name, "" if k else " -- SURVIVED (%s)" % msg[:90]), k)
        miss = BR.missing()
        check("every declared print branch executed (%d / %d); missing %s" % (len(BR.declared) - len(miss), len(BR.declared), miss), not miss)
    finally:
        for r_, ds, fs in os.walk(tmp):
            for f in fs:
                try:
                    os.chmod(os.path.join(r_, f), stat.S_IWRITE)
                except OSError:
                    pass
        shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for _, ok in checks if not ok)
    n_mut = sum(1 for n, _ in checks if n.startswith("MUTANT"))
    n_kill = sum(1 for n, ok in checks if n.startswith("MUTANT") and ok)
    print("SELFTEST %s: %d checks, %d failed; mutants %d / %d killed; %.1fs" % ("PASS" if n_fail == 0 else "FAIL", len(checks), n_fail,
                                                                              n_kill, n_mut, time.time() - t0))
    return 0 if n_fail == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        if os.environ.get(k) != "1":
            print("[W12] %s is %r (the run-operator sets 1; single-threaded)" % (k, os.environ.get(k)))
            if a.run:                                            # READY e451753 D7: refuse, never only warn, on the real read
                raise SystemExit("[W12] --run refused: %s is %r, not '1' (export it before starting python)" % (k, os.environ.get(k)))
    if a.selftest:
        sys.exit(selftest())
    if MUTANT is not None:
        raise SystemExit("[MUTANT] %r is set: a real mode refuses" % MUTANT)
    mode(real_cfg(), a.dry_run)


if __name__ == "__main__":
    main()
