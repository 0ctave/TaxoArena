"""route_source_null.py: ROUTE-SOURCE-NULL -- how much of AF-U's +1.52pp routing gain over the best single model is beyond source
identity, against a 6-cell source policy (SRC) and random within-source cells at AF-U's per-source size profile (RWS)?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader (T1 of the testing-logic review).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — ROUTE-SOURCE-NULL: how much of AF-U's +1.52pp
  routing gain over the best single model is beyond source identity, ..." (L24265-L24276, _as_of b66b075d): RS1, Support (a)-(g),
  P1-P3, F-RS, WILL-NOT-SHOW. Record L24259-L24263 (AF-U is [SC], source-conditioned, not label-free). Source:
  docs/literature/2026-10-04_testing_logic_review.md (bd5ca001) T1.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; never beside a construction: every step reads the pool):
  0. python tools/analysis/route_source_null.py --selftest   # synthetic fixtures (temp on E: via scratch_dir); opens NO DB of record
     python tools/analysis/route_source_null.py --mutants    # the mutant table below, re-run (each must make the selftest fail)
  1. python tools/analysis/route_source_null.py --dry-run    # POOL line first; pins; registered denominators; B0-2 pool check; the
                                                             #   UNION-AF-ROUTE inputs re-hashed; the frozen policy's sha; NO key, NO
                                                             #   statistic; writes nothing
  2. python tools/analysis/route_source_null.py --run        # ONE EVAL key read (marker first); outcome WRITE-ONCE:
       experiment_results/archv2/route_source_null/outcome.txt (+ route_source_null.READ_STARTED). Never committed: pin by sha256
       and back up to E:/TaxoArena_backup_<date>_route_source_null with SHA256SUMS.txt (registration HYGIENE).
  --data-root <dir> (optional, every mode): the checkout whose experiment_results/, data_v2/ and cache DBs are read (set before any
  import); from a worktree: --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena. Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome and marker absent (write-once); the B0-2 pool check; (2) AF-U state (D-8, one-cell evidence), the inputs
  manifest (sha256-lf pinned) with every file re-hashed, the AF and K0..K4 cells, the frozen TRAIN policy (sha256 8d68018c...);
  (3) the gen view (TRAIN key) and the eval view through v2_declared_cells' guarded openers (union_route_common.read_views), the
  marker mode "x", THE EVAL KEY READ; [RSN-DENOM] 5,907 / 5,404; [B3] the point policy re-fitted beside EVAL equals the frozen
  file (best single, AF, K0..K4, TRUE source, TRUE source/domain); (4) v2_declared_cells.run_boot (B 2,000, default_rng(42));
  [RSN-IDENTITY] before any new number (union_route_common.COMMON identity); (5) RS1, the RWS null (200 draws), descriptive lines,
  predictions, F-RS; the outcome written mode "x" (a view whose sha changed during the read writes *_VOID.txt instead).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  SRC = v2_declared_cells' "TRUE source" arm (index 1): the best TRAIN model per stratum source (6 sources: BBH, GPQA, IFEVAL,
      MATH, MMLU_PRO, MUSR), fitted by G14's reader; G_SRC = acc(SRC) - acc(best single).
  R2  D_S = G_AF - G_SRC = acc(AF-U) - acc(SRC), item-paired inside run_boot's two-stage replicates; deciding 95% interval = point
      +- 1.96 SE_2stage (G14's reader form, v2_declared_cells.contrast; UNION-AF-ROUTE R5); percentile beside.
  R3  RWS size profile: for each source s, the sizes of AF-U's cells among the SCORED TRAIN items whose stratum source is s (the
      policy-fit set of G14's reader, 11,841 key-complete items), in AF cell-index order. A multi-class TRAIN item whose modal leaf
      belongs to another member's cell contributes to its own stratum source's profile (the per-source cell counts are printed
      beside AF-U's leaf counts). RWS_r (r = 1..200, default_rng(20261004 + r)): per source (sorted) a uniform permutation of its
      scored TRAIN items (position order) cut into blocks of those sizes; then each EVAL item of the source filed to a random cell
      of its source drawn with the TRAIN size weights, one rng stream in that order. Per-cell policy by V.fit (unchanged) on the
      full TRAIN; G_RWS_r = acc(RWS_r) - acc(best single). Points only (the registration decides on the point against the band).
  R4  Percentiles of the 200 G_RWS: numpy linear interpolation; "G_AF > the 97.5th percentile" strict; "inside the central 95%
      band" = p2.5 <= G_AF <= p97.5 (closed). Monte Carlo SE of p97.5 = the SD of p97.5 over 2,000 resamples of the 200 draws
      (default_rng(20261004)).
  R5  RS1 = ABOVE-SOURCE iff D_S's 95% interval is wholly > 0 (lo > 0) AND G_AF > p97.5; SOURCE-EXPLAINED iff p2.5 <= G_AF <=
      p97.5 AND lo <= 0 <= hi; UNDETERMINED otherwise (exclusive: lo > 0 vs lo <= 0). Rule 8: ABOVE-SOURCE is refuted iff lo <= 0
      <= hi. F-RS fires iff SOURCE-EXPLAINED.
  R6  Predictions "X [lo, hi]" HELD iff the point lies in the closed interval; RS1's probabilities scored by the three-outcome
      Brier sum.
  R7  Not applicable (stated): no judge verdict (key-scored), so no wrong(established) count and no tie convention A / B; no call
      cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; escalation_rc's fixture layout via union_route_common.build_layout: union_af_route's fixture with a
one-cell member, --build-inputs and --run executed; v2_declared_cells' sealed fixture views; stubbed readers / pool check):
  branches      RS1 ABOVE-SOURCE / SOURCE-EXPLAINED / UNDETERMINED by value, incl. lo exactly 0, G_AF exactly at p97.5 and at
                p2.5; rule-8 line; F-RS fired / not fired; P1 / P3 bands inclusive at both ends; the Brier values; required lines
  run_e2e       --run end to end: G_SRC, D_S (point, interval, SE), G_AF, the RWS percentiles and median against an INDEPENDENT
                oracle (plain-loop fits on the fixture's raw rows; the RWS draws re-implemented by loops on the same rng protocol;
                the two-stage replicates from the same unit draws); RS1 / F-RS from the printed numbers by the hand rule; a second
                --run refused, outcome unchanged
  refusals      pool check (POOL line still first), the manifest pin, the policy sha, [RSN-DENOM], [RSN-IDENTITY] (an arm digit;
                TRUE source digit; one interval end only), [B3], the marker present; no outcome written by any
  dry_run       POOL first, no statistic, nothing written; the REAL constants' lines
  branch_cover  every print / refusal branch executed
MUTANTS: see MUTANTS at the end of this file and the commit message (table, killed / survived).
NOT DONE HERE: the real --run (the operator's, after READY); no Kotlin / Gradle.
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import types         # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc, union_cells_io, union_af_route)

TAG = "[RSN]"
TEST_ID = "ROUTE-SOURCE-NULL"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — ROUTE-SOURCE-NULL: how much of AF-U\'s'
            ' +1.52pp routing gain over the best single model is beyond source identity, ..." L24265-L24276 (_as_of b66b075d)')
OUT = "experiment_results/archv2/route_source_null"
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/route_source_null.READ_STARTED")
FIXTURE_REG = dict(out="res/rsn/outcome.txt", marker="res/rsn/READ_STARTED")
_REG = [REG]


def reg():
    return _REG[0]


SUPPORT = dict(deff=2.867, n_eff=2060, se=0.0044, mde=0.0123)
VERDICT_LINE = ("RS1 ABOVE-SOURCE DESCRIPTIVE-ONLY at the prediction (D_S +0.3pp lies 0.3pp from 0, short of the MDE 1.23pp);"
                " SOURCE-EXPLAINED reachable (it needs no power beyond the band)")
PRED_GSRC = (0.004, 0.020)
PRED_DS = (-0.006, 0.012)
PRED_RWS_MED = (0.0, 0.016)
PROB_RS1 = (("ABOVE-SOURCE", 0.15), ("SOURCE-EXPLAINED", 0.45), ("UNDETERMINED", 0.40))
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def rs1_verdict(ds, g_af, band):
    above = ds["lo"] > 0 and g_af > band[1]
    expl = band[0] <= g_af <= band[1] and ds["lo"] <= 0 <= ds["hi"]
    if above and expl:
        refuse("[RS1-OVERLAP] both words fire on the same data (registration defect; for the registrar)")
    if above:
        return "ABOVE-SOURCE"
    if expl:
        return "SOURCE-EXPLAINED"
    return "UNDETERMINED"


def rs_lines(st):
    """Every line of the RS1 block (the outcome prints them verbatim); -> (lines, words)."""
    L = []
    ds, gs, ga, dd = st["ds"], st["gsrc"], st["gaf"], st["decl_src"]
    band, rws = st["band"], st["rws"]
    L.append("=== ROUTE-SOURCE-NULL RS1 (%s) ===" % REG_TEXT)
    L.append("DENOMINATOR: %d EVAL items in %d components (Kish mean cluster size %.3f; Support (a) 5907 / 5404); TRAIN %d scored"
             " items (the policy-fit set of G14's reader); B %d two-stage replicates" % (ds["n"], st["comp"], st["kish"], st["n_train"], st["B"]))
    L.append("LIKE WITH LIKE: AF-U (anchor-free tree federated per source) [SC] | SRC (6 source cells) [SC] | RWS (random within-source"
             " cells, AF-U's size profile) [SC] | K_0 (per-source k-means) [SC] | declared (source, domain) [DECL], a labelled reference"
             " (cross); AF-U vs SRC / RWS / K_0 is like with like")
    L.append("G_AF = acc(AF-U leaf cells) - acc(best single) = %s (%+.5f) | two-stage 95%% [%s, %s]" % (U.pp(ga["point"]), ga["point"], U.pp(ga["lo"]), U.pp(ga["hi"])))
    L.append("G_SRC = acc(SRC: best TRAIN model per source) - acc(best single) = %s (%+.5f) | two-stage 95%% [%s, %s]" % (
        U.pp(gs["point"]), gs["point"], U.pp(gs["lo"]), U.pp(gs["hi"])))
    L.append("RS1 (DECIDING with the RWS band): D_S = G_AF - G_SRC = %s (%+.5f) | two-stage 95%% [%s, %s] (%+.5f, %+.5f) | percentile"
             " [%s, %s]" % (U.pp(ds["point"]), ds["point"], U.pp(ds["lo"]), U.pp(ds["hi"]), ds["lo"], ds["hi"], U.pp(ds["pct"][0]), U.pp(ds["pct"][1])))
    L.append("  support D_S: n %d, SE_2stage %.5f (registered 0.0044), i.i.d. SE %.5f, DEFF %.3f (registered 2.867, transported from"
             " U2), n_eff %.0f (registered 2060), MDE80 %s (registered +1.23pp); verdict line of record: %s" % (
                 ds["n"], ds["se2"], ds["se_iid"], ds["deff"], ds["n_eff"], U.pp(ds["mde"]), VERDICT_LINE))
    L.append("RWS NULL: %d draws (default_rng(%d + r), r = 1..%d), each a random partition of every source's scored TRAIN items at"
             " AF-U's per-source size profile; G_RWS min %s | p2.5 %s | median %s | p97.5 %s | max %s | mean %s" % (
                 len(rws), st["rws_seed0"], len(rws), U.pp(min(rws)), U.pp(band[0]), U.pp(st["rws_med"]), U.pp(band[1]), U.pp(max(rws)),
                 U.pp(float(np.mean(rws)))))
    L.append("  RWS band (central 95%%, numpy linear percentiles): [%+.5f, %+.5f]; Monte Carlo SE of p97.5 %.5f (2,000 resamples of the"
             " %d draws)" % (band[0], band[1], st["mc_se"], len(rws)))
    L.append("  RWS profile (cells per source on the scored TRAIN items; AF-U leaves per source beside): %s" % st["profile_text"])
    pos = "ABOVE p97.5" if st["gaf"]["point"] > band[1] else ("INSIDE the band" if band[0] <= st["gaf"]["point"] else "BELOW p2.5")
    L.append("  G_AF %+.5f against the band: %s" % (st["gaf"]["point"], pos))
    v = rs1_verdict(ds, st["gaf"]["point"], band)
    if v == "ABOVE-SOURCE":
        hit("RS1.ABOVE")
        L.append("  RS1 -> ABOVE-SOURCE (D_S's 95%% interval lies wholly above 0 AND G_AF %+.5f > p97.5 %+.5f)" % (st["gaf"]["point"], band[1]))
    elif v == "SOURCE-EXPLAINED":
        hit("RS1.EXPLAINED")
        L.append("  RS1 -> SOURCE-EXPLAINED (G_AF %+.5f lies inside the RWS band [%+.5f, %+.5f] AND D_S's 95%% interval contains 0)" % (
            st["gaf"]["point"], band[0], band[1]))
    else:
        hit("RS1.UNDETERMINED")
        L.append("  RS1 -> UNDETERMINED (neither ABOVE-SOURCE: interval wholly > 0 and G_AF > p97.5; nor SOURCE-EXPLAINED: G_AF inside"
                 " the band and the interval containing 0)")
    if ds["lo"] <= 0 <= ds["hi"]:
        hit("RULE8.REFUTED")
        L.append("RULE 8: ABOVE-SOURCE is REFUTED (D_S's 95% interval contains 0)")
    else:
        hit("RULE8.NOT")
        L.append("RULE 8: ABOVE-SOURCE is not refuted by D_S's interval (it excludes 0)")
    if v == "SOURCE-EXPLAINED":
        hit("FRS.FIRED")
        L.append("FALSIFIER F-RS: FIRES (RS1 SOURCE-EXPLAINED): '+1.52pp' is rewritten as source identity; AF-U stays tagged [SC]"
                 " everywhere (done as a status correction); memo v3's SQ1 [LF] routing claim is withdrawn")
    else:
        hit("FRS.NOT")
        L.append("FALSIFIER F-RS: NOT FIRED (RS1 %s; F-RS fires iff RS1 SOURCE-EXPLAINED)" % v)
    L.append("DESCRIPTIVE: G_SRC - G_best = %s (the SRC arm's gain over the best single; interval above)" % U.pp(gs["point"]))
    L.append("DESCRIPTIVE: G_declared - G_SRC = acc(TRUE (source, domain)) - acc(SRC) = %s | two-stage 95%% [%s, %s] (declared: [DECL],"
             " cross)" % (U.pp(dd["point"]), U.pp(dd["lo"]), U.pp(dd["hi"])))
    L.append("DESCRIPTIVE: K_s (per-source k-means, seeds 0-4) G_K,s = %s; mean %s; D_S-like G_AF - G_K = %s" % (
        " / ".join(U.pp(x) for x in st["gk"]), U.pp(float(np.mean(st["gk"]))), U.pp(st["gaf"]["point"] - float(np.mean(st["gk"])))))
    for lab, x, band_ in (("P1 G_SRC +1.2pp [+0.4, +2.0]", gs["point"], PRED_GSRC), ("P1 D_S +0.3pp [-0.6, +1.2]", ds["point"], PRED_DS),
                          ("P3 median G_RWS +0.8pp [0.0, +1.6]", st["rws_med"], PRED_RWS_MED)):
        ok = U.in_band(x, band_)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION %s: observed %+.5f -> %s" % (lab, x, "HELD" if ok else "FAILED"))
    L.append("PREDICTION P2 RS1 ABOVE-SOURCE 0.15, SOURCE-EXPLAINED 0.45, UNDETERMINED 0.40: observed %s; Brier %.4f" % (v, U.brier(PROB_RS1, v)))
    L.append("WORDS: AF-U is SOURCE-CONDITIONED [SC] (federated per source, prog L22633), never label-free; key-scored end to end, no"
             " judge verdict (no wrong(established) count, no tie convention A / B arises); one draw, one roster")
    L.append("WILL NOT SHOW (registered): that cells beat source on other corpora or rosters; a label-free routing gain (no [LF] arm"
             " here); judged decisions; anything beyond one draw")
    return L, dict(RS1=v, F_RS=(v == "SOURCE-EXPLAINED"), RULE8=bool(ds["lo"] <= 0 <= ds["hi"]))


def denominators(say):
    c = reg()
    idn = c["identity"]
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d components (G14's set; Kish 1.09); DEFF 2.867 (UNION-AF-ROUTE U2"
        " D_K two-stage, transported), n_eff 2,060, SE 0.44pp, MDE80 1.23pp; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); RWS %d draws, default_rng(%d + r); SRC = TRUE source arm; K_s seeds 0-4"
        % (c["B"], c["seed"], c["rws_n"], c["rws_seed0"]))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(idn)))


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS])
    denominators(say)
    S = U.prepare(say, reg(), refuse, hit)
    per = Counter(U.UCI.cell_member(cl) for cl in set(S["af"].values()) if cl != U.V.NO_ROUTING_ROW)
    say("  AF-U cells per member (all sides, structure only): %s" % ", ".join("%s %d" % kv for kv in sorted(per.items())))
    cfg = U.UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(U.UAR.reg()["policy"])
    U.read_views(cfg, say, True, S["af"], S["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no EVAL key read; no statistic of EVAL printed.")
    hit("DRY.DONE")
    return 0


def rws_null(D, bt, P0):
    """The RWS draws (R3): -> (G_RWS list, profile, profile text)."""
    c = reg()
    g_af = D.groupings["tree"][0]
    prof = U.rws_profile(D, g_af)
    best = bt["point"][0, U.V.BS]
    out = []
    for r in range(1, c["rws_n"] + 1):
        g, ng = U.rws_cells(D, prof, c["rws_seed0"] + r)
        pol, gb = U.point_fit(D, g, ng)
        if gb != P0.gb:
            refuse("[RWS] the RWS fit's best single differs from the frozen policy's")
        out.append(float(U.routed_correct(D, pol, gb, g).mean()) - float(best))
    return out, prof


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS])
    for p in (c["out"], c["marker"]):
        if os.path.exists(U.P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    denominators(say)
    S = U.prepare(say, c, refuse, hit)
    cfg = U.UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(U.UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    D, ok_sha = U.read_views(cfg, say, False, S["af"], S["kx"], c["marker"],
                             "ROUTE-SOURCE-NULL: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "RSN")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    P0 = U.b3_check(D, cfg, S["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % S["pol"]["best_single"])
    bt = U.V.run_boot(D, c["B"], c["seed"])
    if D.fit_asserts != c["B"] + 2:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, c["B"] + 2))
    ok, got = U.identity(bt, D, c["identity"])
    if not ok:
        hit("REFUSE.IDENTITY")
        refuse("[RSN-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
    say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
    hit("IDENTITY.OK")
    rws, prof = rws_null(D, bt, P0)
    ksrc = S["ksrc"]
    ptxt = ", ".join("%s %d (AF-U %s)" % (s, len(prof[s]), ksrc.get(s, ksrc.get(s + "_LB", "?"))) for s in sorted(prof))
    st = dict(comp=n_comp, kish=U.kish_eval(D), n_train=D.n_train, B=c["B"], rws_seed0=c["rws_seed0"],
              ds=U.V.contrast(bt, D, "ALL", U.V.TREE, U.V.TSRC), gsrc=U.V.contrast(bt, D, "ALL", U.V.TSRC, U.V.BS),
              gaf=U.V.contrast(bt, D, "ALL", U.V.TREE, U.V.BS), decl_src=U.V.contrast(bt, D, "ALL", U.V.TDOM, U.V.TSRC),
              gk=[float(bt["point"][0, U.karm(D, nm)] - bt["point"][0, U.V.BS]) for nm in U.KNAMES],
              rws=rws, band=(U.pctl(rws, 2.5), U.pctl(rws, 97.5)), rws_med=U.pctl(rws, 50), mc_se=U.mc_se_pct(rws, 97.5),
              profile_text=ptxt)
    L, words = rs_lines(st)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, bt=bt, prof=prof)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=None, help="the checkout whose results / views / caches are read (set before any import)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return U.run_mutants(os.path.abspath(__file__), "route_source_null", MUTANTS, TAG, only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

BRANCHES = ("RS1.ABOVE", "RS1.EXPLAINED", "RS1.UNDETERMINED", "RULE8.REFUTED", "RULE8.NOT", "FRS.FIRED", "FRS.NOT", "PRED.HELD",
            "PRED.FAILED", "IDENTITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "REFUSE.WRITE_ONCE", "REFUSE.POOL",
            "REFUSE.POLICY_SHA", "REFUSE.MANIFEST", "REFUSE.DENOM", "REFUSE.IDENTITY", "REFUSE.B3", "REFUSE.NOROW")


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _ci(pt, lo, hi):
    return dict(point=pt, lo=lo, hi=hi, pct=(lo, hi), se2=0.0044, se_iid=0.0026, deff=2.86, n_eff=2065.0, mde=0.0123, n=5907)


def _syn(ds=(0.005, -0.003, 0.013), gaf=0.0152, band=(0.002, 0.012), gsrc=0.0101, med=0.007):
    rws = [band[0]] * 3 + [med] * 34 + [band[1]] * 3
    return dict(comp=5404, kish=1.09, n_train=11841, B=2000, rws_seed0=20261004, ds=_ci(*ds), gsrc=_ci(gsrc, gsrc - 0.004, gsrc + 0.004),
                gaf=_ci(gaf, gaf - 0.014, gaf + 0.014), decl_src=_ci(0.0166, 0.01, 0.02), gk=[0.022, 0.018, 0.016, 0.021, 0.021],
                rws=rws, band=band, rws_med=med, mc_se=0.0011, profile_text="BBH 36 (AF-U 36)")


def st_branches():
    B_ = {"ABOVE-SOURCE": 0.7225 + 0.2025 + 0.16, "SOURCE-EXPLAINED": 0.0225 + 0.3025 + 0.16, "UNDETERMINED": 0.0225 + 0.2025 + 0.36}
    cases = [(dict(ds=(0.008, 0.001, 0.015), gaf=0.0152), "ABOVE-SOURCE"),
             (dict(ds=(0.008, 1e-12, 0.015), gaf=0.0121), "ABOVE-SOURCE"),
             (dict(ds=(0.008, 0.0, 0.015), gaf=0.0152), "UNDETERMINED"),          # lo exactly 0: not wholly above, outside the band
             (dict(ds=(0.008, 0.001, 0.015), gaf=0.012), "UNDETERMINED"),         # G_AF exactly at p97.5: not above; interval excludes 0
             (dict(ds=(0.004, -0.003, 0.011), gaf=0.012), "SOURCE-EXPLAINED"),    # G_AF at p97.5 is inside the closed band
             (dict(ds=(0.004, -0.003, 0.011), gaf=0.002), "SOURCE-EXPLAINED"),    # at p2.5, inside
             (dict(ds=(0.004, 0.0, 0.011), gaf=0.007), "SOURCE-EXPLAINED"),       # lo exactly 0 contains 0
             (dict(ds=(0.004, -0.003, 0.011), gaf=0.0019), "UNDETERMINED"),       # below the band
             (dict(ds=(0.004, -0.003, 0.011), gaf=0.0152), "UNDETERMINED"),       # above the band, interval contains 0
             (dict(ds=(-0.008, -0.015, -0.001), gaf=0.007), "UNDETERMINED")]      # inside the band, interval wholly below 0
    for kw, want in cases:
        st = _syn(**kw)
        L, w = rs_lines(st)
        t = "\n".join(L)
        assert w["RS1"] == want, (kw, w)
        need(t, "  RS1 -> %s" % want, "verdict line of record: " + VERDICT_LINE,
             "D_S = G_AF - G_SRC = %s (%+.5f) | two-stage 95%% [%s, %s]" % (U.pp(kw["ds"][0]), kw["ds"][0], U.pp(kw["ds"][1]), U.pp(kw["ds"][2])),
             "PREDICTION P2 RS1 ABOVE-SOURCE 0.15, SOURCE-EXPLAINED 0.45, UNDETERMINED 0.40: observed %s; Brier %.4f" % (want, B_[want]),
             "WILL NOT SHOW (registered)", "DENOMINATOR: 5907 EVAL items in 5404 components", "support D_S: n 5907", "[SC]", "[DECL]",
             "LIKE WITH LIKE")
        refuted = kw["ds"][1] <= 0 <= kw["ds"][2]
        need(t, "RULE 8: ABOVE-SOURCE is REFUTED" if refuted else "RULE 8: ABOVE-SOURCE is not refuted")
        assert w["RULE8"] is refuted
        if want == "SOURCE-EXPLAINED":
            assert w["F_RS"] is True
            need(t, "FALSIFIER F-RS: FIRES (RS1 SOURCE-EXPLAINED)")
        else:
            assert w["F_RS"] is False
            need(t, "FALSIFIER F-RS: NOT FIRED (RS1 %s; F-RS fires iff RS1 SOURCE-EXPLAINED)" % want)
    for g_, want in ((0.004, "HELD"), (0.020, "HELD"), (0.0039, "FAILED"), (0.0201, "FAILED")):
        need("\n".join(rs_lines(_syn(gsrc=g_))[0]), "PREDICTION P1 G_SRC +1.2pp [+0.4, +2.0]: observed %+.5f -> %s" % (g_, want))
    for d_, want in ((-0.006, "HELD"), (0.012, "HELD"), (-0.0061, "FAILED"), (0.0121, "FAILED")):
        need("\n".join(rs_lines(_syn(ds=(d_, d_ - 0.008, d_ + 0.008)))[0]), "PREDICTION P1 D_S +0.3pp [-0.6, +1.2]: observed %+.5f -> %s" % (d_, want))
    for m_, want in ((0.0, "HELD"), (0.016, "HELD"), (-0.0001, "FAILED"), (0.0161, "FAILED")):
        need("\n".join(rs_lines(_syn(med=m_, band=(min(m_, 0.002) - 0.001, max(m_, 0.012) + 0.001)))[0]),
             "PREDICTION P3 median G_RWS +0.8pp [0.0, +1.6]: observed %+.5f -> %s" % (m_, want))
    t = "\n".join(rs_lines(_syn())[0])
    need(t, "G_RWS min +0.20pp | p2.5 +0.20pp | median +0.70pp | p97.5 +1.20pp | max +1.20pp", "Monte Carlo SE of p97.5 0.00110",
         "DESCRIPTIVE: G_declared - G_SRC = acc(TRUE (source, domain)) - acc(SRC) = +1.66pp", "G_AF +0.01520 against the band: ABOVE p97.5",
         "DESCRIPTIVE: K_s (per-source k-means, seeds 0-4) G_K,s = +2.20pp / +1.80pp / +1.60pp / +2.10pp / +2.10pp; mean +1.96pp")
    assert abs(U.brier(PROB_RS1, "UNDETERMINED") - B_["UNDETERMINED"]) < 1e-12
    assert U.in_band(0.004, PRED_GSRC) is True and U.in_band(0.0039, PRED_GSRC) is False


def _oracle(lay, res):
    """Plain-loop recomputation of the arms, D_S's two-stage interval and the RWS draws from the fixture's raw rows."""
    fx, D = lay.fx, res["D"]
    mu, val = U.o_key(fx.spec)
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    man = U.json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = U.V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    src = {i: fx.strata[i][0] for i in tr + ev}
    cells_src = {i: src[i] for i in tr + ev}
    o = {}
    best, pa = U.o_fit(tr, af, val, mu)
    _b, ps = U.o_fit(tr, cells_src, val, mu)
    abest = U.o_acc(ev, af, val, best, {})
    o["gaf"] = U.o_acc(ev, af, val, best, pa) - abest
    o["gsrc"] = U.o_acc(ev, cells_src, val, best, ps) - abest
    o["ds"] = o["gaf"] - o["gsrc"]
    # two-stage: the same unit draws as run_boot (default_rng(seed): TRAIN units then EVAL units per replicate)
    rng = np.random.default_rng(lay.common["seed"])
    reps = []
    for _b in range(lay.common["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = U.V.draw_units(rng, D.train_units)
        v = U.V.draw_units(rng, D.eval_units)
        w = {D.items[k]: int(wt[k]) for k in D.T}
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        b_, pa_ = U.o_fit(tr, af, val, mu, w)
        _x, ps_ = U.o_fit(tr, cells_src, val, mu, w)
        reps.append(U.o_acc(ev, af, val, b_, pa_, vv) - U.o_acc(ev, cells_src, val, b_, ps_, vv))
    o["ds_se2"] = float(np.std(reps, ddof=1))
    # RWS by loops on the registered rng protocol
    sources = sorted(set(src[i] for i in tr))
    trs = {s: [i for i in tr if src[i] == s] for s in sources}           # D's position order = item_id order
    prof = {}
    for s in sources:
        cnt = Counter(af[i] for i in trs[s])
        prof[s] = [cnt[cl] for cl in sorted(cnt)]
    g_list = []
    for r in range(1, lay.common["rws_n"] + 1):
        rr = np.random.default_rng(lay.common["rws_seed0"] + r)
        cell = {}
        for s in sources:
            perm = rr.permutation(len(trs[s]))
            off = 0
            for j, sz in enumerate(prof[s]):
                for q in perm[off:off + sz]:
                    cell[trs[s][q]] = (s, j)
                off += sz
        for s in sources:
            es = [i for i in ev if src[i] == s]
            if not es:
                continue
            wts = np.array(prof[s], float)
            dr = rr.choice(len(wts), size=len(es), p=wts / wts.sum())
            for i, j in zip(es, dr):
                cell[i] = (s, int(j))
        b_, pr = U.o_fit(tr, cell, val, mu)
        g_list.append(U.o_acc(ev, cell, val, b_, pr) - abest)
    o["rws"] = g_list
    o["prof"] = prof
    return o


def st_run_e2e(base, mk):
    lay = U.clone(base, mk())
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "rsn", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (ROUTE-SOURCE-NULL; --run" % U.POOL)
    assert os.path.isfile(os.path.join(lay.tmp, "res", "rsn", "READ_STARTED"))
    o = _oracle(lay, res)
    ga, = U.num(out, r"G_AF = acc\(AF-U leaf cells\) - acc\(best single\) = \S+ \(([+-][0-9.]+)\)")
    gs, = U.num(out, r"G_SRC = acc\(SRC: best TRAIN model per source\) - acc\(best single\) = \S+ \(([+-][0-9.]+)\)")
    p_, lo, hi = U.num(out, r"D_S = G_AF - G_SRC = \S+ \(([+-][0-9.]+)\) \| two-stage 95% \[\S+, \S+\] \(([+-][0-9.]+), ([+-][0-9.]+)\)")
    se2, = U.num(out, r"support D_S: n \d+, SE_2stage ([0-9.]+) ")
    assert abs(ga - o["gaf"]) < 6e-6 and abs(gs - o["gsrc"]) < 6e-6 and abs(p_ - o["ds"]) < 6e-6, (ga, gs, p_, o)
    assert abs(o["gsrc"]) > 1e-4 and abs(o["ds"]) > 1e-4, "the fixture does not discriminate SRC from AF-U"
    assert abs(se2 - o["ds_se2"]) < 6e-6 and abs(lo - (o["ds"] - 1.96 * o["ds_se2"])) < 2e-5 and abs(hi - (o["ds"] + 1.96 * o["ds_se2"])) < 2e-5, (se2, o["ds_se2"])
    lo_b, hi_b = U.num(out, r"RWS band \(central 95%, numpy linear percentiles\): \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    assert abs(lo_b - float(np.percentile(o["rws"], 2.5))) < 6e-6 and abs(hi_b - float(np.percentile(o["rws"], 97.5))) < 6e-6, (lo_b, hi_b)
    assert len(set(round(x, 9) for x in o["rws"])) > 3, "the RWS draws do not vary on the fixture"
    med, = U.num(out, r"PREDICTION P3 median G_RWS \+0.8pp \[0.0, \+1.6\]: observed ([+-][0-9.]+)")
    assert abs(med - float(np.median(o["rws"]))) < 6e-6
    assert sorted(res["prof"].items()) == sorted(o["prof"].items()), (res["prof"], o["prof"])
    want = "ABOVE-SOURCE" if (lo > 0 and ga > hi_b) else ("SOURCE-EXPLAINED" if (lo_b <= ga <= hi_b and lo <= 0 <= hi) else "UNDETERMINED")
    need(out, "  RS1 -> %s" % want, "FALSIFIER F-RS: %s" % ("FIRES" if want == "SOURCE-EXPLAINED" else "NOT FIRED"),
         "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]), "B3: the point policy re-fitted beside EVAL equals")
    t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "rsn", "outcome.txt")), "an outcome was written by a refusal"


def st_refusals(base, mk):
    lay = U.clone(base, mk())
    saved = U.UAR._POOL[0]
    import io
    import contextlib
    buf = io.StringIO()
    with U.mine(_me(), lay):
        U.UAR._POOL[0] = lambda pool: (1, "stub failure")
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    run(out=lambda s: print(s))
                    err = None
                except SystemExit as e:
                    err = str(e)
        finally:
            U.UAR._POOL[0] = saved
    assert err and "B0-2 pool check failed" in err, err
    assert buf.getvalue().splitlines()[0].startswith("POOL "), "the POOL line is not first"
    _no_outcome(lay)
    for over, needle in ((dict(uar_policy_sha="0" * 64), "frozen TRAIN policy"), (dict(manifest_sha="0" * 64), "inputs manifest is sha256")):
        lay = U.clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and needle in err, (over, err)
        assert not os.path.exists(os.path.join(lay.tmp, "res", "rsn", "READ_STARTED")), "a pre-read refusal wrote the marker"
        _no_outcome(lay)
    lay = U.clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, n_route=lay.common["n_route"] + 1)
    assert err and "[RSN-DENOM]" in err, err
    _no_outcome(lay)
    idn = lay.common["identity"]
    bump = lambda s: s[:-1] + str((int(s[-1]) + 1) % 10)
    for k in ("best", "tsrc", "af", "k0"):
        lay = U.clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, identity=dict(idn, **{k: bump(idn[k])}))
        assert err and "[RSN-IDENTITY]" in err, (k, err)
        assert "RS1 (DECIDING" not in _t and "RWS NULL" not in _t, "a new number was printed before the identity refusal"
        _no_outcome(lay)
    for k in ("c1", "g_af"):
        for j in (0, 2):
            lay = U.clone(base, mk())
            t_ = list(idn[k])
            t_[j] = t_[j].replace("pp", "") + "1pp"
            _t, err, _r = U.cap(_me(), run, lay, identity=dict(idn, **{k: tuple(t_)}))
            assert err and "[RSN-IDENTITY]" in err, (k, j, err)
            _no_outcome(lay)
    st_b3(base, mk, run, _me, _no_outcome)
    lay = U.clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, B=lay.common["B"] + 1)
    assert err and "B / seed" in err, err
    _no_outcome(lay)
    lay = U.clone(base, mk())
    real_prep = U.prepare

    def prep_drop(say, c, refuse_, hit_):
        S = real_prep(say, c, refuse_, hit_)
        ev = sorted(i for i, (_c, s_) in lay.fx.side.items() if s_ == "EVAL" and i in S["af"])
        S["af"] = {k: v for k, v in S["af"].items() if k not in ev[:1]}
        return S
    U.prepare = prep_drop
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        U.prepare = real_prep
    assert err and "[G14-NOROW] AF-U" in err, err
    assert not os.path.exists(os.path.join(lay.tmp, "res", "rsn", "READ_STARTED")), "the NOROW refusal came after the marker"
    _no_outcome(lay)
    lay = U.clone(base, mk())
    os.makedirs(os.path.join(lay.tmp, "res", "rsn"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "rsn", "READ_STARTED"), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_b3(base, mk, run_fn, me, no_outcome):
    """[B3]: one pick changed in each policy arm of the frozen file (K3, TRUE source, AF tree cell, TRUE source/domain)."""
    for arm, label in ((("xtree_cell", "K3"), "xtree_cell.K3"), (("true_source",), "true_source"), (("tree_cell",), "tree_cell"),
                       (("true_source_domain",), "true_source_domain")):
        lay = U.clone(base, mk())
        pol_p = os.path.join(lay.tmp, "res", "scratch", "pol.json")
        pol = U.json.load(open(pol_p, encoding="utf-8"))
        d = pol
        for k in arm:
            d = d[k]
        key = sorted(k for k in d if d[k] is not None)[0]
        d[key] = sorted(set(pol["roster"]) - {d[key]})[0]
        with open(pol_p, "w", encoding="utf-8") as f:
            U.json.dump(pol, f)
        _t, err, _r = U.cap(me(), run_fn, lay, uar_policy_sha=U.sha256_bytes(pol_p))
        assert err and "[B3]" in err and label in err, (label, err)
        no_outcome(lay)


def st_dry_run(base, mk):
    lay = U.clone(base, mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (ROUTE-SOURCE-NULL; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no EVAL key read", "AF-U cells per member", "POOL CHECK (B0-2): rc 0")
    for bad in ("RS1 (DECIDING", "D_S =", "IDENTITY:", "RWS NULL", "PREDICTION"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "rsn")), "the dry-run wrote under res/rsn"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (ROUTE-SOURCE-NULL; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 components", "DEFF 2.867", "n_eff 2,060", "SE 0.44pp", "MDE80 1.23pp", VERDICT_LINE,
         "B = 2000 two-stage replicates (default_rng(42))", "RWS 200 draws, default_rng(20261004 + r)",
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "e50a8e0fa267db96", "L24265-L24276", "calls 0")
    assert REG["out"] == "experiment_results/archv2/route_source_null/outcome.txt" and REG["uar_policy_sha"].startswith("8d68018c")
    assert REG["manifest_sha"].startswith("53021e26") and REG["rws_n"] == 200 and REG["B"] == 2000


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


need = U.need
CASES = (("branches", "RS1 three words incl. lo = 0 / G_AF at p97.5 and p2.5, rule 8, F-RS, P1 / P3 bands inclusive, Brier", "plain"),
         ("run_e2e", "--run end to end: G_SRC, D_S (point, interval, SE), RWS band and median vs an independent oracle; verdict by hand; write-once", "base"),
         ("refusals", "pool check, manifest pin, policy sha, DENOM, IDENTITY (each arm digit; each C1 / G_AF end), B3 (K3), marker exists; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run, "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    return U.run_selftest(TAG, CASES, _FN, HIT, only=only, quiet=quiet, base=base)


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "S", "", ""),
    ("X01 RS1 ABOVE at lo >= 0 (boundary)", "S", 'above = ds["lo"] > 0 and g_af > band[1]', 'above = ds["lo"] >= 0 and g_af > band[1]'),
    ("X02 RS1 ABOVE at G_AF >= p97.5 (boundary)", "S", 'above = ds["lo"] > 0 and g_af > band[1]', 'above = ds["lo"] > 0 and g_af >= band[1]'),
    ("X03 band open at both ends", "S", 'expl = band[0] <= g_af <= band[1] and', 'expl = band[0] < g_af < band[1] and'),
    ("X04 SOURCE-EXPLAINED without the interval clause", "S", 'expl = band[0] <= g_af <= band[1] and ds["lo"] <= 0 <= ds["hi"]', 'expl = band[0] <= g_af <= band[1]'),
    ("X05 ABOVE without the RWS clause", "S", 'above = ds["lo"] > 0 and g_af > band[1]', 'above = ds["lo"] > 0'),
    ("X06 F-RS fires on any non-ABOVE word", "S", '    if v == "SOURCE-EXPLAINED":' + NL + '        hit("FRS.FIRED")', '    if v != "ABOVE-SOURCE":' + NL + '        hit("FRS.FIRED")'),
    ("X07 rule 8 strict (end point 0 not 'contains')", "S", '    if ds["lo"] <= 0 <= ds["hi"]:' + NL + '        hit("RULE8.REFUTED")', '    if ds["lo"] < 0 < ds["hi"]:' + NL + '        hit("RULE8.REFUTED")'),
    ("X08 D_S against declared instead of SRC (wrong arm)", "S", 'ds=U.V.contrast(bt, D, "ALL", U.V.TREE, U.V.TSRC)', 'ds=U.V.contrast(bt, D, "ALL", U.V.TREE, U.V.TDOM)'),
    ("X09 G_SRC against the placebo (wrong baseline)", "S", 'gsrc=U.V.contrast(bt, D, "ALL", U.V.TSRC, U.V.BS)', 'gsrc=U.V.contrast(bt, D, "ALL", U.V.TSRC, U.V.PLAC)'),
    ("X10 band = min / max (min<->max of the draws)", "S", 'band=(U.pctl(rws, 2.5), U.pctl(rws, 97.5))', 'band=(min(rws), max(rws))'),
    ("X11 band upper = p95", "S", 'band=(U.pctl(rws, 2.5), U.pctl(rws, 97.5))', 'band=(U.pctl(rws, 2.5), U.pctl(rws, 95))'),
    ("X12 G_RWS without the best-single baseline", "S", 'out.append(float(U.routed_correct(D, pol, gb, g).mean()) - float(best))', 'out.append(float(U.routed_correct(D, pol, gb, g).mean()))'),
    ("X13 every RWS draw on one seed", "S", 'g, ng = U.rws_cells(D, prof, c["rws_seed0"] + r)', 'g, ng = U.rws_cells(D, prof, c["rws_seed0"])'),
    ("X14 identity refusal removed", "S", '    if not ok:' + NL + '        hit("REFUSE.IDENTITY")', '    if False:' + NL + '        hit("REFUSE.IDENTITY")'),
    ("X15 pre-read write-once check removed", "S", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X16 P3 read against P1's D_S band", "S", '("P3 median G_RWS +0.8pp [0.0, +1.6]", st["rws_med"], PRED_RWS_MED)', '("P3 median G_RWS +0.8pp [0.0, +1.6]", st["rws_med"], PRED_DS)'),
    ("X17 Brier scored on a fixed outcome", "S", 'U.brier(PROB_RS1, v)', 'U.brier(PROB_RS1, "UNDETERMINED")'),
    ("X18 verdict line of record dropped", "S", 'verdict line of record: %s" % (', '%s" % ('),
    ("X19 F-RS NOT FIRED line dropped (skip path)", "S", '        L.append("FALSIFIER F-RS: NOT FIRED (RS1 %s; F-RS fires iff RS1 SOURCE-EXPLAINED)" % v)', '        pass'),
    ("X20 rule-8 'not refuted' line dropped (skip path)", "S", '''        L.append("RULE 8: ABOVE-SOURCE is not refuted by D_S's interval (it excludes 0)")''', '        pass'),
    ("X21 B / seed check removed", "S", 'if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):', 'if False:'),
    ("X22 median = mean of the draws", "S", 'rws_med=U.pctl(rws, 50)', 'rws_med=float(np.mean(rws))'),
    ("C01 RWS EVAL filing ignores the TRAIN size weights", "C", 'rng.choice(len(w), size=len(epos), p=w / w.sum())', 'rng.choice(len(w), size=len(epos), p=None)'),
    ("C02 RWS blocks without the permutation", "C", 'g[pos[perm[off:off + sz]]] = base + j', 'g[pos[off:off + sz]] = base + j'),
    ("C03 RWS EVAL filed among the first source's cells (wrong source)", "C", 'g[epos] = starts[s] + rng.choice', 'g[epos] = 0 + rng.choice'),
    ("C04 RWS profile from EVAL (wrong split side)", "C", '        pos = [k for k in D.T if D.src[k] == s]' + NL + '        cnt = {}', '        pos = [k for k in D.E if D.src[k] == s]' + NL + '        cnt = {}'),
    ("C05 point fit with EVAL weight (uncapped fit)", "C", 'Pp = V.fit(L, V.train_full(D))', 'Pp = V.fit(L, np.ones(D.n, dtype=np.int64))'),
    ("C06 identity: TRUE source digit not compared", "C", 'for k in ("best", "tsrc", "af", "k0")) and', 'for k in ("best", "af", "k0")) and'),
    ("C07 identity: G_AF interval not compared", "C", '        and tuple(got["g_af"]) == tuple(idn["g_af"])', '        and True'),
    ("C08 identity: C1 not compared", "C", 'and tuple(got["c1"]) == tuple(idn["c1"])', 'and True'),
    ("C09 B3: K arms not compared", "C", '    for nm in KNAMES:' + NL + '        if nm not in pol', '    for nm in ():' + NL + '        if nm not in pol'),
    ("C10 denominator check skipped", "C", 'if (D.n_eval, n_comp) != (c["n_route"], c["comp_route"]):', 'if False:'),
    ("C11 marker not written before the EVAL key read", "C", '    G.read_marker(P(marker_path), marker_text)' + NL, '    pass' + NL),
    ("C12 manifest pin not checked", "C", 'if msha != c["manifest_sha"]:', 'if False:'),
    ("C13 policy sha not checked", "C", 'if sh != c["uar_policy_sha"]:', 'if False:'),
    ("C14 pool check ignored", "C", '    if rc != 0:' + NL + '        hit("REFUSE.POOL")', '    if rc < 0:' + NL + '        hit("REFUSE.POOL")'),
    ("C15 percentile rule = lower", "C", 'return float(np.percentile(np.asarray(xs, dtype=np.float64), q))', 'return float(np.percentile(np.asarray(xs, dtype=np.float64), q, method="lower"))'),
    ("C16 prediction bands exclusive", "C", '    return bool(band[0] <= x <= band[1])', '    return bool(band[0] < x < band[1])'),
    ("C17 Brier indicator inverted", "C", '(1.0 if o == observed else 0.0)', '(0.0 if o == observed else 1.0)'),
    ("C18 NOROW refusal removed", "C", '        if norow:' + NL + '            hit("REFUSE.NOROW")', '        if False:' + NL + '            hit("REFUSE.NOROW")'),
    ("C19 B3: TRUE source not compared", "C", 'for k in ("tree_cell", "true_source", "true_source_domain"):', 'for k in ("tree_cell", "true_source_domain"):'),
)


if __name__ == "__main__":
    sys.exit(main())
