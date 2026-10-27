"""CERT-REDRAW-R512 -- do the only two splits the thesis may call certified (bareq512_s42 Chemistry n00000006 and
Engineering n00000015, hierarchical BH at per-family q = 0.05, R512) keep that status on the two recorded R512 re-draws
(dimsweep2 s137, s2048), and which sites survive a top-down weighted FWER at 0.05?  Zero calls; no DB is opened.

REGISTRATION OF RECORD: docs/judge_v2_program.md L21680-L21703 (commit a357ef0, parent b9491bf), heading "## Registered
2026-09-27 (before any code or call) -- CERT-REDRAW-R512: ...". DESCRIPTIVE, POST-HOC-SEEN (the registration's
disclosure). The registration governs; this docstring restates it and never replaces it.

INSTRUMENT: tools/analysis/cert_resolution.py (blob:dbe9425d, the base) is IMPORTED UNCHANGED; its reading, pinning,
k-recovery, identity check, p / CP / flat BH / BY / hierarchical BH and E-words are reused as they are. This file adds
the NEW TREE SPEC for the two re-draws, the D11 top-down weighted FWER (R2), the qualifier rule (R3), C1 / C2, P1-P4 and
F1. Every mode REFUSES unless the imported base's LF sha256 equals BASE_LF below, so the reused logic is the pinned logic
and the base's behaviour for its own four trees cannot change through this instrument (the base file is not edited).

LAUNCH SEQUENCE
  python tools/analysis/cert_redraw_r512.py --selftest   synthetic fixtures only (tempfile): every check, every registered
                                                         print branch, this file's mutants, and the base's reviewer
                                                         mutants crB / crK as source-level copies (all must be killed)
  python tools/analysis/cert_redraw_r512.py --dry-run    reads the real CSVs and parent maps: pins, locations, m, snapshot
                                                         ids, last records, k recovery, identity checks, multi-parent
                                                         counts, the structural leg (g) per site (n_s / N only); computes
                                                         NO p, CP, BH or FWER on a real row; writes nothing
  python tools/analysis/cert_redraw_r512.py --run        after the READY and after the OPEN RULINGS below are recorded:
                                                         selftest in-process first (refuses if red), then WRITE-ONCE (mode
                                                         "x"; refuses if either exists)
                                                         experiment_results/cert_redraw_r512/cert_redraw_r512_outcome.txt
                                                         experiment_results/cert_redraw_r512/cert_redraw_r512_sites.csv
  Options: --data-root DIR (repeatable; default: this checkout, then the main checkout through git's common dir),
           --evidence-dir DIR (as cert_resolution.py; used for bareq512_s42's dag_snapshots.jsonl only),
           --out-dir DIR.

POOL: none. The first printed line of every mode is "pool: none (no DB opened)". Not a pool reader (CONTEXT rule 7).

INPUTS (registration HYGIENE; full sha256 of the LF rendering pinned below; blob = git blob id of the LF bytes)
  bareq512_s42    the CSV and parent map of CERT-RESOLUTION (the base's TREES[0] spec, pins unchanged)
  bareq512_s137   experiment_results/dimsweep2/site_null_bareq512_s137.csv (67 sites, snapshot 20260909_154122_...)
                  + experiment_results/dimsweep2/bareq512_s137/seed_137/dag_snapshots.jsonl (last record: iteration 10,
                  152 nodes; the byte-identical diagnostics/ copy is an accepted location)
  bareq512_s2048  experiment_results/dimsweep2/site_null_bareq512_s2048.csv (71 sites, snapshot 20260909_160314_...)
                  + .../bareq512_s2048/seed_2048/dag_snapshots.jsonl (last record: iteration 13, 160 nodes)

DEFINITIONS (registration INSTRUMENT / READOUTS; k and p exactly as the base)
  k = round(q_site x 300) (the null exceedance count), p = (k + 1) / 301 (fractions.Fraction).
  R1  the base's hierarchical BH (per-family q = 0.05), flat BH and BY, per re-draw (s42 printed beside as an instrument
      check against CERT-RESOLUTION's recorded set {n00000006, n00000015}; not a criterion).
  R2  D11 top-down weighted FWER: alpha_s = 0.05 x n_s / N; N = sum of n over the sites with NO site ancestor; s is tested
      only if its parent site (if any) is rejected; rejection iff p_s <= alpha_s. Applied to s42, s137, s2048.
      BUILDER'S READING (inert when every tree has 0 multi-parent sites, printed): "parent site" = the nearest site
      ancestor along parentIds[0] (the base's family key); a tree with a multi-parent site has R2 VOID (never guessed).
  R3  qualifier words per exhibit (literal below); the R2 status beside, per tree.
  Anchors (the exhibits) are matched by LABEL among each tree's depth-1 sites.

OPEN RULINGS (the --run REFUSES while OPEN_RULINGS is non-empty; reported to the registrar, NOT resolved in code)
  O1  fringe-site identity ("one-to-one Jaccard >= 0.5 on shared train texts", ANCHOR-FREE-REDRAW's rule) needs node
      member sets, which exist only in snapshots.db (graph queryIds); dag_snapshots.jsonl carries none. The registration's
      HYGIENE says "No DB" and COST "CSVs and snapshot files only". No readout (R1-R3, C1, C2, P1-P4, F1) uses a fringe
      identity; it is NOT computed here.
  O2  P4 "R2 on s42 rejects a non-empty subset of {Chemistry, Engineering}" has two readings that can disagree on the
      same data: (A) R2's rejections include at least one of the two; (B) R2's rejected set is non-empty and contained
      in the two. Both branches are implemented and executed by the selftest; P4_READING stays None until ruled.
[RULED 2026-09-27, ruling R1 (the orchestrator's; programme L21831-L21846, 3fdc5d2; insertion only, the text above stands as
the builder's report): O1 NOT COMPUTED; O2 = reading (A) ("at least one of {Chemistry, Engineering} rejected"), with the
disclosure that Engineering is R2-unreachable on s42, so under (A) P4 is equivalent to "R2 on s42 rejects Chemistry" (P4's
prior 0.55 was set without this). OPEN_RULINGS = {} and P4_READING = "A". Engineering / any exhibit outside R2's reachable set
prints "UNREACHABLE at 300 reps (n/N x.xxxx < 0.0664)", never "not FWER 0.05" (READY 114f80f H2). H1: R2's p is (k + 1) / 301
through analyze(), pinned by a k = 0 unreachable site (tested, not rejected) beside its reachable twin (rejected). M-1: each
tree prints whether R2 at 300 reps reduces to a weighted Bonferroni over its top family. D4 / D5: the sites CSV's
fwer_rejected and alpha_s are asserted row by row. M-3 (the soft instrument-check mismatch) and M-2 (non-nested weights,
forward) are unchanged: not ruled.]
[DELTA 2026-09-29 w0-delta3, the engine-coder, after delta-2 READY b2ad5ef C6-1 and ruling 13 (registrar's record 2026-09-29,
e09e551); insertion only, the text above stands] Ruling 13 (M-3): an INSTRUMENT CHECK MISMATCH REFUSES. run() evaluates
instrument_check(res) BEFORE render and before any output file or directory is created; on a mismatch it prints a REFUSAL LOG
(the header and inputs lines, then "INSTRUMENT CHECK MISMATCH (ruling 13): ... REFUSED: no outcome is written ...") and raises;
C1, C2, R3, P1-P4 and F1 are never printed. render() raises the same refusal on a mismatch (defence in depth; the "suspect"
wording is gone). A VOID s42 hierarchical leg is not a mismatch and is unchanged (printed, "cannot be compared"). Selftest
st5b_mismatch_refuses runs run() end to end on a fixture whose s42 set differs (refusal, log, no file, none of the verdict
lines); st5's full-path fixture now carries s42's recorded ids n00000006 / n00000015 (MATCH, outcome written); st6 asserts
render's refusal. Mutant "ic_soft" (the delta-1 soft check restored) is in MUTANTS. LOW: st4b's conditional assert
parenthesised. M-2 (ruling 14) stays forward (RP50).
[DELTA 2026-09-29, the engine-coder, after ruling N6-1 (the registrar's; programme section "## Registrar's record 2026-09-29
... the N6-1 ruling ...", 1ba9a04); insertion only, the text above stands] A VOID s42 hierarchical leg is a FAILED
PRECONDITION exactly as a mismatch is (ruling 13 extended): run() REFUSES before render and before any output file or directory
(REFUSAL LOG: the header and inputs lines, then "INSTRUMENT CHECK VOID (ruling N6-1, ruling 13 extended): ... REFUSED ..."),
and render() raises the same refusal (defence in depth). The sentence above "A VOID s42 hierarchical leg is not a mismatch and
is unchanged" is superseded by this bracket. INERT for the run of record (the check REPRODUCED {n00000006, n00000015}; no VOID
leg arose). Selftest st5c_void_refuses runs run() end to end on a fixture whose s42 identity check fails ("n00000006 depth 1 !=
CSV 2", the re-draws intact): refusal, log, no path created, none of the verdict lines. st6: scenario 7 (s42 VOID) is replaced
by s42 MATCH with no depth-1 site labelled Engineering (keeps R3-not-exhibit executed) and render's VOID refusal is asserted.
Mutant "ic_void_soft" (the old behaviour: printed "cannot be compared", then the readouts) is in MUTANTS.
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import io
import math
import os
import shutil
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cert_resolution as CR          # noqa: E402  (the base; imported, never edited)

BASE_REL = "tools/analysis/cert_resolution.py"
BASE_BLOB = "dbe9425dc406edcd41661a6df4e00d33b44299b6"
BASE_LF = "3e3fb1b91aa3d361490d1321e2e609c47c7b292c076881f5e77643d363ad24af"

REPS = CR.REPS
Q = CR.Q
POOL_LINE = CR.POOL_LINE
FLOOR = Fraction(1, REPS + 1)

OUT_REL = "experiment_results/cert_redraw_r512"
OUT_OUTCOME = "cert_redraw_r512_outcome.txt"
OUT_SITES = "cert_redraw_r512_sites.csv"
REG_LINE = ("CERT-REDRAW-R512 outcome (registration docs/judge_v2_program.md L21680-L21703, a357ef0). Zero calls. "
            "DESCRIPTIVE, POST-HOC-SEEN.")

S42 = dict(CR.TREES[0], snapshot="20260909_212117_Headless_Run_Auto_ge")
S137 = dict(name="bareq512_s137", recipe="R512", m=67, snapshot="20260909_154122_Headless_Run_Auto_ge",
            csv=dict(rel="experiment_results/dimsweep2/site_null_bareq512_s137.csv",
                     lf="8bd6c8de94a6de28641c1e1bf4f85497c96580b68c1626b546ec031ae8049ba9"),
            jsonl=dict(rels=["experiment_results/dimsweep2/bareq512_s137/seed_137/dag_snapshots.jsonl",
                             "experiment_results/dimsweep2/bareq512_s137/seed_137/diagnostics/dag_snapshots.jsonl"],
                       lf="8da4e1ef92f72de126b532d5d052d7b3ade9bd590fccebe3d006300c5d86c0a0"),
            last_iter=10, last_nodes=152)
S2048 = dict(name="bareq512_s2048", recipe="R512", m=71, snapshot="20260909_160314_Headless_Run_Auto_ge",
             csv=dict(rel="experiment_results/dimsweep2/site_null_bareq512_s2048.csv",
                      lf="a88d75edc5be5d5b5cec669f7cfd9693823b8cc75d5d3a86b210582be353241f"),
             jsonl=dict(rels=["experiment_results/dimsweep2/bareq512_s2048/seed_2048/dag_snapshots.jsonl",
                              "experiment_results/dimsweep2/bareq512_s2048/seed_2048/diagnostics/dag_snapshots.jsonl"],
                        lf="ab36d2fcc255a35a3e93862598e36a9b7f8d80df80c3018464899562c1ee6abe"),
             last_iter=13, last_nodes=160)
TREES = [S42, S137, S2048]
RECORD = "bareq512_s42"
REDRAWS = ["bareq512_s137", "bareq512_s2048"]
EXHIBITS = ["Engineering", "Chemistry"]                     # C1 = Engineering, C2 = Chemistry
RECORDED_S42_HIER = {"n00000006", "n00000015"}              # CERT-RESOLUTION outcome (instrument check only)
RECORDED_S42_LABELS = {"Chemistry": "n00000006", "Engineering": "n00000015"}
P1_PROB, P2_PROB, P3_PROB, P4_PROB = "0.70", "0.65", "0.70", "0.55"
P3_RANGE = (1, 4)

R3_PREFIX = "certified at per-family FDR q = 0.05 on bareq512_s42"
R3_BOTH = R3_PREFIX + " and on both R512 re-draws"
R3_ONE = R3_PREFIX + " and on 1 of 2 R512 re-draws ({name})"
R3_NEITHER = R3_PREFIX + " not on either R512 re-draw"
FWER_WORDS = "FWER 0.05 against the Gaussian site null, arbitrary dependence across sites"
FWER_ALSO = "also FWER 0.05"
FWER_NOT = "not FWER 0.05"

OPEN_RULINGS = {}                     # O1 / O2 RULED (R1, programme L21831-L21846, 3fdc5d2): O1 not computed, O2 = reading A
P4_READING = "A"                      # R1: "at least one of {Chemistry, Engineering} rejected"
UNREACHABLE_FMT = "UNREACHABLE at 300 reps (n/N %.4f < 0.0664)"

SITES_COLUMNS = CR.SITES_COLUMNS + ["n_over_N", "alpha_s", "fwer_reachable_k0", "fwer_tested", "fwer_rejected",
                                    "exhibit"]

MUTANT = None
BRANCH_HITS = set()


class Refusal(CR.Refusal):
    pass


def _m(name):
    return MUTANT == name


def _hit(tag):
    BRANCH_HITS.add(tag)


# ----------------------------------------------------------------------------------------------------------- identity
def file_pins(path):
    with open(path, "rb") as fh:
        return CR.pins_of_bytes(fh.read())


def base_identity_check(module=CR):
    p = file_pins(module.__file__)
    if (p["lf"] != BASE_LF or p["blob"] != BASE_BLOB) and not _m("no_base_pin"):
        raise Refusal("REFUSED: the imported base %s is blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s"
                      % (module.__file__, p["blob"][:8], p["lf"][:16], BASE_BLOB[:8], BASE_LF[:16]))
    return ("base %s blob:%s / sha256-lf16:%s / sha256-crlf16:%s (imported unchanged; working file %s)"
            % (BASE_REL, p["blob"][:8], p["lf"][:16], p["crlf"][:16], "CRLF" if p["raw_crlf"] else "LF"))


def self_identity():
    p = file_pins(os.path.abspath(__file__))
    return "script tools/analysis/cert_redraw_r512.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (
        p["blob"][:8], p["lf"][:16], p["crlf"][:16])


# ----------------------------------------------------------------------------------------------------------- inputs
def locate_any(spec, data_roots, evidence_dir, out):
    """spec: rel (str) or rels (list), lf, optional evidence. First candidate whose LF sha256 equals the pin wins."""
    rels = spec.get("rels") or [spec["rel"]]
    lf = spec["lf"] if not _m("no_pin_check") else None
    last = None
    for i, rel in enumerate(rels):
        sub = dict(rel=rel, lf=lf if lf is not None else "")
        if spec.get("evidence") and i == 0:
            sub["evidence"] = spec["evidence"]
        if lf is None:                                   # mutant: accept the first existing file
            for r in data_roots:
                c = os.path.join(r, rel)
                if os.path.isfile(c):
                    with open(c, "rb") as fh:
                        raw = fh.read()
                    return c, raw, CR.pins_of_bytes(raw)
            continue
        try:
            return CR.locate(sub, data_roots, evidence_dir if spec.get("evidence") else None, out)
        except CR.Refusal as e:
            last = e
    raise Refusal("REFUSED: no candidate location of %s matches its pin sha256-lf16:%s (%s)"
                  % (rels, spec["lf"][:16], last))


def load_inputs(trees, data_roots, evidence_dir, out):
    loaded = []
    for t in trees:
        cpath, craw, cp = locate_any(t["csv"], data_roots, None, out)
        out.write(CR.pin_line("  %-14s csv  " % t["name"], cpath, cp) + "\n")
        jpath, jraw, jp = locate_any(t["jsonl"], data_roots, evidence_dir, out)
        out.write(CR.pin_line("  %-14s dag  " % t["name"], jpath, jp) + "\n")
        sites, snap = CR.read_sites(craw, t["name"])
        if len(sites) != t["m"] and not _m("no_m_check"):
            raise Refusal("REFUSED: %s has %d site rows, the registration fixes m = %d" % (t["name"], len(sites), t["m"]))
        if snap != t["snapshot"] and not _m("no_snapshot_check"):
            raise Refusal("REFUSED: %s CSV snapshot_id %s, registered %s" % (t["name"], snap, t["snapshot"]))
        rec = CR.read_last_record(jraw)
        if t.get("last_iter") is not None and not _m("no_last_record_check") and (
                rec["iteration"] != t["last_iter"] or len(rec["nodes"]) != t["last_nodes"]):
            raise Refusal("REFUSED: %s last record is iteration %s with %d nodes; pinned %s / %s"
                          % (t["name"], rec["iteration"], len(rec["nodes"]), t["last_iter"], t["last_nodes"]))
        fails = CR.identity_check(sites, rec)
        loaded.append((t, sites, rec, fails, snap))
    return loaded


# ----------------------------------------------------------------------------------------------------------- R2
def top_sites(sites, anc):
    return [s for s in sites if not anc[s["node_id"]]]


def fwer_denominator(sites, anc):
    if _m("fwer_N_all"):
        return sum(s["n"] for s in sites)
    return sum(s["n"] for s in top_sites(sites, anc))


def fwer_reachable_k0(n, N):
    """Structural leg (g): at k = 0, p = 1/301 <= 0.05 x n / N. No null count is read."""
    return FLOOR <= Q * Fraction(n, N)


def fwer_topdown(sites, fam, anc, pmap, q=Q):
    """D11 top-down weighted FWER. Returns N, alpha per site, tested set, rejected set, reachable (structural) set."""
    CR.STAT_CALLS[0] += 1
    N = fwer_denominator(sites, anc)
    if N <= 0:
        raise Refusal("REFUSED: FWER denominator N = %d" % N)
    for s in sites:                                   # fam TOP <=> no site ancestor (asserted; multi-parent trees are VOID)
        if (fam[s["node_id"]] == "TOP") != (not anc[s["node_id"]]):
            raise Refusal("REFUSED: %s: family key and site-ancestor set disagree" % s["node_id"])
    order = sorted(sites, key=lambda s: (len(anc[s["node_id"]]), s["node_id"]))
    alpha, tested, rejected, reach = {}, set(), set(), set()
    for s in order:
        v = s["node_id"]
        if _m("fwer_unweighted"):
            a = q / len(top_sites(sites, anc))
        else:
            a = q * Fraction(s["n"], N)
        alpha[v] = a
        if fwer_reachable_k0(s["n"], N):
            reach.add(v)
        parent = fam[v]
        if parent != "TOP" and parent not in rejected and not _m("fwer_no_parent_gate"):
            continue
        tested.add(v)
        if (pmap[v] < a) if _m("fwer_lt") else (pmap[v] <= a):
            rejected.add(v)
    return dict(N=N, alpha=alpha, tested=tested, rejected=rejected, reachable=reach, void=None)


# ----------------------------------------------------------------------------------------------------------- per tree
def anchors_of(sites):
    """label -> node_id over the depth-1 sites; refuses on a duplicated depth-1 label."""
    out = {}
    for s in sites:
        if s["depth"] == 1:
            if s["label"] in out:
                raise Refusal("REFUSED: depth-1 label %r appears twice" % s["label"])
            out[s["label"]] = s["node_id"]
    return out


def structure(sites, rec, fails):
    if fails:
        return None, None, None
    return CR.site_structure(sites, rec)


def analyze(spec, sites, rec, fails, module=CR):
    base = module.analyze_tree(spec, sites, rec, fails)
    anchors = anchors_of(sites)
    if _m("anchor_by_id"):
        anchors = dict(RECORDED_S42_LABELS)
    pmap = {s["node_id"]: CR.p_site(s["k"], s["reps"]) for s in sites}
    fam, anc, multi = structure(sites, rec, fails)
    if fails:
        fw = dict(void="identity check failed")
    elif multi and not _m("multi_not_void"):
        fw = dict(void="%d multi-parent site(s): 'its parent site' is unruled for a multi-parent site" % multi)
    else:
        fw = fwer_topdown(sites, fam, anc, pmap)
    base.update(anchors=anchors, fwer=fw, n_of={s["node_id"]: s["n"] for s in sites},
                top_ids=None if anc is None else {s["node_id"] for s in top_sites(sites, anc)})
    return base


# ----------------------------------------------------------------------------------------------------------- readouts
def in_hier(r, label):
    """True / False, or None when the hierarchical leg is VOID."""
    if r["hier"] is None:
        return None
    v = r["anchors"].get(label)
    return bool(v is not None and v in r["hier"])


def in_fwer(r, label):
    if r["fwer"].get("void"):
        return None
    v = r["anchors"].get(label)
    return bool(v is not None and v in r["fwer"]["rejected"])


def fwer_word(r, label):
    """The R2 word beside an exhibit (READY 114f80f H2 / ruling R1): VOID; rejected -> 'also FWER 0.05'; outside the
    structurally reachable set -> 'UNREACHABLE at 300 reps (n/N ...)' (a property of the tree, never a data outcome);
    otherwise 'not FWER 0.05'."""
    st = in_fwer(r, label)
    if st is None:
        return "R2 VOID"
    if st:
        return FWER_ALSO
    v = r["anchors"].get(label)
    if v is not None and v not in r["fwer"]["reachable"]:
        _hit("R2-UNREACHABLE")
        return UNREACHABLE_FMT % (r["n_of"][v] / r["fwer"]["N"])
    return FWER_NOT


def m1_line(fw, top_ids):
    """READY 114f80f M-1: whether R2 at 300 reps reduces to a weighted Bonferroni over the top family."""
    deeper = sorted(v for v in fw["reachable"] if v not in top_ids)
    if not deeper:
        return ("  R2 at 300 reps reduces to weighted Bonferroni over the %d top-family sites (no deeper site reachable)"
                % len(top_ids))
    return ("  R2 at 300 reps reaches %d site(s) below the top family (%s): the top-down gate is active"
            % (len(deeper), ", ".join(deeper)))


def r3_words(k_redraws, names):
    if k_redraws == 2:
        return R3_BOTH
    if k_redraws == 1:
        return R3_ONE.format(name=names[0])
    return R3_NEITHER


def support_lines():
    se = math.sqrt(0.05 * 0.95 / REPS)
    return [
        "SUPPORT (registered)",
        " (a) denominators: sites per tree 70 / 67 / 71 (bareq512_s42 / s137 / s2048); 300 null reps per site",
        " (b) DEFF 1, BY CONSTRUCTION (independent Monte-Carlo reps; declared, not measured)",
        " (c) n_eff = 300 per site",
        " (d) SE at the per-site bar: sqrt(0.05 x 0.95 / 300) = sqrt(%.8f) = %.5f" % (0.05 * 0.95 / REPS, se),
        " (e) MDE80: 2.80 x %.5f = %.4f on q_site" % (se, 2.80 * se),
        " (f) VERDICT LINE: DESCRIPTIVE-ONLY (the outcome is largely seen; no prediction is scoreable)",
        " (g) STRUCTURAL LEG: p floor 1/301 = %.5f; a rank-1 BH rejection in a family of m_f needs 0.05 / m_f >= p: k = 1 "
        "(p = 2/301 = %.5f) needs m_f <= %d, k = 0 needs m_f <= %d; R2 reaches a site at k = 0 only if n_s / N >= "
        "(1/301) / 0.05 = %.4f; smaller sites are UNREACHABLE at 300 reps by construction (per site, per tree)"
        % (float(FLOOR), 2 / 301.0, max(m for m in range(1, 100) if Fraction(2, 301) <= Q / m),
           max(m for m in range(1, 100) if FLOOR <= Q / m), float(FLOOR / Q)),
    ]


def reach_line(name, sites, anc):
    N = sum(s["n"] for s in top_sites(sites, anc))
    reach = [s for s in sites if fwer_reachable_k0(s["n"], N)]
    return ("  %-14s R2 structural: N = %d (top family %d sites); reachable at k = 0: %d of %d: %s"
            % (name, N, len(top_sites(sites, anc)), len(reach), len(sites),
               ", ".join("%s %s (n/N %.4f)" % (s["node_id"], s["label"], s["n"] / N) for s in reach) or "(none)"))


def instrument_check(res):
    """-> ("VOID" | "MATCH" | "MISMATCH", bareq512_s42's hierarchical set sorted or None)."""
    b = res[RECORD]
    if b["hier"] is None:
        return "VOID", None
    return ("MATCH" if set(b["hier"]) == RECORDED_S42_HIER else "MISMATCH"), sorted(b["hier"])


def mismatch_line(hier):
    _hit("IC-mismatch")
    return ("INSTRUMENT CHECK MISMATCH (ruling 13): bareq512_s42's hierarchical BH set %s differs from CERT-RESOLUTION's "
            "recorded {n00000006, n00000015}. REFUSED: no outcome is written; C1, C2, R3, P1-P4 and F1 are not printed (a READY "
            "defect, not an outcome)." % hier)


def void_line():
    """Ruling N6-1 (the registrar's, programme section "## Registrar's record 2026-09-29 ... the N6-1 ruling ...", 1ba9a04):
    a VOID s42 hierarchical leg is a FAILED PRECONDITION exactly as a mismatch is (ruling 13 extended)."""
    _hit("IC-VOID")
    return ("INSTRUMENT CHECK VOID (ruling N6-1, ruling 13 extended): bareq512_s42's hierarchical leg is VOID, so "
            "CERT-RESOLUTION's recorded {n00000006, n00000015} cannot be compared. REFUSED: a failed precondition, as a mismatch; "
            "no outcome is written; C1, C2, R3, P1-P4 and F1 are not printed.")


def render(res, header_lines):
    L = list(header_lines)
    L += support_lines()
    L.append("R512 ONLY: never set against R256 counts. The re-draws are on their own pre-closure splits (id-disjoint only) "
             "and pre-P7-FIX, like s42.")
    for t in TREES:
        r = res[t["name"]]
        L.append("")
        L.append("== %s (%s): m = %d sites%s" % (r["name"], r["recipe"], r["m"],
                                                  "  [record; R1 printed as an instrument check]" if r["name"] == RECORD else ""))
        if r["identity_fails"]:
            _hit("identity-void")
            L.append("  IDENTITY CHECK FAILED (%d): hierarchical leg and R2 VOID for this tree (a failed precondition, not an "
                     "outcome): %s" % (len(r["identity_fails"]), "; ".join(r["identity_fails"][:10])))
        else:
            _hit("identity-pass")
            L.append("  identity check: PASS (%d sites; multi-parent sites: %d)" % (r["m"], r["multi"]))
        L.append("  R1 flat BH at q = 0.05: %d of %d%s; BY (descriptive): %d of %d"
                 % (len(r["flat"]), r["m"], (" (cutoff %.6f)" % float(r["flat_thr"])) if r["flat_thr"] is not None else "",
                    len(r["by"]), r["m"]))
        if r["hier"] is None:
            _hit("R1-VOID")
            L.append("  R1 hierarchical BH: VOID")
        else:
            _hit("R1-computed")
            L.append("  R1 hierarchical BH (per-family q = 0.05; tree-wide FDR NOT claimed): %d: %s; top family %s sites"
                     % (len(r["hier"]), ", ".join("%s %s" % (v, r["labels"].get(v, "")) for v in sorted(r["hier"])) or "(empty)",
                        r["top_size"]))
        fw = r["fwer"]
        if fw.get("void"):
            _hit("R2-VOID")
            L.append("  R2 (%s): VOID (%s)" % (FWER_WORDS, fw["void"]))
        else:
            _hit("R2-computed")
            L.append("  R2 (%s): N = %d; tested %d; reachable at k = 0 %d; rejected %d: %s"
                     % (FWER_WORDS, fw["N"], len(fw["tested"]), len(fw["reachable"]), len(fw["rejected"]),
                        ", ".join("%s %s (alpha_s %.6f)" % (v, r["labels"].get(v, ""), float(fw["alpha"][v]))
                                  for v in sorted(fw["rejected"])) or "(empty)"))
            L.append("  R2 structural leg (g): reachable at k = 0 (n_s / N >= 0.0664): %s; every other site UNREACHABLE at 300 reps"
                     % (", ".join("%s %s (n/N %.4f)" % (v, r["labels"].get(v, ""), r["n_of"][v] / fw["N"])
                                  for v in sorted(fw["reachable"])) or "(none)"))
            if r.get("top_ids") is not None:
                L.append(m1_line(fw, r["top_ids"]))
    b = res[RECORD]
    L.append("")
    if b["hier"] is None:
        if not _m("ic_void_soft"):
            raise Refusal("REFUSED: " + void_line())                               # ruling N6-1
        _hit("IC-VOID")                                  # the pre-N6-1 behaviour, reachable only under mutant ic_void_soft
        L.append("INSTRUMENT CHECK: bareq512_s42's hierarchical leg VOID; CERT-RESOLUTION's recorded set cannot be compared.")
    elif set(b["hier"]) == RECORDED_S42_HIER:
        _hit("IC-match")
        L.append("INSTRUMENT CHECK: bareq512_s42's hierarchical BH set reproduces CERT-RESOLUTION's recorded {n00000006, n00000015}.")
    elif _m("ic_soft"):
        _hit("IC-mismatch")
        L.append("INSTRUMENT CHECK MISMATCH: bareq512_s42's hierarchical BH set %s differs from CERT-RESOLUTION's recorded "
                 "{n00000006, n00000015}; the readouts below are printed but the instrument is suspect." % sorted(b["hier"]))
    else:
        raise Refusal("REFUSED: " + mismatch_line(sorted(b["hier"])))           # ruling 13
    L.append("")
    L.append("R3 QUALIFIERS (the words of record for each exhibit)")
    memb = {lab: {n: in_hier(res[n], lab) for n in REDRAWS} for lab in EXHIBITS}
    for lab in EXHIBITS:
        vals = memb[lab]
        beside = "; ".join("%s %s" % (n, fwer_word(res[n], lab)) for n in [RECORD] + REDRAWS)
        if in_hier(b, lab) is not True:
            _hit("R3-not-exhibit")
            L.append("  %s: not in bareq512_s42's hierarchical BH set here; the R3 words do not apply. R2: %s" % (lab, beside))
            continue
        if any(v is None for v in vals.values()):
            _hit("R3-VOID")
            L.append("  %s: R3 VOID (a re-draw's hierarchical leg is VOID). R2: %s" % (lab, beside))
            continue
        yes = [n for n in REDRAWS if vals[n]]
        _hit("R3-%d" % len(yes))
        L.append("  %s: \"%s\". R2: %s" % (lab, r3_words(len(yes), yes), beside))
    L.append("")
    L.append("CRITERIA (scored as readouts, POST-HOC-SEEN; the POINT decides; the CP never decides)")
    crit = {}
    for cname, lab in (("C1", "Engineering"), ("C2", "Chemistry")):
        vals = memb[lab]
        detail = ", ".join("%s %s" % (n, {True: "in", False: "absent", None: "VOID"}[vals[n]]) for n in REDRAWS)
        if any(v is None for v in vals.values()):
            _hit(cname + "-VOID")
            crit[cname] = None
            L.append("%s VOID POST-HOC-SEEN: %s; a re-draw's hierarchical leg is VOID (%s)." % (cname, lab, detail))
        elif all(vals.values()) if not _m("c_any") else any(vals.values()):
            _hit(cname + "-HELD")
            crit[cname] = True
            L.append("%s HELD POST-HOC-SEEN: %s is in the hierarchical BH set of both re-draws (%s)." % (cname, lab, detail))
        else:
            _hit(cname + "-FAILED")
            crit[cname] = False
            L.append("%s FAILED POST-HOC-SEEN: %s is absent from a re-draw's hierarchical BH set (%s)." % (cname, lab, detail))
    for lab in EXHIBITS:
        for n in REDRAWS:
            if res[n]["hier"] is not None and lab not in res[n]["anchors"]:
                _hit("anchor-missing")
                L.append("  NOTE: %s has no depth-1 SITE labelled %s (a leaf or absent); counted as absent." % (n, lab))
    L.append("")
    L.append("PREDICTIONS (DESCRIPTIVE; scored HELD / FAILED, not a test)")
    c1 = crit["C1"]
    if c1 is None:
        _hit("P1-UNSCORED")
        L.append("P1 UNSCORED: C1 VOID (registered probability %s)." % P1_PROB)
    else:
        _hit("P1-HELD" if c1 else "P1-FAILED")
        L.append("P1 %s: Engineering in R1's set on both re-draws: %s (registered probability %s)."
                 % ("HELD" if c1 else "FAILED", "yes" if c1 else "no", P1_PROB))
    ch = memb["Chemistry"]
    if any(v is None for v in ch.values()):
        _hit("P2-UNSCORED")
        L.append("P2 UNSCORED: a re-draw's hierarchical leg is VOID.")
    else:
        ok = bool(ch["bareq512_s137"] and not ch["bareq512_s2048"])
        if _m("p2_swap"):
            ok = bool(ch["bareq512_s2048"] and not ch["bareq512_s137"])
        _hit("P2-HELD" if ok else "P2-FAILED")
        L.append("P2 %s: Chemistry in R1's set on s137 (%s) and not on s2048 (%s) (registered probability %s)."
                 % ("HELD" if ok else "FAILED", "in" if ch["bareq512_s137"] else "absent",
                    "in" if ch["bareq512_s2048"] else "absent", P2_PROB))
    if any(res[n]["hier"] is None for n in REDRAWS):
        _hit("P3-UNSCORED")
        L.append("P3 UNSCORED: a re-draw's hierarchical leg is VOID.")
    else:
        lo, hi = P3_RANGE if not _m("p3_range_wide") else (0, 5)
        sizes = {n: len(res[n]["hier"]) for n in REDRAWS}
        ok = all(lo <= s <= hi for s in sizes.values())
        _hit("P3-HELD" if ok else "P3-FAILED")
        L.append("P3 %s: each re-draw's R1 set has 1-4 sites: %s (registered probability %s)."
                 % ("HELD" if ok else "FAILED", ", ".join("%s %d" % kv for kv in sizes.items()), P3_PROB))
    fw = b["fwer"]
    ce = {b["anchors"][lab] for lab in ("Chemistry", "Engineering") if lab in b["anchors"]}
    if fw.get("void"):
        _hit("P4-UNSCORED")
        L.append("P4 UNSCORED: R2 on bareq512_s42 VOID.")
    elif P4_READING is None:
        _hit("P4-OPEN")
        L.append("P4 UNSCORED: its reading is OPEN (ruling O2); R2 on bareq512_s42 rejects %s; {Chemistry, Engineering} "
                 "among them: %d (registered probability %s)."
                 % (sorted(fw["rejected"]), len(fw["rejected"] & ce), P4_PROB))
    else:
        rej = fw["rejected"]
        ok = bool(rej & ce) if P4_READING == "A" else bool(rej and rej <= ce)
        _hit("P4-%s-%s" % (P4_READING, "HELD" if ok else "FAILED"))
        L.append("P4 %s (reading %s, ruled): R2 on bareq512_s42 rejects %s (registered probability %s)."
                 % ("HELD" if ok else "FAILED", P4_READING, sorted(rej), P4_PROB))
        unr = [lab for lab in ("Chemistry", "Engineering") if lab in b["anchors"] and b["anchors"][lab] not in fw["reachable"]]
        if unr:
            L.append("  DISCLOSED (R1): %s %s on bareq512_s42, so under reading A P4 reads the other exhibit alone; the prior %s "
                     "was set without this." % (", ".join(unr), ", ".join(UNREACHABLE_FMT % (b["n_of"][b["anchors"][x]] / fw["N"])
                                                                        for x in unr), P4_PROB))
    L.append("")
    L.append("FALSIFIER")
    allv = [memb[lab][n] for lab in EXHIBITS for n in REDRAWS]
    if any(v is None for v in allv):
        _hit("F1-NOT-SCORED")
        L.append("F1 NOT SCORED: a re-draw's hierarchical leg is VOID.")
    elif (not any(allv)) if not _m("f1_any") else (not all(allv)):
        _hit("F1-FIRES")
        L.append("F1 FIRES: neither exhibit is in R1's set on either re-draw: the certified exhibits carry \"not re-draw-stable "
                 "at R512\"; no CERT-RESOLUTION number is revised (the qualifier is added by bracket).")
    else:
        _hit("F1-NOT")
        L.append("F1 does not fire (an exhibit is in R1's set on at least one re-draw).")
    L.append("")
    L.append("NOT COMPUTED: fringe-site identity (Jaccard >= 0.5 on shared train texts) -- ruling O1; no readout above uses it.")
    return "\n".join(L) + "\n"


ALL_BRANCHES = {"identity-void", "identity-pass", "R1-VOID", "R1-computed", "R2-VOID", "R2-computed", "IC-VOID", "IC-match",
                "IC-mismatch", "R3-not-exhibit", "R3-VOID", "R3-0", "R3-1", "R3-2", "C1-VOID", "C1-HELD", "C1-FAILED",
                "C2-VOID", "C2-HELD", "C2-FAILED", "anchor-missing", "P1-UNSCORED", "P1-HELD", "P1-FAILED",
                "P2-UNSCORED", "P2-HELD", "P2-FAILED", "P3-UNSCORED", "P3-HELD", "P3-FAILED", "P4-UNSCORED", "P4-OPEN",
                "P4-A-HELD", "P4-A-FAILED", "P4-B-HELD", "P4-B-FAILED", "F1-NOT-SCORED", "F1-FIRES", "F1-NOT",
                "R2-UNREACHABLE"}


# ----------------------------------------------------------------------------------------------------------- modes
def dry_run(trees, data_roots, evidence_dir, out):
    out.write(POOL_LINE + "\n")
    out.write(self_identity() + "\n")
    out.write(base_identity_check() + "\n")
    out.write("DRY-RUN: pins, locations, m, snapshot ids, last records, k recovery, identity, multi-parent counts and the "
              "structural leg (g); NO p, CP, BH or FWER on a real row.\n")
    before = CR.STAT_CALLS[0]
    loaded = load_inputs(trees, data_roots, evidence_dir, out)
    if _m("dryrun_computes"):
        for _t, sites, _r, _f, _s in loaded:
            CR.p_site(sites[0]["k"])
    for t, sites, rec, fails, snap in loaded:
        anchors = anchors_of(sites)
        fam, anc, multi = structure(sites, rec, fails)
        out.write("  %-14s %s snapshot %s (registered); m = %d (registered %d); reps 300 / feasibility OK / k recovery PASS; "
                  "last record iteration %s, %d nodes; identity check: %s; multi-parent sites: %s; exhibits: %s\n"
                  % (t["name"], t["recipe"], snap, len(sites), t["m"], rec["iteration"], len(rec["nodes"]),
                     "PASS" if not fails else "FAIL (%d): %s" % (len(fails), "; ".join(fails[:5])),
                     "VOID" if multi is None else multi,
                     ", ".join("%s -> %s" % (lab, anchors.get(lab, "NOT A SITE")) for lab in EXHIBITS)))
        if anc is not None:
            out.write(reach_line(t["name"], sites, anc) + "\n")
    for line in support_lines():
        out.write(line + "\n")
    out.write("OPEN RULINGS (the --run refuses until recorded): %s\n"
              % ("; ".join("%s %s" % kv for kv in sorted(OPEN_RULINGS.items())) or "none"))
    if CR.STAT_CALLS[0] != before:
        raise Refusal("REFUSED: the dry-run evaluated %d statistics on real rows" % (CR.STAT_CALLS[0] - before))
    out.write("DRY-RUN done: 0 statistics evaluated on real rows; nothing written.\n")
    return loaded


def run(trees, data_roots, evidence_dir, out_dir, out, skip_selftest=False):
    if OPEN_RULINGS and not _m("open_rulings_ignored"):
        raise Refusal("REFUSED: open rulings %s must be recorded before the run" % sorted(OPEN_RULINGS))
    out_txt = os.path.join(out_dir, OUT_OUTCOME)
    out_csv = os.path.join(out_dir, OUT_SITES)
    for p in (out_txt, out_csv):
        if os.path.exists(p) and not _m("no_write_once"):
            raise Refusal("REFUSED: %s exists; outcome files of record are write-once" % p)
    if not skip_selftest and not run_selftest(io.StringIO()):
        raise Refusal("REFUSED: the in-process selftest is red")
    hdr = io.StringIO()
    hdr.write(POOL_LINE + "\n" + self_identity() + "\n" + base_identity_check() + "\n" + REG_LINE + "\n")
    hdr.write(CR.K_HEADER_LINE + "\n")
    hdr.write("INPUTS\n")
    loaded = load_inputs(trees, data_roots, evidence_dir, hdr)
    res = {t["name"]: analyze(t, sites, rec, fails) for t, sites, rec, fails, _s in loaded}
    ic, hier = instrument_check(res)
    if ic == "MISMATCH" and not _m("ic_soft"):                                  # ruling 13: REFUSE, before any output file
        msg = mismatch_line(hier)
        out.write(hdr.getvalue() + "REFUSAL LOG\n" + msg + "\n")
        raise Refusal("REFUSED: " + msg)
    if ic == "VOID" and not _m("ic_void_soft"):                                 # ruling N6-1: REFUSE, before any output file
        msg = void_line()
        out.write(hdr.getvalue() + "REFUSAL LOG\n" + msg + "\n")
        raise Refusal("REFUSED: " + msg)
    text = render(res, hdr.getvalue().rstrip("\n").split("\n"))
    os.makedirs(out_dir, exist_ok=True)
    mode = "w" if _m("no_write_once") else "x"
    with open(out_csv, mode, newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SITES_COLUMNS, lineterminator="\n")
        w.writeheader()
        for t in trees:
            r = res[t["name"]]
            fw = r["fwer"]
            ex = {v: lab for lab, v in r["anchors"].items() if lab in EXHIBITS}
            for row in r["rows"]:
                v = row["node_id"]
                row = dict(row)
                if fw.get("void"):
                    row.update(n_over_N="VOID", alpha_s="VOID", fwer_reachable_k0="VOID", fwer_tested="VOID",
                               fwer_rejected="VOID")
                else:
                    row.update(n_over_N="%.6f" % (r["n_of"][v] / fw["N"]), alpha_s="%.6f" % float(fw["alpha"][v]),
                               fwer_reachable_k0="true" if v in fw["reachable"] else "false",
                               fwer_tested="true" if v in fw["tested"] else "false",
                               fwer_rejected="true" if v in fw["rejected"] else "false")
                row["exhibit"] = ex.get(v, "")
                w.writerow(row)
    with open(out_txt, mode, newline="\n", encoding="utf-8") as fh:
        fh.write(text)
    out.write(text)
    return res


# ----------------------------------------------------------------------------------------------------------- selftest
def _node(N, i, d, leaf, parents, children):
    N.append(dict(id=i, depth=d, isLeaf=leaf, parentIds=parents, childIds=children, isBridge=False))


def _gap_tree():
    """R (not a site) -> A (site, k 0), B (site); B -> C (site, k 0), D (site, cert, high p), E00..E25 (sites);
    30 sites in all. Hier: top {A, B} m_f 2: A rejected at cutoff 0.025 (not MC-MARGINAL); B not; everything under B
    unreached. Flat: A and C at k 0, r* 2, cutoff 2 x 0.05 / 30 = 0.003333, 1/301 = 0.003322 below it by 0.0000111
    (< 1/301): MC-MARGINAL under the flat cutoff."""
    N = []
    es = ["E%02d" % i for i in range(26)]
    _node(N, "R", 0, False, [], ["A", "B"])
    _node(N, "A", 1, False, ["R"], ["a1", "a2"])
    _node(N, "B", 1, False, ["R"], ["C", "D"] + es)
    for i, par in (("C", "B"), ("D", "B")):
        _node(N, i, 2, False, [par], [i + "1", i + "2"])
    for e in es:
        _node(N, e, 2, False, ["B"], [e + "1", e + "2"])
    for par in ["A", "C", "D"] + es:
        for j in ("1", "2"):
            _node(N, par.lower() + j if par == "A" else par + j, 3 if par != "A" else 2, True, [par], [])
    sites = [dict(node_id="A", label="a", depth=1, n=100, k_children=2, k=0, reps=300, q_site="0.0000", cert=True),
             dict(node_id="B", label="b", depth=1, n=100, k_children=28, k=150, reps=300, q_site="0.5000", cert=False),
             dict(node_id="C", label="c", depth=2, n=50, k_children=2, k=0, reps=300, q_site="0.0000", cert=True),
             dict(node_id="D", label="d", depth=2, n=50, k_children=2, k=10, reps=300, q_site="0.0333", cert=True)]
    sites += [dict(node_id=e, label=e.lower(), depth=2, n=10, k_children=2, k=200, reps=300, q_site="0.6667", cert=False)
              for e in es]
    return sites, dict(iteration=1, nodes=N)


def gap_checks(module):
    """D1 (crB) and D2 (crK) of the CERT-RESOLUTION READY, on the base's analyze_tree as this instrument calls it."""
    sites, rec = _gap_tree()
    r = module.analyze_tree(dict(name="T", recipe="R512"), sites, rec, [])
    assert r["hier"] == {"A"}, r["hier"]
    assert r["flat"] == {"A", "C"}, r["flat"]
    e1 = module.WORDS_E1.format(tree="T", recipe="R512")
    assert r["words"]["A"] == e1, r["words"]["A"]                                    # hier cutoff 0.025: not MC (crB)
    assert r["words"]["C"] == module.WORDS_E2 + "; " + module.WORDS_MC, r["words"]["C"]
    assert r["e1"] == ["A"] and r["e2"] == ["C"] and r["e3"] == ["D"], (r["e1"], r["e2"], r["e3"])   # crK


UPSTREAM_MUTANTS = {
    # name: (anchor text in the base, replacement) -- the CERT-RESOLUTION READY's surviving reviewer mutants
    "crB_mc_uses_flat_cutoff_for_E1": ('thr = hier["cutoff_of"].get(v) if in_h else (flat_thr if in_f else None)',
                                       'thr = flat_thr if in_f else (hier["cutoff_of"].get(v) if in_h else None)'),
    "crK_E3_includes_flat": ('r["cert_site_p95"] == "true" and r["flat_bh"] != "true"', 'r["cert_site_p95"] == "true"'),
    "crL_P1_ge_not_eq": ('ok = all(len(res[n]["flat"]) == v for n, v in P1_REPRO.items())',
                         'ok = all(len(res[n]["flat"]) >= v for n, v in P1_REPRO.items())'),
}
UPSTREAM_REACHABLE = {"crB_mc_uses_flat_cutoff_for_E1", "crK_E3_includes_flat"}
UPSTREAM_NOTE = ("crL (render_outcome's P1) is not reachable from this instrument (render_outcome is never called); raG "
                 "(recipe_edge_audit.audit) is in a file this instrument does not import. Both stay open in the base "
                 "(queue CERT-RES-SELFTEST-GAPS).")


def upstream_mutant_results(tmp):
    """Build each mutant as a source copy of the base, import it, run gap_checks. Returns {name: 'KILLED'|'SURVIVED'}."""
    with open(CR.__file__, "rb") as fh:
        src = fh.read().decode("utf-8")
    out = {}
    for name, (a, b) in UPSTREAM_MUTANTS.items():
        assert src.count(a) == 1, (name, src.count(a))
        path = os.path.join(tmp, "cr_%s.py" % name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src.replace(a, b))
        spec = importlib.util.spec_from_file_location("cr_mut_%s" % name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            gap_checks(mod)
            out[name] = "SURVIVED"
        except AssertionError:
            out[name] = "KILLED"
    return out


def _fixture_specs(tmp, rows_by_tree, nodes_by_tree):
    specs = []
    for base in TREES:
        nm = base["name"]
        cs, jl = CR._fixture_tree(tmp, nm, nodes_by_tree[nm], rows_by_tree[nm])
        s = CR._spec_for(nm, "R512", cs, jl, len(rows_by_tree[nm]))
        s.update(snapshot="SNAP", last_iter=1, last_nodes=len(nodes_by_tree[nm]))
        specs.append(s)
    return specs


def _anchor_nodes(eng_id, chem_id="C6"):
    """root -> Chemistry (<chem_id>), Engineering (<eng_id>), Law (L1): all sites, each with two leaves."""
    N = []
    _node(N, "root", 0, False, [], [chem_id, eng_id, "L1"])
    for i in (chem_id, eng_id, "L1"):
        _node(N, i, 1, False, ["root"], [i + "x", i + "y"])
        for j in "xy":
            _node(N, i + j, 2, True, [i], [])
    return N


def selftest(out):
    checks = []

    def check(fn):
        checks.append(fn)
        return fn

    @check
    def st0_base_pin_and_isolation():
        base_identity_check()
        assert CR.MUTANT is None and [t["name"] for t in CR.TREES] == ["bareq512_s42", "af_clean_s42", "o0_clean_s42",
                                                                        "frozen"]
        assert S42["csv"]["lf"] == CR.TREES[0]["csv"]["lf"] and S42["jsonl"]["lf"] == CR.TREES[0]["jsonl"]["lf"]
        # a wrong base refuses
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        fake = os.path.join(tmp, "cert_resolution.py")
        with open(fake, "w", encoding="utf-8") as fh:
            fh.write("# not the base\n")

        class M:
            __file__ = fake
        try:
            base_identity_check(M)
            raise AssertionError("a wrong base was accepted")
        except CR.Refusal:
            pass

    @check
    def st1_registered_constants():
        assert (S137["m"], S2048["m"], S42["m"]) == (67, 71, 70)
        assert S137["snapshot"].startswith("20260909_154122") and S2048["snapshot"].startswith("20260909_160314")
        assert abs(math.sqrt(0.05 * 0.95 / 300) - 0.01258) < 5e-6 and abs(2.80 * math.sqrt(0.05 * 0.95 / 300) - 0.0352) < 5e-5
        assert abs(float(FLOOR) - 0.00332) < 5e-6 and abs(float(FLOOR / Q) - 0.0664) < 5e-5
        assert max(m for m in range(1, 100) if FLOOR <= Q / m) == 15
        assert max(m for m in range(1, 100) if Fraction(2, 301) <= Q / m) == 7          # k = 0 needed when m >= 8
        assert R3_BOTH == "certified at per-family FDR q = 0.05 on bareq512_s42 and on both R512 re-draws"
        assert R3_ONE.format(name="X") == "certified at per-family FDR q = 0.05 on bareq512_s42 and on 1 of 2 R512 re-draws (X)"
        assert R3_NEITHER == "certified at per-family FDR q = 0.05 on bareq512_s42 not on either R512 re-draw"
        assert FWER_WORDS == "FWER 0.05 against the Gaussian site null, arbitrary dependence across sites"

    @check
    def st2_fwer_hand():
        F = Fraction
        N = CR._chain_tree()
        # drop the multi-parent site M: A, B top; A1, A2 under A; B1 under B; A1a under A1
        N = [n for n in N if n["id"] not in ("M", "y1", "y2")]
        rec = dict(iteration=1, nodes=[dict(n, isBridge=False) for n in N])
        sites = [dict(node_id=i, depth=d, n=n) for i, d, n in (("A", 1, 20), ("B", 1, 281), ("A1", 2, 20), ("A2", 2, 10),
                                                               ("B1", 2, 200), ("A1a", 3, 20))]
        fam, anc, multi = CR.site_structure(sites, rec)
        assert multi == 0
        # N = 20 + 281 = 301; alpha_A = 0.05 x 20/301 = 1/301 exactly (boundary: p = 1/301 rejects)
        p = dict(A=FLOOR, B=F(1), A1=FLOOR, A2=FLOOR, B1=FLOOR, A1a=F(2, 301))
        h = fwer_topdown(sites, fam, anc, p)
        assert h["N"] == 301
        assert h["alpha"]["A"] == FLOOR and h["alpha"]["B1"] == Q * F(200, 301)
        # A rejected (equality); A1 alpha 1/301 rejected; A2 alpha 0.5/301 < 1/301 not; B not; B1 untested
        # (B unrejected); A1a alpha 1/301 < 2/301 not
        assert h["rejected"] == {"A", "A1"}, h["rejected"]
        assert h["tested"] == {"A", "B", "A1", "A2", "A1a"}, h["tested"]
        assert h["reachable"] == {"A", "B", "A1", "B1", "A1a"}, h["reachable"]
        # B rejected -> B1 tested and rejected (alpha 10/301)
        h2 = fwer_topdown(sites, fam, anc, dict(p, B=FLOOR))
        assert h2["rejected"] == {"A", "A1", "B", "B1"}, h2["rejected"]
        # a deep site whose parent is unrejected is never tested even at p = 1/301
        h3 = fwer_topdown(sites, fam, anc, dict(p, A=F(1)))
        assert "A1" not in h3["tested"] and h3["rejected"] == set(), h3
        # READY 114f80f X1: a depth-3 site under a REJECTED grandparent and an UNREJECTED parent is never tested
        h4 = fwer_topdown(sites, fam, anc, dict(p, A1=F(1)))
        assert "A" in h4["rejected"] and "A1" in h4["tested"] and "A1" not in h4["rejected"] and "A1a" not in h4["tested"], h4
        # READY 114f80f X7 / M-1: the reach line's N is the TOP family's (300 here, not 350), and the M-1 line
        rl = reach_line("t", [dict(node_id="A", label="a", n=100), dict(node_id="B", label="b", n=200),
                              dict(node_id="A1", label="a1", n=50)], dict(A=set(), B=set(), A1={"A"}))
        assert "N = 300 (top family 2 sites); reachable at k = 0: 3 of 3" in rl, rl
        assert m1_line(dict(reachable={"A", "B"}), {"A", "B", "C"}).endswith(
            "reduces to weighted Bonferroni over the 3 top-family sites (no deeper site reachable)")
        assert "reaches 1 site(s) below the top family (A1)" in m1_line(dict(reachable={"A", "A1"}), {"A", "B"})

    @check
    def st3_selftest_gaps_D1_D2():
        gap_checks(CR)

    @check
    def st3b_upstream_mutants_killed():
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        r = upstream_mutant_results(tmp)
        UPSTREAM_LAST.clear()
        UPSTREAM_LAST.update(r)
        for name in UPSTREAM_REACHABLE:
            assert r[name] == "KILLED", (name, r[name])

    @check
    def st4_anchor_by_label_and_multi_void():
        # the re-draw's Engineering has a different id than s42's n00000015: matched by LABEL
        N = _anchor_nodes("E9")
        rec = dict(iteration=1, nodes=N)
        sites = [dict(node_id="C6", label="Chemistry", depth=1, n=100, k_children=2, k=20, reps=300, q_site="0.0667", cert=True),
                 dict(node_id="E9", label="Engineering", depth=1, n=100, k_children=2, k=0, reps=300, q_site="0.0000", cert=True),
                 dict(node_id="L1", label="Law", depth=1, n=100, k_children=2, k=100, reps=300, q_site="0.3333", cert=False)]
        r = analyze(dict(name="bareq512_s137", recipe="R512"), sites, rec, [])
        assert r["anchors"]["Engineering"] == "E9" and in_hier(r, "Engineering") is True and in_hier(r, "Chemistry") is False
        # hier top family of 3: E9 (1/301 <= 0.01667) only; C6 21/301 = 0.0698 > 0.0333 / 0.05.
        # R2: N = 300, alpha = 0.05/3 = 0.01667 each; E9 rejected; C6 not
        assert r["fwer"]["rejected"] == {"E9"} and in_fwer(r, "Engineering") is True
        # multi-parent -> R2 VOID
        N2 = [dict(n) for n in N] + [dict(id="MP", depth=2, isLeaf=False, parentIds=["C6", "E9"], childIds=["mpx", "mpy"],
                                          isBridge=False)]
        N2 += [dict(id="mp" + j, depth=3, isLeaf=True, parentIds=["MP"], childIds=[], isBridge=False) for j in "xy"]
        sites2 = sites + [dict(node_id="MP", label="mp", depth=2, n=10, k_children=2, k=0, reps=300, q_site="0.0000", cert=True)]
        r2 = analyze(dict(name="x", recipe="R512"), sites2, dict(iteration=1, nodes=N2), [])
        assert r2["fwer"].get("void") and "multi-parent" in r2["fwer"]["void"], r2["fwer"]
        # identity failure -> hier and R2 VOID, in_hier None
        r3 = analyze(dict(name="x", recipe="R512"), sites, rec, ["x missing"])
        assert r3["hier"] is None and r3["fwer"].get("void") and in_hier(r3, "Engineering") is None

    @check
    def st4b_k0_unreachable_through_analyze():
        # READY 114f80f H1 (X3): p = (k + 1) / 301 through analyze(). E9 (k = 0, n/N = 10/210 = 0.0476 < 0.0664) is TESTED and
        # NOT rejected (alpha 0.00238 < 1/301); its reachable twin C6 (k = 0, n/N 0.476) is rejected; L1 (k = 100) is not.
        N = _anchor_nodes("E9")
        sites = [dict(node_id="C6", label="Chemistry", depth=1, n=100, k_children=2, k=0, reps=300, q_site="0.0000", cert=True),
                 dict(node_id="E9", label="Engineering", depth=1, n=10, k_children=2, k=0, reps=300, q_site="0.0000", cert=True),
                 dict(node_id="L1", label="Law", depth=1, n=100, k_children=2, k=100, reps=300, q_site="0.3333", cert=False)]
        r = analyze(dict(name="bareq512_s42", recipe="R512"), sites, dict(iteration=1, nodes=N), [])
        fw = r["fwer"]
        assert fw["N"] == 210 and fw["tested"] == {"C6", "E9", "L1"} and fw["rejected"] == {"C6"}, fw
        assert fw["reachable"] == {"C6", "L1"} and fw["alpha"]["E9"] == Q * Fraction(10, 210)
        assert fwer_word(r, "Engineering") == "UNREACHABLE at 300 reps (n/N 0.0476 < 0.0664)" and fwer_word(r, "Chemistry") == FWER_ALSO
        assert (fwer_word(r, "Law") == FWER_NOT) if ("Law" in r["anchors"]) else True

    @check
    def st5_full_path():
        global TREES, OPEN_RULINGS
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        rows = [("C6", "Chemistry", 1, 100, 2, "0.0000", True), ("E9", "Engineering", 1, 100, 2, "0.0000", True),
                ("L1", "Law", 1, 100, 2, "0.5000", False)]
        rows42 = [("n00000006",) + rows[0][1:], ("n00000015",) + rows[1][1:], rows[2]]   # s42 carries the recorded ids: MATCH
        nodes = {t["name"]: (_anchor_nodes("n00000015", "n00000006") if t["name"] == RECORD else _anchor_nodes("E9")) for t in TREES}
        specs = _fixture_specs(tmp, {t["name"]: (rows42 if t["name"] == RECORD else rows) for t in TREES}, nodes)
        buf = io.StringIO()
        before = CR.STAT_CALLS[0]
        dry_run(specs, [tmp], None, buf)
        assert CR.STAT_CALLS[0] == before
        txt = buf.getvalue()
        assert txt.startswith(POOL_LINE) and "C1 " not in txt and "R2 (" not in txt and "Engineering -> E9" in txt
        assert "reachable at k = 0: 3 of 3" in txt and "OPEN RULINGS" in txt
        for bad in ([dict(s, csv=dict(s["csv"], lf="0" * 64)) for s in specs],
                    [dict(s, m=4) for s in specs],
                    [dict(s, snapshot="OTHER") for s in specs],
                    [dict(s, last_nodes=1) for s in specs]):
            try:
                dry_run(bad, [tmp], None, io.StringIO())
                raise AssertionError("a bad spec was accepted")
            except CR.Refusal:
                pass
        od = os.path.join(tmp, "out")
        saved_o0 = OPEN_RULINGS
        OPEN_RULINGS = {"O-test": "an open ruling (selftest)"}
        try:
            run(specs, [tmp], None, od, io.StringIO(), skip_selftest=True)
            raise AssertionError("run with open rulings accepted")
        except CR.Refusal as e:
            assert "open rulings" in str(e)
        finally:
            OPEN_RULINGS = saved_o0
        assert not os.path.exists(od)
        saved_t, saved_o = TREES, OPEN_RULINGS
        TREES, OPEN_RULINGS = specs, {}
        try:
            res = run(specs, [tmp], None, od, io.StringIO(), skip_selftest=True)
            with open(os.path.join(od, OUT_SITES), encoding="utf-8") as fh:
                rd = list(csv.DictReader(fh))
            assert list(rd[0].keys()) == SITES_COLUMNS and len(rd) == 9
            assert [r["exhibit"] for r in rd[:3]] == ["Chemistry", "Engineering", ""]
            # READY 114f80f D4 / D5 (X5, X11): the FWER columns row by row (N = 300, alpha = 0.05 / 3 each)
            assert [(r["node_id"], r["fwer_rejected"], r["fwer_tested"], r["alpha_s"], r["n_over_N"]) for r in rd[:6]] == [
                ("n00000006", "true", "true", "0.016667", "0.333333"), ("n00000015", "true", "true", "0.016667", "0.333333"),
                ("L1", "false", "true", "0.016667", "0.333333"),
                ("C6", "true", "true", "0.016667", "0.333333"), ("E9", "true", "true", "0.016667", "0.333333"),
                ("L1", "false", "true", "0.016667", "0.333333")], rd[:6]
            with open(os.path.join(od, OUT_OUTCOME), encoding="utf-8") as fh:
                otxt = fh.read()
            assert otxt.startswith(POOL_LINE) and CR.K_HEADER_LINE in otxt and REG_LINE in otxt
            assert "R2 at 300 reps reduces to weighted Bonferroni over the 3 top-family sites (no deeper site reachable)" in otxt
            assert "C1 HELD POST-HOC-SEEN" in otxt and "INSTRUMENT CHECK MISMATCH" not in otxt
            assert "INSTRUMENT CHECK: bareq512_s42's hierarchical BH set reproduces CERT-RESOLUTION's recorded" in otxt
            assert otxt.count("R2 structural leg (g): reachable at k = 0 (n_s / N >= 0.0664): C6 Chemistry (n/N 0.3333), "
                              "E9 Engineering (n/N 0.3333), L1 Law (n/N 0.3333)") == 2, otxt
            assert otxt.count("R2 structural leg (g): reachable at k = 0 (n_s / N >= 0.0664): L1 Law (n/N 0.3333), "
                              "n00000006 Chemistry (n/N 0.3333), n00000015 Engineering (n/N 0.3333)") == 1, otxt
            try:
                run(specs, [tmp], None, od, io.StringIO(), skip_selftest=True)
                raise AssertionError("second run overwrote an outcome of record")
            except CR.Refusal:
                pass
        finally:
            TREES, OPEN_RULINGS = saved_t, saved_o
        assert res["bareq512_s137"]["fwer"]["rejected"] == {"C6", "E9"}

    @check
    def st5b_mismatch_refuses():
        # ruling 13: s42's hierarchical set {C6, E9} != the recorded {n00000006, n00000015} -> run() REFUSES before any file
        global TREES, OPEN_RULINGS
        import re as _re
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        rows = [("C6", "Chemistry", 1, 100, 2, "0.0000", True), ("E9", "Engineering", 1, 100, 2, "0.0000", True),
                ("L1", "Law", 1, 100, 2, "0.5000", False)]
        specs = _fixture_specs(tmp, {t["name"]: rows for t in TREES}, {t["name"]: _anchor_nodes("E9") for t in TREES})
        od = os.path.join(tmp, "out")
        saved_t, saved_o = TREES, OPEN_RULINGS
        TREES, OPEN_RULINGS = specs, {}
        buf = io.StringIO()
        try:
            run(specs, [tmp], None, od, buf, skip_selftest=True)
            raise AssertionError("an instrument-check mismatch did not refuse (ruling 13)")
        except CR.Refusal as e:
            msg = str(e)
        finally:
            TREES, OPEN_RULINGS = saved_t, saved_o
        log = buf.getvalue()
        assert "INSTRUMENT CHECK MISMATCH (ruling 13): bareq512_s42's hierarchical BH set ['C6', 'E9'] differs" in msg, msg
        assert log.startswith(POOL_LINE) and "REFUSAL LOG\nINSTRUMENT CHECK MISMATCH (ruling 13)" in log, log
        assert not os.path.exists(od), "an output path was created"
        assert "suspect" not in log and "R3 QUALIFIERS" not in log and "CRITERIA" not in log and "PREDICTIONS" not in log \
            and "FALSIFIER" not in log, log
        assert not _re.search(r"\b(C1|C2|R3|P1|P2|P3|P4|F1) (HELD|FAILED|VOID|UNSCORED|FIRES|does|NOT SCORED)", log), log

    @check
    def st5c_void_refuses():
        # ruling N6-1: s42's hierarchical leg VOID (an identity-check failure: n00000006 at CSV depth 2, snapshot depth 1)
        # -> run() REFUSES before any file, exactly as a mismatch (ruling 13 extended); the re-draws are intact
        global TREES, OPEN_RULINGS
        import re as _re
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        rows = [("C6", "Chemistry", 1, 100, 2, "0.0000", True), ("E9", "Engineering", 1, 100, 2, "0.0000", True),
                ("L1", "Law", 1, 100, 2, "0.5000", False)]
        rows42 = [("n00000006", "Chemistry", 2, 100, 2, "0.0000", True), ("n00000015",) + rows[1][1:], rows[2]]
        nodes = {t["name"]: (_anchor_nodes("n00000015", "n00000006") if t["name"] == RECORD else _anchor_nodes("E9")) for t in TREES}
        specs = _fixture_specs(tmp, {t["name"]: (rows42 if t["name"] == RECORD else rows) for t in TREES}, nodes)
        od = os.path.join(tmp, "out")
        saved_t, saved_o = TREES, OPEN_RULINGS
        TREES, OPEN_RULINGS = specs, {}
        buf = io.StringIO()
        try:
            run(specs, [tmp], None, od, buf, skip_selftest=True)
            raise AssertionError("a VOID s42 hierarchical leg did not refuse (ruling N6-1)")
        except CR.Refusal as e:
            msg = str(e)
        finally:
            TREES, OPEN_RULINGS = saved_t, saved_o
        log = buf.getvalue()
        assert "INSTRUMENT CHECK VOID (ruling N6-1, ruling 13 extended): bareq512_s42's hierarchical leg is VOID" in msg, msg
        assert log.startswith(POOL_LINE) and "REFUSAL LOG\nINSTRUMENT CHECK VOID (ruling N6-1" in log, log
        fl = {t["name"]: f for t, _s, _r, f, _n in load_inputs(specs, [tmp], None, io.StringIO())}
        assert fl[RECORD] == ["n00000006 depth 1 != CSV 2"] and all(fl[n] == [] for n in REDRAWS), fl   # the VOID is s42's alone
        assert not os.path.exists(od), "an output path was created"
        assert "R3 QUALIFIERS" not in log and "CRITERIA" not in log and "PREDICTIONS" not in log and "FALSIFIER" not in log, log
        assert not _re.search(r"\b(C1|C2|R3|P1|P2|P3|P4|F1) (HELD|FAILED|VOID|UNSCORED|FIRES|does|NOT SCORED)", log), log

    @check
    def st6_branches():
        global P4_READING, TREES
        BRANCH_HITS.clear()
        CE = dict(Chemistry="n6", Engineering="n15")

        def tr(name, hier, fwer_rej=(), void=False, fwer_void=False, anchors=None, m=70):
            a = dict(CE) if anchors is None else anchors
            return dict(name=name, recipe="R512", m=m, flat=set(), flat_thr=None, by=set(),
                        hier=None if void else set(hier), top_size=None if void else 14, multi=0,
                        identity_fails=["x missing"] if void else [], labels={}, anchors=a,
                        n_of=collections.defaultdict(lambda: 100),
                        fwer=dict(void="identity check failed") if (void or fwer_void) else
                        dict(N=1000, tested=set(), reachable=set(a.values()) | set(fwer_rej), rejected=set(fwer_rej),
                             alpha={v: Q for v in fwer_rej}))
        S = RECORD
        a, b = REDRAWS
        rec_ok = tr(S, ["n00000006", "n00000015"], anchors=dict(RECORDED_S42_LABELS))
        scen = [
            # 0: all hold (Eng both; Chem s137 only; sizes 2 / 1; R2 s42 {Chem}) -> C1 HELD, C2 FAILED, P2 HELD, F1 not
            ({S: dict(rec_ok, fwer=dict(rec_ok["fwer"], rejected={"n00000006"}, alpha={"n00000006": Q})),
              a: tr(a, ["n6", "n15"], ["n15"]), b: tr(b, ["n15"])}, None),
            # 1: nothing on either re-draw -> C1 C2 FAILED, P3 FAILED (size 0), F1 FIRES; s42 mismatch; Eng not a site on b
            ({S: rec_ok, a: tr(a, []), b: tr(b, [], anchors=dict(Chemistry="n6"))}, "A"),
            # 2: VOID re-draw, R2 VOID on s42 (s42's hierarchical leg intact)
            ({S: dict(rec_ok, fwer=dict(void="identity check failed")), a: tr(a, [], void=True), b: tr(b, ["n15"])}, "B"),
            # 3: both exhibits both re-draws; P3 FAILED at 5; P2 FAILED (Chem on both); R2 s42 {n6, other}
            ({S: dict(rec_ok, fwer=dict(rec_ok["fwer"], rejected={"n00000006", "zz"}, alpha={"n00000006": Q, "zz": Q})),
              a: tr(a, ["n6", "n15", "x1", "x2", "x3"]), b: tr(b, ["n6", "n15"])}, "A"),
            # 4: reading B with R2 s42 {n6, zz} -> FAILED; reading B HELD in scen 5
            ({S: dict(rec_ok, fwer=dict(rec_ok["fwer"], rejected={"n00000006", "zz"}, alpha={"n00000006": Q, "zz": Q})),
              a: tr(a, ["n15"]), b: tr(b, ["n15"])}, "B"),
            ({S: dict(rec_ok, fwer=dict(rec_ok["fwer"], rejected={"n00000015"}, alpha={"n00000015": Q})),
              a: tr(a, ["n15"]), b: tr(b, ["n6"])}, "B"),
            # 6: reading A FAILED (R2 s42 rejects only another site); R2 s42 fwer void on a tree
            ({S: dict(rec_ok, fwer=dict(rec_ok["fwer"], rejected={"zz"}, alpha={"zz": Q})),
              a: tr(a, ["n15"], fwer_void=True), b: tr(b, [])}, "A"),
            # 7: [ruling N6-1: s42 VOID now REFUSES (asserted below)] s42 MATCHES by id but no depth-1 site is labelled
            #    Engineering -> the R3 words do not apply to Engineering (the R3-not-exhibit branch stays reachable)
            ({S: dict(rec_ok, anchors=dict(Chemistry="n00000006")), a: tr(a, ["n15"]), b: tr(b, ["n15"])}, None),
            # 8: ruling R1 / H2: Engineering outside R2's reachable set on s42 (n/N 0.0600) -> UNREACHABLE words; P4 (A) HELD on
            #    Chemistry with the disclosure line
            ({S: dict(rec_ok, n_of=collections.defaultdict(lambda: 100, {"n00000015": 60}),
                      fwer=dict(rec_ok["fwer"], rejected={"n00000006"}, alpha={"n00000006": Q}, reachable={"n00000006"})),
              a: tr(a, ["n15"]), b: tr(b, ["n15"])}, "A"),
        ]
        saved_t, saved_p = TREES, P4_READING
        texts = []
        try:
            TREES = [dict(name=n) for n in [S] + REDRAWS]
            for sc, reading in scen:
                P4_READING = reading
                texts.append(render(sc, [POOL_LINE]))
        finally:
            TREES = saved_t
            P4_READING = saved_p
        try:                                                      # ruling 13: render refuses on a mismatch, prints nothing
            TREES = [dict(name=n) for n in [S] + REDRAWS]
            render({S: tr(S, ["n6"]), a: tr(a, []), b: tr(b, [])}, [POOL_LINE])
            raise AssertionError("render printed readouts on an instrument-check mismatch")
        except CR.Refusal as e:
            assert "INSTRUMENT CHECK MISMATCH (ruling 13)" in str(e) and "['n6']" in str(e), str(e)
        finally:
            TREES = saved_t
        try:                                                      # ruling N6-1: render refuses on a VOID s42 leg, prints nothing
            TREES = [dict(name=n) for n in [S] + REDRAWS]
            render({S: tr(S, [], void=True), a: tr(a, ["n15"]), b: tr(b, ["n15"])}, [POOL_LINE])
            raise AssertionError("render printed readouts on a VOID s42 hierarchical leg (ruling N6-1)")
        except CR.Refusal as e:
            assert "INSTRUMENT CHECK VOID (ruling N6-1, ruling 13 extended)" in str(e) and "REFUSED" in str(e), str(e)
        finally:
            TREES = saved_t
        sup = dict(rec_ok, hier={"n00000006", "n00000015", "zz"})           # a SUPERSET of the recorded set is a mismatch too
        ic_sup = instrument_check({S: sup})
        try:
            TREES = [dict(name=n) for n in [S] + REDRAWS]
            render({S: sup, a: tr(a, ["n15"]), b: tr(b, ["n15"])}, [POOL_LINE])
            raise AssertionError("render accepted a superset of the recorded set")
        except CR.Refusal as e:
            assert ic_sup == ("MISMATCH", ["n00000006", "n00000015", "zz"]) and "'zz'" in str(e), (ic_sup, str(e))
        finally:
            TREES = saved_t
        assert instrument_check({S: rec_ok}) == ("MATCH", ["n00000006", "n00000015"]) and instrument_check({S: tr(S, [], void=True)}) == ("VOID", None)
        missing = ALL_BRANCHES - BRANCH_HITS
        assert not missing, "print branches never executed: %s" % sorted(missing)
        t0, t1, t2, t3, t4, t5, t6, t7, t8 = texts
        assert "Engineering: \"%s\". R2: bareq512_s42 UNREACHABLE at 300 reps (n/N 0.0600 < 0.0664); %s %s" % (R3_BOTH, a, FWER_NOT) in t8, t8
        assert "not FWER 0.05" not in t8.split("Engineering:")[1].split("\n")[0].split(";")[0]
        assert "P4 HELD (reading A, ruled)" in t8 and "DISCLOSED (R1): Engineering UNREACHABLE at 300 reps (n/N 0.0600 < 0.0664)" in t8
        assert "C1 HELD POST-HOC-SEEN" in t0 and "C2 FAILED POST-HOC-SEEN" in t0 and "P2 HELD" in t0 and "P3 HELD" in t0
        assert "F1 does not fire" in t0 and "P4 UNSCORED: its reading is OPEN" in t0
        assert "INSTRUMENT CHECK: bareq512_s42's hierarchical BH set reproduces" in t0
        assert '"%s"' % R3_BOTH in t0 and '"%s"' % R3_ONE.format(name=a) in t0
        assert "Engineering: \"%s\". R2: bareq512_s42 %s" % (R3_BOTH, FWER_NOT) in t0
        assert "Chemistry: \"%s\". R2: bareq512_s42 %s; %s %s" % (R3_ONE.format(name=a), FWER_ALSO, a, FWER_NOT) in t0
        assert "C1 FAILED" in t1 and "C2 FAILED" in t1 and "P3 FAILED" in t1 and "F1 FIRES" in t1 and "P1 FAILED" in t1
        assert "INSTRUMENT CHECK MISMATCH" not in t1 and "NOTE: %s has no depth-1 SITE labelled Engineering" % b in t1
        assert not any("suspect" in t for t in texts)
        assert "C1 VOID" in t2 and "P2 UNSCORED" in t2 and "F1 NOT SCORED" in t2 and "P4 UNSCORED: R2" in t2
        assert "P3 FAILED" in t3 and "P2 FAILED" in t3 and "P4 HELD (reading A" in t3 and '"%s"' % R3_BOTH in t3
        assert "P4 FAILED (reading B" in t4 and "P4 HELD (reading B" in t5 and "P4 FAILED (reading A" in t6
        assert "C1 HELD" in t4 and "C2 FAILED" in t4 and '"%s"' % R3_NEITHER in t4
        assert "R2 VOID" in t6 and "P1 FAILED" in t6 and "C1 FAILED" in t6
        assert "C1 VOID" in t2 and "C2 VOID" in t2 and "R3 VOID" in t2 and "P1 UNSCORED" in t2 and "P3 UNSCORED" in t2
        assert "Engineering: not in bareq512_s42's hierarchical BH set here; the R3 words do not apply" in t7, t7
        assert "INSTRUMENT CHECK: bareq512_s42's hierarchical BH set reproduces" in t7
        assert not any("hierarchical leg VOID; CERT-RESOLUTION" in t for t in texts)      # ruling N6-1: never printed as a readout
        for t in texts:
            assert t.startswith(POOL_LINE) and "NOT COMPUTED: fringe-site identity" in t

    results = []
    TMPS = []
    for fn in checks:
        try:
            fn()
            results.append((fn.__name__, None))
        except Exception as e:                                  # noqa: BLE001  (a check fails on ANY exception)
            results.append((fn.__name__, "%s: %s" % (type(e).__name__, e)))
    for t in TMPS:
        shutil.rmtree(t, ignore_errors=True)
    return results


UPSTREAM_LAST = {}
MUTANTS = ["no_base_pin", "no_pin_check", "no_m_check", "no_snapshot_check", "no_last_record_check", "fwer_N_all",
           "fwer_unweighted", "fwer_no_parent_gate", "fwer_lt", "anchor_by_id", "multi_not_void", "c_any", "p2_swap",
           "p3_range_wide", "f1_any", "dryrun_computes", "open_rulings_ignored", "no_write_once", "ic_soft", "ic_void_soft"]


def run_selftest(out):
    global MUTANT
    MUTANT = None
    base = selftest(out)
    nfail = sum(1 for _, e in base if e)
    for name, e in base:
        out.write("  %-40s %s\n" % (name, "PASS" if e is None else "FAIL " + e))
    out.write("SELFTEST: %d checks, %d failed\n" % (len(base), nfail))
    for name in UPSTREAM_MUTANTS:
        out.write("  upstream mutant %-32s %s%s\n" % (name, UPSTREAM_LAST.get(name, "NOT RUN"),
                                                     "" if name in UPSTREAM_REACHABLE else " (not reachable here)"))
    out.write("  upstream mutant %-32s NOT RUN (recipe_edge_audit.py is not imported)\n" % "raG_bar_ratio_swapped")
    out.write("  " + UPSTREAM_NOTE + "\n")
    killed, survived = [], []
    for mu in MUTANTS:
        MUTANT = mu
        try:
            r = selftest(io.StringIO())
        finally:
            MUTANT = None
        bad = [n for n, e in r if e]
        (killed if bad else survived).append((mu, bad))
    for mu, bad in killed:
        out.write("  mutant %-22s KILLED by %s\n" % (mu, ", ".join(bad)))
    for mu, _ in survived:
        out.write("  mutant %-22s SURVIVED\n" % mu)
    out.write("MUTANTS: %d run, %d killed, %d survived\n" % (len(MUTANTS), len(killed), len(survived)))
    up_ok = all(UPSTREAM_LAST.get(n) == "KILLED" for n in UPSTREAM_REACHABLE)
    return nfail == 0 and not survived and up_ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", action="append", default=None)
    ap.add_argument("--evidence-dir", default=CR.DEFAULT_EVIDENCE_DIR)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    print(POOL_LINE)
    root = os.path.normpath(os.path.join(HERE, "..", ".."))
    try:
        if a.selftest:
            print(self_identity())
            print(base_identity_check())
            ok = run_selftest(sys.stdout)
            sys.exit(0 if ok else 1)
        roots = a.data_root
        if not roots:
            roots = [root]
            mc = CR.main_checkout_of(root)
            if mc and os.path.normcase(os.path.normpath(mc)) != os.path.normcase(roots[0]):
                roots.append(mc)
        if a.dry_run:
            print("data roots: %s; evidence dir: %s" % (roots, a.evidence_dir))
            buf = io.StringIO()
            try:
                dry_run(TREES, roots, a.evidence_dir, buf)
            finally:
                sys.stdout.write(buf.getvalue().split("\n", 1)[-1])
        else:
            if OPEN_RULINGS:
                raise Refusal("REFUSED: open rulings %s must be recorded before the run" % sorted(OPEN_RULINGS))
            buf = io.StringIO()
            if not run_selftest(buf):
                sys.stdout.write(buf.getvalue())
                raise Refusal("REFUSED: selftest red (checks or mutants)")
            run(TREES, roots, a.evidence_dir, a.out_dir or os.path.join(root, OUT_REL), sys.stdout, skip_selftest=True)
    except CR.Refusal as e:
        print(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
