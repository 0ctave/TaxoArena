"""JUDGE-SOLVED-SPLIT -- on K46-KEY-READ's key-decidable ONE matches, does the recipe's key accuracy depend on whether the judge
model solved the item itself (ZERO judge calls; CPU readout on the K46 verdict store and the judge's cached solves).

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-02 (before any code or call) — JUDGE-SOLVED-SPLIT:
on K46-KEY-READ's key-decidable ONE matches (the v2 recipe with a cached reference), does the judge's key accuracy depend on whether
the judge model solved the item itself, when the reference is right (JS1, deciding), and does its own solve decide whether it follows a
wrong reference (JS2, descriptive; the Krumdick-2025 reconciliation)? ..." (L23437-L23462 as of d635fec5, parent 1a922a80; resolve by
the heading, the last bracket wins); record docs/agents/results/JUDGE-SOLVED-SPLIT.json; go: plan Amendment 38.

  python tools/analysis/judge_solved_split.py --selftest   # synthetic store + sealed view + solve DB under tempfile; NO DB of record
  python tools/analysis/judge_solved_split.py --dry-run    # 0 calls, WRITES NOTHING: pins, shas, identity, DENOMINATORS (counts only;
                                                           #   no accuracy by solve status is computed or printed)
  python tools/analysis/judge_solved_split.py --run        # the readout; write-once outcome (REFUSES while a PRECONDITION is unset)

LAUNCH SEQUENCE: registration d635fec5 -> this script (engine-coder) -> adversarial-reviewer READY -> registrar bracket on the
interval form (PRECONDITION form_bracket, below) -> run-operator --dry-run (denominators vs the registration) -> --run (single-threaded,
OMP / MKL / OPENBLAS = 1) -> adversarial-reviewer on the numbers -> registrar. Run from the MAIN checkout (TAXOARENA_DATA_ROOT may point
the inputs elsewhere). Zero calls in every mode; no pool is read beyond the store and the sealed eval view (both read-only).

PRECONDITION THAT REFUSES --run WHILE UNSET (CONDITION FOR THE REGISTRAR, not resolved here):
  interval_form / form_bracket. The registration's READOUTS AND CRITERIA line reads "95% percentile intervals, CK-CLOSE components
  resampled, B 2,000, K46-KEY-READ's seed". The orchestrator's build brief (2026-10-02) asks for "the NORMAL interval form with analytic
  DEFF, as the K46 analyses do" (k46_repost.py C-K1: point +- 1.96 x the component-clustered bootstrap SE; DEFF ANALYTIC). The two
  differ, and the form decides JS1 ("the INTERVAL decides"). Building the brief's form silently would be criterion substitution
  (BFCL-JUDGED-PILOT C1 precedent), so interval_form = "normal" (the brief) is implemented, BOTH forms are printed with a FORMS
  AGREE / DISAGREE line, and --run REFUSES until form_bracket names the registrar's bracket ratifying the form of record (a delta of
  this script sets it, or changes interval_form to "percentile" if the registrar rules for the registered text).
  [DELTA 2026-10-02, the engine-coder, insertion only; the orchestrator's ruling on C1 relayed 2026-10-02: "the registration is the
  record"] THE DECIDING FORM IS THE 95% PERCENTILE INTERVAL, AS REGISTERED. interval_form = "percentile"; form_bracket names the
  registration itself (no registrar bracket is needed: the form of record is the registered text). The NORMAL form (point +- 1.959964 x
  the component bootstrap SE) and the analytic DEFF are printed beside, labelled DESCRIPTIVE, NOT DECIDING; the FORMS line reports
  agreement only. New mutant normal_decides (the normal bounds decide) killed. The paragraph above is history.

GUARDS (every real mode):
  (1) first printed line: POOL pv2_41dbd3dbcd399df0.
  (2) k46_key_read.py is imported UNCHANGED: its LF git blob is asserted == c6a6729bb0256d394072ae844120867d2fa5c652 (the delta-3
      READY pin) before anything opens; its MUTANT is asserted None.
  (3) the K46 store (sha256-bytes 44724d25...) and the eval view (e35b7518...) open through K46-KEY-READ's own openers
      (data_v2.ro.open_ro, mode=ro&immutable=1, -wal / -journal refusal), its identity gate is run (refusing in --run), both are
      re-hashed after the read.
  (4) the judge's solves experiment_results/judge_solve/grok.db open through data_v2.ro.open_ro (mode=ro&immutable=1) with
      expect_sha256 0f2d96d416c70dc3... (sha256-bytes; = the registrar's re-hash), behind a KeyTripwire that never admits the columns
      answer / gt / raw (only question_id and correct are selected, and only for the joined qids); re-hashed after the read.
  (5) THE JOIN (registration DATA, verbatim chain): K46 schedule.reference_row_id "ref:<variant>|<vintage>|<source_key>" -> eval_view
      reference row (corpus_version mmlu-pro-v2, variant_id, vintage grok-reasoning-v0, source_key) -> reference.legacy_qid ->
      grok.db answers.question_id. A reference row whose source_key is not "qid:<legacy_qid>" REFUSES (the two carriers of the qid
      must agree). A qid absent from grok.db is UNCOVERED: it is never counted as unsolved; uncovered matches stay out of JS1 / JS2
      and are printed beside (JS3).
  (6) IDENTITY PRECONDITION (refuse in --run, printed in --dry-run): K46-KEY-READ C1 on all 544 reproduced (0.8787 in 160
      components; reference right 0.9249 / 506, wrong 0.2632 / 38; 4-digit rounding) and the steward's cell counts (446 covered;
      right 226 / 188; wrong 5 / 27). The DATA-section counts (wrong cells in 2 / 7 variants; 98 uncovered matches on 29 qids;
      2,801 solve rows) are printed and flagged (OK / MISMATCH), deciding nothing.
  (7) write-once outcome experiment_results/archv2/judge_solved_split/outcome.txt (mode "x") and a write-once read marker
      judge_solved_split.READ_STARTED beside it (refused if present); a sha that differs after the read writes *_VOID.txt instead.
  (8) --run refuses unless OMP_NUM_THREADS / MKL_NUM_THREADS / OPENBLAS_NUM_THREADS are "1" (registration HYGIENE: CPU single-threaded).

INSTRUMENT (K46-KEY-READ's, imported). Key-decidable = exactly one side key-correct (the key of a side = is_correct of the SHOWN
response). CONVENTION A (DECIDES): TIE / INVALID / NON_TERMINATED / CONTENT_FILTER on a key-decidable match count WRONG and stay in the
denominator; CONVENTION B (beside): committed verdicts only. Bootstraps B = 2,000 from numpy default_rng(42) (K46-KEY-READ's seed):
JS1's Delta_S resamples the CK-CLOSE components of the 414 covered reference-right matches JOINTLY for both arms (solve status is a
question-level attribute; a component may carry both arms only through twins) -- identical, for convention A, to K46-KEY-READ's
boot_diff (the selftest asserts equality). Normal form = point +- 1.959964 x the component bootstrap SE; percentile = 2.5 / 97.5.
DEFF of record is ANALYTIC (k46_repost.deff_analytic's definition, extended to a difference of two ratio means): the linearised
component-clustered variance sum_g [ (s1_g - p1 c1_g) / n1 - (s2_g - p2 c2_g) / n2 ]^2 over the plug-in iid variance
sum_i (v_i - p1)^2 / n1^2 + sum_j (v_j - p2)^2 / n2^2; n_eff = n / DEFF per arm; MDE80 = 2.80 x SE. The K46 C1 DEFF 2.727 (bootstrap
ratio, the registration's transported value) is reproduced and printed beside. No model-edge count is computed, so no wrong(established)
count arises (stated).

CRITERIA (registered, verbatim in the print): JS1 (DECIDING; the INTERVAL decides) Delta_S = acc(solved) - acc(unsolved) on the covered
reference-right matches, convention A: HELD iff the 95% interval lies wholly above 0 (lower > 0); FAILED (REVERSED) iff wholly below 0
(upper < 0); UNDETERMINED otherwise, never parity. JS2 (DESCRIPTIVE-ONLY) covered reference-wrong matches: acc(solved), acc(unsolved),
counts and variants. JS3 (DESCRIPTIVE) the full 2 x 2 with TIE shares and convention B; the uncovered matches beside. READING, P1-P3,
F-JS as registered.

READINGS (stated, not silent):
  (a) "variants" in JS2 = distinct scheduled variant_id among the cell's matches.
  (b) A prediction "X [lo, hi]" is HELD iff the observed point lies in [lo, hi], endpoints inclusive (K46-KEY-READ reading (c)). P2 and
      P3 carry two intervals each and are scored as P2a / P2b and P3a / P3b; P3 on an empty cell prints NOT SCOREABLE. The JS1 word
      probabilities (HELD 0.15 / FAILED 0.05 / UNDETERMINED 0.80) are scored by the multi-class Brier score sum_k (p_k - o_k)^2.
  (c) JS3's TIE share = TIE / all key-decidable matches of the cell (the convention A denominator); INVALID-type share beside.
  (d) The READING sentence for UNDETERMINED prints the realised n ("n = 414" when the identity passed).

MUTANT TABLE (each run through mode() --run on a fresh fixture whose answer is known, value-asserted against an independent recomputation
(naive(), K46-KEY-READ's boot_diff on the naive rows); a refusal kills only when it is the named guard's; non-vacuity: every kill predicate
reads "not killed" on the unmutated code; 18 / 18 killed, selftest 63 checks, every one of the 28 declared print branches executed):
  wrong_key (grok.db joined on the contestants' response legacy_qid)   killed (identity refusal: covered / cell counts)
  ref_wrong_in_js1 (reference-wrong rows in JS1)                       killed (Delta_S / n vs naive)
  match_level_boot (i.i.d. matches resampled, not components)          killed (SE vs boot_diff on components)
  conv_b_decides (convention B decides JS1)                            killed (Delta_S vs naive convention A)
  uncovered_as_unsolved (uncovered rows counted unsolved)              killed (identity refusal: cell counts)
  sign_swap (unsolved - solved)                                        killed (Delta_S sign)
  z90 (1.645 in the normal form)                                       killed (normal bound vs point - 1.959964 SE)
  deff_one_group (analytic DEFF from one arm)                          killed (DEFF vs independent linearised ratio)
  deff_boot (Monte-Carlo bootstrap ratio as the DEFF)                  killed (DEFF vs analytic)
  js2_uses_right (JS2 read on reference-right cells)                   killed (JS2 printed line vs naive)
  tie_share_committed (TIE share over committed verdicts)              killed (JS3 TIE share vs naive)
  form_ignored (the other form decides)                                killed (FORMS line bounds vs the percentile bounds)
  normal_decides (the NORMAL bounds decide JS1)                        killed (FORMS line / JS1 word vs the percentile bounds; decide())
  falsifier_on_undet (F-JS fires on UNDETERMINED)                      killed (UNDETERMINED fixture prints NOT FIRED)
  bar_inclusive (lower >= 0 reads HELD)                                killed (js1_word(0.0, 0.2) == UNDETERMINED)
  write_w (outcome opened "w")                                         killed (the second write is observed)
  dry_writes (dry-run writes the outcome)                              killed (no file after --dry-run)
  ident_off (identity precondition bypassed)                           killed (a perturbed cell count must refuse)
"""
import os, sys, io, math, argparse, tempfile, shutil, stat, contextlib, time; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import v2_reader_guards as G
import k46_key_read as K
from data_v2 import ro as dv2ro

TEST_ID = "JUDGE-SOLVED-SPLIT"
PROG = ("docs/judge_v2_program.md L23437-L23462 (as of d635fec5, parent 1a922a80; heading \"## Registered 2026-10-02 (before any code"
        " or call) — JUDGE-SOLVED-SPLIT: on K46-KEY-READ's key-decidable ONE matches ...\")")
K46_BLOB = "c6a6729bb0256d394072ae844120867d2fa5c652"
DATA_ROOT = K.DATA_ROOT
SOLVE_REL = os.path.join("experiment_results", "judge_solve", "grok.db")
SOLVE_SHA = "0f2d96d416c70dc334353750e3dfa041fc372a37c92a1a0e3da4d0bc9ef4c0b7"
SOLVE_FORBIDDEN = ("answer", "gt", "raw")
OUT_DIR = os.path.join(ROOT, "experiment_results", "archv2", "judge_solved_split")
Z95 = 1.959963984540054
PRECONDITIONS = dict(
    interval_form="percentile",  # the registration (READOUTS AND CRITERIA: "95% percentile intervals"); orchestrator's C1 ruling 2026-10-02
    form_bracket=("the registration itself: docs/judge_v2_program.md L23437-L23462 (d635fec5), READOUTS AND CRITERIA \"95% percentile"
                  " intervals, CK-CLOSE components resampled, B 2,000, K46-KEY-READ's seed\"; NORMAL with analytic DEFF printed beside,"
                  " descriptive, not deciding"))
INTERVAL_FORMS = ("normal", "percentile")
# IDENTITY PRECONDITION (registration INSTRUMENT, refuse) and the DATA-section counts (printed, flagged)
IDENT = dict(c1_point=0.8787, c1_n=544, c1_comp=160, right_point=0.9249, right_n=506, wrong_point=0.2632, wrong_n=38,
             covered=446, right_solved=226, right_unsolved=188, wrong_solved=5, wrong_unsolved=27)
DATA_FLAGS = dict(right_cov=414, wrong_cov=32, wrong_solved_variants=2, wrong_unsolved_variants=7, uncovered=98, uncovered_qids=29,
                  solve_rows=2801, c1_deff=2.727)
# SUPPORT of record (registration (b)-(f)); recomputed by plan_js1 and asserted by value in the selftest
PLAN_IN = dict(deff=2.727, n_s=226, n_u=188, p_s=0.95, p_u=0.90, pred=-0.01)
PRED = dict(P1=(-0.09, 0.07), P2a=(0.88, 0.97), P2b=(0.86, 0.96), P3a=(0.05, 0.40), P3b=(0.20, 1.00))
PROBS = dict(HELD=0.15, FAILED=0.05, UNDETERMINED=0.80)
READING = dict(
    HELD="on the content-closed v2 split, with a right reference, the recipe is more key-accurate where its judge solves the item"
         " (Delta_S %+.4f, 95%% %s interval [%+.4f, %+.4f])",
    UNDETERMINED="not shown either way at n = %d",
    FAILED="recorded, no sentence")
FALSIFIER = ("F-JS (fires iff JS1 HELD): overturns, on the content-closed v2 split, the reading the record took from JUDGE-2x2 (history):"
             " \"holding the reference fixed, judge ability makes no difference ... a cheap judge does not need to solve the question,"
             " it needs the right answer\"; the cheap-judge sentence then carries \"judge competence still matters with a right reference"
             " (Delta_S, interval)\". No recorded number is revised; a non-fire is not shown parity.")
PFAM = ("JUDGE-2x2 comparators 0.780 (judge solved) / 0.796 (judge failed) at right references, 0.250 / 0.145 at wrong ones [P-FAM"
        " 2026-09-27: p2dca judged family — history, not evidence (docs/reviews/RULING_w0_p2dca_family.md)]; printed beside, never pooled,"
        " never deciding")
NOT_SHOW = ("WILL NOT SHOW: a causal effect of judge competence (separate cached solve, 5.7% retest noise, difficulty confounds); the 98"
            " uncovered matches' solve status; the Krumdick reconciliation (JS2 descriptive, 9 variants); another judge, recipe, split or the"
            " NONE matches; a reference policy (D2 the author's); parity (no TOST).")
MUTANT = None
BRANCH_NAMES = ("IDENT.PASS", "IDENT.REFUSED", "FORM.normal", "FORM.percentile", "FORMS.AGREE", "FORMS.DISAGREE", "JS1.HELD",
                "JS1.FAILED", "JS1.UNDETERMINED", "READ.HELD", "READ.UNDETERMINED", "READ.FAILED", "MEAS.INSIDE", "MEAS.OUTSIDE",
                "P1.HELD", "P1.FAILED", "P2a.HELD", "P2a.FAILED", "P2b.HELD", "P2b.FAILED", "P3a.HELD", "P3a.FAILED",
                "P3a.NOT_SCOREABLE", "P3b.HELD", "P3b.FAILED", "P3b.NOT_SCOREABLE", "F.FIRED", "F.NOT_FIRED")
BR = G.Branches(BRANCH_NAMES)


class Cfg(K.Cfg):
    pass


def real_cfg():
    k = K.real_cfg()
    return Cfg(**dict(k.__dict__, solve_path=os.path.join(DATA_ROOT, SOLVE_REL), solve_sha=SOLVE_SHA, ident=dict(IDENT),
                      flags=dict(DATA_FLAGS), jpre=dict(PRECONDITIONS), out=os.path.join(OUT_DIR, "outcome.txt"),
                      mark=os.path.join(OUT_DIR, "judge_solved_split.READ_STARTED")))


def plan_js1(deff, n_s, n_u, p_s, p_u, pred):
    """Registration Support (c)-(f): n_eff = n / DEFF; SE = sqrt(p_s q_s / n_s + p_u q_u / n_u) x sqrt(DEFF); MDE80 = 2.80 x SE;
    DESCRIPTIVE-ONLY at the prediction iff |pred| < MDE80; the interval reachable where |Delta| > 1.96 x SE."""
    se_iid = math.sqrt(p_s * (1 - p_s) / n_s + p_u * (1 - p_u) / n_u)
    se = se_iid * math.sqrt(deff)
    mde = 2.80 * se
    return dict(neff_s=n_s / deff, neff_u=n_u / deff, se_iid=se_iid, se=se, mde=mde, reach=1.96 * se,
                word="DESCRIPTIVE-ONLY" if abs(pred) < mde else "SCOREABLE")


PLAN = plan_js1(**PLAN_IN)


def missing_preconditions(pre):
    bad = []
    if pre.get("interval_form") not in INTERVAL_FORMS:
        bad.append("interval_form (one of %s)" % (INTERVAL_FORMS,))
    if not pre.get("form_bracket"):
        bad.append("form_bracket (the registration reads \"95% percentile intervals\"; the build brief asked for the NORMAL form: the"
                   " registrar's bracket ratifying the form of record must be named before --run)")
    return bad


# ============================================================================================ reading
def k46_identity(say):
    blob = G.script_identity(K.__file__)[0]
    say("  " + G.identity_line(K.__file__, "k46_key_read.py (imported unchanged; pinned blob:%s)" % K46_BLOB))
    if blob != K46_BLOB or K.MUTANT is not None:
        raise SystemExit("[PIN] k46_key_read.py blob:%s != the pinned blob:%s (or its MUTANT %r is set)" % (blob, K46_BLOB, K.MUTANT))


def read_ref_qids(tw, cv, M, vintage):
    """ref_row_id -> legacy_qid for the ONE matches, by (variant_id, vintage, source_key) of the scheduled reference_row_id."""
    parsed = {}
    for m in M.values():
        if m["klass"] != "ONE":
            continue
        v, vt, sk = m["ref"][4:].split("|", 2)
        if vt != vintage:
            raise SystemExit("[REF] reference vintage %r is not %s" % (vt, vintage))
        parsed[(v, vt, sk)] = m["ref"]
    vars_ = sorted({v for (v, _, _) in parsed})
    out = {}
    if MUTANT == "wrong_key":                       # the defect: the contestants' response legacy_qid, not the reference's
        for s0 in range(0, len(vars_), 500):
            ch = vars_[s0:s0 + 500]
            for v, q in tw.execute("SELECT seen_ck, MIN(legacy_qid) FROM response WHERE corpus_version=? AND seen_ck IN (%s) GROUP BY"
                                   " seen_ck" % ",".join("?" * len(ch)), [cv] + ch):
                for (pv, pvt, psk), rid in parsed.items():
                    if pv == v:
                        out[rid] = int(q)
        return out
    bad = 0
    for s0 in range(0, len(vars_), 500):
        ch = vars_[s0:s0 + 500]
        for v, vt, sk, q in tw.execute("SELECT variant_id, vintage, source_key, legacy_qid FROM reference WHERE corpus_version=? AND"
                                       " vintage=? AND variant_id IN (%s)" % ",".join("?" * len(ch)), [cv, vintage] + ch):
            if (v, vt, sk) in parsed:
                if q is None or sk != "qid:%d" % int(q):
                    bad += 1
                    continue
                out[parsed[(v, vt, sk)]] = int(q)
    if bad:
        raise SystemExit("[JOIN] %d reference rows: source_key is not 'qid:<legacy_qid>' (the two carriers of the qid disagree)" % bad)
    missing = set(parsed.values()) - set(out)
    if missing:
        raise SystemExit("[JOIN] %d scheduled ONE references have no eval_view reference row" % len(missing))
    return out


def read_solves(cfg, qids, say):
    before = G.sha256_file(cfg.solve_path)
    say("  solves %s | sha256-bytes BEFORE %s (%s) | sidecars: %s" % (cfg.solve_path, before, "= the pinned sha" if before ==
                                                                       cfg.solve_sha else "NOT the pinned %s" % cfg.solve_sha,
                                                                       G.sidecar_line(cfg.solve_path)))
    if before != cfg.solve_sha:
        raise SystemExit("[PIN] solve DB sha256-bytes %s != the pinned %s" % (before, cfg.solve_sha))
    tw = G.KeyTripwire(dv2ro.open_ro(cfg.solve_path, expect_sha256=cfg.solve_sha), SOLVE_FORBIDDEN, key=("correct",),
                       label="grok.db")
    n_rows = tw.execute("SELECT COUNT(question_id) FROM answers").fetchone()[0]
    tw.unseal("JUDGE-SOLVED-SPLIT: the judge's own solve status for the joined qids (registration DATA)")
    q = sorted(qids)
    solved = {}
    for s0 in range(0, len(q), 500):
        ch = q[s0:s0 + 500]
        for qid, c in tw.execute("SELECT question_id, correct FROM answers WHERE question_id IN (%s)" % ",".join("?" * len(ch)), ch):
            if c is None:
                raise SystemExit("[SOLVE] question_id %s has correct NULL" % qid)
            solved[int(qid)] = int(c)
    tw.close()
    after = G.sha256_file(cfg.solve_path)
    say("  solves sha256-bytes AFTER %s (%s) | rows %d | joined qids %d, present %d, absent (UNCOVERED) %d"
        % (after, "EQUAL to before" if after == before else "DIFFERS from before", n_rows, len(q), len(solved), len(q) - len(solved)))
    return solved, n_rows, after == before


def attach_solve(rows, qid_of, solved):
    for r in rows:
        q = qid_of.get(r["m"]["ref"]) if r["klass"] == "ONE" else None
        r["qid"] = q
        s = solved.get(q) if q is not None else None
        if MUTANT == "uncovered_as_unsolved" and s is None and r["klass"] == "ONE":
            s = 0
        r["solved"] = s


def cells(kd_one):
    C = {}
    for v0 in (1, 0):
        for sv in (1, 0, None):
            C[(v0, sv)] = [r for r in kd_one if r["v0"] == v0 and r["solved"] == sv]
    return C


def js1_rows(kd_one):
    if MUTANT == "ref_wrong_in_js1":
        right = [r for r in kd_one if r["v0"] in (0, 1) and r["solved"] is not None]
    else:
        right = [r for r in kd_one if r["v0"] == 1 and r["solved"] is not None]
    return [r for r in right if r["solved"] == 1], [r for r in right if r["solved"] == 0]


def acc(rows, conv):
    if conv == "A":
        y = [r["right_A"] for r in rows]
    else:
        y = [r["right_B"] for r in rows if r["committed"]]
    return (float(np.mean(y)) if y else float("nan")), len(y)


def kish(rows):
    c = Counter(r["comp"] for r in rows)
    n = len(rows)
    return len(c), (sum(v * v for v in c.values()) / n if n else float("nan"))


def identity_js(cfg, kd_one, C, n_rows, B, seed, say, refuse):
    I, F = cfg.ident, cfg.flags
    c1 = acc(kd_one, "A"); nc1 = len({r["comp"] for r in kd_one})
    r_ = acc([r for r in kd_one if r["v0"] == 1], "A"); w_ = acc([r for r in kd_one if r["v0"] == 0], "A")
    cov = [r for r in kd_one if r["solved"] is not None]
    unc = [r for r in kd_one if r["solved"] is None]
    cnt = lambda v0, sv: len(C[(v0, sv)])
    nvar = lambda v0, sv: len({r["m"]["variant"] for r in C[(v0, sv)]})
    rows = [("K46 C1 point (convention A)", round(c1[0], 4), I["c1_point"]), ("K46 C1 key-decidable ONE n", c1[1], I["c1_n"]),
            ("K46 C1 CK-CLOSE components", nc1, I["c1_comp"]),
            ("reference right: accuracy (A)", round(r_[0], 4), I["right_point"]), ("reference right: n", r_[1], I["right_n"]),
            ("reference wrong: accuracy (A)", round(w_[0], 4), I["wrong_point"]), ("reference wrong: n", w_[1], I["wrong_n"]),
            ("covered (solve status known)", len(cov), I["covered"]),
            ("covered reference-right, judge solved", cnt(1, 1), I["right_solved"]),
            ("covered reference-right, judge unsolved", cnt(1, 0), I["right_unsolved"]),
            ("covered reference-wrong, judge solved", cnt(0, 1), I["wrong_solved"]),
            ("covered reference-wrong, judge unsolved", cnt(0, 0), I["wrong_unsolved"])]
    say("IDENTITY PRECONDITION (registration INSTRUMENT; a FAILED PRECONDITION on any mismatch, refused before any readout):")
    ok = True
    for name, got, want in rows:
        hit = got == want
        ok &= hit
        say("  %-44s %10s  (registered %10s)  %s" % (name, got, want, "OK" if hit else "MISMATCH"))
    _, reps_c, _, _ = K.boot_acc(kd_one, "A", "comp", B, seed)
    _, reps_i, _, _ = K.boot_acc(kd_one, "A", "iid", B, seed)
    sec, sei = K._sd(reps_c), K._sd(reps_i)
    deff_c1 = (sec / sei) ** 2 if sei > 0 else float("nan")
    flags = [("covered reference-right", cnt(1, 1) + cnt(1, 0), F["right_cov"]),
             ("covered reference-wrong", cnt(0, 1) + cnt(0, 0), F["wrong_cov"]),
             ("variants, reference-wrong solved", nvar(0, 1), F["wrong_solved_variants"]),
             ("variants, reference-wrong unsolved", nvar(0, 0), F["wrong_unsolved_variants"]),
             ("uncovered key-decidable ONE matches", len(unc), F["uncovered"]),
             ("uncovered qids", len({r["qid"] for r in unc}), F["uncovered_qids"]),
             ("grok.db answers rows", n_rows, F["solve_rows"]),
             ("K46 C1 DEFF (bootstrap ratio, transported)", round(deff_c1, 3), F["c1_deff"])]
    say("  DATA-section counts (printed and flagged; deciding nothing):")
    for name, got, want in flags:
        say("    %-46s %8s  (DATA %8s)  %s" % (name, got, want, "OK" if got == want else "MISMATCH (flagged)"))
    if MUTANT == "ident_off":
        ok = True
    if not ok:
        BR.hit("IDENT.REFUSED")
        if refuse:
            raise SystemExit("[IDENTITY] K46-KEY-READ C1 or the steward's cell counts are not reproduced: refused before any readout")
        say("  -> IDENTITY: FAIL (dry-run: printed, not refused)")
        return False, deff_c1
    BR.hit("IDENT.PASS")
    say("  -> IDENTITY: PASS")
    return True, deff_c1


# ============================================================================================ statistics
def _vals(rows, conv):
    if conv == "A":
        return [(r, r["right_A"]) for r in rows]
    return [(r, r["right_B"]) for r in rows if r["committed"]]


def boot_diff(rows1, rows2, conv, B, seed, unit="comp"):
    """acc(rows1) - acc(rows2), the resampling unit's groups resampled JOINTLY (unit 'comp' = CK-CLOSE components; 'iid' = matches).
    -> dict(point, se, n_lo, n_hi, p_lo, p_hi, se_lin, deff, n1, n2, k, reps). Convention A with unit comp == K.boot_diff."""
    if MUTANT == "match_level_boot":
        unit = "iid"
    a, b = _vals(rows1, conv), _vals(rows2, conv)
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        nan = float("nan")
        return dict(point=nan, se=nan, n_lo=nan, n_hi=nan, p_lo=nan, p_hi=nan, se_lin=nan, deff=nan, n1=n1, n2=n2, k=0)
    if unit == "iid":
        ga = list(range(n1)); gb = list(range(n1, n1 + n2)); keys = list(range(n1 + n2))
    else:
        ga = [r["comp"] for r, _ in a]; gb = [r["comp"] for r, _ in b]; keys = sorted(set(ga) | set(gb))
    pos = {k: i for i, k in enumerate(keys)}
    ng = len(keys)
    ia = np.array([pos[g] for g in ga], dtype=np.int64); ib = np.array([pos[g] for g in gb], dtype=np.int64)
    va = np.array([v for _, v in a], dtype=np.float64); vb = np.array([v for _, v in b], dtype=np.float64)
    s1 = np.bincount(ia, weights=va, minlength=ng); c1 = np.bincount(ia, minlength=ng).astype(np.float64)
    s2 = np.bincount(ib, weights=vb, minlength=ng); c2 = np.bincount(ib, minlength=ng).astype(np.float64)
    p1, p2 = s1.sum() / c1.sum(), s2.sum() / c2.sum()
    pt = float(p1 - p2)
    if MUTANT == "sign_swap":
        pt = -pt
    rng = np.random.default_rng(seed)
    reps = np.empty(B)
    for i in range(B):
        w = np.bincount(rng.integers(0, ng, ng), minlength=ng)
        reps[i] = (w @ s1) / (w @ c1) - (w @ s2) / (w @ c2)
    if MUTANT == "sign_swap":
        reps = -reps
    se = K._sd(reps)
    z = 1.6448536269514722 if MUTANT == "z90" else Z95
    pc = [float(x) for x in np.nanpercentile(reps, [2.5, 97.5])]
    # analytic DEFF (k46_repost D1 definition, for a difference of two ratio means)
    d = (s1 - p1 * c1) / n1 - (s2 - p2 * c2) / n2
    if MUTANT == "deff_one_group":
        d = (s1 - p1 * c1) / n1
    var_c = float(np.sum(d * d))
    var_i = float(np.sum((va - p1) ** 2)) / n1 ** 2 + float(np.sum((vb - p2) ** 2)) / n2 ** 2
    deff = var_c / var_i if var_i > 0 else float("nan")
    if MUTANT == "deff_boot":                       # the defect: a Monte-Carlo bootstrap ratio instead of the analytic DEFF
        rng2 = np.random.default_rng(seed)
        ri = np.empty(B)
        for i in range(B):
            ri[i] = va[rng2.integers(0, n1, n1)].mean() - vb[rng2.integers(0, n2, n2)].mean()
        deff = (se / K._sd(ri)) ** 2
    return dict(point=pt, se=se, n_lo=pt - z * se, n_hi=pt + z * se, p_lo=pc[0], p_hi=pc[1], se_lin=math.sqrt(var_c), deff=deff,
                n1=n1, n2=n2, k=ng, reps=reps, p1=float(p1), p2=float(p2))


def boot_one(rows, conv, B, seed):
    """One arm's accuracy, components resampled (K46-KEY-READ's boot_acc), with its normal / percentile 95% bounds."""
    pt, reps, n, ng = K.boot_acc(rows, conv, "comp", B, seed)
    se = K._sd(reps)
    if n == 0:
        return dict(point=pt, n=0, k=0, se=float("nan"), n_lo=float("nan"), n_hi=float("nan"), p_lo=float("nan"), p_hi=float("nan"))
    pc = [float(x) for x in np.nanpercentile(reps, [2.5, 97.5])]
    return dict(point=pt, n=n, k=ng, se=se, n_lo=pt - Z95 * se, n_hi=pt + Z95 * se, p_lo=pc[0], p_hi=pc[1])


def js1_word(lo, hi):
    """HELD iff the interval lies wholly above 0; FAILED (REVERSED) iff wholly below 0; UNDETERMINED otherwise (never parity)."""
    if G.as_bool(lo >= 0) if MUTANT == "bar_inclusive" else G.as_bool(lo > 0):
        return "HELD"
    if G.as_bool(hi < 0):
        return "FAILED"
    return "UNDETERMINED"


def decide(iv, form):
    if MUTANT == "normal_decides":
        form = "normal"
    if MUTANT == "form_ignored":
        form = "percentile" if form == "normal" else "normal"
    lo, hi = (iv["n_lo"], iv["n_hi"]) if form == "normal" else (iv["p_lo"], iv["p_hi"])
    return js1_word(lo, hi), (lo, hi)


def compute(kd_one, B, seed):
    C = cells(kd_one)
    S, U = js1_rows(kd_one)
    conv = "B" if MUTANT == "conv_b_decides" else "A"
    st = dict(B=B, seed=seed, nS=len(S), nU=len(U))
    st["js1"] = boot_diff(S, U, conv, B, seed)
    st["js1_B"] = boot_diff(S, U, "B", B, seed)
    st["accS"] = boot_one(S, "A", B, seed); st["accU"] = boot_one(U, "A", B, seed)
    st["accS_B"] = acc(S, "B"); st["accU_B"] = acc(U, "B")
    st["kish414"] = kish(S + U)
    wS, wU = (C[(0, 1)], C[(0, 0)]) if MUTANT != "js2_uses_right" else (C[(1, 1)], C[(1, 0)])
    st["js2"] = dict(S=(acc(wS, "A"), acc(wS, "B"), len({r["m"]["variant"] for r in wS})),
                     U=(acc(wU, "A"), acc(wU, "B"), len({r["m"]["variant"] for r in wU})))
    js3 = {}
    for k_, rr in C.items():
        n = len(rr)
        tie = sum(1 for r in rr if r["m"].get("combined") == "TIE")
        inv = sum(1 for r in rr if r["m"].get("combined") in ("INVALID", "NON_TERMINATED", "CONTENT_FILTER"))
        den = sum(1 for r in rr if r["committed"]) if MUTANT == "tie_share_committed" else n
        js3[k_] = dict(n=n, A=acc(rr, "A"), B=acc(rr, "B"), tie=(tie / den if den else float("nan")), inv=(inv / n if n else float("nan")),
                       variants=len({r["m"]["variant"] for r in rr}), qids=len({r["qid"] for r in rr}))
    st["js3"] = js3
    unc = C[(1, None)] + C[(0, None)]
    st["unc"] = dict(n=len(unc), A=acc(unc, "A"), B=acc(unc, "B"), qids=len({r["qid"] for r in unc}))
    return st


def in_range(x, lo, hi):
    return G.as_bool(x == x and lo <= x <= hi)


def brier(word):
    return sum((p - (1.0 if k == word else 0.0)) ** 2 for k, p in PROBS.items())


def verdict_lines(st, form, form_bracket):
    L = []
    say = L.append
    j = st["js1"]
    say("")
    say("=== VERDICTS (%s; registration %s) ===" % (TEST_ID, PROG))
    say("POPULATION: K46-KEY-READ's key-decidable ONE matches (the v2 recipe as ARCH-V2-PILOT-K46 posted it, ONE = the cached"
        " grok-reasoning-v0 solve; health / math; split pv2_41dbd3dbcd399df0, content-closed under CK-CLOSE-v2, residual disclosed),"
        " split by the judge model's own cached solve (grok-4-1-fast-non-reasoning, experiment_results/judge_solve/grok.db).")
    say("DENOMINATOR (JS1): %d covered reference-right matches (judge solved %d / unsolved %d) in %d CK-CLOSE components (Kish mean"
        " cluster size %.3f), of K46-KEY-READ's 544 key-decidable ONE matches." % (j["n1"] + j["n2"], j["n1"], j["n2"], st["kish414"][0],
                                                                               st["kish414"][1]))
    say("  acc(judge solved, reference right)   convention A %.4f on %d (%d components) | 95%% normal [%.4f, %.4f] percentile [%.4f, %.4f]"
        " | convention B %.4f on %d" % (st["accS"]["point"], st["accS"]["n"], st["accS"]["k"], st["accS"]["n_lo"], st["accS"]["n_hi"],
                                        st["accS"]["p_lo"], st["accS"]["p_hi"], st["accS_B"][0], st["accS_B"][1]))
    say("  acc(judge unsolved, reference right) convention A %.4f on %d (%d components) | 95%% normal [%.4f, %.4f] percentile [%.4f, %.4f]"
        " | convention B %.4f on %d" % (st["accU"]["point"], st["accU"]["n"], st["accU"]["k"], st["accU"]["n_lo"], st["accU"]["n_hi"],
                                        st["accU"]["p_lo"], st["accU"]["p_hi"], st["accU_B"][0], st["accU_B"][1]))
    say("JS1 Delta_S (convention A) = %+.4f | component-clustered (DECIDING unit; B %d, default_rng(%d), components resampled jointly)"
        " 95%% %s [%+.4f, %+.4f] (DECIDING, the form of record: %s) | beside, DESCRIPTIVE, NOT DECIDING: 95%% normal [%+.4f, %+.4f]"
        " (SE %.4f), percentile [%+.4f, %+.4f]"
        % (j["point"], st["B"], st["seed"], form, *((j["p_lo"], j["p_hi"]) if form == "percentile" else (j["n_lo"], j["n_hi"])),
           form_bracket or "form_bracket UNSET", j["n_lo"], j["n_hi"], j["se"], j["p_lo"], j["p_hi"]))
    jb = st["js1_B"]
    say("    beside (convention B, deciding nothing): Delta_S %+.4f on %d / %d committed, normal [%+.4f, %+.4f], percentile [%+.4f, %+.4f]"
        % (jb["point"], jb["n1"], jb["n2"], jb["n_lo"], jb["n_hi"], jb["p_lo"], jb["p_hi"]))
    neff_s = j["n1"] / j["deff"] if j["deff"] == j["deff"] and j["deff"] > 0 else float("nan")
    neff_u = j["n2"] / j["deff"] if j["deff"] == j["deff"] and j["deff"] > 0 else float("nan")
    mde = 2.80 * j["se"]
    say("    SUPPORT (MEASURED; DESCRIPTIVE, NOT DECIDING): DEFF %.3f (ANALYTIC: linearised component-clustered variance of Delta_S / iid variance; SE_lin %.4f)"
        " | n_eff %.1f solved / %.1f unsolved | SE %.4f (component bootstrap) | MDE80 = 2.80 x SE = %.4f"
        % (j["deff"], j["se_lin"], neff_s, neff_u, j["se"], mde))
    say("    SUPPORT (registered, (b)-(f)): DEFF %.3f TRANSPORTED from K46-KEY-READ C1 (n_eff %.0f / %.0f), SE %.4f, MDE80 %.3f, interval"
        " reachable where |Delta_S| > %.3f; VERDICT LINE: JS1 %s at its prediction (|%+.2f| vs MDE80 %.3f); K46 C1 DEFF reproduced"
        " here %.3f" % (PLAN_IN["deff"], PLAN["neff_s"], PLAN["neff_u"], PLAN["se"], PLAN["mde"], PLAN["reach"], PLAN["word"],
                        PLAN_IN["pred"], PLAN["mde"], st.get("deff_c1", float("nan"))))
    inside = G.as_bool(abs(j["point"]) < mde)
    BR.hit("MEAS.INSIDE" if inside else "MEAS.OUTSIDE")
    say("    MEASURED SUPPORT vs the observed point: |Delta_S| %.4f %s the measured MDE80 %.4f (%s)"
        % (abs(j["point"]), "<" if inside else ">=", mde, "inside: DESCRIPTIVE-ONLY at the observed point" if inside
           else "outside: the observed contrast exceeds the 80%-power detectable size"))
    BR.hit("FORM." + form)
    w, (lo, hi) = decide(j, form)
    other = "percentile" if form == "normal" else "normal"
    w_o = js1_word(*((j["n_lo"], j["n_hi"]) if other == "normal" else (j["p_lo"], j["p_hi"])))
    agree = w == w_o
    BR.hit("FORMS.AGREE" if agree else "FORMS.DISAGREE")
    say("  FORMS: %s (of record) reads %s on [%+.4f, %+.4f]; %s (beside; DESCRIPTIVE, NOT DECIDING) reads %s -> %s" % (
        form, w, lo, hi, other, w_o, "AGREE" if agree else "DISAGREE (the form of record decides; the disagreement is reported)"))
    BR.hit("JS1." + w)
    say("  JS1 -> %s (HELD iff the 95%% interval lies wholly above 0; FAILED (REVERSED) iff wholly below 0; UNDETERMINED otherwise,"
        " never parity)" % w)
    BR.hit("READ." + w)
    if w == "HELD":
        say("  READING: " + READING["HELD"] % (j["point"], form, lo, hi))
    elif w == "UNDETERMINED":
        say("  READING: " + READING["UNDETERMINED"] % (j["n1"] + j["n2"]) + " (never \"judge ability makes no difference\")")
    else:
        say("  READING: " + READING["FAILED"])
    say("JS2 (DESCRIPTIVE-ONLY; the Krumdick reconciliation; never a criterion, never \"shown\"): covered reference-wrong matches")
    for lab, k_ in (("judge solved", "S"), ("judge unsolved", "U")):
        (a_, na), (b_, nb), nv = st["js2"][k_]
        say("  acc(%-14s, reference wrong) convention A %s on %d in %d variants | convention B %s on %d" % (
            lab, "%.4f" % a_ if na else "n/a", na, nv, "%.4f" % b_ if nb else "n/a", nb))
    say("JS3 (DESCRIPTIVE): the full 2 x 2 (reference right / wrong x judge solved / unsolved), key-decidable ONE matches")
    for (v0, sv), x in sorted(st["js3"].items(), key=lambda kv: (-kv[0][0], {1: 0, 0: 1, None: 2}[kv[0][1]])):
        say("  reference %-5s judge %-9s n %4d (%3d variants, %3d qids) | convention A %s | convention B %s on %d | TIE share %s |"
            " INVALID-type share %s" % ("right" if v0 == 1 else "wrong", {1: "solved", 0: "unsolved", None: "UNCOVERED"}[sv], x["n"],
                                        x["variants"], x["qids"], "%.4f" % x["A"][0] if x["n"] else "n/a",
                                        "%.4f" % x["B"][0] if x["B"][1] else "n/a", x["B"][1],
                                        "%.4f" % x["tie"] if x["n"] else "n/a", "%.4f" % x["inv"] if x["n"] else "n/a"))
    u = st["unc"]
    say("  UNCOVERED beside (K46-KEY-READ's rows; qids absent from grok.db; never counted as unsolved): n %d on %d qids | convention A"
        " %s | convention B %s on %d" % (u["n"], u["qids"], "%.4f" % u["A"][0] if u["n"] else "n/a",
                                         "%.4f" % u["B"][0] if u["B"][1] else "n/a", u["B"][1]))
    say("  " + PFAM)
    say("  No model-edge count is computed, so no wrong(established) count arises.")
    say("PREDICTIONS (HELD iff the observed point lies in the registered 80% interval, endpoints included):")
    scored = (("P1", j["point"], "Delta_S (convention A)"), ("P2a", st["accS"]["point"], "acc(solved, reference right)"),
              ("P2b", st["accU"]["point"], "acc(unsolved, reference right)"),
              ("P3a", st["js2"]["U"][0][0] if st["js2"]["U"][0][1] else None, "acc(unsolved, reference wrong)"),
              ("P3b", st["js2"]["S"][0][0] if st["js2"]["S"][0][1] else None, "acc(solved, reference wrong)"))
    for p, x, what in scored:
        lo_, hi_ = PRED[p]
        if x is None:
            BR.hit(p + ".NOT_SCOREABLE")
            say("  %s %s predicted [%s, %s], observed none (empty cell) -> NOT SCOREABLE" % (p, what, lo_, hi_))
            continue
        ww = "HELD" if in_range(x, lo_, hi_) else "FAILED"
        BR.hit("%s.%s" % (p, ww))
        say("  %s %s predicted [%s, %s], observed %.4f -> %s" % (p, what, lo_, hi_, x, ww))
    say("  P1 word probabilities HELD 0.15 / FAILED 0.05 / UNDETERMINED 0.80; realised %s; Brier %.4f" % (w, brier(w)))
    say("FALSIFIER:")
    fired = (w == "HELD") if MUTANT != "falsifier_on_undet" else (w != "FAILED")
    if fired:
        BR.hit("F.FIRED")
        say("  F-JS FIRED (JS1 HELD). " + FALSIFIER)
    else:
        BR.hit("F.NOT_FIRED")
        say("  F-JS NOT FIRED (JS1 %s); a non-fire is not shown parity." % w)
    say(NOT_SHOW)
    return L, w


# ============================================================================================ the mode
def header(cfg, say):
    say("POOL %s (%s; %s; the first line of every mode)" % (cfg.pool, TEST_ID, cfg.cv))
    say("%s | registration %s | record docs/agents/results/JUDGE-SOLVED-SPLIT.json | zero calls" % (TEST_ID, PROG))
    say("  " + G.identity_line(os.path.abspath(__file__)))
    say("  " + G.identity_line(G.__file__))
    k46_identity(say)
    say("  MUTANT %r (must be None in every real mode)" % MUTANT)
    say("  WORDS: the store's split is 'content-closed under CK-CLOSE-v2 (residual disclosed)'; 'solved' = a SEPARATE cached solve"
        " (judge_solve_map.py, max_tokens 4096), measured with error (5.7% retest noise, DECOMP); the covered subset is not a random"
        " sample of the 544.")
    say("PRECONDITIONS (None REFUSES --run):")
    for k in ("interval_form", "form_bracket"):
        say("  %-14s %r" % (k, cfg.jpre.get(k)))
    miss = missing_preconditions(cfg.jpre)
    say("  -> %s" % ("ALL SET" if not miss else "%d UNSET: %s" % (len(miss), "; ".join(miss))))
    return miss


def write_outcome(path, text):
    if MUTANT == "write_w":
        os.makedirs(os.path.dirname(path), exist_ok=True)
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
    B, seed = cfg.reg["B"], cfg.reg["seed"]
    st_tw, s_before = K.open_store(cfg, say)
    run_ids, M, verd = K.read_store(st_tw)
    st_tw.close()
    ok_s = K.after(cfg.store_path, s_before, "store", say)
    vw, v_before = K.open_view(cfg, say)
    var_item, side = K.view_structure(vw, cfg.cv)
    K.attach_structure(M, var_item, side)
    K.identity_gate(cfg, run_ids, M, verd, say, refuse=not dry)
    vw.unseal("JUDGE-SOLVED-SPLIT %s: K46-KEY-READ's key read is of record (b61e496); %s" % (
        "dry-run" if dry else "run", "counts only, no accuracy by solve status" if dry else "the registered readout"))
    key, refused, refs, missing_ref = K.read_keys(vw, cfg.cv, M, K.VINTAGE)
    qid_of = read_ref_qids(vw, cfg.cv, M, K.VINTAGE)
    vw.close()
    ok_v = K.after(cfg.eval_path, v_before, "eval_view", say)
    solved, n_rows, ok_g = read_solves(cfg, set(qid_of.values()), say)
    say("JOIN: K46 schedule.reference_row_id -> eval_view reference (variant, %s, source_key) -> legacy_qid -> grok.db question_id |"
        " sides refused %s (expected 0); ONE references %d, missing %d; distinct ONE qids %d" % (
            K.VINTAGE, dict(refused) or 0, len(refs), missing_ref, len(set(qid_of.values()))))
    rows = K.classify(M, key, refs)
    attach_solve(rows, qid_of, solved)
    kd_one = [r for r in rows if r["kd"] and r["klass"] == "ONE"]
    C = cells(kd_one)
    S, U = js1_rows(kd_one)
    ok_id, deff_c1 = identity_js(cfg, kd_one, C, n_rows, B, seed, say, refuse=not dry)
    nk, km = kish(S + U)
    say("DENOMINATORS: covered %d of %d key-decidable ONE matches (uncovered %d on %d qids, out of JS1 / JS2) | reference right %d"
        " covered of %d (judge solved %d / unsolved %d) | reference wrong %d covered of %d (judge solved %d in %d variants / unsolved"
        " %d in %d variants) | JS1's %d matches sit in %d CK-CLOSE components, Kish mean cluster size %.3f" % (
            sum(1 for r in kd_one if r["solved"] is not None), len(kd_one), len(C[(1, None)]) + len(C[(0, None)]),
            len({r["qid"] for r in C[(1, None)] + C[(0, None)]}), len(C[(1, 1)]) + len(C[(1, 0)]),
            sum(1 for r in kd_one if r["v0"] == 1), len(C[(1, 1)]), len(C[(1, 0)]), len(C[(0, 1)]) + len(C[(0, 0)]),
            sum(1 for r in kd_one if r["v0"] == 0), len(C[(0, 1)]), len({r["m"]["variant"] for r in C[(0, 1)]}), len(C[(0, 0)]),
            len({r["m"]["variant"] for r in C[(0, 0)]}), len(S) + len(U), nk, km))
    say("  registered: 446 / 544; right 414 of 506 (226 / 188); wrong 32 of 38 (5 in 2 variants / 27 in 7 variants); 98 uncovered on"
        " 29 qids; 160 components for the 544, Kish m 4.934 (registration DATA / Support (a))")
    say("SUPPORT (registered plan, recomputed): DEFF %.3f transported, n_eff %.1f / %.1f, SE %.4f, MDE80 %.3f, reachable |Delta_S| >"
        " %.3f; JS1 %s at its prediction" % (PLAN_IN["deff"], PLAN["neff_s"], PLAN["neff_u"], PLAN["se"], PLAN["mde"], PLAN["reach"],
                                              PLAN["word"]))
    if not dry:                                     # the solve-split read starts only after the identity precondition passed
        G.read_marker(cfg.mark, "JUDGE-SOLVED-SPLIT: the solve-split read started\n")
    if dry:
        if MUTANT == "dry_writes":
            write_outcome(cfg.out, "\n".join(lines))
        say("PLANNED: B = %d, default_rng(%d); JS1 by the %s form (form_bracket %r); outputs %s, %s (write-once)" % (
            B, seed, cfg.jpre.get("interval_form"), cfg.jpre.get("form_bracket"), cfg.out, cfg.mark))
        say("DRY-RUN: identity %s; zero calls; nothing written; no accuracy by solve status computed or printed." % (
            "PASS" if ok_id else "FAIL"))
        return None
    st = compute(kd_one, B, seed)
    st["deff_c1"] = deff_c1
    L, word = verdict_lines(st, cfg.jpre["interval_form"], cfg.jpre["form_bracket"])
    for l in L:
        say(l)
    if not (ok_s and ok_v and ok_g):
        write_outcome(cfg.out.replace(".txt", "_VOID.txt"), "\n".join(lines) + "\n[VOID] a sha differs after the read\n")
        raise SystemExit("[PIN] a sha differs after the read: written to _VOID, not to the file of record")
    write_outcome(cfg.out, "\n".join(lines) + "\n")
    print("OUTCOME written write-once: %s" % cfg.out)
    return dict(st=st, word=word, text="\n".join(lines), rows=rows)


# ============================================================================================ selftest
SCEN = {   # P(judge picks the key side | committed), by (reference correct, judge solved); None = uncovered
    "held": {(1, 1): 0.99, (1, 0): 0.55, (1, None): 0.80, (0, 1): 0.70, (0, 0): 0.10, (0, None): 0.30},
    "failed": {(1, 1): 0.55, (1, 0): 0.99, (1, None): 0.80, (0, 1): 0.70, (0, 0): 0.10, (0, None): 0.30},
    "undet": {(1, 1): 0.90, (1, 0): 0.90, (1, None): 0.80, (0, 1): 0.05, (0, 0): 0.10, (0, None): 0.30}}


def _mk_fixture(tmp, name, scen, wrong_solved_empty=False, seed=11):
    """Synthetic K46 store (data_v2.verdicts DDL), sealed eval view (reference carries legacy_qid; response legacy_qid lives in another
    id space), and a solve DB. Returns (cfg, truth) where truth carries every per-match fact for the independent recomputation."""
    from data_v2 import verdicts as dv2v
    d = os.path.join(tmp, name); os.makedirs(d)
    rs = np.random.RandomState(seed)
    models = ["m%02d" % i for i in range(8)]
    items = []
    for anchor, n in (("health", 60), ("math", 100)):
        for j in range(n):
            iid = "i:%s%03d" % (anchor[0], j)
            klass = "ONE" if j % 8 else "NONE"
            items.append(dict(id=iid, var="v:" + iid[2:], comp="c:%s%03d" % (anchor[0], j // 2 * 2), anchor=anchor, klass=klass,
                              stem="s:" + iid[2:]))
    vp = os.path.join(d, "eval.db")
    c = dv2ro.create_new(vp)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT INTO meta VALUES ('view_kind', 'eval')")
    c.execute("CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT, side TEXT, stratum_source TEXT, stratum_domain TEXT,"
              " corpora TEXT)")
    c.execute("CREATE TABLE variant (corpus_version TEXT, variant_id TEXT, item_id TEXT, PRIMARY KEY (corpus_version, variant_id))")
    c.execute("CREATE TABLE response (corpus_version TEXT, response_id TEXT, model TEXT, legacy_qid INTEGER, seen_ck TEXT, item_id TEXT,"
              " is_correct INTEGER, output_zlib BLOB, gt_raw TEXT, pred TEXT, PRIMARY KEY (corpus_version, response_id))")
    c.execute("CREATE TABLE reference (corpus_version TEXT, variant_id TEXT, vintage TEXT, source_key TEXT, item_id TEXT, legacy_qid"
              " INTEGER, correct INTEGER, PRIMARY KEY (corpus_version, variant_id, vintage, source_key))")
    truth, k = {}, 0
    qid, v0, solved = {}, {}, {}
    one_items = [it for it in items if it["klass"] == "ONE"]
    for i, it in enumerate(items):
        c.execute("INSERT INTO side VALUES (?,?,?,?,?,?)", (it["id"], it["comp"], "EVAL", "MMLU_PRO", it["anchor"].title(), "mmlu"))
        c.execute("INSERT INTO variant VALUES (?,?,?)", ("mmlu", it["var"], it["id"]))
        for mo in models:
            k += 1
            truth[(mo, it["var"])] = int(rs.rand() < 0.5)
            c.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?)", ("mmlu", "x%d" % k, mo, 50000 + k, it["var"], it["id"],
                                                                           truth[(mo, it["var"])], b"z", "g", "p"))
        if it["klass"] == "ONE":
            q = 1000 + 3 * i
            qid[it["var"]] = q
            v0[it["var"]] = int(rs.rand() < 0.80)
            c.execute("INSERT INTO reference VALUES (?,?,?,?,?,?,?)", ("mmlu", it["var"], K.VINTAGE, "qid:%d" % q, it["id"], q,
                                                                      v0[it["var"]]))
            j1 = one_items.index(it)
            if j1 % 9 == 4:
                solved[it["var"]] = None                                  # uncovered: no grok.db row
            elif wrong_solved_empty and v0[it["var"]] == 0:
                solved[it["var"]] = 0
            else:
                solved[it["var"]] = int(rs.rand() < 0.55)
    c.commit()
    vsha = dv2ro.seal(c, vp, "selftest eval view")["sha256_bytes"]
    gp = os.path.join(d, "grok.db")
    g = dv2ro.create_new(gp)
    g.execute("CREATE TABLE answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, tokens INTEGER,"
              " latency REAL, ts REAL)")
    for var, s in solved.items():
        if s is not None:
            g.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?)", (qid[var], "A", "B", s, "r", 1, 0.1, 0.0))
    for x in range(7):                                                    # unrelated solves (outside the joined qids)
        g.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?)", (90000 + x, "A", "B", 1, "r", 1, 0.1, 0.0))
    g.commit(); g.close()
    os.chmod(gp, stat.S_IREAD)
    gsha = G.sha256_file(gp)
    sp = os.path.join(d, "store.db")
    s = dv2ro.create_new(sp)
    s.executescript(dv2v.DDL)
    s.execute("INSERT INTO run_meta VALUES ('schema_id', ?)", (dv2ro.RUN_SCHEMA_ID,))
    matches, mid = [], 0
    for it in items:
        for rep_ in range(4):
            if rep_ < 3:                                                  # key-decidable when the truth allows it
                cand = [(a, b) for a in range(8) for b in range(8) if a != b and truth[(models[a], it["var"])] != truth[(models[b], it["var"])]]
                a, b = cand[rs.randint(len(cand))] if cand else tuple(rs.choice(8, 2, replace=False))
            else:
                a, b = rs.choice(8, 2, replace=False)
            mid += 1
            matches.append(dict(mid="M%05d" % mid, it=it, a=models[a], b=models[b]))
    for m in matches:
        it = m["it"]
        ref = ("ref:%s|%s|qid:%d" % (it["var"], K.VINTAGE, qid[it["var"]])) if it["klass"] == "ONE" else None
        m["ref"] = ref
        for order in (1, 2):
            first, second = (m["a"], m["b"]) if order == 1 else (m["b"], m["a"])
            s.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                "RUN", m["mid"], order, 0, it["var"], it["stem"], it["comp"], m["a"], m["b"], first, second, "h1", "h2", ref,
                K.VINTAGE if ref else None, None))
    P = SCEN[scen]
    for m in matches:
        it = m["it"]
        ka, kb = truth[(m["a"], it["var"])], truth[(m["b"], it["var"])]
        r = rs.rand()
        good = "A" if ka >= kb else "B"
        if r < 0.015:
            comb = ("INVALID", "INVALID")
        elif r < 0.05:
            comb = ("A", "B")
        else:
            p = P[(v0[it["var"]], solved[it["var"]])] if it["klass"] == "ONE" else 0.7
            pick = good if rs.rand() < p else ("B" if good == "A" else "A")
            comb = (pick, pick)
        m["comb"] = "INVALID" if comb[0] == "INVALID" else ("TIE" if comb[0] != comb[1] else comb[0])
        for order, vc in ((1, comb[0]), (2, comb[1])):
            if vc in ("A", "B"):
                shown_first = m["a"] if order == 1 else m["b"]
                vote = "FIRST" if (m["a"] if vc == "A" else m["b"]) == shown_first else "SECOND"
            else:
                vote = vc
            s.execute("INSERT INTO verdict (run_id, match_id, presentation_order, draw_index, vote, raw_text, parse_version, payload_sha256,"
                      " body_zlib, body_codec, judge_requested, provider, response_model, finish_reason, max_tokens, temperature_sent,"
                      " temperature_label, content_filter, n_attempts, prompt_template_blob, script_blob, combiner_blob,"
                      " reference_row_id, reference_vintage, stem_key, pool_id, created_at) VALUES"
                      " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                          "RUN", m["mid"], order, 0, vote, "raw", "p1", "ps", b"z", "zlib", "j", "prov", K.IDENTITY["response_model"],
                          "stop", 8192, None, "omitted", 0, 1, "pt", "sb", "cb", m["ref"], K.VINTAGE if m["ref"] else None, it["stem"],
                          "pv", "t"))
    s.commit(); s.close()
    os.chmod(sp, stat.S_IREAD)
    ssha = G.sha256_file(sp)
    comb = Counter(m["comb"] for m in matches)
    one_s = sum(1 for m in matches if m["it"]["klass"] == "ONE")
    kident = dict(scheduled=len(matches), order_verdicts=2 * len(matches), finish_stop=2 * len(matches),
                  response_model=K.IDENTITY["response_model"], usable=comb["A"] + comb["B"] + comb["TIE"], A=comb["A"], B=comb["B"],
                  TIE=comb["TIE"], INVALID=comb["INVALID"],
                  invalid_none=sum(1 for m in matches if m["comb"] == "INVALID" and m["it"]["klass"] == "NONE"),
                  one_sched=one_s, none_sched=len(matches) - one_s,
                  none_usable=sum(1 for m in matches if m["it"]["klass"] == "NONE" and m["comb"] != "INVALID"),
                  arena12_sched=sum(1 for m in matches if m["a"] in models[:4] and m["b"] in models[:4]),
                  arena12_usable=sum(1 for m in matches if m["a"] in models[:4] and m["b"] in models[:4] and m["comb"] != "INVALID"),
                  variants=len(items), anchors={"health": 60, "math": 100}, run_ids=("RUN",))
    T = dict(matches=matches, truth=truth, qid=qid, v0=v0, solved=solved, n_solve_rows=sum(1 for v in solved.values() if v is not None) + 7)
    nv = naive(T)
    ident = dict(c1_point=round(nv["c1"][0], 4), c1_n=nv["c1"][1], c1_comp=nv["c1_comp"], right_point=round(nv["right"][0], 4),
                 right_n=nv["right"][1], wrong_point=round(nv["wrong"][0], 4), wrong_n=nv["wrong"][1], covered=nv["covered"],
                 right_solved=nv["cell"][(1, 1)]["n"], right_unsolved=nv["cell"][(1, 0)]["n"], wrong_solved=nv["cell"][(0, 1)]["n"],
                 wrong_unsolved=nv["cell"][(0, 0)]["n"])
    flags = dict(right_cov=nv["cell"][(1, 1)]["n"] + nv["cell"][(1, 0)]["n"], wrong_cov=nv["cell"][(0, 1)]["n"] + nv["cell"][(0, 0)]["n"],
                 wrong_solved_variants=nv["cell"][(0, 1)]["variants"], wrong_unsolved_variants=nv["cell"][(0, 0)]["variants"],
                 uncovered=nv["unc"]["n"], uncovered_qids=nv["unc"]["qids"], solve_rows=T["n_solve_rows"], c1_deff=-1.0)
    out = os.path.join(d, "out")
    cfg = Cfg(store_path=sp, store_sha=ssha, eval_path=vp, eval_sha=vsha, pool="pv_m", cv="mmlu", identity=kident, reg=dict(K.REG, B=400),
              pre=dict(K.PRECONDITIONS), arena12=frozenset(models[:4]), solve_path=gp, solve_sha=gsha, ident=ident, flags=flags,
              jpre=dict(PRECONDITIONS), out=os.path.join(out, "outcome.txt"),
              mark=os.path.join(out, "judge_solved_split.READ_STARTED"))
    return cfg, T, nv


def naive(T):
    """INDEPENDENT recomputation from the fixture's own truth (no import of the script's row logic)."""
    cell = defaultdict(lambda: dict(rows=[], vars=set(), qids=set()))
    kd = []
    for m in T["matches"]:
        it = m["it"]
        if it["klass"] != "ONE":
            continue
        ka, kb = T["truth"][(m["a"], it["var"])], T["truth"][(m["b"], it["var"])]
        if ka + kb != 1:
            continue
        side = "A" if ka == 1 else "B"
        r = dict(comp=it["comp"], right_A=int(m["comb"] == side), committed=m["comb"] in ("A", "B"),
                 right_B=int(m["comb"] == side) if m["comb"] in ("A", "B") else None, tie=m["comb"] == "TIE",
                 inv=m["comb"] == "INVALID", var=it["var"], qid=T["qid"][it["var"]])
        kd.append(r)
        key = (T["v0"][it["var"]], T["solved"][it["var"]])
        cell[key]["rows"].append(r); cell[key]["vars"].add(it["var"]); cell[key]["qids"].add(r["qid"])
    mean = lambda xs: (sum(xs) / len(xs)) if xs else float("nan")
    A = lambda rows: (mean([r["right_A"] for r in rows]), len(rows))
    Bc = lambda rows: (mean([r["right_B"] for r in rows if r["committed"]]), sum(1 for r in rows if r["committed"]))
    out = dict(kd=kd, c1=A(kd), c1_comp=len({r["comp"] for r in kd}), right=A(sum((cell[(1, s)]["rows"] for s in (1, 0, None)), [])),
               wrong=A(sum((cell[(0, s)]["rows"] for s in (1, 0, None)), [])), covered=sum(len(cell[(v, s)]["rows"]) for v in (0, 1) for s in (0, 1)),
               cell={}, rows={})
    for v in (0, 1):
        for s in (1, 0, None):
            rr = cell[(v, s)]["rows"]
            out["cell"][(v, s)] = dict(n=len(rr), A=A(rr), B=Bc(rr), tie=(sum(r["tie"] for r in rr) / len(rr)) if rr else float("nan"),
                                       inv=(sum(r["inv"] for r in rr) / len(rr)) if rr else float("nan"),
                                       variants=len(cell[(v, s)]["vars"]), qids=len(cell[(v, s)]["qids"]))
            out["rows"][(v, s)] = rr
    unc = out["rows"][(1, None)] + out["rows"][(0, None)]
    out["unc"] = dict(n=len(unc), A=A(unc), B=Bc(unc), qids=len({r["qid"] for r in unc}))
    S, U = out["rows"][(1, 1)], out["rows"][(1, 0)]
    out["delta"] = A(S)[0] - A(U)[0]
    out["delta_B"] = Bc(S)[0] - Bc(U)[0]
    # independent analytic DEFF of the difference
    comps = sorted({r["comp"] for r in S + U})
    p1, p2 = A(S)[0], A(U)[0]
    n1, n2 = len(S), len(U)
    var_c = 0.0
    for cpt in comps:
        e1 = sum(r["right_A"] - p1 for r in S if r["comp"] == cpt) / n1
        e2 = sum(r["right_A"] - p2 for r in U if r["comp"] == cpt) / n2
        var_c += (e1 - e2) ** 2
    var_i = sum((r["right_A"] - p1) ** 2 for r in S) / n1 ** 2 + sum((r["right_A"] - p2) ** 2 for r in U) / n2 ** 2
    out["deff"] = var_c / var_i
    cc = Counter(r["comp"] for r in S + U)
    out["kish"] = (len(cc), sum(v * v for v in cc.values()) / (n1 + n2))
    return out


def selftest():
    global MUTANT
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="jss_selftest_")
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok))); print("  [%s] %s" % ("PASS" if ok else "FAIL", name), flush=True)
    counter = [0]
    def fx(scen="held", **kw):
        counter[0] += 1
        return _mk_fixture(tmp, "f%d" % counter[0], scen, **kw)
    def run(cfg, dry=False):
        with contextlib.redirect_stdout(io.StringIO()) as so:
            R = mode(cfg, dry)
        return R, so.getvalue()
    def refusal(cfg, dry=False):
        try:
            run(cfg, dry)
        except SystemExit as e:
            return str(e)
        return None
    try:
        # ---------------------------------------------------------------- registered plan, by value
        check("PLAN (registration Support (c)-(f)): n_eff %.1f / %.1f == 82.9 / 68.9; SE %.4f == 0.0433; MDE80 %.3f == 0.121; reach"
              " %.3f == 0.085; DESCRIPTIVE-ONLY" % (PLAN["neff_s"], PLAN["neff_u"], PLAN["se"], PLAN["mde"], PLAN["reach"]),
              round(PLAN["neff_s"], 1) == 82.9 and round(PLAN["neff_u"], 1) == 68.9 and round(PLAN["se"], 4) == 0.0433
              and round(PLAN["mde"], 3) == 0.121 and round(PLAN["reach"], 3) == 0.085 and PLAN["word"] == "DESCRIPTIVE-ONLY")
        check("plan_js1 SCOREABLE branch (|pred| 0.2 > MDE)", plan_js1(2.727, 226, 188, 0.95, 0.90, 0.2)["word"] == "SCOREABLE")
        check("PRECONDITIONS of record: interval_form 'percentile' (as registered), form_bracket names the registration -> none missing",
              PRECONDITIONS["interval_form"] == "percentile" and PRECONDITIONS["form_bracket"].startswith("the registration itself:")
              and "95% percentile intervals" in PRECONDITIONS["form_bracket"] and missing_preconditions(PRECONDITIONS) == [])
        check("IDENT of record = the registration's identity numbers", IDENT == dict(
            c1_point=0.8787, c1_n=544, c1_comp=160, right_point=0.9249, right_n=506, wrong_point=0.2632, wrong_n=38, covered=446,
            right_solved=226, right_unsolved=188, wrong_solved=5, wrong_unsolved=27))
        # ---------------------------------------------------------------- dry-run
        cfg, T, nv = fx("held")
        R, txt = run(cfg, True)
        exp_den = ("DENOMINATORS: covered %d of %d key-decidable ONE matches (uncovered %d on %d qids, out of JS1 / JS2) | reference right"
                   " %d covered of %d (judge solved %d / unsolved %d) | reference wrong %d covered of %d (judge solved %d in %d variants /"
                   " unsolved %d in %d variants) | JS1's %d matches sit in %d CK-CLOSE components, Kish mean cluster size %.3f" % (
                       nv["covered"], nv["c1"][1], nv["unc"]["n"], nv["unc"]["qids"], nv["cell"][(1, 1)]["n"] + nv["cell"][(1, 0)]["n"],
                       nv["right"][1], nv["cell"][(1, 1)]["n"], nv["cell"][(1, 0)]["n"], nv["cell"][(0, 1)]["n"] + nv["cell"][(0, 0)]["n"],
                       nv["wrong"][1], nv["cell"][(0, 1)]["n"], nv["cell"][(0, 1)]["variants"], nv["cell"][(0, 0)]["n"],
                       nv["cell"][(0, 0)]["variants"], nv["cell"][(1, 1)]["n"] + nv["cell"][(1, 0)]["n"], nv["kish"][0], nv["kish"][1]))
        check("dry-run: returns None; writes neither outcome nor marker; first line POOL; identity PASS",
              R is None and not os.path.exists(cfg.out) and not os.path.exists(cfg.mark) and txt.startswith("POOL pv_m")
              and "-> IDENTITY: PASS" in txt and "DRY-RUN: identity PASS" in txt)
        check("dry-run: the DENOMINATORS line equals the independent count (%d / %d; right %d / %d; wrong %d / %d)" % (
            nv["covered"], nv["c1"][1], nv["cell"][(1, 1)]["n"], nv["cell"][(1, 0)]["n"], nv["cell"][(0, 1)]["n"], nv["cell"][(0, 0)]["n"]),
            exp_den in txt)
        check("dry-run: no accuracy by solve status printed (no JS1 / JS2 / P lines, no 'acc(')",
              "JS1 Delta_S" not in txt and "acc(" not in txt and "PREDICTIONS" not in txt and "JS2 (" not in txt and "Brier" not in txt)
        check("dry-run: the registered denominators are printed beside", "registered: 446 / 544; right 414 of 506 (226 / 188)" in txt)
        check("dry-run: k46_key_read.py blob pinned and printed", "pinned blob:%s" % K46_BLOB in txt and ("blob:%s" % K46_BLOB) in txt)
        # ---------------------------------------------------------------- refusals
        c0, _, _ = fx("held"); c0.jpre = dict(PRECONDITIONS, form_bracket=None)
        e = refusal(c0)
        check("--run refuses with form_bracket unset (the precondition of record) BEFORE any read",
              e is not None and "[PRECONDITION]" in e and "form_bracket" in e and not os.path.exists(c0.mark))
        c0b, _, _ = fx("held"); c0b.jpre = dict(interval_form="bootstrap-t", form_bracket="X")
        e = refusal(c0b)
        check("--run refuses an interval_form outside (normal, percentile)", e is not None and "interval_form" in e)
        for fld, delta in (("c1_point", 0.0001), ("right_solved", 1), ("wrong_unsolved", 1), ("covered", -1), ("c1_comp", 1)):
            ci, _, _ = fx("held"); ci.ident = dict(ci.ident, **{fld: ci.ident[fld] + delta})
            e = refusal(ci)
            check("identity: %s perturbed by %s refuses before any readout (no outcome)" % (fld, delta),
                  e is not None and "[IDENTITY]" in e and not os.path.exists(ci.out))
        cs, _, _ = fx("held"); cs.solve_sha = "0" * 64
        e = refusal(cs)
        check("a solve DB sha other than the pin refuses", e is not None and "[PIN] solve DB" in e)
        # ---------------------------------------------------------------- the run, HELD fixture: values vs the independent recomputation
        R, txt = run(cfg)
        st = R["st"]; j = st["js1"]
        ind = K.boot_diff(nv["rows"][(1, 1)], nv["rows"][(1, 0)], cfg.reg["B"], cfg.reg["seed"])
        se_ind = K._sd(ind[1])
        check("HELD fixture: Delta_S %+.6f == naive %+.6f; n %d / %d == naive" % (j["point"], nv["delta"], j["n1"], j["n2"]),
              abs(j["point"] - nv["delta"]) < 1e-12 and j["n1"] == nv["cell"][(1, 1)]["n"] and j["n2"] == nv["cell"][(1, 0)]["n"])
        check("JS1 SE %.6f == K46-KEY-READ's boot_diff on the independent rows (components jointly, same seed) %.6f" % (j["se"], se_ind),
              abs(j["se"] - se_ind) < 1e-12 and abs(ind[0] - nv["delta"]) < 1e-12)
        check("normal bounds = point +- 1.959964 x SE (printed)", abs(j["n_lo"] - (nv["delta"] - Z95 * se_ind)) < 1e-12 and
              ("95%% normal [%+.4f, %+.4f] (SE %.4f)" % (nv["delta"] - Z95 * se_ind, nv["delta"] + Z95 * se_ind, se_ind)) in txt)
        pc = np.nanpercentile(ind[1], [2.5, 97.5])
        check("percentile bounds = the 2.5 / 97.5 percentiles of the independent replicates", abs(j["p_lo"] - pc[0]) < 1e-12 and abs(j["p_hi"] - pc[1]) < 1e-12)
        check("analytic DEFF %.6f == the independent linearised ratio %.6f (printed 'DEFF %.3f (ANALYTIC')" % (j["deff"], nv["deff"], nv["deff"]),
              abs(j["deff"] - nv["deff"]) < 1e-9 and ("DEFF %.3f (ANALYTIC" % nv["deff"]) in txt)
        check("n_eff printed = n / analytic DEFF", ("n_eff %.1f solved / %.1f unsolved" % (j["n1"] / nv["deff"], j["n2"] / nv["deff"])) in txt)
        check("Kish of JS1's matches == independent (%d components, %.3f)" % nv["kish"], st["kish414"][0] == nv["kish"][0]
              and abs(st["kish414"][1] - nv["kish"][1]) < 1e-12)
        check("printed JS1 line carries the naive point", ("JS1 Delta_S (convention A) = %+.4f" % nv["delta"]) in txt)
        check("HELD fixture: JS1 -> HELD; reading HELD sentence; F-JS FIRED", "  JS1 -> HELD (" in txt and R["word"] == "HELD"
              and "READING: on the content-closed v2 split, with a right reference, the recipe is more key-accurate" in txt
              and "F-JS FIRED (JS1 HELD)" in txt)
        check("convention B beside == naive (%+.4f)" % nv["delta_B"], abs(st["js1_B"]["point"] - nv["delta_B"]) < 1e-12)
        check("acc(solved / unsolved, right) printed == naive", ("convention A %.4f on %d" % nv["cell"][(1, 1)]["A"]) in txt
              and ("convention A %.4f on %d" % nv["cell"][(1, 0)]["A"]) in txt)
        js2s, js2u = nv["cell"][(0, 1)], nv["cell"][(0, 0)]
        check("JS2 printed == naive (solved %.4f on %d in %d variants; unsolved %.4f on %d in %d)" % (
            js2s["A"][0], js2s["n"], js2s["variants"], js2u["A"][0], js2u["n"], js2u["variants"]),
            ("acc(judge solved  , reference wrong) convention A %.4f on %d in %d variants" % (js2s["A"][0], js2s["n"], js2s["variants"])) in txt
            and ("acc(judge unsolved, reference wrong) convention A %.4f on %d in %d variants" % (js2u["A"][0], js2u["n"], js2u["variants"])) in txt)
        ok3 = True
        for (v0, sv), x in nv["cell"].items():
            line = "  reference %-5s judge %-9s n %4d (%3d variants, %3d qids) | convention A %s | convention B %s on %d | TIE share %s |" % (
                "right" if v0 == 1 else "wrong", {1: "solved", 0: "unsolved", None: "UNCOVERED"}[sv], x["n"], x["variants"], x["qids"],
                "%.4f" % x["A"][0] if x["n"] else "n/a", "%.4f" % x["B"][0] if x["B"][1] else "n/a", x["B"][1],
                "%.4f" % x["tie"] if x["n"] else "n/a")
            ok3 &= line in txt
        check("JS3: all six 2 x 2 (+ uncovered) lines == naive incl. TIE share over all key-decidable", ok3)
        u = nv["unc"]
        check("uncovered beside == naive (n %d on %d qids, A %.4f)" % (u["n"], u["qids"], u["A"][0]),
              ("UNCOVERED beside (K46-KEY-READ's rows; qids absent from grok.db; never counted as unsolved): n %d on %d qids | convention A %.4f"
               % (u["n"], u["qids"], u["A"][0])) in txt)
        w_p1 = "HELD" if -0.09 <= nv["delta"] <= 0.07 else "FAILED"
        w_p2a = "HELD" if 0.88 <= nv["cell"][(1, 1)]["A"][0] <= 0.97 else "FAILED"
        w_p2b = "HELD" if 0.86 <= nv["cell"][(1, 0)]["A"][0] <= 0.96 else "FAILED"
        w_p3a = "HELD" if 0.05 <= js2u["A"][0] <= 0.40 else "FAILED"
        w_p3b = "HELD" if 0.20 <= js2s["A"][0] <= 1.00 else "FAILED"
        check("predictions scored on the naive points: P1 %s, P2a %s, P2b %s, P3a %s, P3b %s" % (w_p1, w_p2a, w_p2b, w_p3a, w_p3b),
              ("P1 Delta_S (convention A) predicted [-0.09, 0.07], observed %.4f -> %s" % (nv["delta"], w_p1)) in txt
              and ("P2a acc(solved, reference right) predicted [0.88, 0.97], observed %.4f -> %s" % (nv["cell"][(1, 1)]["A"][0], w_p2a)) in txt
              and ("P2b acc(unsolved, reference right) predicted [0.86, 0.96], observed %.4f -> %s" % (nv["cell"][(1, 0)]["A"][0], w_p2b)) in txt
              and ("P3a acc(unsolved, reference wrong) predicted [0.05, 0.4], observed %.4f -> %s" % (js2u["A"][0], w_p3a)) in txt
              and ("P3b acc(solved, reference wrong) predicted [0.2, 1.0], observed %.4f -> %s" % (js2s["A"][0], w_p3b)) in txt)
        check("Brier of the realised HELD = (0.85^2 + 0.05^2 + 0.80^2) = 1.3650", "realised HELD; Brier 1.3650" in txt)
        check("outcome written once with the full text; marker written", os.path.exists(cfg.out) and os.path.exists(cfg.mark)
              and open(cfg.out, encoding="utf-8").read() == R["text"] + "\n")
        e = refusal(cfg)
        check("re-run refused (outcome / marker exist)", e is not None and "[WRITE-ONCE]" in e)
        os.chmod(cfg.mark, stat.S_IWRITE); os.remove(cfg.mark)
        e = refusal(cfg)
        check("outcome present alone: re-run refused", e is not None and "[WRITE-ONCE]" in e)
        # ---------------------------------------------------------------- FAILED fixture (and P3b NOT SCOREABLE)
        cf, Tf, nvf = fx("failed", wrong_solved_empty=True)
        R, txt = run(cf)
        check("FAILED fixture: Delta_S %+.4f == naive, JS1 -> FAILED, reading 'recorded, no sentence', F-JS NOT FIRED" % nvf["delta"],
              abs(R["st"]["js1"]["point"] - nvf["delta"]) < 1e-12 and "  JS1 -> FAILED (" in txt and "READING: recorded, no sentence" in txt
              and "F-JS NOT FIRED (JS1 FAILED)" in txt)
        check("FAILED fixture: P3b on the empty solved/wrong cell -> NOT SCOREABLE", nvf["cell"][(0, 1)]["n"] == 0
              and "P3b acc(solved, reference wrong) predicted [0.2, 1.0], observed none (empty cell) -> NOT SCOREABLE" in txt)
        # ---------------------------------------------------------------- UNDETERMINED fixture
        cu, Tu, nvu = fx("undet", seed=3)
        R, txt = run(cu)
        ju = R["st"]["js1"]
        check("UNDETERMINED fixture: interval straddles 0 ([%+.4f, %+.4f]); JS1 -> UNDETERMINED; reading 'not shown either way at n = %d';"
              " F-JS NOT FIRED" % (ju["n_lo"], ju["n_hi"], ju["n1"] + ju["n2"]),
              ju["p_lo"] <= 0 <= ju["p_hi"] and "  JS1 -> UNDETERMINED (" in txt and
              ("READING: not shown either way at n = %d" % (nvu["cell"][(1, 1)]["n"] + nvu["cell"][(1, 0)]["n"])) in txt
              and "F-JS NOT FIRED (JS1 UNDETERMINED)" in txt and "MEASURED SUPPORT vs the observed point" in txt)
        # ---------------------------------------------------------------- deciding-function boundaries
        check("js1_word: lower == 0 is NOT HELD; upper == 0 is NOT FAILED; (0.001, 0.2) HELD; (-0.2, -0.001) FAILED",
              js1_word(0.0, 0.2) == "UNDETERMINED" and js1_word(-0.2, 0.0) == "UNDETERMINED" and js1_word(0.001, 0.2) == "HELD"
              and js1_word(-0.2, -0.001) == "FAILED")
        ivx = dict(n_lo=0.01, n_hi=0.2, p_lo=-0.01, p_hi=0.19)
        check("decide: the normal form reads HELD and the percentile form UNDETERMINED on the same replicates",
              decide(ivx, "normal")[0] == "HELD" and decide(ivx, "percentile")[0] == "UNDETERMINED")
        # forms disagree / percentile-of-record branch through verdict_lines on a synthetic st
        syn = dict(B=400, seed=42, nS=10, nU=10, deff_c1=2.7,
                   js1=dict(point=0.1, se=0.05, n_lo=0.002, n_hi=0.198, p_lo=-0.003, p_hi=0.19, se_lin=0.05, deff=2.0, n1=10, n2=10),
                   js1_B=dict(point=0.1, se=0.05, n_lo=0.0, n_hi=0.2, p_lo=0.0, p_hi=0.2, n1=9, n2=9),
                   accS=dict(point=0.9, n=10, k=5, se=0.05, n_lo=0.8, n_hi=1.0, p_lo=0.8, p_hi=1.0),
                   accU=dict(point=0.8, n=10, k=5, se=0.05, n_lo=0.7, n_hi=0.9, p_lo=0.7, p_hi=0.9), accS_B=(0.95, 9), accU_B=(0.85, 9),
                   kish414=(5, 4.0), js2=dict(S=((0.5, 2), (0.5, 2), 1), U=((0.0, 0), (0.0, 0), 0)),
                   js3={(v, s): dict(n=0, A=(float("nan"), 0), B=(float("nan"), 0), tie=float("nan"), inv=float("nan"), variants=0, qids=0)
                        for v in (0, 1) for s in (1, 0, None)}, unc=dict(n=0, A=(float("nan"), 0), B=(float("nan"), 0), qids=0))
        with contextlib.redirect_stdout(io.StringIO()):
            Lp, wp = verdict_lines(syn, "percentile", "SYN")
        tp = "\n".join(Lp)
        with contextlib.redirect_stdout(io.StringIO()):
            Ln, wn = verdict_lines(syn, "normal", "SYN")
        check("a normal form set by a delta would decide on the normal bounds (HELD on [+0.0020, +0.1980]); percentile then beside",
              wn == "HELD" and "FORMS: normal (of record) reads HELD on [+0.0020, +0.1980]" in "\n".join(Ln))
        check("percentile of record: decides UNDETERMINED; FORMS DISAGREE printed; P3a NOT SCOREABLE on an empty cell",
              wp == "UNDETERMINED" and "FORMS: percentile (of record) reads UNDETERMINED" in tp and "normal (beside; DESCRIPTIVE, NOT DECIDING) reads HELD -> DISAGREE" in tp
              and "P3a acc(unsolved, reference wrong) predicted [0.05, 0.4], observed none (empty cell) -> NOT SCOREABLE" in tp)
        # ---------------------------------------------------------------- mutants (each through mode() on a fresh fixture)
        def ref_values(scen="held", **kw):
            c, T_, n_ = fx(scen, **kw)
            return c, n_
        def kill_values(scen="held", **kw):
            """killed iff the run refuses OR any deciding value differs from the independent recomputation."""
            c, n_ = ref_values(scen, **kw)
            R_, t_ = run(c)
            j_ = R_["st"]["js1"]
            ind_ = K.boot_diff(n_["rows"][(1, 1)], n_["rows"][(1, 0)], c.reg["B"], c.reg["seed"])
            se_ = K._sd(ind_[1])
            good = (abs(j_["point"] - n_["delta"]) < 1e-12 and j_["n1"] == n_["cell"][(1, 1)]["n"] and j_["n2"] == n_["cell"][(1, 0)]["n"]
                    and abs(j_["se"] - se_) < 1e-12 and abs(j_["n_lo"] - (n_["delta"] - Z95 * se_)) < 1e-12
                    and abs(j_["deff"] - n_["deff"]) < 1e-9
                    and ("acc(judge unsolved, reference wrong) convention A %.4f on %d" % n_["cell"][(0, 0)]["A"]) in t_
                    and ("UNCOVERED beside (K46-KEY-READ's rows; qids absent from grok.db; never counted as unsolved): n %d" % n_["unc"]["n"]) in t_
                    and all(("TIE share %.4f" % x["tie"]) in t_ for x in n_["cell"].values() if x["n"]))
            return not good
        def kill_form():
            c, n_ = ref_values()
            R_, t_ = run(c)
            j_ = R_["st"]["js1"]
            return (("FORMS: percentile (of record) reads %s on [%+.4f, %+.4f]" % (js1_word(j_["p_lo"], j_["p_hi"]), j_["p_lo"], j_["p_hi"])) not in t_
                    or ("  JS1 -> %s (" % js1_word(j_["p_lo"], j_["p_hi"])) not in t_)
        def kill_normal():
            """a fixture whose two forms disagree about 0 is not guaranteed, so the deciding pair is read off the printed FORMS line"""
            return kill_form() or decide(dict(n_lo=0.01, n_hi=0.2, p_lo=-0.01, p_hi=0.19), "percentile")[0] != "UNDETERMINED"
        def kill_undet_falsifier():
            c, n_ = ref_values("undet", seed=3)
            R_, t_ = run(c)
            return "F-JS NOT FIRED (JS1 UNDETERMINED)" not in t_
        def kill_bar():
            return js1_word(0.0, 0.2) != "UNDETERMINED"
        def kill_write():
            p = os.path.join(tmp, "w%d.txt" % counter[0]); counter[0] += 1
            write_outcome(p, "a"); write_outcome(p, "b")
            return open(p, encoding="utf-8").read() == "b"                 # the overwrite was admitted: observed
        def kill_dry():
            c, n_ = ref_values()
            run(c, True)
            return os.path.exists(c.out)
        def kill_ident():
            c, n_ = ref_values(); c.ident = dict(c.ident, right_solved=c.ident["right_solved"] + 1)
            e_ = refusal(c)
            return e_ is None or "[IDENTITY]" not in e_
        # a refusal kills a mutant only when it is the named guard's refusal (expect); otherwise the kill is a value difference
        ID = "[IDENTITY]"
        MUTS = [("wrong_key", kill_values, ID), ("ref_wrong_in_js1", kill_values, ID), ("match_level_boot", kill_values, ID),
                ("conv_b_decides", kill_values, ID), ("uncovered_as_unsolved", kill_values, ID), ("sign_swap", kill_values, ID),
                ("z90", kill_values, ID), ("deff_one_group", kill_values, ID), ("deff_boot", kill_values, ID),
                ("js2_uses_right", kill_values, ID), ("tie_share_committed", kill_values, ID), ("form_ignored", kill_form, None), ("normal_decides", kill_normal, None),
                ("falsifier_on_undet", kill_undet_falsifier, None), ("bar_inclusive", kill_bar, None), ("write_w", kill_write, None),
                ("dry_writes", kill_dry, None), ("ident_off", kill_ident, None)]
        # non-vacuity: every kill predicate reads 'not killed' on the UNMUTATED code
        vac = [n_ for n_, fn_ in (("kill_values", kill_values), ("kill_form", kill_form), ("kill_undet_falsifier", kill_undet_falsifier),
                                  ("kill_bar", kill_bar), ("kill_normal", kill_normal), ("kill_dry", kill_dry), ("kill_ident", kill_ident)) if fn_()]
        try:
            kill_write(); vac.append("kill_write")
        except SystemExit as e_:
            if "[WRITE-ONCE]" not in str(e_):
                vac.append("kill_write")
        check("non-vacuity: every kill predicate reads 'not killed' on the unmutated code (offenders %s)" % vac, not vac)
        table = []
        for name, fn, expect in MUTS:
            MUTANT = name
            msg = ""
            try:
                k = bool(fn())
            except SystemExit as e_:
                msg = str(e_)
                k = bool(expect) and expect in msg               # only the named guard's refusal kills
            finally:
                MUTANT = None
            table.append((name, "killed" if k else "SURVIVED", msg[:60]))
            check("MUTANT %-22s %s%s" % (name, "killed" if k else "SURVIVED", (" (by refusal: %s)" % msg[:70]) if msg else ""), k)
        miss = BR.missing()
        check("every declared print branch executed (%d / %d); missing %s" % (len(BR.declared) - len(miss), len(BR.declared), miss), not miss)
        print("MUTANT TABLE: " + "; ".join("%s %s" % (n, w) for n, w, _ in table))
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
            print("[HYGIENE] %s is %r (CPU single-threaded: the run-operator sets 1)" % (k, os.environ.get(k)))
            if a.run:
                raise SystemExit("[HYGIENE] --run refused: %s is %r, not '1'" % (k, os.environ.get(k)))
    if a.selftest:
        sys.exit(selftest())
    if MUTANT is not None:
        raise SystemExit("[MUTANT] %r is set: a real mode refuses" % MUTANT)
    mode(real_cfg(), a.dry_run)


if __name__ == "__main__":
    main()
