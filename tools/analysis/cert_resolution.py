"""CERT-RESOLUTION -- at the recorded 300-rep site nulls, which splits of bareq512_s42 (R512) and of af_clean_s42,
o0_clean_s42 and the frozen tree (R256) survive a STATED ERROR RATE (a Clopper-Pearson interval on each site's null
exceedance, Benjamini-Hochberg over each tree's sites, and a prefix-closed hierarchical BH that respects nesting), and
which certified exhibits may the talk name?  Zero calls; no DB is opened.

REGISTRATION OF RECORD: docs/judge_v2_program.md L20752-L20815 (commit 6402b0a), heading "## Registered 2026-09-26
(before any code or call) -- CERT-RESOLUTION: ...". The registration governs; this docstring restates it and never
replaces it. Record: docs/agents/results/CERT-RESOLUTION.json.

LAUNCH SEQUENCE
  python tools/analysis/cert_resolution.py --selftest     synthetic fixtures only (tempfile); every check, every
                                                          registered print branch, and every mutant (all must be killed)
  python tools/analysis/cert_resolution.py --dry-run      reads the real CSVs and parent maps: prints the pins, the
                                                          location used, m per tree, the k-recovery and identity checks
                                                          and the reachability printout; computes NO p, CP or BH on a
                                                          real row; writes nothing
  python tools/analysis/cert_resolution.py --run          after the READY: runs the selftest in-process first (refuses if
                                                          red), then writes WRITE-ONCE (mode "x"; refuses if either exists)
                                                          experiment_results/cert_resolution/cert_resolution_outcome.txt
                                                          experiment_results/cert_resolution/cert_resolution_sites.csv
  Options: --data-root DIR (repeatable; default: this checkout, then the main checkout found through git's common dir),
           --evidence-dir DIR (default Z:/FAC/TUBerlin/THESIS/TaxoArena_data/evidence_2026-09-25/bareq512_s42_unpinned,
           the orchestrator's archived copy of the untracked bareq512_s42 files, SHA256SUMS beside them),
           --out-dir DIR (default <this checkout>/experiment_results/cert_resolution).

POOL: none. The first printed line of every mode is "pool: none (no DB opened)". Not a pool reader (CONTEXT rule 7).

INPUTS (pinned; every input is accepted from ANY candidate location only if its LF-rendering sha256 equals the pin; the
LF rendering is the rendering of record, CRLF working trees are normalised before hashing; blob = git blob id of the LF
bytes). Registered prefixes (programme L20768-L20776) are asserted equal to the full pins below by the selftest.
  site-null CSVs    bareq512_s42 / af_clean_s42 / o0_clean_s42 / frozen   (70 / 69 / 60 / 66 site rows)
  parent maps       the LAST record of each tree's dag_snapshots.jsonl (fields id, depth, isLeaf, isBridge, parentIds,
                    childIds)

DEFINITIONS (registration, "DEFINITIONS (fixed now)")
  k       = round(q_site x reps) -- the NULL EXCEEDANCE COUNT. NOTE: the input CSVs carry a column also named "k", the
            site's number of children; it is read ONLY by the identity check and is called k_children in this code.
            ASSERTED: reps = 300, feasibility = OK, |q_site x reps - k| <= 0.016 on every row; REFUSED otherwise.
  p_site  = (k + 1) / (reps + 1), exact rational arithmetic (fractions.Fraction) in every BH / BY comparison.
  CP      = exact two-sided 95% Clopper-Pearson on k of reps (bisection on the binomial CDF; the selftest checks it
            against scipy's beta quantiles and the closed form 1 - 0.025^(1/300) = 0.012221 at k = 0).
  FLAT BH = the BH step-up at q = 0.05 over the m sites of ONE tree; BY (c(m) = sum 1/i) printed beside, DESCRIPTIVE.
  HIER BH = prefix-closed: site ancestors = sites reachable upward along parentIds (every path); family key = nearest
            site ancestor along parentIds[0] (TOP if none); BH in TOP; a site enters its family's BH only when ALL its
            site ancestors are rejected; a family is run once its key site is rejected; iterate to the deepest level.
            BUILDER'S READINGS (reported to the registrar; inert on the four trees of record, whose multi-parent count
            is printed and is 0): (i) a family is run only when every site ancestor of its members that lies OUTSIDE
            the family is decided; (ii) a member whose site ancestors are not all rejected at that moment does not
            enter the BH and is not counted in m_f.
  IDENTITY CHECK (precondition; failure VOIDS that tree's hierarchical leg, never an outcome; the flat leg still
            runs): every CSV node_id is in the last record, isLeaf false, the CSV's depth, and a count of non-bridge
            childIds equal to the CSV's children column.

[RULED 2026-09-26 (orchestrator; recorded at 23f9f00, programme L20921-L20955): A1 the output k is the exceedance count,
stated in the outcome header (K_HEADER_LINE); A2 the leading `tree` column of the sites CSV; A3 the multi-parent family
rule (i)-(ii) above; A4 the MC-MARGINAL reading below; E2 printed literally. All ACCEPTED.]

EXHIBIT RULE (E1-E4, registered words, written literally in WORDS_* below). MC-MARGINAL: a rejected site whose p_site
lies within 1/301 of its BH threshold. BUILDER'S READING: "its BH threshold" = the step-up cutoff r* x q / m of the
procedure that grants the site its words (the family's for E1, the tree's flat one for E2); "within" = strictly less
than 1/301 below it (one more null exceedance would lose the rejection).

CRITERIA: C1 (hier BH of bareq512_s42 non-empty), C2-<tree> flat BH (three POST-HOC-SEEN), C3-<tree> hier BH on the
R256 trees; predictions P1-P5; falsifiers F1, F2; D1 descriptive. The POINT decides; the CP never decides.
Counts are NEVER compared across R256 and R512.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

REPS = 300
Q = Fraction(1, 20)
K_TOL = 0.016
CP_ALPHA = 0.05
BAR = Fraction(1, 20)            # the per-site bar used by E4 (CP interval contains 0.05)

DEFAULT_EVIDENCE_DIR = "Z:/FAC/TUBerlin/THESIS/TaxoArena_data/evidence_2026-09-25/bareq512_s42_unpinned"
OUT_REL = "experiment_results/cert_resolution"
OUT_OUTCOME = "cert_resolution_outcome.txt"
OUT_SITES = "cert_resolution_sites.csv"
POOL_LINE = "pool: none (no DB opened)"
K_HEADER_LINE = ("k = the null exceedance count round(q_site x reps); the input CSV's k (the site's children) is used only by "
                 "the identity check")                                  # RC1 / ruling A1 (23f9f00)

# Trees, pins (full sha256 of the LF rendering; registered 16-hex prefixes in REGISTERED_PINS), the registered m.
TREES = [
    dict(name="bareq512_s42", recipe="R512", m=70,
         csv=dict(rel="experiment_results/promoted/site_null_bareq512_s42.csv",
                  lf="ea0cb19865f63036d9e8531bf93192c6c92a831c560bbb5338ef7499a20bb642"),
         jsonl=dict(rel="experiment_results/promoted/bareq512_s42/seed_42/dag_snapshots.jsonl",
                    evidence="dag_snapshots.jsonl",
                    lf="0bf29bbc8c9b10b2349ae6a38ec57247db1bcab0d8bb26e54376caeb47c38e8c"),
         last_iter=18, last_nodes=158),
    dict(name="af_clean_s42", recipe="R256", m=69,
         csv=dict(rel="experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv",
                  lf="e15302b76a1aba3a67fbb0ecd203ff650cc00ac655ec787646f754357096a049"),
         jsonl=dict(rel="experiment_results/anchorfree/redraw/af_clean_s42/seed_42/dag_snapshots.jsonl",
                    lf="1b9bd34d648ef29e1e1623573d0a70e32c5f1c3756d1ceb01fbb2325ed833b93"),
         last_iter=None, last_nodes=None),
    dict(name="o0_clean_s42", recipe="R256", m=60,
         csv=dict(rel="experiment_results/anchorfree/redraw/site_null_o0_clean_s42.csv",
                  lf="f44c4dbff0d8e360dae181daf29bcb520249df03a96cb8f2d8da3ec47ba522f0"),
         jsonl=dict(rel="experiment_results/anchorfree/redraw/o0_clean_s42/seed_42/dag_snapshots.jsonl",
                    lf="c73b1cc206b728079abc7872f3b3fd01a9072e69da5a907e78ac36406650dd48"),
         last_iter=None, last_nodes=None),
    dict(name="frozen", recipe="R256", m=66,
         csv=dict(rel="docs/data/site_null_frozen.csv",
                  lf="09c41b45ef5d0596a05a1c1a95da7543d07d529616e0e530ed356c18c27a0ef0"),
         jsonl=dict(rel="experiment_results/freeze_mcs55/seed_42/dag_snapshots.jsonl",
                    lf="6e7c577210f755291693f9c9c21b89f1ea64429b035b050f17c9f597674a5224"),
         last_iter=10, last_nodes=154),
]
# programme L20768-L20776, verbatim prefixes (blob / sha256-lf16 [/ sha256-crlf16])
REGISTERED_PINS = {
    "experiment_results/promoted/site_null_bareq512_s42.csv": ("16aaf5a4", "ea0cb19865f63036", "8b3d32ffd88f4a3c"),
    "experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv": ("8ed1b699", "e15302b76a1aba3a", "a21f1836900cb8bc"),
    "experiment_results/anchorfree/redraw/site_null_o0_clean_s42.csv": ("f69179a0", "f44c4dbff0d8e360", "58d79630d11bc689"),
    "docs/data/site_null_frozen.csv": ("1577e9e4", "09c41b45ef5d0596", "71965a361d7954fa"),
    "experiment_results/promoted/bareq512_s42/seed_42/dag_snapshots.jsonl": ("ffbbb321", "0bf29bbc8c9b10b2", None),
    "experiment_results/anchorfree/redraw/af_clean_s42/seed_42/dag_snapshots.jsonl": ("e8a76790", "1b9bd34d648ef29e", None),
    "experiment_results/anchorfree/redraw/o0_clean_s42/seed_42/dag_snapshots.jsonl": ("8a60a143", "c73b1cc206b72807", None),
    "experiment_results/freeze_mcs55/seed_42/dag_snapshots.jsonl": ("1c020ca5", "6e7c577210f75529", "fedbe53b5b3e9d60"),
}
POST_HOC_SEEN = {"bareq512_s42", "af_clean_s42", "frozen"}       # C2 legs seen in the brief's disclosure
R256_TREES = ["af_clean_s42", "o0_clean_s42", "frozen"]
# Predictions (registration "PREDICTIONS")
P1_REPRO = {"bareq512_s42": 0, "af_clean_s42": 12, "frozen": 0}
P2_INTERVAL = (0, 5)
P3_INTERVALS = {"bareq512_s42": (3, 1, 6), "af_clean_s42": (11, 6, 14), "o0_clean_s42": (3, 1, 6), "frozen": (2, 1, 4)}
P5_POINT, P5_INTERVAL = 5, (3, 7)

WORDS_E1 = ("certified at per-family FDR q = 0.05 (hierarchical BH over nested sites, 300 reps, {tree}, {recipe})")
WORDS_E2 = "BH-certified at q = 0.05 over the tree's m sites (nesting not respected)"
WORDS_E3 = "passes its own site-null p95 (per-site, uncorrected, 300 reps)"
WORDS_E4 = "resolution-limited at 300 reps"
WORDS_MC = "MC-MARGINAL"

SITES_COLUMNS = ["tree", "node_id", "label", "depth", "n", "k", "reps", "q_site", "p_site", "cp_lo", "cp_hi",
                 "cert_site_p95", "flat_bh", "by", "family_key", "reached", "hier_bh", "words"]

MUTANT = None                    # selftest only: the name of the check a mutant removes
STAT_CALLS = [0]                 # counts p / CP / BH evaluations (the dry-run must leave it at 0)
BRANCH_HITS = set()              # every registered print branch records itself here


class Refusal(Exception):
    pass


def _m(name):
    return MUTANT == name


def _hit(tag):
    BRANCH_HITS.add(tag)


# ----------------------------------------------------------------------------------------------------------- pins
def pins_of_bytes(raw):
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(),
                lf=hashlib.sha256(lf).hexdigest(), crlf=hashlib.sha256(crlf).hexdigest(),
                raw_crlf=(raw != lf))


def pin_line(label, path, p):
    return ("%s  %s  blob:%s / sha256-lf16:%s / sha256-crlf16:%s (working file %s)"
            % (label, path, p["blob"][:8], p["lf"][:16], p["crlf"][:16], "CRLF" if p["raw_crlf"] else "LF"))


def main_checkout_of(root):
    try:
        common = subprocess.run(["git", "-C", root, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return os.path.dirname(os.path.normpath(common))
    except Exception:
        return None


def repo_root():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def locate(spec, data_roots, evidence_dir, out):
    """Return (path, bytes, pins) for the first candidate whose LF sha256 equals the pin; REFUSE if none does."""
    cands = [os.path.join(r, spec["rel"]) for r in data_roots]
    if spec.get("evidence") and evidence_dir:
        cands.append(os.path.join(evidence_dir, spec["evidence"]))
    seen = []
    for c in cands:
        if not os.path.isfile(c):
            continue
        with open(c, "rb") as fh:
            raw = fh.read()
        p = pins_of_bytes(raw)
        if p["lf"] == spec["lf"] or _m("no_pin_check"):
            return c, raw, p
        seen.append(c)
        out.write("  WARN pin mismatch at %s: sha256-lf16 %s, pinned %s (candidate skipped)\n"
                  % (c, p["lf"][:16], spec["lf"][:16]))
    raise Refusal("REFUSED: no candidate location of %s matches its pin sha256-lf16:%s (tried %s; mismatched %s)"
                  % (spec["rel"], spec["lf"][:16], cands, seen))


# ----------------------------------------------------------------------------------------------------------- inputs
def parse_bool(s, what):
    if s == "true":
        return True
    if s == "false":
        return False
    raise Refusal("REFUSED: %s is %r, not true/false" % (what, s))


def read_sites(raw, tree):
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    rows = list(csv.DictReader(io.StringIO(text)))
    sites = []
    ids = set()
    snaps = set()
    for r in rows:
        nid = r["node_id"]
        if nid in ids:
            raise Refusal("REFUSED: %s: duplicate node_id %s" % (tree, nid))
        ids.add(nid)
        snaps.add(r["snapshot_id"])
        reps = int(r["reps"])
        if reps != REPS and not _m("no_reps_check"):
            raise Refusal("REFUSED: %s %s: reps = %d, the registration fixes 300" % (tree, nid, reps))
        if r["feasibility"] != "OK" and not _m("no_feasibility_check"):
            raise Refusal("REFUSED: %s %s: feasibility = %r, not OK" % (tree, nid, r["feasibility"]))
        q = float(r["q_site"])
        x = q * reps
        k = int(round(x))
        if abs(x - k) > K_TOL and not _m("no_offint_check"):
            raise Refusal("REFUSED: %s %s: q_site x reps = %.4f is %.4f off the integer %d (> %.3f)"
                          % (tree, nid, x, abs(x - k), k, K_TOL))
        sites.append(dict(node_id=nid, label=r["label"], depth=int(r["depth"]), n=int(r["n"]),
                          k_children=int(r["k"]), k=k, reps=reps, q_site=r["q_site"],
                          cert=parse_bool(r["cert_site_p95"], "%s %s cert_site_p95" % (tree, nid))))
    if len(snaps) != 1:
        raise Refusal("REFUSED: %s: %d snapshot ids in one site-null CSV" % (tree, len(snaps)))
    return sites, snaps.pop()


def read_last_record(raw):
    last = None
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            last = line
    if last is None:
        raise Refusal("REFUSED: empty dag_snapshots.jsonl")
    if _m("first_record"):
        last = next(line for line in raw.decode("utf-8").splitlines() if line.strip())
    rec = json.loads(last)
    return rec


def identity_check(sites, rec):
    """Return a list of failure strings (empty = pass)."""
    nodes = {n["id"]: n for n in rec["nodes"]}
    fails = []
    for s in sites:
        n = nodes.get(s["node_id"])
        if n is None:
            if not _m("id_no_missing"):
                fails.append("%s missing from the last record" % s["node_id"])
            continue
        if n["isLeaf"] and not _m("id_no_leaf"):
            fails.append("%s is a leaf" % s["node_id"])
        if n["depth"] != s["depth"] and not _m("id_no_depth"):
            fails.append("%s depth %d != CSV %d" % (s["node_id"], n["depth"], s["depth"]))
        nb = [c for c in n["childIds"] if not nodes.get(c, {}).get("isBridge", False)]
        if len(nb) != s["k_children"] and not _m("id_no_k"):
            fails.append("%s has %d non-bridge children, CSV k = %d" % (s["node_id"], len(nb), s["k_children"]))
    return fails


# ----------------------------------------------------------------------------------------------------------- statistics
def p_site(k, reps=REPS):
    STAT_CALLS[0] += 1
    return Fraction(k + 1, reps + 1)


def _binom_cdf(k, n, p):
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 1.0 if k >= n else 0.0
    lp, lq = math.log(p), math.log1p(-p)
    tot = 0.0
    for i in range(0, k + 1):
        tot += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
    return min(tot, 1.0)


def _bisect(f, lo=0.0, hi=1.0, it=200):
    # f decreasing in p; find p with f(p) = 0
    for _ in range(it):
        mid = (lo + hi) / 2.0
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def clopper_pearson(k, n=REPS, alpha=CP_ALPHA):
    STAT_CALLS[0] += 1
    a2 = alpha / 2.0 if not _m("cp_one_sided") else alpha
    if k == 0:
        lo = 0.0
    else:   # P(X >= k | p) = a2  <=>  1 - cdf(k-1) = a2 ; 1 - cdf(k-1) increasing in p
        lo = _bisect(lambda p: a2 - (1.0 - _binom_cdf(k - 1, n, p)))
    if k == n:
        hi = 1.0
    else:   # cdf(k | p) = a2 ; cdf decreasing in p
        hi = _bisect(lambda p: _binom_cdf(k, n, p) - a2)
    return lo, hi


def bh_cutoff(ps, q):
    """BH step-up. ps: list of Fractions. Returns (rejected index set, cutoff threshold r* q / m or None)."""
    STAT_CALLS[0] += 1
    m = len(ps)
    if m == 0:
        return set(), None
    order = sorted(range(m), key=lambda i: ps[i])
    rstar = 0
    for r in range(1, m + 1):
        if ps[order[r - 1]] <= Fraction(r) * q / m:
            rstar = r
            if _m("bh_stepdown"):
                continue
        elif _m("bh_stepdown"):
            break
    if rstar == 0:
        return set(), None
    thr = Fraction(rstar) * q / m
    return {i for i in range(m) if ps[i] <= thr}, thr


def by_q(m, q=Q):
    c = sum(Fraction(1, i) for i in range(1, m + 1))
    if _m("by_no_cm"):
        c = Fraction(1)
    return q / c


def site_structure(sites, rec):
    """family key (nearest site ancestor along parentIds[0], or 'TOP') and the full site-ancestor set of each site."""
    nodes = {n["id"]: n for n in rec["nodes"]}
    sid = {s["node_id"] for s in sites}
    anc = {}
    fam = {}
    multi = 0
    for s in sites:
        v = s["node_id"]
        if len(nodes[v]["parentIds"]) > 1:
            multi += 1
        seen = set()
        stack = list(nodes[v]["parentIds"])
        while stack:
            u = stack.pop()
            if u in seen or u not in nodes:
                continue
            seen.add(u)
            stack.extend(nodes[u]["parentIds"])
        anc[v] = {u for u in seen if u in sid}
        key = "TOP"
        u = nodes[v]["parentIds"][0] if nodes[v]["parentIds"] else None
        guard = 0
        while u is not None:
            guard += 1
            if guard > len(nodes) + 1:
                raise Refusal("REFUSED: parentIds[0] chain cycles at %s" % v)
            if u in sid:
                key = u
                break
            pu = nodes[u]["parentIds"] if u in nodes else []
            u = pu[0] if pu else None
        fam[v] = key
    return fam, anc, multi


def hierarchical_bh(sites, fam, anc, pmap, q=Q):
    """Returns dict with rejected set, reached set, per-family records (key, m_f, rejected, cutoff), and the
    per-site cutoff used. Refuses on no progress."""
    STAT_CALLS[0] += 1
    members = {}
    for s in sites:
        members.setdefault(fam[s["node_id"]], []).append(s["node_id"])
    decided = {}
    reached = set()
    cutoff_of = {}
    fams_run = []
    pending = set(members)
    while pending:
        progressed = False
        for key in sorted(pending, key=lambda x: (x != "TOP", x)):
            if key != "TOP" and key not in decided:
                continue
            if key != "TOP" and not decided[key] and not _m("hier_no_parent_gate"):
                for v in members[key]:
                    decided[v] = False
                pending.discard(key)
                fams_run.append(dict(key=key, m_f=0, rejected=0, cutoff=None, run=False))
                progressed = True
                continue
            inside = set(members[key])
            if not _m("hier_no_wait"):
                blocked = any(a not in decided for v in members[key] for a in anc[v] if a not in inside)
                if blocked:
                    continue
            if _m("hier_no_wait") or _m("hier_no_parent_gate"):
                elig = [v for v in members[key]]
            else:
                elig = [v for v in members[key] if all(decided.get(a) is True for a in anc[v])]
            rej_idx, thr = bh_cutoff([pmap[v] for v in elig], q)
            rej = {elig[i] for i in rej_idx}
            for v in members[key]:
                decided[v] = v in rej
                if v in elig:
                    reached.add(v)
                if v in rej:
                    cutoff_of[v] = thr
            fams_run.append(dict(key=key, m_f=len(elig), rejected=len(rej), cutoff=thr, run=True))
            pending.discard(key)
            progressed = True
        if not progressed:
            raise Refusal("REFUSED: hierarchical BH made no progress (families %s wait on each other)" % sorted(pending))
    rejected = {v for v, d in decided.items() if d}
    return dict(rejected=rejected, reached=reached, cutoff_of=cutoff_of, families=fams_run)


def words_for(tree, recipe, in_hier, in_flat, cert, cp, p, thr):
    STAT_CALLS[0] += 1
    if in_hier:
        w = WORDS_E1.format(tree=tree, recipe=recipe)
    elif in_flat:
        w = WORDS_E2
    elif cert:
        w = WORDS_E3
    else:
        return ""
    if (cp[0] <= float(BAR) <= cp[1]) and not _m("e4_off"):
        w += "; " + WORDS_E4
    if (in_hier or in_flat) and thr is not None and not _m("mc_off"):
        if thr - p < Fraction(1, REPS + 1):
            w += "; " + WORDS_MC
    return w


def analyze_tree(spec, sites, rec, identity_fails):
    name, recipe = spec["name"], spec["recipe"]
    m = len(sites)
    pmap = {s["node_id"]: p_site(s["k"], s["reps"]) for s in sites}
    cps = {s["node_id"]: clopper_pearson(s["k"], s["reps"]) for s in sites}
    ids = [s["node_id"] for s in sites]
    flat_idx, flat_thr = bh_cutoff([pmap[v] for v in ids], Q)
    flat = {ids[i] for i in flat_idx}
    by_idx, _ = bh_cutoff([pmap[v] for v in ids], by_q(m))
    by = {ids[i] for i in by_idx}
    hier = None
    fam = {}
    multi = None
    if not identity_fails:
        fam, anc, multi = site_structure(sites, rec)
        hier = hierarchical_bh(sites, fam, anc, pmap)
    rows = []
    for s in sites:
        v = s["node_id"]
        in_h = bool(hier is not None and v in hier["rejected"])
        in_f = v in flat
        thr = hier["cutoff_of"].get(v) if in_h else (flat_thr if in_f else None)
        w = words_for(name, recipe, in_h, in_f, s["cert"], cps[v], pmap[v], thr)
        rows.append(dict(tree=name, node_id=v, label=s["label"], depth=s["depth"], n=s["n"], k=s["k"],
                         reps=s["reps"], q_site=s["q_site"], p_site="%.6f" % float(pmap[v]),
                         cp_lo="%.6f" % cps[v][0], cp_hi="%.6f" % cps[v][1],
                         cert_site_p95="true" if s["cert"] else "false",
                         flat_bh="true" if in_f else "false", by="true" if v in by else "false",
                         family_key=fam.get(v, "VOID") if hier is not None else "VOID",
                         reached=("true" if v in hier["reached"] else "false") if hier is not None else "VOID",
                         hier_bh=("true" if in_h else "false") if hier is not None else "VOID", words=w))
    cert = [s for s in sites if s["cert"]]
    cp_has_bar = [s for s in cert if cps[s["node_id"]][0] <= float(BAR) <= cps[s["node_id"]][1]]
    xtab = {(c, lowk): 0 for c in (True, False) for lowk in (True, False)}
    for s in sites:
        xtab[(s["cert"], s["k"] <= 14)] += 1
    top = [f for f in (hier["families"] if hier else []) if f["key"] == "TOP"]
    return dict(name=name, recipe=recipe, m=m, flat=flat, flat_thr=flat_thr, by=by,
                hier=(None if hier is None else hier["rejected"]),
                families=(None if hier is None else hier["families"]),
                top_size=(top[0]["m_f"] if top else None), multi=multi, identity_fails=identity_fails,
                n_cert=len(cert), n_cert_cp_has_bar=len(cp_has_bar), xtab=xtab, rows=rows,
                e1=[r["node_id"] for r in rows if r["hier_bh"] == "true"],
                e2=[r["node_id"] for r in rows if r["flat_bh"] == "true" and r["hier_bh"] != "true"],
                e3=[r["node_id"] for r in rows if r["cert_site_p95"] == "true" and r["flat_bh"] != "true"
                    and r["hier_bh"] != "true"],
                labels={r["node_id"]: r["label"] for r in rows}, words={r["node_id"]: r["words"] for r in rows})


# ----------------------------------------------------------------------------------------------------------- printouts
def reachability_lines():
    """Pure arithmetic of the registration (no data)."""
    L = []
    minp = Fraction(1, REPS + 1)
    L.append("REACHABILITY (registered arithmetic, no data): min p = 1/301 = %.6f" % float(minp))
    holm_m = next(m for m in range(1, 1000) if Q / m < minp)
    L.append("  Holm / Bonferroni first threshold 0.05/m < 1/301 for every m >= %d (0.05/15 = %.6f >= %.6f > 0.05/16 = %.6f):"
             " Holm can reject NOTHING on any of the four trees at 300 reps (m = 70 / 69 / 60 / 66), whatever the data"
             % (holm_m, float(Q / 15), float(minp), float(Q / 16)))
    need = {t["name"]: math.ceil(Fraction(t["m"]) / (Fraction(REPS + 1) * Q)) for t in TREES}
    L.append("  flat BH can reject only if at least ceil(m / 15.05) sites sit at k = 0: "
             + ", ".join("%d of %d (%s)" % (need[t["name"]], t["m"], t["name"]) for t in TREES))
    fam_max = max(mf for mf in range(1, 1000) if minp <= Q / mf)
    L.append("  a hierarchical family of at most %d sites can reject a single k = 0 site" % fam_max)
    kmax = max(k for k in range(0, 30) if clopper_pearson_nocount(k)[1] < 0.05)
    L.append("  the largest k whose CP upper bound is below 0.05 is %d (k = %d: %.4f; k = %d: %.4f)"
             % (kmax, kmax, clopper_pearson_nocount(kmax)[1], kmax + 1, clopper_pearson_nocount(kmax + 1)[1]))
    return L, dict(holm_m=holm_m, need=need, fam_max=fam_max, kmax=kmax)


def clopper_pearson_nocount(k):
    before = STAT_CALLS[0]
    r = clopper_pearson(k)
    STAT_CALLS[0] = before          # registered arithmetic on no data: not a statistic of a real row
    return r


def support_lines():
    se = math.sqrt(0.05 * 0.95 / REPS)
    return ["SUPPORT (registered): deciding denominators m = 70 / 69 / 60 / 66 sites (C1: bareq512_s42's 70); within a site "
            "DEFF = 1 by construction (independent parametric null draws; declared, not measured); n_eff = 300 draws per site; "
            "MC SE of an exceedance at the per-site bar 0.05: sqrt(0.05 x 0.95 / 300) = %.5f; exact 95%% upper bound at k = 0: "
            "1 - 0.025^(1/300) = %.5f; MDE at 80%% power (2.80 SE) = %.4f; sites are nested, not independent units "
            "(BH's positive dependence NOT shown; BY printed as the sensitivity)."
            % (se, 1 - 0.025 ** (1.0 / REPS), 2.80 * se)]


def _in(x, iv):
    return iv[0] <= x <= iv[1]


def render_outcome(res, header_lines):
    """res: dict name -> tree result (analyze_tree output, or a synthetic equivalent). Pure; records branches."""
    L = list(header_lines)
    L += reachability_lines()[0]
    L += support_lines()
    L.append("RECIPES ARE NEVER COMPARED: bareq512_s42 is R512 (512 d, bar 0.0145); af_clean_s42, o0_clean_s42 and frozen are "
             "R256 (256 d, bar 0.025); no count or share below is ranked or differenced across R256 and R512.")
    for t in TREES:
        r = res[t["name"]]
        L.append("")
        L.append("== %s (%s): m = %d sites" % (r["name"], r["recipe"], r["m"]))
        if r["identity_fails"]:
            _hit("identity-void")
            L.append("  IDENTITY CHECK FAILED (%d): hierarchical leg VOID for this tree (a failed precondition, not an outcome): %s"
                     % (len(r["identity_fails"]), "; ".join(r["identity_fails"][:10])))
        else:
            _hit("identity-pass")
            L.append("  identity check: PASS (%d sites; multi-parent sites: %d)" % (r["m"], r["multi"]))
        L.append("  flat BH at q = 0.05: %d of %d rejected%s" % (len(r["flat"]), r["m"],
                 (" (cutoff %.6f)" % float(r["flat_thr"])) if r["flat_thr"] is not None else ""))
        L.append("  BY (descriptive): %d of %d" % (len(r["by"]), r["m"]))
        if r["hier"] is None:
            L.append("  hierarchical BH: VOID")
        else:
            L.append("  hierarchical BH (per-family q = 0.05; tree-wide FDR NOT claimed): %d rejected; top family %s sites"
                     % (len(r["hier"]), r["top_size"]))
            fr = [f for f in r["families"] if f["run"]]
            L.append("  families reached: %d; sizes m_f = %s" % (len(fr), [f["m_f"] for f in fr]))
        L.append("  D1: cert_site_p95 sites %d, of which CP interval contains 0.05: %d" % (r["n_cert"], r["n_cert_cp_has_bar"]))
        x = r["xtab"]
        L.append("  D1 cross-tab (cert_site_p95 x k <= 14): cert&k<=14 %d, cert&k>14 %d, uncert&k<=14 %d, uncert&k>14 %d"
                 % (x[(True, True)], x[(True, False)], x[(False, True)], x[(False, False)]))
        for tag, lst in (("E1", r["e1"]), ("E2", r["e2"]), ("E3", r["e3"])):
            L.append("  %s list (%d): %s" % (tag, len(lst), ", ".join("%s %s [%s]" % (v, r["labels"].get(v, ""), r["words"].get(v, ""))
                                                                       for v in lst) or "(empty)"))
    L.append("")
    L.append("CRITERIA (the POINT decides; the CP never decides)")
    b = res["bareq512_s42"]
    if b["hier"] is None:
        _hit("C1-VOID")
        c1 = None
        L.append("C1 VOID: the identity check of bareq512_s42 failed; the hierarchical leg is a failed precondition, not an outcome.")
    elif bool(len(b["hier"]) > 0):
        _hit("C1-HELD")
        c1 = True
        L.append("C1 HELD: the hierarchical BH set of bareq512_s42 at per-family q = 0.05 is NON-EMPTY (%d sites)." % len(b["hier"]))
    else:
        _hit("C1-FAILED")
        c1 = False
        L.append("C1 FAILED: the hierarchical BH set of bareq512_s42 at per-family q = 0.05 is EMPTY.")
    for t in TREES:
        r = res[t["name"]]
        seen = t["name"] in POST_HOC_SEEN
        tag = " POST-HOC-SEEN" if seen else " (unseen)"
        _hit("C2-seen" if seen else "C2-unseen")
        if bool(len(r["flat"]) > 0):
            _hit("C2-HELD")
            L.append("C2-%s HELD%s: flat BH non-empty (%d of %d)." % (t["name"], tag, len(r["flat"]), r["m"]))
        else:
            _hit("C2-FAILED")
            L.append("C2-%s FAILED%s: flat BH empty (0 of %d)." % (t["name"], tag, r["m"]))
    for n in R256_TREES:
        r = res[n]
        if r["hier"] is None:
            _hit("C3-VOID")
            L.append("C3-%s VOID: identity check failed." % n)
        elif bool(len(r["hier"]) > 0):
            _hit("C3-HELD")
            L.append("C3-%s HELD: hierarchical BH non-empty (%d)." % (n, len(r["hier"])))
        else:
            _hit("C3-FAILED")
            L.append("C3-%s FAILED: hierarchical BH empty." % n)
    L.append("")
    L.append("EXHIBITS (the only words of record for a named split)")
    if b["hier"] is not None and bool(len(b["e1"]) > 0):
        _hit("E1-R512-nonempty")
        L.append("The talk's certified R512 exhibits are bareq512_s42's E1 list (%d)." % len(b["e1"]))
    else:
        _hit("E1-R512-empty")
        L.append("bareq512_s42's E1 list is empty: no R512 split is named as certified (E3 words only).")
    L.append("")
    L.append("PREDICTIONS")
    ok = all(len(res[n]["flat"]) == v for n, v in P1_REPRO.items())
    _hit("P1-HELD" if ok else "P1-FAILED")
    L.append("P1 %s (reproduction, not a test): flat BH %s; registered %s."
             % ("HELD" if ok else "FAILED", ", ".join("%s %d/%d" % (n, len(res[n]["flat"]), res[n]["m"]) for n in P1_REPRO),
                ", ".join("%s %d" % (n, v) for n, v in P1_REPRO.items())))
    p1_ok = bool(ok)
    o0 = len(res["o0_clean_s42"]["flat"])
    ok = _in(o0, P2_INTERVAL)
    _hit("P2-HELD" if ok else "P2-FAILED")
    L.append("P2 %s: flat BH on o0_clean_s42 = %d (point 0, 80%% interval [0, 5])." % ("HELD" if ok else "FAILED", o0))
    for n, (pt, lo, hi) in P3_INTERVALS.items():
        r = res[n]
        if r["hier"] is None:
            _hit("P3-VOID")
            L.append("P3-%s UNSCORED: hierarchical leg VOID." % n)
            continue
        ok = _in(len(r["hier"]), (lo, hi))
        _hit("P3-HELD" if ok else "P3-FAILED")
        L.append("P3-%s %s: hierarchical BH size %d (point %d, 80%% interval [%d, %d])."
                 % (n, "HELD" if ok else "FAILED", len(r["hier"]), pt, lo, hi))
    if c1 is None:
        _hit("P4-VOID")
        L.append("P4 UNSCORED: C1 VOID.")
    else:
        _hit("P4-HELD" if c1 else "P4-FAILED")
        L.append("P4 %s: C1 %s (registered probability 0.80 of HELD)." % ("HELD" if c1 else "FAILED", "HELD" if c1 else "FAILED"))
    n5 = b["n_cert_cp_has_bar"]
    ok = _in(n5, P5_INTERVAL)
    _hit("P5-HELD" if ok else "P5-FAILED")
    L.append("P5 %s: %d of bareq512_s42's %d cert_site_p95 sites resolution-limited (point 5, 80%% interval [3, 7])."
             % ("HELD" if ok else "FAILED", n5, b["n_cert"]))
    L.append("")
    L.append("FALSIFIERS")
    if c1 is None:
        _hit("F1-VOID")
        L.append("F1 NOT SCORED: C1 VOID.")
    elif not c1:
        _hit("F1-FIRES")
        L.append("F1 FIRES: the tree of record's hierarchical BH set is EMPTY at 300 reps; bareq512_s42's '10/70 certify' is not a set "
                 "with an error rate; R512 splits are named with E3 words only; no recorded count is revised.")
    else:
        _hit("F1-NOT")
        L.append("F1 does not fire (C1 HELD).")
    if not p1_ok:
        _hit("F2-FIRES")
        L.append("F2 FIRES (instrument check): P1 FAILED; the brief's Q2 counts are withdrawn and replaced by this outcome's.")
    else:
        _hit("F2-NOT")
        L.append("F2 does not fire (P1 HELD: the brief's Q2 counts reproduce).")
    return "\n".join(L) + "\n"


ALL_BRANCHES = {"identity-void", "identity-pass", "C1-VOID", "C1-HELD", "C1-FAILED", "C2-seen", "C2-unseen", "C2-HELD",
                "C2-FAILED", "C3-VOID", "C3-HELD", "C3-FAILED", "E1-R512-nonempty", "E1-R512-empty", "P1-HELD", "P1-FAILED",
                "P2-HELD", "P2-FAILED", "P3-VOID", "P3-HELD", "P3-FAILED", "P4-VOID", "P4-HELD", "P4-FAILED", "P5-HELD",
                "P5-FAILED", "F1-VOID", "F1-FIRES", "F1-NOT", "F2-FIRES", "F2-NOT"}


# ----------------------------------------------------------------------------------------------------------- modes
def self_identity():
    with open(os.path.abspath(__file__), "rb") as fh:
        p = pins_of_bytes(fh.read())
    return "script tools/analysis/cert_resolution.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (
        p["blob"][:8], p["lf"][:16], p["crlf"][:16])


def load_inputs(trees, data_roots, evidence_dir, out):
    loaded = []
    for t in trees:
        cpath, craw, cp = locate(t["csv"], data_roots, None, out)
        out.write(pin_line("  %-13s csv  " % t["name"], cpath, cp) + "\n")
        jpath, jraw, jp = locate(t["jsonl"], data_roots, evidence_dir if t["jsonl"].get("evidence") else None, out)
        out.write(pin_line("  %-13s dag  " % t["name"], jpath, jp) + "\n")
        sites, snap = read_sites(craw, t["name"])
        if len(sites) != t["m"] and not _m("no_m_check"):
            raise Refusal("REFUSED: %s has %d site rows, the registration fixes m = %d" % (t["name"], len(sites), t["m"]))
        rec = read_last_record(jraw)
        if t.get("last_iter") is not None and (rec["iteration"] != t["last_iter"] or len(rec["nodes"]) != t["last_nodes"]):
            raise Refusal("REFUSED: %s last record is iteration %s with %d nodes; registered %s / %s"
                          % (t["name"], rec["iteration"], len(rec["nodes"]), t["last_iter"], t["last_nodes"]))
        fails = identity_check(sites, rec)
        loaded.append((t, sites, rec, fails, snap))
    return loaded


def dry_run(trees, data_roots, evidence_dir, out):
    out.write(POOL_LINE + "\n")
    out.write(self_identity() + "\n")
    out.write("DRY-RUN: pins, locations, m, k recovery, identity checks and the reachability printout; NO p, CP or BH on a real row.\n")
    before = STAT_CALLS[0]
    loaded = load_inputs(trees, data_roots, evidence_dir, out)
    if _m("dryrun_computes") or _m("dryrun_computes_unguarded"):     # the defect a mutant models: a statistic on a real row
        for _t, sites, _r, _f, _s in loaded:
            for s in sites:
                p_site(s["k"], s["reps"])
    for t, sites, rec, fails, snap in loaded:
        nodes = {n["id"]: n for n in rec["nodes"]}
        multi = sum(1 for s in sites if len(nodes.get(s["node_id"], {}).get("parentIds", [])) > 1)
        nonsite_internal = sorted(n["id"] for n in rec["nodes"] if not n["isLeaf"])
        nonsite_internal = [v for v in nonsite_internal if v not in {s["node_id"] for s in sites}]
        out.write("  %-13s %s snapshot %s; m = %d site rows (registered %d); reps 300 / feasibility OK / k recovery: PASS on all rows; "
                  "last record iteration %s, %d nodes; identity check: %s; multi-parent sites: %d; internal non-site nodes: %s\n"
                  % (t["name"], t["recipe"], snap, len(sites), t["m"], rec["iteration"], len(rec["nodes"]),
                     "PASS" if not fails else "FAIL (%d): %s" % (len(fails), "; ".join(fails[:5])), multi,
                     nonsite_internal))
    for line in reachability_lines()[0]:
        out.write(line + "\n")
    if STAT_CALLS[0] != before and not _m("dryrun_computes_unguarded"):
        raise Refusal("REFUSED: the dry-run evaluated %d statistics on real rows" % (STAT_CALLS[0] - before))
    out.write("DRY-RUN done: 0 statistics evaluated on real rows; nothing written.\n")
    return loaded


def run(trees, data_roots, evidence_dir, out_dir, out, skip_selftest=False):
    out_txt = os.path.join(out_dir, OUT_OUTCOME)
    out_csv = os.path.join(out_dir, OUT_SITES)
    for p in (out_txt, out_csv):
        if os.path.exists(p) and not _m("no_write_once"):
            raise Refusal("REFUSED: %s exists; outcome files of record are write-once" % p)
    if not skip_selftest:
        ok = run_selftest(io.StringIO())
        if not ok:
            raise Refusal("REFUSED: the in-process selftest is red")
    hdr = io.StringIO()
    hdr.write(POOL_LINE + "\n")
    hdr.write(self_identity() + "\n")
    hdr.write("CERT-RESOLUTION outcome (registration docs/judge_v2_program.md L20752-L20815, 6402b0a). Zero calls.\n")
    hdr.write(K_HEADER_LINE + "\n")
    hdr.write("INPUTS\n")
    loaded = load_inputs(trees, data_roots, evidence_dir, hdr)
    res = {}
    for t, sites, rec, fails, snap in loaded:
        res[t["name"]] = analyze_tree(t, sites, rec, fails)
    text = render_outcome(res, hdr.getvalue().rstrip("\n").split("\n"))
    os.makedirs(out_dir, exist_ok=True)
    mode = "w" if _m("no_write_once") else "x"
    with open(out_csv, mode, newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SITES_COLUMNS, lineterminator="\n")
        w.writeheader()
        for t in trees:
            for row in res[t["name"]]["rows"]:
                w.writerow(row)
    with open(out_txt, mode, newline="\n", encoding="utf-8") as fh:
        fh.write(text)
    out.write(text)
    return res


# ----------------------------------------------------------------------------------------------------------- selftest
def _fixture_tree(tmp, name, nodes, csv_rows, reps=300, feas="OK", records=1):
    """nodes: list of dicts id, depth, isLeaf, parentIds, childIds (isBridge False). csv_rows: (id, label, depth, n, kch, q, cert)."""
    jl = os.path.join(tmp, name + ".jsonl")
    with open(jl, "w", encoding="utf-8", newline="\n") as fh:
        for it in range(1, records + 1):
            fh.write(json.dumps(dict(iteration=it, nodes=[dict(n, isBridge=n.get("isBridge", False)) for n in nodes])) + "\n")
    cs = os.path.join(tmp, name + ".csv")
    with open(cs, "w", encoding="utf-8", newline="") as fh:
        fh.write("snapshot_id,node_id,label,depth,n,k,observed_sep,site_null_p50,site_null_p95,q_site,site_reach_pct,"
                 "site_accept_pct,defl_dims,defl_null_p50,defl_null_p95,q_deflated,defl_reach_pct,defl_accept_pct,"
                 "cert_site_p95,cert_deflated_p95,trunk_member,feasibility,reps\r\n")
        for (i, lab, d, n, kc, q, cert) in csv_rows:
            fh.write('"SNAP",%s,%s,%d,%d,%d,0.05,0.03,0.04,%s,100.0,100.0,1,0.02,0.03,0.0,100.0,0.0,%s,true,false,%s,%d\r\n'
                     % (i, lab, d, n, kc, q, "true" if cert else "false", feas, reps))
    return cs, jl


def _spec_for(name, recipe, cs, jl, m):
    with open(cs, "rb") as fh:
        cp = pins_of_bytes(fh.read())
    with open(jl, "rb") as fh:
        jp = pins_of_bytes(fh.read())
    return dict(name=name, recipe=recipe, m=m, csv=dict(rel=os.path.basename(cs), lf=cp["lf"]),
                jsonl=dict(rel=os.path.basename(jl), lf=jp["lf"]), last_iter=None, last_nodes=None)


def _chain_tree():
    """Three-level synthetic tree: root R (not a site) -> A, B (sites) ; A -> A1, A2 (sites) ; A1 -> A1a (site),
    B -> B1 (site); multi-parent site M with parents [A2, B1]; leaves under each."""
    N = []

    def node(i, d, leaf, parents, children):
        N.append(dict(id=i, depth=d, isLeaf=leaf, parentIds=parents, childIds=children))
    node("R", 0, False, [], ["A", "B"])
    node("A", 1, False, ["R"], ["A1", "A2"])
    node("B", 1, False, ["R"], ["B1", "Lb"])
    node("A1", 2, False, ["A"], ["A1a", "La1"])
    node("A2", 2, False, ["A"], ["M", "La2"])
    node("B1", 2, False, ["B"], ["M", "Lb1"])
    node("A1a", 3, False, ["A1"], ["x1", "x2"])
    node("M", 3, False, ["A2", "B1"], ["y1", "y2"])
    for leaf, par, d in (("Lb", "B", 2), ("La1", "A1", 3), ("La2", "A2", 3), ("Lb1", "B1", 3), ("x1", "A1a", 4),
                         ("x2", "A1a", 4), ("y1", "M", 4), ("y2", "M", 4)):
        node(leaf, d, True, [par], [])
    return N


def selftest(out):
    global MUTANT
    checks = []

    def check(fn):
        checks.append(fn)
        return fn

    @check
    def st0_registered_pins():
        for t in TREES:
            for part in ("csv", "jsonl"):
                rel, lf = t[part]["rel"], t[part]["lf"]
                assert REGISTERED_PINS[rel][1] == lf[:16], (rel, lf[:16])

    @check
    def st1_cp():
        from scipy.stats import beta
        lo, hi = clopper_pearson(0)
        assert lo == 0.0 and abs(hi - (1 - 0.025 ** (1 / 300.0))) < 1e-9, hi
        assert abs(hi - 0.012221) < 5e-7, hi
        for k in (1, 2, 7, 8, 14, 150, 299, 300):
            lo, hi = clopper_pearson(k)
            rlo = 0.0 if k == 0 else beta.ppf(0.025, k, 300 - k + 1)
            rhi = 1.0 if k == 300 else beta.ppf(0.975, k + 1, 300 - k)
            assert abs(lo - rlo) < 1e-8 and abs(hi - rhi) < 1e-8, (k, lo, rlo, hi, rhi)
        assert round(clopper_pearson(7)[1], 4) == 0.0475 and round(clopper_pearson(8)[1], 4) == 0.0519

    @check
    def st2_flat_bh_by():
        F = Fraction
        # hand-computed: m = 10, q = 0.05; thresholds r*0.005
        ps = [F(1, 301)] * 3 + [F(2, 301), F(4, 301), F(30, 301), F(60, 301), F(100, 301), F(200, 301), F(1)]
        # 1/301=.003322 <= .005 (r1), .010 (r2), .015 (r3); 2/301=.006645 <= .020 (r4); 4/301=.013289 <= .025 (r5);
        # 30/301=.0997 > .030; ... so r* = 5, reject 5
        rej, thr = bh_cutoff(ps, Q)
        assert rej == {0, 1, 2, 3, 4} and thr == F(5, 1) * Q / 10, (rej, thr)
        # step-up (not step-down): p_(1) fails its own rank but a later rank passes
        ps2 = [F(6, 1000), F(6, 1000), F(7, 1000)] + [F(1)] * 7        # m=10: r1 .005 < .006 FAIL; r3 .015 >= .007 PASS
        rej2, thr2 = bh_cutoff(ps2, Q)
        assert rej2 == {0, 1, 2}, rej2
        # ties across the cutoff: all tied values rejected together
        ps3 = [F(1, 301)] * 5 + [F(1)] * 65                              # m=70: r5 thr 5*.05/70=.003571 >= .003322
        rej3, _ = bh_cutoff(ps3, Q)
        assert rej3 == set(range(5)), rej3
        ps4 = [F(1, 301)] * 4 + [F(1)] * 66                              # r4 .002857 < .003322: nothing
        assert bh_cutoff(ps4, Q)[0] == set()
        # k = 0 on 4 of 60 sites: needed 4 (registration) -> reject
        assert bh_cutoff([F(1, 301)] * 4 + [F(1)] * 56, Q)[0] == set(range(4))
        # BY: c(10) = 7381/2520; q' = 0.05 / 2.928968 = 0.017071; ps: 1/301 <= r*q'/10 (0.0017071 r) -> r>=2:
        # r3 .005121 >= .003322 ; r4 .006828 >= .006645 ; r5 .008535 < .013289 ; so r* = 4
        assert by_q(10) == Q / F(7381, 2520)
        rej5, _ = bh_cutoff(ps, by_q(10))
        assert rej5 == {0, 1, 2, 3}, rej5

    @check
    def st3_hierarchical():
        F = Fraction
        N = _chain_tree()
        rec = dict(iteration=1, nodes=[dict(n, isBridge=False) for n in N])
        sites = [dict(node_id=i, depth=d) for i, d in (("A", 1), ("B", 1), ("A1", 2), ("A2", 2), ("B1", 2), ("A1a", 3), ("M", 3))]
        fam, anc, multi = site_structure(sites, rec)
        assert multi == 1
        assert fam == {"A": "TOP", "B": "TOP", "A1": "A", "A2": "A", "B1": "B", "A1a": "A1", "M": "A2"}, fam
        assert anc["M"] == {"A2", "B1", "A", "B"}, anc["M"]
        lo, hi = F(1, 301), F(1)
        # case 1: A rejected, B not; A1, A2 rejected (family A, m_f 2); A1a rejected; B1 never tested (B unrejected);
        # M waits for B1 and is never tested
        p = dict(A=lo, B=hi, A1=lo, A2=lo, B1=lo, A1a=lo, M=lo)
        h = hierarchical_bh(sites, fam, anc, p)
        assert h["rejected"] == {"A", "A1", "A2", "A1a"}, h["rejected"]
        assert "B1" not in h["reached"] and "M" not in h["reached"], h["reached"]
        # prefix closure
        for v in h["rejected"]:
            assert all(a in h["rejected"] for a in anc[v]), v
        # case 2: all ancestors rejected -> M tested (family A2, m_f 1)
        p2 = dict(p, B=lo)
        h2 = hierarchical_bh(sites, fam, anc, p2)
        assert h2["rejected"] == {"A", "B", "A1", "A2", "B1", "A1a", "M"}, h2["rejected"]
        fm = {f["key"]: f for f in h2["families"]}
        assert fm["TOP"]["m_f"] == 2 and fm["A"]["m_f"] == 2 and fm["A2"]["m_f"] == 1
        # case 3: family size gate: a top family of 16 at k=0 alone cannot reject a single one (1/301 > 0.05/16)
        sites16 = [dict(node_id="s%d" % i, depth=1) for i in range(16)]
        rec16 = dict(nodes=[dict(id="root", depth=0, isLeaf=False, parentIds=[], childIds=["s%d" % i for i in range(16)])]
                     + [dict(id="s%d" % i, depth=1, isLeaf=False, parentIds=["root"], childIds=[]) for i in range(16)])
        f16, a16, _ = site_structure(sites16, rec16)
        p16 = {"s0": lo}
        p16.update({"s%d" % i: hi for i in range(1, 16)})
        assert hierarchical_bh(sites16, f16, a16, p16)["rejected"] == set()
        p15 = {k: v for k, v in p16.items() if k != "s15"}
        s15 = [s for s in sites16 if s["node_id"] != "s15"]
        rec15 = dict(nodes=[n for n in rec16["nodes"] if n["id"] != "s15"])
        f15, a15, _ = site_structure(s15, rec15)
        assert hierarchical_bh(s15, f15, a15, p15)["rejected"] == {"s0"}

    @check
    def st4_k_recovery():
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        N = _chain_tree()
        good = [("A", "a", 1, 100, 2, "0.0067", True)]
        cs, _ = _fixture_tree(tmp, "g", N, good)
        with open(cs, "rb") as fh:
            sites, _ = read_sites(fh.read(), "g")
        assert sites[0]["k"] == 2 and sites[0]["k_children"] == 2
        for bad, kw in (([("A", "a", 1, 100, 2, "0.0050", True)], {}),          # 1.5 off-integer
                        ([("A", "a", 1, 100, 2, "0.0067", True)], dict(reps=299)),
                        ([("A", "a", 1, 100, 2, "0.0067", True)], dict(feas="INFEASIBLE"))):
            cs, _ = _fixture_tree(tmp, "b", N, bad, **kw)
            with open(cs, "rb") as fh:
                raw = fh.read()
            try:
                read_sites(raw, "b")
            except Refusal:
                continue
            raise AssertionError("k recovery accepted %r %r" % (bad, kw))

    @check
    def st5_identity():
        N = _chain_tree()
        rec = dict(iteration=1, nodes=[dict(n, isBridge=False) for n in N])
        base = dict(node_id="A", depth=1, k_children=2)
        assert identity_check([base], rec) == []
        assert identity_check([dict(base, node_id="ZZ")], rec)
        assert identity_check([dict(node_id="x1", depth=4, k_children=0)], rec)           # a leaf
        assert identity_check([dict(base, depth=2)], rec)
        assert identity_check([dict(base, k_children=3)], rec)
        # bridge children are not counted
        rec2 = dict(iteration=1, nodes=[dict(n, isBridge=(n["id"] == "A2")) for n in N])
        assert identity_check([base], rec2) and identity_check([dict(base, k_children=1)], rec2) == []

    @check
    def st5b_last_record_and_void():
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        N = _chain_tree()
        _, jl = _fixture_tree(tmp, "r", N, [], records=3)
        with open(jl, "rb") as fh:
            lines = fh.read().decode("utf-8").splitlines()
        lines[-1] = lines[-1].replace('"iteration": 3', '"iteration": 99')
        rec = read_last_record(("\n".join(lines) + "\n").encode("utf-8"))
        assert rec["iteration"] == 99, rec["iteration"]
        # an identity failure VOIDS the hierarchical leg (flat leg still runs)
        spec = dict(name="bareq512_s42", recipe="R512", m=1)
        sites = [dict(node_id="ZZ", label="z", depth=1, n=10, k_children=2, k=0, reps=300, q_site="0.0000", cert=True)]
        r = analyze_tree(spec, sites, dict(nodes=[dict(n, isBridge=False) for n in N]), ["ZZ missing"])
        assert r["hier"] is None and r["flat"] == {"ZZ"} and r["rows"][0]["hier_bh"] == "VOID"

    @check
    def st6_reachability():
        _, v = reachability_lines()
        assert v["holm_m"] == 16 and v["fam_max"] == 15 and v["kmax"] == 7
        assert v["need"] == {"bareq512_s42": 5, "af_clean_s42": 5, "o0_clean_s42": 4, "frozen": 5}, v["need"]
        assert Fraction(1, 301) < Q / 15 and Q / 16 < Fraction(1, 301)

    @check
    def st7_words():
        F = Fraction
        # the registered words, LITERALLY (programme L20779 E1-E4 and the WORDING RULE)
        assert WORDS_E1.format(tree="bareq512_s42", recipe="R512") == ("certified at per-family FDR q = 0.05 (hierarchical BH over "
                                                                      "nested sites, 300 reps, bareq512_s42, R512)")
        assert WORDS_E2 == "BH-certified at q = 0.05 over the tree's m sites (nesting not respected)"
        assert WORDS_E3 == "passes its own site-null p95 (per-site, uncorrected, 300 reps)"
        assert WORDS_E4 == "resolution-limited at 300 reps" and WORDS_MC == "MC-MARGINAL"
        cp0 = clopper_pearson(0)
        cp10 = clopper_pearson(10)
        w = words_for("T", "R512", True, True, True, cp0, F(1, 301), Q * 3 / 70)       # thr .002143 < p? use feasible
        assert w.startswith(WORDS_E1.format(tree="T", recipe="R512"))
        # E4 when CP contains 0.05
        assert words_for("T", "R256", False, False, True, cp10, F(11, 301), None) == WORDS_E3 + "; " + WORDS_E4
        assert words_for("T", "R256", False, False, False, cp0, F(1, 301), None) == ""
        # MC-MARGINAL: threshold 5*0.05/70 = .003571; p = 1/301 = .003322; gap .000249 < 1/301 -> marginal
        assert words_for("T", "R256", False, True, True, cp0, F(1, 301), F(5) * Q / 70) == WORDS_E2 + "; " + WORDS_MC
        # not marginal: threshold 0.05, p 1/301
        assert words_for("T", "R256", False, True, True, cp0, F(1, 301), Q) == WORDS_E2

    @check
    def st8_pin_and_dryrun_and_writeonce():
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        N = _chain_tree()
        rows = [("A", "a", 1, 100, 2, "0.0000", True), ("B", "b", 1, 100, 2, "0.5000", False),
                ("A1", "a1", 2, 50, 2, "0.0000", True), ("A2", "a2", 2, 50, 2, "0.0033", True),
                ("B1", "b1", 2, 50, 2, "0.0000", True), ("A1a", "a1a", 3, 20, 2, "0.0000", True),
                ("M", "m", 3, 20, 2, "0.0000", True)]
        specs = []
        for nm in ("bareq512_s42", "af_clean_s42", "o0_clean_s42", "frozen"):
            cs, jl = _fixture_tree(tmp, nm, N, rows)
            specs.append(_spec_for(nm, "R512" if nm == "bareq512_s42" else "R256", cs, jl, 7))
        buf = io.StringIO()
        before = STAT_CALLS[0]
        dry_run(specs, [tmp], None, buf)
        assert STAT_CALLS[0] == before, "dry-run computed statistics"
        txt = buf.getvalue()
        assert txt.startswith(POOL_LINE) and "flat BH at" not in txt and "C1 " not in txt
        # pin mismatch refuses
        bad = [dict(s, csv=dict(s["csv"], lf="0" * 64)) for s in specs]
        try:
            dry_run(bad, [tmp], None, io.StringIO())
            raise AssertionError("pin mismatch accepted")
        except Refusal:
            pass
        # m mismatch refuses
        try:
            dry_run([dict(s, m=8) for s in specs], [tmp], None, io.StringIO())
            raise AssertionError("m mismatch accepted")
        except Refusal:
            pass
        # run writes once, refuses the second time; outputs have the registered columns
        od = os.path.join(tmp, "out")
        global TREES
        saved = TREES
        TREES = specs
        try:
            res = run(specs, [tmp], None, od, io.StringIO(), skip_selftest=True)
            with open(os.path.join(od, OUT_SITES), encoding="utf-8") as fh:
                hdr = fh.readline().strip().split(",")
            assert hdr == SITES_COLUMNS
            with open(os.path.join(od, OUT_OUTCOME), encoding="utf-8") as fh:
                otxt = fh.read()
            # RC1 (ruling A1): the header line, LITERALLY
            assert ("k = the null exceedance count round(q_site x reps); the input CSV's k (the site's children) is used "
                    "only by the identity check") in otxt.split("INPUTS\n", 1)[0]
            try:
                run(specs, [tmp], None, od, io.StringIO(), skip_selftest=True)
                raise AssertionError("second run overwrote an outcome of record")
            except Refusal:
                pass
        finally:
            TREES = saved
        # hierarchical on the fixture: top {A,B} m_f 2, A (p 1/301) and B (q .5) -> A rejected (1/301 <= .025)
        r = res["bareq512_s42"]
        assert r["hier"] == {"A", "A1", "A2", "A1a"}, r["hier"]
        assert r["flat"] == {"A", "A1", "A2", "B1", "A1a", "M"}, r["flat"]

    @check
    def st9_branches():
        BRANCH_HITS.clear()

        def tres(name, recipe, m, flat, hier, ncert=10, ncp=5, ident=()):
            ids = ["n%d" % i for i in range(m)]
            return dict(name=name, recipe=recipe, m=m, flat=set(ids[:flat]), flat_thr=(Q * flat / m) if flat else None,
                        by=set(), hier=(None if hier is None else set(ids[:hier])),
                        families=([] if hier is None else [dict(key="TOP", m_f=5, rejected=hier, cutoff=None, run=True)]),
                        top_size=(None if hier is None else 5), multi=0, identity_fails=list(ident), n_cert=ncert,
                        n_cert_cp_has_bar=ncp, xtab={(a, b): 0 for a in (True, False) for b in (True, False)}, rows=[],
                        e1=ids[:hier or 0], e2=[], e3=[], labels={}, words={})
        scen = [
            # all HELD
            dict(bareq512_s42=tres("bareq512_s42", "R512", 70, 0, 3), af_clean_s42=tres("af_clean_s42", "R256", 69, 12, 11),
                 o0_clean_s42=tres("o0_clean_s42", "R256", 60, 0, 3), frozen=tres("frozen", "R256", 66, 0, 2)),
            # all FAILED
            dict(bareq512_s42=tres("bareq512_s42", "R512", 70, 1, 0, ncp=9), af_clean_s42=tres("af_clean_s42", "R256", 69, 0, 0),
                 o0_clean_s42=tres("o0_clean_s42", "R256", 60, 9, 0), frozen=tres("frozen", "R256", 66, 3, 9)),
            # VOID
            dict(bareq512_s42=tres("bareq512_s42", "R512", 70, 0, None, ident=["x missing"]),
                 af_clean_s42=tres("af_clean_s42", "R256", 69, 12, None, ident=["x"]),
                 o0_clean_s42=tres("o0_clean_s42", "R256", 60, 0, 3), frozen=tres("frozen", "R256", 66, 0, 2)),
        ]
        texts = [render_outcome(s, [POOL_LINE]) for s in scen]
        missing = ALL_BRANCHES - BRANCH_HITS
        assert not missing, "print branches never executed: %s" % sorted(missing)
        assert "C1 HELD" in texts[0] and "F1 does not fire" in texts[0] and "P1 HELD" in texts[0]
        assert "C1 FAILED" in texts[1] and "F1 FIRES" in texts[1] and "F2 FIRES" in texts[1]
        assert "C1 VOID" in texts[2] and "P4 UNSCORED" in texts[2]
        assert "C2-bareq512_s42 HELD POST-HOC-SEEN" in texts[1] and "C2-o0_clean_s42 HELD (unseen)" in texts[1]
        for t in texts:
            assert t.startswith(POOL_LINE)

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


MUTANTS = ["no_reps_check", "no_feasibility_check", "no_offint_check", "id_no_missing", "id_no_leaf", "id_no_depth",
           "id_no_k", "cp_one_sided", "bh_stepdown", "by_no_cm", "hier_no_wait", "hier_no_parent_gate",
           "e4_off", "mc_off", "no_pin_check", "no_m_check", "dryrun_computes", "dryrun_computes_unguarded",
           "no_write_once", "first_record"]


def run_selftest(out):
    global MUTANT
    MUTANT = None
    base = selftest(out)
    nfail = sum(1 for _, e in base if e)
    for name, e in base:
        out.write("  %-40s %s\n" % (name, "PASS" if e is None else "FAIL " + e))
    out.write("SELFTEST: %d checks, %d failed\n" % (len(base), nfail))
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
    return nfail == 0 and not survived


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", action="append", default=None)
    ap.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE_DIR)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    print(POOL_LINE)
    if a.selftest:
        ok = run_selftest(sys.stdout)
        sys.exit(0 if ok else 1)
    roots = a.data_root
    if not roots:
        roots = [repo_root()]
        mc = main_checkout_of(repo_root())
        if mc and os.path.normcase(os.path.normpath(mc)) != os.path.normcase(roots[0]):
            roots.append(mc)
    buf = io.StringIO()
    try:
        if a.dry_run:
            print("data roots: %s; evidence dir: %s" % (roots, a.evidence_dir))
            buf = io.StringIO()
            dry_run(TREES, roots, a.evidence_dir, buf)
            sys.stdout.write(buf.getvalue().split("\n", 1)[1])     # POOL_LINE already printed
        else:
            out_dir = a.out_dir or os.path.join(repo_root(), OUT_REL)
            buf = io.StringIO()
            if not run_selftest(buf):
                sys.stdout.write(buf.getvalue())
                raise Refusal("REFUSED: selftest red (checks or mutants)")
            run(TREES, roots, a.evidence_dir, out_dir, sys.stdout, skip_selftest=True)
    except Refusal as e:
        if a.dry_run:
            sys.stdout.write(buf.getvalue().split("\n", 1)[-1])      # what was verified before the refusal
        print(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
