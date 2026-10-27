"""g12_reader.py: the G-3 / G12 READER of RP12 ARCH-V2-E-T-R2 (lane r2): the hierarchical-BH site certificate of B0's
MMLU_PRO_LB member, its support bar, and every bracket since. ZERO calls; no DB is opened; nothing is launched.

REGISTRATION OF RECORD (the registration governs; this docstring restates it and never replaces it):
  docs/judge_v2_program.md "## Registered 2026-09-29 (before any code or call) -- ARCH-V2-E-T: ..." (span L22028-L22060 as
  registered), criterion G12, verbatim: "G12 (certificate; = F-TAX N-1, set readout): N-1 FIRES iff the hierarchical-BH set at
  per-family q = 0.05 (300 reps) on B0's MMLU-Pro member contains NO depth-1 site; it does not fire iff any depth-1 site is in
  the set. The per-site p95 count is printed beside against Binomial(m, 0.05). UNDETERMINED-by-support if the top family has
  m > 15 (1/301 > 0.05/m) or the corpus is below the site-null floor."
  Brackets carried: B0-1 (the member is MMLU_PRO_LB under pv2_1575de61bb20e977); the 2026-09-30 G12 bracket (own review before
  the site null; m <= 15 printed against the 14 declared domains); B-A2 (2026-10-01): "G12 is read beside MMLU-GOLD-GEOMETRY's
  H ...; if N-1 fires while H <= its permutation p95, the text says 'the declared depth-1 boundary is not shown to be
  geometric', not 'the construction fails to certify'; the N-1 verdict is unchanged". MMLU-GOLD-GEOMETRY of record:
  H 0.2912 > random p95 0.0264 (outcome experiment_results/mmlu_gold_geometry/outcome.txt blob:ec65dd67, VALID 207d800e).
  "## Registered 2026-10-01 ... -- ARCH-V2-E-T-R2" (L22417-L22434): G10-G15 verbatim with their brackets, applied to the R2 set.
  Support (ARCH-V2-E-T SUPPORT (a)-(g)): G12 denominator = the member's sites, 300 reps each; DEFF 1 by construction; SE per
  site sqrt(0.05 x 0.95 / 300) = 0.01258; MDE80 0.0352 per site; SCOREABLE as a deterministic set readout; structural leg:
  reachable at 300 reps only if the top family has m <= 15.
  Prediction P3: "G12 hierarchical-BH set size = 1 [0, 3]; N-1 fires: 0.30 ...; UNDETERMINED-by-support: 0.15."
  F-TAX N-1 / F2 are scored in F-TAX by the registrar, never here.
  Review conditions: READY_rp12_et3 (92afcc3) D-12 ("refuse ... unless sorted({depth of TOP members}) == [1]") and G-3 ("before
  G12 is read: cert_resolution's identity check PASS with multi-parent sites 0, and its top-family m equal to G-1's M").
  G-1 of record (bf32edf8, experiment_results/archv2/rp12_r2/readouts/g12_dryrun.txt): sites 60, families 33, TOP m = 14,
  depths [1], snapshot 20261001_094311_Headless_Run_Auto_ge.

INSTRUMENT. cert_resolution.py (blob:dbe9425d, sha256-lf16:3e3fb1b91aa3d361; the registered reader) is IMPORTED, not copied:
  read_sites (reps 300, feasibility OK, k = round(q_site x reps) within 0.016, else REFUSED), read_last_record, identity_check,
  site_structure (family key = nearest site ancestor along parentIds[0], TOP if none), hierarchical_bh (prefix-closed) and
  p_site = (k + 1) / 301 in exact fractions. Its LF sha256 is asserted against the pin before import; a mismatch REFUSES.

BUILDER'S READINGS (each flagged to the registrar in the hand-back; none is reachable on the run of record unless stated):
  R-a "Binomial(m, 0.05)": m = the number of sites the per-site p95 count is taken over (all S sites of the CSV), as F-TAX N-1
      prints it for bareq512_s42 ("P(>= 5 of 70 | 5%) = 0.272", m = its 70 sites); printed P(X >= c).
  D-G12-1 (a REGISTRATION DEFECT, reported, NOT resolved): with TOP m > 15 the bar "UNDETERMINED-by-support" and an N-1
      clause both apply on the same data: FIRES when no depth-1 site is rejected, and "does not fire" when >= ceil(m / 15.05)
      TOP sites sit at k = 0 (the parenthetical 1/301 > 0.05/m holds for ONE k = 0 site only; BH rejects r sites at r/m x
      0.05). The reader prints "REGISTRATION CONFLICT" with both sentences and scores nothing. Unreachable on the run of
      record: G-3 refuses unless TOP m = G-1's 14.
  R-c "the site-null floor" has NO numeric definition in the record (grep of the programme, CONTEXT, plan rev2 L825). The
      reader checks the only floor it can: every site row carries feasibility OK and reps 300 (cert_resolution REFUSES
      otherwise); it prints that the numeric floor clause is NOT EVALUATED. A registrar bracket is owed.

LAUNCH SEQUENCE
  python tools/analysis/g12_reader.py --selftest            fixtures (tempfile) + the frozen-tree reproduction of
                                                            cert_resolution_sites.csv; every print branch executed
  python tools/analysis/g12_reader.py --mutants             every mutant below against the selftest; all must be killed
  python tools/analysis/g12_reader.py --dry-run --lane r2   pins, the G10 gate, B-A2's H line, the snapshot, the identity check,
                                                            multi-parent count, TOP m and depths (D-12, G-3); NO p, BH or
                                                            count of a real row; writes nothing
  python tools/analysis/g12_reader.py --run --lane r2       selftest + mutants in-process (refuses if red), then the dry-run
                                                            gates, then writes WRITE-ONCE (mode "x"):
                                                            experiment_results/archv2/rp12_r2/g12/G12_OUTCOME.txt
                                                            experiment_results/archv2/rp12_r2/g12/G12_sites.csv
  --lane r1 REFUSES (R1's G10 FAILED, F2: no other R1 readout is scored). --root DIR overrides the data root (selftest only).

POOL: none (no DB opened). The first printed line of every mode is "pool: none (no DB opened)".

SELFTEST (15 checks; each runs the real entry point run() / dry_run() / main() on a fixture whose answer is known by hand and
asserts the printed VALUE): not-fire (set {a0, a1, a0_c0}, P3 HELD 3, P(X >= 3 | 15) = 0.036), FIRES (empty set; B-A2 both
wordings incl. the boundary H == p95), P3 FAILED (5), m = 15 boundary reachable, q enters (k = 1 rejects nothing at 0.05),
m = 16 CONFLICT (D-G12-1), D-12 vacuous root and mixed depths [1, 2], empty CSV and off-integer k, G-3 identity and multi-parent,
pins / lane r1 / snapshot / G10 / gold-line gates, the default --run gate and main()'s refusals, the dry-run computing nothing,
and the REPRODUCTION of cert_resolution of record on the frozen tree (cert_resolution_sites.csv blob 6d83df50: all 66 sites'
p_site, family_key, reached, hier_bh, cert_site_p95; set {n00000006 Chemistry, n00000005 Biology}; TOP m 14, depths [1]; an
instrument reproduction, never an evidential comparator, rev2 B8).

MUTANT TABLE (2026-10-01, builder; --mutants runs the first 25 in-process; H1-H12 were temporary source edits, reverted)
  no_pin_check K | no_g10_gate K | no_snapshot_gate K | no_identity_gate K | no_multi_gate K | no_d0_gate K | no_d12_gate K |
  d12_weak (!= [1] -> 1 not in) K | no_g1_gate K | tail_strict (P(X > c)) K | tail_m_top (Binomial(m_top)) K | wrong_depth K |
  set_nonempty K | bar_ge (m = 15 read as over) K | fires_first K | q_010 K | flat_not_hier K | ba2_strict (H < p95) K |
  p3_lo1 ([1, 3]) K | p_k_over_300 (p = k/300, RP06 X3) K | lane_r1 K | no_write_once K | no_selftest_gate K |
  default_gate_true K | dryrun_computes K                                                              -> 25 / 25 killed
  H1 TOP = first member only K | H2 FIRES/NOT words swapped K | H3 B-A2 comparison reversed K | H4 gold gate accepts >= 1 line
  K (survived once; st05 duplicate / absent G-1 line added) | H5 reach sign flipped K | H6 binomial mean x10 K | H7 sites CSV
  hier_bh = reached K | H8 depth-1 from all sites, not the set K | H9 per-site count from the set K | H10 G10 substring match K |
  H11 snapshot gate vs G-1 only K | H12 P3 Brier with the wrong p K                                     -> 12 / 12 killed
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[G12-READ]"
POOL_LINE = "pool: none (no DB opened)"
REPS = 300
Q = Fraction(1, 20)
M_TOP_MAX = 15                     # registered: 1/301 <= 0.05/m iff m <= 15
DECLARED_DOMAINS = 14
CERT_RESOLUTION_LF = "3e3fb1b91aa3d361490d1321e2e609c47c7b292c076881f5e77643d363ad24af"   # blob dbe9425d

# lane r2 inputs: (rel path, sha256 of the LF rendering, blob)
LANE_R2 = dict(
    csv=("experiment_results/archv2/rp12_r2/g12/site_null_B0_mmlu_pro_lb.csv",
         "d8f2c379f28234967e33a4772259a62945a4617cf2cc094f081c2d8f5ab52892", "ec8619f86766b0ad867de17f280f6e74d4357d20"),
    jsonl=("experiment_results/archv2/rp12_r2/B0/mmlu_pro_lb/seed_42/dag_snapshots.jsonl",
           "9656f171bf6c028577b1e6e7006b6b7383ab4561a365fc92073017cf88c8973e", "11dc92d84bd33416cfd1b38780abb4beddfedbc4"),
    pointer=("experiment_configs/rp12_r2/objects_of_record.json",
             "6f6e40b25e265035aec34572da2b035f1007d3376adf005abed5d6693c7f44e5", "ec718d47e4baa4e777afc573fd6b8e4febf4c128"),
    g10=("experiment_results/archv2/rp12_r2/readouts/g10_r2.txt",
         "aa2317e4bcb716b6a10f30302f0327e29b68fc8c45644b0396c4dbfefd32918f", "fd6fe0ae244720fa9b93734b80b4e5a644c23528"),
    gold=("experiment_results/mmlu_gold_geometry/outcome.txt",
          "1e078ddc387f65a620bb35b672004a0ebf2834cdc2b2b259ec08aabbfa31a2d7", "ec65dd67010bc84985e12aecfb931083a5201382"),
)
LANE_R2_EXPECT = dict(pointer_entry="B0/mmlu_pro_lb", snapshot="20261001_094311_Headless_Run_Auto_ge", sites=60, families=33,
                      m_top=14)
OUT_DIR_R2 = "experiment_results/archv2/rp12_r2/g12"
OUT_OUTCOME = "G12_OUTCOME.txt"
OUT_SITES = "G12_sites.csv"
GOLD_H, GOLD_P95 = Fraction(2912, 10000), Fraction(264, 10000)      # of record (B-A2)
GOLD_LINE = re.compile(r"^G-1: HELD \(H (\d+\.\d+) > p95 (\d+\.\d+); the point decides\)$")
P3_POINT, P3_INTERVAL, P3_P_FIRES, P3_P_UNDET = 1, (0, 3), 0.30, 0.15

W_FIRES = "N-1 FIRES: the hierarchical-BH set at per-family q = 0.05 (300 reps) contains NO depth-1 site"
W_NOT = "N-1 does not fire: depth-1 site(s) in the hierarchical-BH set"
W_UNDET = "UNDETERMINED-by-support"
W_BA2_ALT = "the declared depth-1 boundary is not shown to be geometric"
W_BA2_NOTCERT = "the construction fails to certify"
SITE_COLUMNS = ["node_id", "label", "depth", "n", "k", "p_site", "family_key", "reached", "hier_bh", "cert_site_p95"]

MUTANT = None
STATS = [0]                        # this reader's statistics on rows (binomial tail, BH verdict); the dry-run leaves it at 0
BRANCH_HITS = set()


class Refusal(Exception):
    pass


def _m(name):
    return MUTANT == name


def _hit(tag):
    BRANCH_HITS.add(tag)


def pins_of_bytes(raw):
    lf = raw.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(), lf=hashlib.sha256(lf).hexdigest(),
                crlf=hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest(), raw_crlf=(raw != lf))


def _import_cert_resolution():
    path = os.path.join(HERE, "cert_resolution.py")
    with open(path, "rb") as fh:
        p = pins_of_bytes(fh.read())
    if p["lf"] != CERT_RESOLUTION_LF:
        raise Refusal("REFUSED: cert_resolution.py sha256-lf16 %s is not the registered reader's %s"
                      % (p["lf"][:16], CERT_RESOLUTION_LF[:16]))
    import cert_resolution as cr
    return cr


CR = _import_cert_resolution()


def _cr(fn, *a):
    """Call a cert_resolution function; its refusals become this reader's (clean rc 2, never a traceback)."""
    try:
        return fn(*a)
    except CR.Refusal as e:
        raise Refusal(str(e))


# ------------------------------------------------------------------------------------------------------------ pins, inputs
def read_pinned(root, spec, what):
    rel, lf, _blob = spec
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        raise Refusal("REFUSED: %s %s is absent" % (what, rel))
    with open(path, "rb") as fh:
        raw = fh.read()
    p = pins_of_bytes(raw)
    if p["lf"] != lf and not _m("no_pin_check"):
        raise Refusal("REFUSED: %s %s sha256-lf16 %s, pinned %s" % (what, rel, p["lf"][:16], lf[:16]))
    line = "%s %-8s %s  blob:%s / sha256-lf16:%s / sha256-crlf16:%s (working file %s)" % (
        TAG, what, rel, p["blob"][:8], p["lf"][:16], p["crlf"][:16], "CRLF" if p["raw_crlf"] else "LF")
    return raw, line


def g10_gate(raw):
    lines = [l.strip() for l in raw.decode("utf-8").replace("\r\n", "\n").split("\n")]
    if "G10: HELD" not in lines and not _m("no_g10_gate"):
        raise Refusal("REFUSED: the R2 G10 readout does not print 'G10: HELD'; a FAILED or absent G10 stops the lane")
    return "%s G10 R2: 'G10: HELD' printed in the pinned readout (the lane is not stopped)" % TAG


def gold_gate(raw):
    lines = [l.strip() for l in raw.decode("utf-8").replace("\r\n", "\n").split("\n")]
    hits = [GOLD_LINE.match(l) for l in lines]
    hits = [h for h in hits if h]
    if len(hits) != 1:
        raise Refusal("REFUSED: MMLU-GOLD-GEOMETRY's outcome carries %d 'G-1: HELD (H .. > p95 ..)' lines, want 1" % len(hits))
    h, p95 = Fraction(hits[0].group(1)), Fraction(hits[0].group(2))
    if (h, p95) != (GOLD_H, GOLD_P95):
        raise Refusal("REFUSED: MMLU-GOLD-GEOMETRY H %s / p95 %s, of record 0.2912 / 0.0264" % (hits[0].group(1), hits[0].group(2)))
    return h, p95


def pointer_snapshot(raw, entry):
    doc = json.loads(raw.decode("utf-8"))
    e = doc.get("entries", {}).get(entry)
    if e is None:
        raise Refusal("REFUSED: the R2 pointer has no entry %s" % entry)
    return e["snapshot_id"]


# ------------------------------------------------------------------------------------------------------------ structure
def structure(sites, rec, expect=None):
    """The gates that precede any statistic (zero p / BH): identity (G-3), multi-parent 0 (G-3), D-12, G-1 equality.
    Returns fam, anc, top list, top depths, multi, depth counts. REFUSES on any failed precondition."""
    fails = CR.identity_check(sites, rec)
    if fails and not _m("no_identity_gate"):
        raise Refusal("REFUSED: G-3: cert_resolution's identity check FAILED (%d): %s" % (len(fails), "; ".join(fails[:5])))
    fam, anc, multi = _cr(CR.site_structure, sites, rec)
    if multi != 0 and not _m("no_multi_gate"):
        raise Refusal("REFUSED: G-3: %d multi-parent site(s); G-3 requires 0" % multi)
    depth = {s["node_id"]: s["depth"] for s in sites}
    d0 = sorted(v for v, d in depth.items() if d == 0)
    top = sorted(v for v, k in fam.items() if k == "TOP")
    top_depths = sorted({depth[v] for v in top})
    if d0 and not _m("no_d0_gate"):
        raise Refusal("REFUSED: D-12: the root is a site (%s, depth 0): a vacuous root; the registered top family is the depth-1"
                      " family; a registrar bracket before any read" % ", ".join(d0))
    bad_depths = (1 not in top_depths) if _m("d12_weak") else (top_depths != [1])
    if bad_depths and not _m("no_d12_gate"):
        raise Refusal("REFUSED: D-12: the TOP family's depths are %s, not [1] (m = %d): the registered top family is not the"
                      " depth-1 family; a registrar bracket before any read" % (top_depths, len(top)))
    if expect is not None:
        nfam = len(set(fam.values()))
        got = (len(sites), nfam, len(top))
        want = (expect["sites"], expect["families"], expect["m_top"])
        if got != want and not _m("no_g1_gate"):
            raise Refusal("REFUSED: G-3: sites / families / TOP m = %s, G-1 of record printed %s" % (got, want))
    by_depth = {}
    for d in depth.values():
        by_depth[d] = by_depth.get(d, 0) + 1
    return dict(fam=fam, anc=anc, top=top, top_depths=top_depths, multi=multi, by_depth=by_depth,
                families=len(set(fam.values())), depth=depth)


def reach_lines(m_top, S):
    minp = Fraction(1, REPS + 1)
    need = math.ceil(Fraction(m_top) / (Fraction(REPS + 1) * Q))
    return ["%s SUPPORT (registered; ARCH-V2-E-T Support (a)-(g)): deciding denominator = the member's %d sites, %d reps each; "
            "DEFF 1 by construction (independent null draws, declared); n_eff %d draws per site; SE at the per-site bar 0.05 = "
            "sqrt(0.05 x 0.95 / 300) = %.5f; MDE80 = 2.80 x SE = %.4f per site; no matches, no questions: tie conventions and a "
            "question-clustered bootstrap are N/A to this set readout" % (TAG, S, REPS, REPS, math.sqrt(0.0475 / REPS),
                                                                          2.80 * math.sqrt(0.0475 / REPS)),
            "%s SUPPORT bar (measured): TOP family m = %d (declared MMLU-Pro domains %d); min p = 1/301 = %.6f %s 0.05/m = %.6f; "
            "a TOP rejection needs >= %d TOP site(s) at k = 0" % (TAG, m_top, DECLARED_DOMAINS, float(minp),
                                                                 "<=" if minp <= Q / m_top else ">", float(Q / m_top), need)]


# ------------------------------------------------------------------------------------------------------------ statistics
def binom_tail(c, m, p=0.05):
    """P(X >= c) for X ~ Binomial(m, p)."""
    STATS[0] += 1
    lo = c + 1 if _m("tail_strict") else c
    return sum(math.comb(m, i) * p ** i * (1 - p) ** (m - i) for i in range(lo, m + 1))


def n1_verdict(hier_set, depth, m_top):
    """The registered G12 verdict. Returns (word, depth-1 sites in the set). m_top > 15 returns CONFLICT (D-G12-1): the
    registered support bar and an N-1 clause both apply on the same data; the reader does not choose."""
    STATS[0] += 1
    d1 = sorted(v for v in hier_set if depth[v] == (2 if _m("wrong_depth") else 1))
    if _m("set_nonempty"):
        d1 = sorted(hier_set)
    bar = (m_top >= M_TOP_MAX) if _m("bar_ge") else (m_top > M_TOP_MAX)
    if _m("fires_first") and not d1:
        return "FIRES", d1
    if bar:
        return "CONFLICT", d1
    if d1:
        return "NOT", d1
    return "FIRES", d1


def analyze(sites, rec, st):
    pmap = {s["node_id"]: (Fraction(s["k"], s["reps"]) if _m("p_k_over_300") else CR.p_site(s["k"], s["reps"])) for s in sites}
    q = Fraction(1, 10) if _m("q_010") else Q
    hier = _cr(CR.hierarchical_bh, sites, st["fam"], st["anc"], pmap, q)
    hset = hier["rejected"]
    if _m("flat_not_hier"):
        ids = [s["node_id"] for s in sites]
        hset = {ids[i] for i in CR.bh_cutoff([pmap[v] for v in ids], Q)[0]}
    word, d1 = n1_verdict(hset, st["depth"], len(st["top"]))
    S = len(sites)
    c = sum(1 for s in sites if s["cert"])
    tail_m = len(st["top"]) if _m("tail_m_top") else S
    tail = binom_tail(c, tail_m)
    return dict(pmap=pmap, hier=hier, hset=hset, word=word, d1=d1, S=S, c=c, tail=tail, tail_m=tail_m)


# ------------------------------------------------------------------------------------------------------------ printouts
def verdict_lines(res, st, sites, h, p95):
    lab = {s["node_id"]: s["label"] for s in sites}
    L = []
    hs = sorted(res["hset"])
    L.append("%s hierarchical-BH set (per-family q = 0.05, 300 reps; cert_resolution's instrument; tree-wide FDR NOT claimed): "
             "%d of %d sites: %s" % (TAG, len(hs), res["S"], ", ".join("%s %s (d%d)" % (v, lab[v], st["depth"][v]) for v in hs)
                                     or "(empty)"))
    fr = [f for f in res["hier"]["families"] if f["run"]]
    L.append("%s families run %d of %d; sizes m_f = %s" % (TAG, len(fr), st["families"], [f["m_f"] for f in fr]))
    w = res["word"]
    if w == "CONFLICT":
        _hit("V-CONFLICT")
        L.append("G12: REGISTRATION CONFLICT (D-G12-1; not resolved by the reader, a registrar bracket is owed): the registered "
                 "bar reads %s (the TOP family has m = %d > 15, 1/301 > 0.05/m) AND N-1's clause reads \"%s\" on the same "
                 "data (depth-1 sites in the set: %d)" % (W_UNDET, len(st["top"]), "does not fire" if res["d1"] else "FIRES",
                                                          len(res["d1"])))
    elif w == "FIRES":
        _hit("V-FIRES")
        L.append("G12: " + W_FIRES + " (0 depth-1 sites of %d in the set)" % st["by_depth"].get(1, 0))
    else:
        _hit("V-NOT")
        L.append("G12: " + W_NOT + " (%d): %s" % (len(res["d1"]), ", ".join("%s %s" % (v, lab[v]) for v in res["d1"])))
    L.append("%s site-null floor: the numeric floor clause is NOT EVALUATED (no registered definition; reading R-c); checked: "
             "%d of %d site rows feasibility OK at 300 reps" % (TAG, res["S"], res["S"]))
    L.append("%s per-site p95 count (printed beside, never deciding): %d of %d sites; Binomial(%d, 0.05): mean %.2f, "
             "P(X >= %d) = %.3f" % (TAG, res["c"], res["S"], res["tail_m"], 0.05 * res["tail_m"], res["c"], res["tail"]))
    alt = (h < p95) if _m("ba2_strict") else (h <= p95)
    if w == "FIRES" and alt:
        _hit("BA2-ALT")
        L.append("B-A2: N-1 fires while H %.4f <= its permutation p95 %.4f: the text says \"%s\", not \"%s\"; the N-1 verdict is "
                 "unchanged" % (float(h), float(p95), W_BA2_ALT, W_BA2_NOTCERT))
    elif w == "FIRES":
        _hit("BA2-GEOM")
        L.append("B-A2: N-1 fires while H %.4f > its permutation p95 %.4f (MMLU-GOLD-GEOMETRY, of record): the B-A2 alternative "
                 "wording does not apply; the N-1 verdict is unchanged" % (float(h), float(p95)))
    else:
        _hit("BA2-NOFIRE")
        L.append("B-A2: read beside MMLU-GOLD-GEOMETRY's H %.4f (permutation p95 %.4f); N-1 did not fire, no wording changes"
                 % (float(h), float(p95)))
    n = len(hs)
    ok = P3_INTERVAL[0] <= n <= P3_INTERVAL[1]
    if _m("p3_lo1"):
        ok = 1 <= n <= P3_INTERVAL[1]
    _hit("P3-HELD" if ok else "P3-FAILED")
    L.append("P3 set size %s: %d (point %d, 80%% interval [%d, %d])" % ("HELD" if ok else "FAILED", n, P3_POINT, *P3_INTERVAL))
    if w == "CONFLICT":
        L.append("P3 N-1 fires (registered p %.2f): NOT SCORED (D-G12-1)" % P3_P_FIRES)
        L.append("P3 UNDETERMINED-by-support (registered p %.2f): NOT SCORED (D-G12-1)" % P3_P_UNDET)
    else:
        ef = 1 if w == "FIRES" else 0
        L.append("P3 N-1 fires (registered p %.2f): event %s, Brier %.4f" % (P3_P_FIRES, "FIRES" if ef else "not fired",
                                                                             (P3_P_FIRES - ef) ** 2))
        L.append("P3 UNDETERMINED-by-support (registered p %.2f): event no (TOP m = %d <= 15), Brier %.4f"
                 % (P3_P_UNDET, len(st["top"]), P3_P_UNDET ** 2))
    L.append("CONSEQUENCE: F-TAX N-1 = %s (F-TAX F2 fires iff N-1 fires); both are scored in F-TAX by the registrar, not here"
             % {"FIRES": "FIRES", "NOT": "does not fire", "CONFLICT": "NOT SCORED (D-G12-1 registration conflict)"}[w])
    return L


def site_rows(sites, st, res):
    out = []
    for s in sites:
        v = s["node_id"]
        out.append(dict(node_id=v, label=s["label"], depth=s["depth"], n=s["n"], k=s["k"], p_site="%.6f" % float(res["pmap"][v]),
                        family_key=st["fam"][v], reached="true" if v in res["hier"]["reached"] else "false",
                        hier_bh="true" if v in res["hset"] else "false", cert_site_p95="true" if s["cert"] else "false"))
    return out


# ------------------------------------------------------------------------------------------------------------ modes
def self_identity():
    with open(os.path.abspath(__file__), "rb") as fh:
        p = pins_of_bytes(fh.read())
    return "%s script tools/analysis/g12_reader.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s; reader cert_resolution.py " \
           "sha256-lf16:%s (blob dbe9425d)" % (TAG, p["blob"][:8], p["lf"][:16], p["crlf"][:16], CERT_RESOLUTION_LF[:16])


def lane_check(lane, root, spec):
    if lane != "r2" and not _m("lane_r1"):
        raise Refusal("REFUSED: lane %s: R1's G10 FAILED (F2), no other R1 readout is scored; G12 is read on lane r2 only" % lane)
    import rp12_lane as LN
    try:
        LN.guard("r2", [(k, v[0]) for k, v in spec.items() if k != "gold"] + [("outDir", OUT_DIR_R2)], root=root)
    except SystemExit as e:
        raise Refusal("REFUSED: %s" % e)


def load(root, spec, expect, out):
    """Every gate before a statistic. Returns (sites, rec, st, h, p95, header lines)."""
    hdr = []
    raws = {}
    for k in ("csv", "jsonl", "pointer", "g10", "gold"):
        raws[k], line = read_pinned(root, spec[k], k)
        hdr.append(line)
    hdr.append(g10_gate(raws["g10"]))
    h, p95 = gold_gate(raws["gold"])
    hdr.append("%s B-A2 MMLU-GOLD-GEOMETRY G-1 of record: H %.4f > p95 %.4f (read from the pinned outcome)" % (TAG, h, p95))
    sites, snap = _cr(CR.read_sites, raws["csv"], "B0/mmlu_pro_lb")
    want = pointer_snapshot(raws["pointer"], expect["pointer_entry"])
    if (snap != want or snap != expect["snapshot"]) and not _m("no_snapshot_gate"):
        raise Refusal("REFUSED: the CSV's snapshot %s is not the pointer's %s / G-1's %s" % (snap, want, expect["snapshot"]))
    hdr.append("%s snapshot %s = the R2 pointer entry %s = G-1's" % (TAG, snap, expect["pointer_entry"]))
    rec = _cr(CR.read_last_record, raws["jsonl"])
    st = structure(sites, rec, expect)
    hdr.append("%s G-3: cert_resolution's identity check PASS (%d sites; multi-parent sites %d); sites %d (by depth: %s); "
               "families %d; TOP family m = %d, depths %s = G-1's (D-12: depths exactly [1], no depth-0 site)"
               % (TAG, len(sites), st["multi"], len(sites), ", ".join("d%d %d" % kv for kv in sorted(st["by_depth"].items())),
                  st["families"], len(st["top"]), st["top_depths"]))
    hdr += reach_lines(len(st["top"]), len(sites))
    for l in hdr:
        out.write(l + "\n")
    return sites, rec, st, h, p95


def dry_run(root, spec, expect, out, lane="r2"):
    out.write(POOL_LINE + "\n" + self_identity() + "\n")
    out.write("%s DRY-RUN (lane %s): pins, gates, structure; NO p, BH or count of a real row; nothing written\n" % (TAG, lane))
    lane_check(lane, root, spec)
    b_cr, b_me = CR.STAT_CALLS[0], STATS[0]
    sites, rec, st, h, p95 = load(root, spec, expect, out)
    if _m("dryrun_computes"):
        analyze(sites, rec, st)
    if (CR.STAT_CALLS[0], STATS[0]) != (b_cr, b_me):
        raise Refusal("REFUSED: the dry-run evaluated %d statistic(s) on real rows"
                      % (CR.STAT_CALLS[0] - b_cr + STATS[0] - b_me))
    out.write("%s DRY-RUN done: 0 statistics evaluated on real rows; nothing written\n" % TAG)
    return st


def _default_gate():
    """--run's in-process gate: the selftest AND the mutant table, both green."""
    return run_selftest(io.StringIO()) and run_mutants(io.StringIO())


def run(root, spec, expect, out_dir, out, lane="r2", gate=None):
    lane_check(lane, root, spec)
    po, ps = os.path.join(out_dir, OUT_OUTCOME), os.path.join(out_dir, OUT_SITES)
    for p in (po, ps):
        if os.path.exists(p) and not _m("no_write_once"):
            raise Refusal("REFUSED: %s exists; outcome files of record are write-once" % p)
    if gate is None:
        gate = (lambda: True) if _m("default_gate_true") else globals()["_default_gate"]
    if not gate() and not _m("no_selftest_gate"):
        raise Refusal("REFUSED: the in-process selftest or mutant table is red")
    hdr = io.StringIO()
    hdr.write(POOL_LINE + "\n" + self_identity() + "\n")
    hdr.write("ARCH-V2-E-T-R2 G12 outcome (lane %s; registration ARCH-V2-E-T G12 with B0-1, B-A2; READY_rp12_et3 D-12, G-3). "
              "Zero calls.\n" % lane)
    hdr.write("k = the null exceedance count round(q_site x reps); p_site = (k + 1) / 301\n")
    sites, rec, st, h, p95 = load(root, spec, expect, hdr)
    res = analyze(sites, rec, st)
    text = hdr.getvalue() + "\n".join(verdict_lines(res, st, sites, h, p95)) + "\n"
    os.makedirs(out_dir, exist_ok=True)
    mode = "w" if _m("no_write_once") else "x"
    with open(ps, mode, newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SITE_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in site_rows(sites, st, res):
            w.writerow(r)
    with open(po, mode, newline="\n", encoding="utf-8") as fh:
        fh.write(text)
    out.write(text)
    return res, text


# ------------------------------------------------------------------------------------------------------------ selftest
def _tree(n_anchors=14, root_site=False, mixed=False, multi=False):
    """root R (depth 0) -> a0..a{n-1} (depth 1, sites) -> two children each; a0_c0 is a depth-2 site (family a0)."""
    N = [dict(id="R", depth=0, isLeaf=False, parentIds=[], childIds=["a%d" % i for i in range(n_anchors)])]
    for i in range(n_anchors):
        N.append(dict(id="a%d" % i, depth=1, isLeaf=False, parentIds=["R"], childIds=["a%d_c0" % i, "a%d_c1" % i]))
        if i == 0:
            N.append(dict(id="a0_c0", depth=2, isLeaf=False, parentIds=["a0"], childIds=["a0_g0", "a0_g1"]))
            N += [dict(id="a0_g%d" % j, depth=3, isLeaf=True, parentIds=["a0_c0"], childIds=[]) for j in range(2)]
        elif i == 1 and multi:
            N.append(dict(id="a1_c0", depth=2, isLeaf=False, parentIds=["a1", "a2"], childIds=["a1_g0", "a1_g1"]))
            N += [dict(id="a1_g%d" % j, depth=3, isLeaf=True, parentIds=["a1_c0"], childIds=[]) for j in range(2)]
        else:
            N.append(dict(id="a%d_c0" % i, depth=2, isLeaf=True, parentIds=["a%d" % i], childIds=[]))
        N.append(dict(id="a%d_c1" % i, depth=2, isLeaf=True, parentIds=["a%d" % i], childIds=[]))
    if multi:
        for n in N:
            if n["id"] == "a2":
                n["childIds"] = n["childIds"] + ["a1_c0"]
    rows = []
    if root_site:
        rows.append(("R", "root", 0, 1000, n_anchors))
    for i in range(n_anchors):
        if not (mixed and i == 0):
            rows.append(("a%d" % i, "anchor%d" % i, 1, 100, 2 + (1 if multi and i == 2 else 0)))
    rows.append(("a0_c0", "sub0", 2, 50, 2))
    if multi:
        rows.append(("a1_c0", "sub1", 2, 50, 2))
    return N, rows


def _fixture(tmp, name, N, rows, k, cert=()):
    """Write a site-null CSV (cert_resolution's fixture writer) + jsonl; k: node -> exceedance count (default 100)."""
    csv_rows = [(i, lab, d, n, kc, "%.4f" % (k.get(i, 100) / 300.0), i in cert) for (i, lab, d, n, kc) in rows]
    return CR._fixture_tree(tmp, name, N, csv_rows)


def _lane_root(tmp, N, rows, k, cert=(), g10="G10: HELD", gold="G-1: HELD (H 0.2912 > p95 0.0264; the point decides)",
               snap="SNAP"):
    """A fake data root with the lane r2 files at their registered paths; returns (root, spec with fixture pins)."""
    root = os.path.join(tmp, "root")
    cs, jl = _fixture(tmp, "m", N, rows, k, cert)
    spec = {}
    files = dict(csv=open(cs, "rb").read(), jsonl=open(jl, "rb").read(),
                 pointer=json.dumps({"entries": {"B0/mmlu_pro_lb": {"snapshot_id": snap}}}).encode(),
                 g10=("[G10] stamp ...\n%s\nrc=0\n" % g10).encode(), gold=("READOUT ...\n%s\n" % gold).encode())
    for key, data in files.items():
        rel = LANE_R2[key][0]
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(data)
        spec[key] = (rel, pins_of_bytes(data)["lf"], None)
    return root, spec


def _expect(sites=15, families=2, m_top=14):
    return dict(pointer_entry="B0/mmlu_pro_lb", snapshot="SNAP", sites=sites, families=families, m_top=m_top)


def _refused(fn, needle):
    try:
        fn()
    except Refusal as e:
        assert needle in str(e), (needle, str(e))
        return str(e)
    raise AssertionError("not refused: %s" % needle)


def _run_fixture(tmp, N, rows, k, cert=(), expect=None, **kw):
    root, spec = _lane_root(tmp, N, rows, k, cert, **kw)
    od = os.path.join(root, OUT_DIR_R2)
    res, text = run(root, spec, expect or _expect(), od, io.StringIO(), gate=lambda: True)
    return res, text, root, spec, od


def selftest(out):
    checks = []

    def check(fn):
        checks.append(fn)
        return fn

    @check
    def st01_pins_registered():
        for key, (rel, lf, blob) in LANE_R2.items():
            assert len(lf) == 64 and len(blob) == 40, key
        assert LANE_R2["csv"][0] == "experiment_results/archv2/rp12_r2/g12/site_null_B0_mmlu_pro_lb.csv"
        assert LANE_R2["csv"][1][:16] == "d8f2c379f2823496" and LANE_R2["csv"][2][:8] == "ec8619f8"
        assert (LANE_R2_EXPECT["sites"], LANE_R2_EXPECT["families"], LANE_R2_EXPECT["m_top"]) == (60, 33, 14)
        assert (GOLD_H, GOLD_P95) == (Fraction("0.2912"), Fraction("0.0264"))

    @check
    def st02_binomial_tail():
        b = STATS[0]
        assert round(binom_tail(5, 70), 3) == 0.272, binom_tail(5, 70)          # F-TAX N-1's registered printout
        assert abs(binom_tail(0, 60) - 1.0) < 1e-12
        assert abs(binom_tail(1, 60) - (1 - 0.95 ** 60)) < 1e-12
        assert STATS[0] == b + 3

    @check
    def st03_verdict_core():
        dep = {"a": 1, "b": 1, "s": 2}
        assert n1_verdict(set(), dep, 14) == ("FIRES", [])
        assert n1_verdict({"a"}, dep, 14) == ("NOT", ["a"])
        assert n1_verdict({"s"}, dep, 14) == ("FIRES", [])                  # a depth-2-only set: no depth-1 site
        assert n1_verdict(set(), dep, 15) == ("FIRES", [])                  # boundary: m = 15 is reachable
        assert n1_verdict({"a"}, dep, 15) == ("NOT", ["a"])
        assert n1_verdict(set(), dep, 16) == ("CONFLICT", [])               # D-G12-1: bar AND FIRES both apply
        assert n1_verdict({"a"}, dep, 16) == ("CONFLICT", ["a"])            # D-G12-1: bar AND "does not fire" both apply

    @check
    def st04_not_fire_end_to_end():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        res, text, root, spec, od = _run_fixture(tmp, N, rows, dict(a0=0, a1=0, a0_c0=0), cert=("a0", "a1", "a0_c0"))
        assert res["hset"] == {"a0", "a1", "a0_c0"}, res["hset"]
        assert res["word"] == "NOT" and res["d1"] == ["a0", "a1"]
        assert "G12: N-1 does not fire: depth-1 site(s) in the hierarchical-BH set (2): a0 anchor0, a1 anchor1" in text, text
        assert "P3 set size HELD: 3 (point 1, 80% interval [0, 3])" in text
        assert "B-A2: read beside MMLU-GOLD-GEOMETRY's H 0.2912 (permutation p95 0.0264); N-1 did not fire" in text
        assert "per-site p95 count (printed beside, never deciding): 3 of 15 sites; Binomial(15, 0.05): mean 0.75, P(X >= 3) = 0.036" \
            in text, text
        assert "CONSEQUENCE: F-TAX N-1 = does not fire" in text
        assert "P3 N-1 fires (registered p 0.30): event not fired, Brier 0.0900" in text
        assert "P3 UNDETERMINED-by-support (registered p 0.15): event no (TOP m = 14 <= 15), Brier 0.0225" in text
        assert "site-null floor: the numeric floor clause is NOT EVALUATED (no registered definition; reading R-c); checked: "             "15 of 15 site rows feasibility OK at 300 reps" in text, text
        assert "families run 2 of 2; sizes m_f = [14, 1]" in text, text
        assert "TOP family m = 14 (declared MMLU-Pro domains 14); min p = 1/301 = 0.003322 <= 0.05/m = 0.003571; a TOP rejection" \
            " needs >= 1 TOP site(s) at k = 0" in text, text
        assert "G-3: cert_resolution's identity check PASS (15 sites; multi-parent sites 0); sites 15 (by depth: d1 14, d2 1); " \
            "families 2; TOP family m = 14, depths [1]" in text, text
        assert text.startswith(POOL_LINE)
        with open(os.path.join(od, OUT_SITES), encoding="utf-8") as fh:
            rd = list(csv.DictReader(fh))
        assert [r["node_id"] for r in rd if r["hier_bh"] == "true"] == ["a0", "a1", "a0_c0"]
        assert {r["node_id"]: r["family_key"] for r in rd}["a0_c0"] == "a0"
        # write-once: a second run refuses and the files are unchanged
        before = open(os.path.join(od, OUT_OUTCOME), "rb").read()
        _refused(lambda: run(root, spec, _expect(), od, io.StringIO(), gate=lambda: True), "write-once")
        assert open(os.path.join(od, OUT_OUTCOME), "rb").read() == before

    @check
    def st05_fires_end_to_end_and_ba2():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        # a0 at k = 5: p 6/301 = .0199 > 0.05/14; nothing in TOP rejects; a0_c0 at k = 0 is never reached
        res, text, *_ = _run_fixture(tmp, N, rows, dict(a0=5, a0_c0=0))
        assert res["hset"] == set() and res["word"] == "FIRES", res["hset"]
        assert "a0_c0" not in res["hier"]["reached"]
        assert "G12: " + W_FIRES + " (0 depth-1 sites of 14 in the set)" in text, text
        assert "0 of 15 sites: (empty)" in text and "site-null floor: the numeric floor clause is NOT EVALUATED" in text
        assert "B-A2: N-1 fires while H 0.2912 > its permutation p95 0.0264 (MMLU-GOLD-GEOMETRY, of record): the B-A2 " \
            "alternative wording does not apply" in text, text
        assert W_BA2_ALT not in text
        assert "P3 set size HELD: 0 (point 1, 80% interval [0, 3])" in text
        assert "P3 N-1 fires (registered p 0.30): event FIRES, Brier 0.4900" in text
        assert "CONSEQUENCE: F-TAX N-1 = FIRES" in text
        assert "per-site p95 count (printed beside, never deciding): 0 of 15 sites; Binomial(15, 0.05): mean 0.75, P(X >= 0) = 1.000" \
            in text
        # B-A2 alternative wording when H <= p95 (boundary H == p95 included)
        for gold, hp in (("G-1: HELD (H 0.0264 > p95 0.0264; the point decides)", "0.0264 <= its permutation p95 0.0264"),
                         ("G-1: HELD (H 0.0100 > p95 0.0264; the point decides)", "0.0100 <= its permutation p95 0.0264")):
            sites, rec = _sites_rec(tmp, N, rows, dict(a0=5))
            st = structure(sites, rec)
            r = analyze(sites, rec, st)
            h, p95 = (Fraction(x) for x in re.match(r"G-1: HELD \(H (\S+) > p95 (\S+);", gold).groups())
            t = "\n".join(verdict_lines(r, st, sites, h, p95))
            assert ("B-A2: N-1 fires while H %s: the text says \"%s\", not \"%s\"; the N-1 verdict is unchanged"
                    % (hp, W_BA2_ALT, W_BA2_NOTCERT)) in t, t
        # the gold gate refuses a value other than the record
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        _refused(lambda: _run_fixture(tmp2, N, rows, dict(a0=5), gold="G-1: HELD (H 0.0100 > p95 0.0264; the point decides)"),
                 "of record 0.2912 / 0.0264")
        tmp3 = tempfile.mkdtemp(); TMPS.append(tmp3)
        g1 = "G-1: HELD (H 0.2912 > p95 0.0264; the point decides)"
        _refused(lambda: _run_fixture(tmp3, N, rows, dict(a0=5), gold=g1 + "\n" + g1), "carries 2 'G-1: HELD")
        tmp4 = tempfile.mkdtemp(); TMPS.append(tmp4)
        _refused(lambda: _run_fixture(tmp4, N, rows, dict(a0=5), gold="G-1: FAILED"), "carries 0 'G-1: HELD")

    @check
    def st06_p3_failed_and_boundary_m15():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        res, text, *_ = _run_fixture(tmp, N, rows, dict(a0=0, a1=0, a2=0, a3=0, a0_c0=0))
        assert len(res["hset"]) == 5 and "P3 set size FAILED: 5 (point 1, 80% interval [0, 3])" in text, text
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        N, rows = _tree(n_anchors=15)
        res, text, *_ = _run_fixture(tmp2, N, rows, dict(a7=0), expect=_expect(sites=16, m_top=15))
        assert res["hset"] == {"a7"} and res["word"] == "NOT", res["hset"]     # 1/301 <= 0.05/15
        assert "G12: N-1 does not fire" in text
        # q enters the BH: a0 at k = 1 (p 2/301 = .00664 > 0.05/14 = .00357) rejects nothing at q = 0.05
        tmp3 = tempfile.mkdtemp(); TMPS.append(tmp3)
        N, rows = _tree()
        res, text, *_ = _run_fixture(tmp3, N, rows, dict(a0=1))
        assert res["hset"] == set() and res["word"] == "FIRES", res["hset"]

    @check
    def st07_undetermined_by_support():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree(n_anchors=16)
        res, text, *_ = _run_fixture(tmp, N, rows, dict(a0=0, a1=0), expect=_expect(sites=17, m_top=16))
        # two k = 0 sites in a TOP of 16: BH rejects both (2/16 x 0.05 = .00625 >= 1/301), so "does not fire" ALSO applies
        assert res["word"] == "CONFLICT" and res["hset"] == {"a0", "a1"}, res
        assert ("G12: REGISTRATION CONFLICT (D-G12-1; not resolved by the reader, a registrar bracket is owed): the registered "
                "bar reads UNDETERMINED-by-support (the TOP family has m = 16 > 15, 1/301 > 0.05/m) AND N-1's clause reads "
                "\"does not fire\" on the same data (depth-1 sites in the set: 2)") in text, text
        assert "CONSEQUENCE: F-TAX N-1 = NOT SCORED (D-G12-1 registration conflict)" in text
        assert "P3 UNDETERMINED-by-support (registered p 0.15): NOT SCORED (D-G12-1)" in text
        assert "G12: N-1" not in text
        assert "per-site p95 count (printed beside, never deciding): 0 of 17 sites" in text and "site-null floor:" in text
        assert "min p = 1/301 = 0.003322 > 0.05/m = 0.003125" in text
        # G-3 against G-1's M = 14 refuses this member on the lane of record
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        _refused(lambda: _run_fixture(tmp2, N, rows, dict(a0=0)), "G-3: sites / families / TOP m = (17, 2, 16), G-1 of record "
                 "printed (15, 2, 14)")

    @check
    def st08_d12_vacuous_root_and_mixed():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree(root_site=True)
        msg = _refused(lambda: _run_fixture(tmp, N, rows, dict(R=0, a0=0), expect=_expect(sites=16, families=3, m_top=1)),
                       "D-12: the root is a site (R, depth 0): a vacuous root")
        assert not os.path.exists(os.path.join(tmp, "root", OUT_DIR_R2, OUT_OUTCOME)), msg
        # D-12 TOP depths != [1] even without a depth-0 row (mixed: a0 not a site, a0_c0 joins TOP: depths [1, 2])
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        N, rows = _tree(mixed=True)
        _refused(lambda: _run_fixture(tmp2, N, rows, {}, expect=_expect(sites=14, families=1, m_top=14)),
                 "D-12: the TOP family's depths are [1, 2], not [1] (m = 14)")
        # without the depth-0 gate the TOP-depths rule still refuses a root site (TOP = {R}, depths [0], m = 1)
        sites, rec = _sites_rec(tmp2, *_tree(root_site=True), {})
        fam, _anc, _mu = CR.site_structure(sites, rec)
        assert sorted(v for v, kk in fam.items() if kk == "TOP") == ["R"]

    @check
    def st08b_empty_and_offint_inputs():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        _refused(lambda: _run_fixture(tmp, N, [], {}), "0 snapshot ids in one site-null CSV")
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        root, spec = _lane_root(tmp2, N, rows, {}, )
        p = os.path.join(root, LANE_R2["csv"][0])
        raw = open(p, "rb").read().replace(b",0.3333,", b",0.3350,", 1)          # q x 300 = 100.5: off-integer
        open(p, "wb").write(raw)
        spec = dict(spec, csv=(spec["csv"][0], pins_of_bytes(raw)["lf"], None))
        _refused(lambda: run(root, spec, _expect(), os.path.join(root, OUT_DIR_R2), io.StringIO(), gate=lambda: True),
                 "off the integer")

    @check
    def st09_g3_identity_multi():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree(multi=True)
        _refused(lambda: _run_fixture(tmp, N, rows, {}, expect=_expect(sites=16, families=3)), "G-3: 1 multi-parent site(s)")
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        N, rows = _tree()
        rows = [r if r[0] != "a3" else (r[0], r[1], 2, r[3], r[4]) for r in rows]      # CSV depth disagrees with the tree
        _refused(lambda: _run_fixture(tmp2, N, rows, {}), "G-3: cert_resolution's identity check FAILED (1): a3 depth 1 != CSV 2")

    @check
    def st10_gates_pins_lane_snapshot_g10():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        root, spec = _lane_root(tmp, N, rows, {})
        od = os.path.join(root, OUT_DIR_R2)
        bad = dict(spec, csv=(spec["csv"][0], "0" * 64, None))
        _refused(lambda: run(root, bad, _expect(), od, io.StringIO(), gate=lambda: True), "REFUSED: csv " + LANE_R2["csv"][0])
        _refused(lambda: dry_run(root, bad, _expect(), io.StringIO()), "sha256-lf16")
        _refused(lambda: run(root, spec, _expect(), od, io.StringIO(), lane="r1", gate=lambda: True),
                 "lane r1: R1's G10 FAILED (F2)")
        _refused(lambda: run(root, spec, _expect(), od, io.StringIO(), gate=lambda: False), "selftest or mutant table is red")
        assert not os.path.exists(os.path.join(od, OUT_OUTCOME))
        _refused(lambda: run(root, spec, dict(_expect(), snapshot="OTHER"), od, io.StringIO(), gate=lambda: True),
                 "the CSV's snapshot SNAP is not the pointer's SNAP / G-1's OTHER")
        tmp2 = tempfile.mkdtemp(); TMPS.append(tmp2)
        _refused(lambda: _run_fixture(tmp2, N, rows, {}, snap="ELSE"), "the CSV's snapshot SNAP is not the pointer's ELSE")
        tmp3 = tempfile.mkdtemp(); TMPS.append(tmp3)
        _refused(lambda: _run_fixture(tmp3, N, rows, {}, g10="G10: FAILED"), "does not print 'G10: HELD'")
        # an out-of-lane output path refuses (rp12_lane guard)
        _refused(lambda: lane_check("r2", root, dict(spec, csv=("experiment_results/archv2/rp12/g12/x.csv", "", None))),
                 "is an object of lane r1")

    @check
    def st10b_default_gate_and_main():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        root, spec = _lane_root(tmp, N, rows, {})
        od = os.path.join(root, OUT_DIR_R2)
        g = globals()
        saved = g["_default_gate"]
        try:
            g["_default_gate"] = lambda: False
            _refused(lambda: run(root, spec, _expect(), od, io.StringIO()), "selftest or mutant table is red")
            g["_default_gate"] = lambda: True
            run(root, spec, _expect(), od, io.StringIO())
        finally:
            g["_default_gate"] = saved
        assert os.path.exists(os.path.join(od, OUT_OUTCOME))
        import contextlib
        for argv, needle in ((["--run"], "--lane is required"), (["--dry-run", "--lane", "r1"], "lane r1: R1's G10 FAILED")):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(argv)
            assert rc == 2 and needle in buf.getvalue(), (argv, rc, buf.getvalue())

    @check
    def st11_dry_run_computes_nothing():
        tmp = tempfile.mkdtemp(); TMPS.append(tmp)
        N, rows = _tree()
        root, spec = _lane_root(tmp, N, rows, dict(a0=0, a1=0), cert=("a0",))
        buf = io.StringIO()
        b = (CR.STAT_CALLS[0], STATS[0])
        st = dry_run(root, spec, _expect(), buf)
        txt = buf.getvalue()
        assert (CR.STAT_CALLS[0], STATS[0]) == b and len(st["top"]) == 14
        assert txt.startswith(POOL_LINE) and "DRY-RUN done: 0 statistics" in txt
        for word in ("G12:", "per-site p95 count", "hierarchical-BH set", "P3 ", "B-A2: "):
            assert word not in txt, word
        assert not os.path.exists(os.path.join(root, OUT_DIR_R2, OUT_OUTCOME))

    @check
    def st12_reproduce_cert_resolution_frozen():
        """cert_resolution of record (experiment_results/cert_resolution/cert_resolution_sites.csv, blob 6d83df50) on the
        frozen tree (an instrument reproduction, not an evidential comparator): every site's p_site, family_key, reached and
        hier_bh, the set {n00000006 Chemistry, n00000005 Biology}, TOP m 14 with depths [1]."""
        cs_raw, _ = read_pinned(ROOT, ("docs/data/site_null_frozen.csv",
                                       "09c41b45ef5d0596a05a1c1a95da7543d07d529616e0e530ed356c18c27a0ef0", None), "frozen")
        jl_raw, _ = read_pinned(ROOT, ("experiment_results/freeze_mcs55/seed_42/dag_snapshots.jsonl",
                                       "6e7c577210f755291693f9c9c21b89f1ea64429b035b050f17c9f597674a5224", None), "frozen")
        ref_raw, _ = read_pinned(ROOT, ("experiment_results/cert_resolution/cert_resolution_sites.csv",
                                        "a151392aa1785b9ef98561900866162debaee5be420e96e5f08e2843eccdd2c7", None), "cert")
        ref = [r for r in csv.DictReader(io.StringIO(ref_raw.decode("utf-8").replace("\r\n", "\n"))) if r["tree"] == "frozen"]
        sites, _snap = CR.read_sites(cs_raw, "frozen")
        rec = CR.read_last_record(jl_raw)
        st = structure(sites, rec, dict(sites=66, families=len({r["family_key"] for r in ref}), m_top=14))
        res = analyze(sites, rec, st)
        mine = {r["node_id"]: r for r in site_rows(sites, st, res)}
        assert len(ref) == 66 == len(mine)
        for r in ref:
            m = mine[r["node_id"]]
            assert (m["p_site"], m["family_key"], m["reached"], m["hier_bh"], m["cert_site_p95"]) == \
                (r["p_site"], r["family_key"], r["reached"], r["hier_bh"], r["cert_site_p95"]), (r, m)
        assert res["hset"] == {"n00000006", "n00000005"} and res["word"] == "NOT" and res["d1"] == ["n00000005", "n00000006"]
        assert st["top_depths"] == [1] and len(st["top"]) == 14 and st["multi"] == 0
        assert res["c"] == sum(1 for r in ref if r["cert_site_p95"] == "true")

    @check
    def st13_branches():
        missing = ALL_BRANCHES - BRANCH_HITS
        assert not missing, "print branches never executed: %s" % sorted(missing)

    TMPS = []
    BRANCH_HITS.clear()
    results = []
    for fn in checks:
        try:
            fn()
            results.append((fn.__name__, None))
        except Exception as e:                                          # noqa: BLE001
            results.append((fn.__name__, "%s: %s" % (type(e).__name__, e)))
    for t in TMPS:
        shutil.rmtree(t, ignore_errors=True)
    return results


def _sites_rec(tmp, N, rows, k, cert=()):
    d = tempfile.mkdtemp(dir=tmp)
    cs, jl = _fixture(d, "x", N, rows, k, cert)
    sites, _ = CR.read_sites(open(cs, "rb").read(), "x")
    return sites, CR.read_last_record(open(jl, "rb").read())


ALL_BRANCHES = {"V-CONFLICT", "V-FIRES", "V-NOT", "BA2-ALT", "BA2-GEOM", "BA2-NOFIRE", "P3-HELD", "P3-FAILED"}

MUTANTS = ["no_pin_check", "no_g10_gate", "no_snapshot_gate", "no_identity_gate", "no_multi_gate", "no_d0_gate", "no_d12_gate",
           "d12_weak", "no_g1_gate", "tail_strict", "tail_m_top", "wrong_depth", "set_nonempty", "bar_ge", "fires_first",
           "q_010", "flat_not_hier", "ba2_strict", "p3_lo1", "p_k_over_300", "lane_r1", "no_write_once", "no_selftest_gate", "default_gate_true", "dryrun_computes"]


def run_selftest(out):
    global MUTANT
    MUTANT = None
    res = selftest(out)
    nf = sum(1 for _, e in res if e)
    for n, e in res:
        out.write("  %-42s %s\n" % (n, "PASS" if e is None else "FAIL " + e))
    out.write("%s SELFTEST: %d checks, %d failed\n" % (TAG, len(res), nf))
    return nf == 0


def run_mutants(out):
    global MUTANT
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
        out.write("  mutant %-18s KILLED by %s\n" % (mu, ", ".join(bad)))
    for mu, _ in survived:
        out.write("  mutant %-18s SURVIVED\n" % mu)
    out.write("%s MUTANTS: %d run, %d killed, %d survived\n" % (TAG, len(MUTANTS), len(killed), len(survived)))
    return not survived


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--lane", choices=["r1", "r2"], default=None)
    a = ap.parse_args(argv)
    print(POOL_LINE)
    try:
        if a.selftest:
            return 0 if run_selftest(sys.stdout) else 1
        if a.mutants:
            return 0 if run_mutants(sys.stdout) else 1
        if a.lane is None:
            raise Refusal("REFUSED: --lane is required (r2; r1 refuses)")
        if a.dry_run:
            buf = io.StringIO()
            try:
                dry_run(ROOT, LANE_R2, LANE_R2_EXPECT, buf, lane=a.lane)
            finally:
                sys.stdout.write(buf.getvalue().split("\n", 1)[1])
            return 0
        run(ROOT, LANE_R2, LANE_R2_EXPECT, os.path.join(ROOT, OUT_DIR_R2), sys.stdout, lane=a.lane)
        return 0
    except Refusal as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
