"""RECORD-RECIPE-EDGE-AUDIT (Part 2, the audit) -- is any of the 10 site-certified splits of the tree of record
bareq512_s42 (snapshot 20260909_212117; NOT a certified fixed point, Part 1) LATE-BORN (its final child set first
reached after the first quiet iteration 8), and how far above the bar 0.0145 do the certified splits sit (BAR RATIO,
descriptive)? The k-edge half is UNDETERMINED BY INSTRUMENT (D3). Zero calls; no DB is opened.

REGISTRATION OF RECORD: docs/judge_v2_program.md L20817-L20844 (commit 6402b0a), heading "## Registered 2026-09-26
(before any code or call) -- RECORD-RECIPE-EDGE-AUDIT: ...", PART 2. The registration governs. Record:
docs/agents/results/RECORD-RECIPE-EDGE-AUDIT.json.

LAUNCH SEQUENCE
  python tools/analysis/recipe_edge_audit.py --selftest     synthetic only (tempfile): ST1-ST4 of the registration plus
                                                            the refusals, the print branches, and every mutant (all killed)
  python tools/analysis/recipe_edge_audit.py --dry-run      reads the real files: pins, locations, the record sequence,
                                                            the iteration-18 counts against iteration_metrics.csv, the
                                                            first quiet iteration, the bar string, the proposals header,
                                                            the identity check; computes NO birth, split iteration or
                                                            ratio; writes nothing
  python tools/analysis/recipe_edge_audit.py --run          after the READY: the selftest in-process first (refuses if red),
                                                            then WRITE-ONCE (mode "x"; refuses if either exists)
                                                            experiment_results/recipe_edge_audit/recipe_edge_audit_outcome.txt
                                                            experiment_results/recipe_edge_audit/recipe_edge_audit_sites.csv
  Options: --data-root DIR (repeatable; default this checkout, then the main checkout via git's common dir),
           --evidence-dir DIR (default Z:/FAC/TUBerlin/THESIS/TaxoArena_data/evidence_2026-09-25/bareq512_s42_unpinned,
           the orchestrator's archive with SHA256SUMS; build.out is gitignored and the jsonl / diagnostics untracked),
           --out-dir DIR.

POOL: none. First printed line: "pool: none (no DB opened)". Not a pool reader.

INPUTS (each accepted from any candidate location only if the sha256 of its LF rendering equals the pin):
  site_null_bareq512_s42.csv (blob:16aaf5a4 / sha256-lf16:ea0cb19865f63036), dag_snapshots.jsonl (all 18 records;
  blob:ffbbb321 / sha256-lf16:0bf29bbc8c9b10b2), diagnostics/iteration_metrics.csv (blob:035b3fc1 /
  sha256-lf16:5f6c376a9aa2dd70), diagnostics/proposals.csv (blob:25b5381e / sha256-lf16:b59070cdf7ea1ca5; its header
  only, the D3 evidence), bareq512_s42.build.out (blob:b35b1148 / sha256-lf16:7617b28829d0fa16 /
  sha256-crlf16:06f4750f8d6c1302; the "proposalSeparationBar=" configuration string only).

PRECONDITIONS (any failure REFUSES; VOID, never an outcome): the records are iterations 1..18 in order; the
iteration-18 record's node and leaf counts equal iteration_metrics.csv's (158 / 87, also the registered values); the
first iteration with editsDelta 0 is 8 (the registered first quiet iteration; LATE-BORN means split iteration >= 9);
every "proposalSeparationBar=" in build.out reads 0.0145 and line 15 carries it (the registration's READY check; any
other effective bar must be recorded by the READY before a number, so the script refuses rather than choose); the
proposals.csv header is the registered one; the 70 CSV sites are in the iteration-18 record with isLeaf false, the CSV's
depth and k non-bridge children; exactly 10 sites carry cert_site_p95 = true.

DEFINITIONS (registered): BIRTH = the first record containing the node id. SPLIT ITERATION = "the first record from
which its set of non-bridge childIds equals its iteration-18 set". BUILDER'S READING, reported to the registrar: the
phrase admits two readings, (a) the first record at which the set equals the final set, and (b) the first record from
which it equals the final set in EVERY later record; they differ only for a site whose child set reaches its final
form, leaves it and returns. The script computes both and REFUSES if they disagree on any site (the registrar rules);
when they agree the reading does not matter. [RULED 2026-09-26, ruling A6 (orchestrator; recorded at 23f9f00, programme
L20921-L20955; supersedes the refusal above): STABLE-FROM (b) is the SPLIT ITERATION of record and decides late_born and
C1; FIRST-EQUAL (a) is carried in every row as DESCRIPTIVE columns split_iter_first_equal / late_born_first_equal; the
run does NOT refuse on disagreement: every disagreeing site is printed and disclosed. Stable-from is never earlier than
first-equal, so it can only ADD late-born sites.] BAR RATIO = observed_sep / 0.0145 (exact rational); BAR-EDGE iff < 1.05;
the count < 1.10 printed beside; P95 RATIO = observed_sep / site_null_p95. "k" in this script and its output is the
CSV's k, the site's number of children.

CRITERION C1 (a census; the POINT decides): HELD iff none of the 10 cert_site_p95 sites is late-born; FAILED iff at least
one is (listed). D1-D3 DESCRIPTIVE. Predictions P1-P4; falsifier F1.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from fractions import Fraction

BAR_STR = "0.0145"
BAR = Fraction(BAR_STR)
EDGE = Fraction(105, 100)
EDGE2 = Fraction(110, 100)
FIRST_QUIET = 8
LATE_FROM = 9
LAST_ITER = 18
LAST_NODES, LAST_LEAVES = 158, 87
N_SITES, N_CERT = 70, 10
PROPOSALS_HEADER = "iter,type,site_id,site_label,dJ,SE_dJ,z,dV,decision,reason,n_site"
BAR_LINE_NO = 15
P2_POINT, P2_INTERVAL = 2, (2, 4)
P4_POINT, P4_INTERVAL = Fraction(25, 10), (Fraction(2), Fraction(32, 10))

DEFAULT_EVIDENCE_DIR = "Z:/FAC/TUBerlin/THESIS/TaxoArena_data/evidence_2026-09-25/bareq512_s42_unpinned"
OUT_REL = "experiment_results/recipe_edge_audit"
OUT_OUTCOME = "recipe_edge_audit_outcome.txt"
OUT_SITES = "recipe_edge_audit_sites.csv"
POOL_LINE = "pool: none (no DB opened)"
K_HEADER_LINE = ("k in this outcome and in recipe_edge_audit_sites.csv = the site's number of (non-bridge) children, the "
                 "site-null CSV's own k; NOT CERT-RESOLUTION's k (a null exceedance count)")
SITES_COLUMNS = ["node_id", "label", "depth", "n", "k", "birth", "split_iter", "late_born", "split_iter_first_equal",
                 "late_born_first_equal", "observed_sep", "bar_ratio",
                 "p95_ratio", "cert_site_p95"]

B = "experiment_results/promoted/bareq512_s42"
INPUTS = dict(
    csv=dict(rel="experiment_results/promoted/site_null_bareq512_s42.csv", evidence=None,
             lf="ea0cb19865f63036d9e8531bf93192c6c92a831c560bbb5338ef7499a20bb642"),
    jsonl=dict(rel=B + "/seed_42/dag_snapshots.jsonl", evidence="dag_snapshots.jsonl",
               lf="0bf29bbc8c9b10b2349ae6a38ec57247db1bcab0d8bb26e54376caeb47c38e8c"),
    metrics=dict(rel=B + "/seed_42/diagnostics/iteration_metrics.csv", evidence="diagnostics/iteration_metrics.csv",
                 lf="5f6c376a9aa2dd70cbcdd0299eabf4b6b25de4c83327e303a3e11dfe56443fe1"),
    proposals=dict(rel=B + "/seed_42/diagnostics/proposals.csv", evidence="diagnostics/proposals.csv",
                   lf="b59070cdf7ea1ca550922f7d5aa85afefd208155c4af43e34a94755fcc9390d5"),
    buildout=dict(rel="experiment_results/promoted/bareq512_s42.build.out", evidence="bareq512_s42.build.out",
                  lf="7617b28829d0fa160b82d4031e482c2d7fbf042c8a0aa8caf3f70e717b19e3bc"),
)
REGISTERED_LF16 = dict(csv="ea0cb19865f63036", jsonl="0bf29bbc8c9b10b2", metrics="5f6c376a9aa2dd70",
                       proposals="b59070cdf7ea1ca5", buildout="7617b28829d0fa16")   # programme L20768 / L20827-L20829

MUTANT = None
STAT_CALLS = [0]
BRANCH_HITS = set()


class Refusal(Exception):
    pass


def _m(name):
    return MUTANT == name


def _hit(tag):
    BRANCH_HITS.add(tag)


# ------------------------------------------------------------------------------------------------ pins, locations
def pins_of_bytes(raw):
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(), lf=hashlib.sha256(lf).hexdigest(),
                crlf=hashlib.sha256(crlf).hexdigest(), raw_crlf=(raw != lf))


def repo_root():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def main_checkout_of(root):
    try:
        common = subprocess.run(["git", "-C", root, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return os.path.dirname(os.path.normpath(common))
    except Exception:
        return None


def locate(spec, data_roots, evidence_dir, out):
    cands = [os.path.join(r, spec["rel"]) for r in data_roots]
    if spec.get("evidence") and evidence_dir:
        cands.append(os.path.join(evidence_dir, spec["evidence"]))
    for c in cands:
        if not os.path.isfile(c):
            continue
        with open(c, "rb") as fh:
            raw = fh.read()
        p = pins_of_bytes(raw)
        if p["lf"] == spec["lf"] or _m("no_pin_check"):
            return c, raw, p
        out.write("  WARN pin mismatch at %s: sha256-lf16 %s, pinned %s (candidate skipped)\n" % (c, p["lf"][:16], spec["lf"][:16]))
    raise Refusal("REFUSED: no candidate location of %s matches its pin sha256-lf16:%s (tried %s)"
                  % (spec["rel"], spec["lf"][:16], cands))


# ------------------------------------------------------------------------------------------------ parsing, preconditions
def _text(raw):
    return raw.decode("utf-8-sig").replace("\r\n", "\n")


def read_sites(raw):
    rows = list(csv.DictReader(io.StringIO(_text(raw))))
    out = []
    for r in rows:
        if r["cert_site_p95"] not in ("true", "false"):
            raise Refusal("REFUSED: cert_site_p95 %r at %s" % (r["cert_site_p95"], r["node_id"]))
        out.append(dict(node_id=r["node_id"], label=r["label"], depth=int(r["depth"]), n=int(r["n"]), k=int(r["k"]),
                        observed_sep=r["observed_sep"], site_null_p95=r["site_null_p95"], q_site=r["q_site"],
                        cert=(r["cert_site_p95"] == "true")))
    if len({s["node_id"] for s in out}) != len(out):
        raise Refusal("REFUSED: duplicate node_id in the site CSV")
    return out


def read_records(raw):
    recs = [json.loads(line) for line in _text(raw).split("\n") if line.strip()]
    its = [r["iteration"] for r in recs]
    if its != list(range(1, len(recs) + 1)) and not _m("no_contiguity"):
        raise Refusal("REFUSED: dag_snapshots.jsonl iterations are %s, not 1..%d in order" % (its, len(recs)))
    return recs


def read_metrics(raw):
    rows = list(csv.DictReader(io.StringIO(_text(raw))))
    return {int(r["iter"]): r for r in rows}


def first_quiet(metrics):
    q = [i for i in sorted(metrics) if float(metrics[i]["editsDelta"]) == 0.0]
    return q[0] if q else None


def check_structure(recs, metrics, last_iter=LAST_ITER, last_nodes=LAST_NODES, last_leaves=LAST_LEAVES,
                    quiet=FIRST_QUIET):
    last = recs[-1]
    nn = len(last["nodes"])
    nl = sum(1 for n in last["nodes"] if n["isLeaf"])
    it = last["iteration"]
    if it != last_iter:
        raise Refusal("REFUSED: the last record is iteration %s, registered %d" % (it, last_iter))
    mrow = metrics.get(it)
    if not _m("id_no_count"):
        if mrow is None or int(mrow["nodes"]) != nn or int(mrow["leaves"]) != nl:
            raise Refusal("REFUSED: iteration-%d record has %d nodes / %d leaves; iteration_metrics.csv %s"
                          % (it, nn, nl, None if mrow is None else (mrow["nodes"], mrow["leaves"])))
        if (nn, nl) != (last_nodes, last_leaves):
            raise Refusal("REFUSED: iteration-%d counts %d / %d, registered %d / %d" % (it, nn, nl, last_nodes, last_leaves))
    fq = first_quiet(metrics)
    if fq != quiet and not _m("no_quiet_check"):
        raise Refusal("REFUSED: the first iteration with editsDelta 0 is %s, registered %d" % (fq, quiet))
    return nn, nl, fq


def check_bar(raw, bar_str=BAR_STR, line_no=BAR_LINE_NO):
    text = _text(raw)
    lines = text.split("\n")
    vals = []
    key = "proposalSeparationBar="
    for ln in lines:
        i = ln.find(key)
        while i >= 0:
            j = i + len(key)
            v = ""
            while j < len(ln) and (ln[j].isdigit() or ln[j] in ".-eE"):
                v += ln[j]
                j += 1
            vals.append(v)
            i = ln.find(key, j)
    if _m("no_bar_check"):
        return vals
    if not vals or set(vals) != {bar_str}:
        raise Refusal("REFUSED: build.out proposalSeparationBar values %s, not only %s; the READY records the effective bar"
                      % (sorted(set(vals)), bar_str))
    if len(lines) < line_no or (key + bar_str) not in lines[line_no - 1]:
        raise Refusal("REFUSED: build.out line %d does not carry %s%s" % (line_no, key, bar_str))
    return vals


def check_header(raw):
    first = _text(raw).split("\n", 1)[0]
    if first != PROPOSALS_HEADER and not _m("no_header_check"):
        raise Refusal("REFUSED: proposals.csv header %r is not the registered one" % first)
    return first


def identity_check(sites, rec):
    nodes = {n["id"]: n for n in rec["nodes"]}
    fails = []
    for s in sites:
        n = nodes.get(s["node_id"])
        if n is None:
            if not _m("id_no_missing"):
                fails.append("%s missing" % s["node_id"])
            continue
        nb = _nonbridge_children(n, nodes)
        if n["isLeaf"] or n["depth"] != s["depth"] or len(nb) != s["k"]:
            fails.append("%s isLeaf=%s depth %d/%d children %d/%d" % (s["node_id"], n["isLeaf"], n["depth"], s["depth"],
                                                                     len(nb), s["k"]))
    return fails


def _nonbridge_children(n, nodes):
    if _m("bridge_counted"):
        return set(n["childIds"])
    return {c for c in n["childIds"] if not nodes.get(c, {}).get("isBridge", False)}


# ------------------------------------------------------------------------------------------------ the audit
def births(recs):
    STAT_CALLS[0] += 1
    b = {}
    for r in recs:
        for n in r["nodes"]:
            if n["id"] not in b:
                b[n["id"]] = r["iteration"]
    return b


def split_iterations(sites, recs):
    """Both readings of the registered definition; returns {site: (first_equal, stable_from)}."""
    STAT_CALLS[0] += 1
    idx = [{n["id"]: n for n in r["nodes"]} for r in recs]
    final = idx[-1]
    out = {}
    for s in sites:
        v = s["node_id"]
        fin = _nonbridge_children(final[v], final)
        eq = [(v in d and _nonbridge_children(d[v], d) == fin) for d in idx]
        first_equal = next(recs[i]["iteration"] for i, e in enumerate(eq) if e)
        stable = recs[-1]["iteration"]
        for i in range(len(eq) - 1, -1, -1):
            if not eq[i]:
                break
            stable = recs[i]["iteration"]
        out[v] = (first_equal, stable)
    return out


def ratio(a, b):
    STAT_CALLS[0] += 1
    return Fraction(a) / Fraction(b)


def is_late(split_iter, late_from=LATE_FROM):
    if _m("late_strict"):
        return split_iter > late_from
    return split_iter >= late_from


def is_edge(r, edge=EDGE):
    if _m("edge_nonstrict"):
        return r <= edge
    return r < edge


def audit(sites, recs, late_from=LATE_FROM):
    b = births(recs)
    sp = split_iterations(sites, recs)
    # RULING A6 (23f9f00, programme L20921-L20955): STABLE-FROM (index 1) is the split iteration of record and decides
    # late_born and C1; FIRST-EQUAL (index 0) is DESCRIPTIVE; disagreement is printed and disclosed, never refused.
    disagree = [s["node_id"] for s in sites if sp[s["node_id"]][0] != sp[s["node_id"]][1]]
    use = 0 if _m("first_equal_decides") else 1
    rows = []
    for s in sites:
        v = s["node_id"]
        si = sp[v][use]
        fe = sp[v][0]
        br = ratio(s["observed_sep"], BAR)
        pr = ratio(s["observed_sep"], s["site_null_p95"])
        rows.append(dict(node_id=v, label=s["label"], depth=s["depth"], n=s["n"], k=s["k"], birth=b[v], split_iter=si,
                         late_born=is_late(si, late_from), split_iter_first_equal=fe,
                         late_born_first_equal=is_late(fe, late_from), observed_sep=s["observed_sep"], bar_ratio=br,
                         p95_ratio=pr, cert=s["cert"], q_site=s["q_site"]))
    last = recs[-1]
    nodes = {n["id"]: n for n in last["nodes"]}
    sid = {s["node_id"] for s in sites}
    late_nodes = sorted(((it, v) for v, it in b.items() if it >= late_from), key=lambda x: (x[0], x[1]))
    late_list = [(it, v, nodes[v]["parentIds"] if v in nodes else None,
                  [p in sid for p in (nodes[v]["parentIds"] if v in nodes else [])]) for it, v in late_nodes]
    return rows, late_list, disagree


def _f(x, d=4):
    return ("%%.%df" % d) % float(x)


def render_outcome(rows, late_list, header, disagree=()):
    L = list(header)
    cert = [r for r in rows if r["cert"]]
    late = [r for r in rows if r["late_born"]]
    late_cert = [r for r in cert if r["late_born"]]
    L.append("")
    L.append("NODES BORN AT ITERATION >= %d (birth = first record containing the id), with their parents (site?):" % LATE_FROM)
    for it, v, par, is_site in late_list:
        L.append("  iteration %d  %s  parents %s  parent is a site %s" % (it, v, par, is_site))
    L.append("")
    L.append("C1 (the criterion; denominator: the %d cert_site_p95 sites of bareq512_s42, of %d; a census)" % (len(cert), len(rows)))
    if bool(len(late_cert) == 0):
        _hit("C1-HELD")
        c1 = True
        L.append("C1 HELD: none of the %d certified sites is late-born (split iteration >= %d)." % (len(cert), LATE_FROM))
    else:
        _hit("C1-FAILED")
        c1 = False
        L.append("C1 FAILED: %d of the %d certified sites are late-born: %s" % (
            len(late_cert), len(cert), ", ".join("%s %s (split iteration %d)" % (r["node_id"], r["label"], r["split_iter"])
                                                 for r in late_cert)))
    fe_cert = [r for r in cert if r["late_born_first_equal"]]
    L.append("  (DESCRIPTIVE, ruling A6; does not decide) certified sites late-born under the FIRST-EQUAL reading: %d%s"
             % (len(fe_cert), (": " + ", ".join("%s (first-equal %d)" % (r["node_id"], r["split_iter_first_equal"])
                                                 for r in fe_cert)) if fe_cert else ""))
    dis = [r for r in rows if r["node_id"] in set(disagree)]
    if dis:
        _hit("DIS-nonempty")
        L.append("  SPLIT-ITERATION READINGS DISAGREE on %d of %d sites (disclosed; STABLE-FROM decides, ruling A6): %s" % (
            len(dis), len(rows), ", ".join("%s %s stable-from %d / first-equal %d%s" % (
                r["node_id"], r["label"], r["split_iter"], r["split_iter_first_equal"], " [certified]" if r["cert"] else "")
                for r in dis)))
    else:
        _hit("DIS-empty")
        L.append("  SPLIT-ITERATION READINGS DISAGREE on 0 of %d sites (stable-from = first-equal everywhere)." % len(rows))
    L.append("")
    L.append("D1 (DESCRIPTIVE) BAR RATIO = observed_sep / 0.0145 (bar-edge iff < 1.05); P95 RATIO = observed_sep / site_null_p95")
    for r in sorted(cert, key=lambda r: r["bar_ratio"]):
        L.append("  certified %s %-28s depth %d n %d k %d  bar ratio %s  p95 ratio %s" % (
            r["node_id"], r["label"], r["depth"], r["n"], r["k"], _f(r["bar_ratio"]), _f(r["p95_ratio"])))
    for lab, grp in (("certified", cert), ("all", rows)):
        L.append("  %s (%d): bar ratio < 1.05: %d; < 1.10: %d; min %s" % (
            lab, len(grp), sum(1 for r in grp if is_edge(r["bar_ratio"])), sum(1 for r in grp if r["bar_ratio"] < EDGE2),
            _f(min(r["bar_ratio"] for r in grp)) if grp else "n/a"))
    L.append("  STRUCTURAL NOTE (registered): a certified site is bar-edge only if its null p95 lies below 1.05 x 0.0145 = 0.01523; "
             "near-vacuous by construction, hence a readout.")
    L.append("")
    L.append("D2 (DESCRIPTIVE) late-born sites, certified or not:")
    if late:
        _hit("D2-nonempty")
        for r in late:
            L.append("  %s %-28s n %d k %d q_site %s cert_site_p95 %s birth %d split iteration %d" % (
                r["node_id"], r["label"], r["n"], r["k"], r["q_site"], "true" if r["cert"] else "false", r["birth"], r["split_iter"]))
    else:
        _hit("D2-empty")
        L.append("  (none)")
    L.append("")
    L.append("D3 THE K-EDGE HALF: UNDETERMINED BY INSTRUMENT. proposals.csv carries only \"%s\" (no k, no per-k separation); "
             "build.out's Splitter lines carry k and sep per candidate keyed by LABEL (repeated \"Emergent Concept #n\" labels), not "
             "by node id; which k competed at which site is not identifiable without a new engine log line; no criterion "
             "(KSEL-ANCHORED-512, a proposal, is the route)." % PROPOSALS_HEADER)
    L.append("")
    L.append("PREDICTIONS")
    _hit("P1-HELD" if c1 else "P1-FAILED")
    L.append("P1 %s: C1 %s (registered probability 0.80 of HELD)." % ("HELD" if c1 else "FAILED", "HELD" if c1 else "FAILED"))
    nl = len(late)
    ok = P2_INTERVAL[0] <= nl <= P2_INTERVAL[1]
    _hit("P2-HELD" if ok else "P2-FAILED")
    L.append("P2 %s: %d of the %d sites are late-born (point %d, 80%% interval [%d, %d])."
             % ("HELD" if ok else "FAILED", nl, len(rows), P2_POINT, P2_INTERVAL[0], P2_INTERVAL[1]))
    ne = sum(1 for r in cert if is_edge(r["bar_ratio"]))
    ok = ne == 0
    _hit("P3-HELD" if ok else "P3-FAILED")
    L.append("P3 %s: %d of %d certified sites bar-edge (ratio < 1.05); registered 0 (probability 0.95)." % (
        "HELD" if ok else "FAILED", ne, len(cert)))
    mn = min(r["bar_ratio"] for r in cert)
    ok = P4_INTERVAL[0] <= mn <= P4_INTERVAL[1]
    _hit("P4-HELD" if ok else "P4-FAILED")
    L.append("P4 %s: the smallest bar ratio among the certified sites is %s (point 2.5, 80%% interval [2.0, 3.2])."
             % ("HELD" if ok else "FAILED", _f(mn)))
    L.append("")
    L.append("FALSIFIER")
    if not c1:
        _hit("F1-FIRES")
        L.append("F1 FIRES: each late-born certified site carries \"late-born (post-quiescence split, iteration <t>)\" in every "
                 "sentence that names it: %s. No recorded count is revised." % ", ".join(
                     "%s: late-born (post-quiescence split, iteration %d)" % (r["node_id"], r["split_iter"]) for r in late_cert))
    else:
        _hit("F1-NOT")
        L.append("F1 does not fire (C1 HELD). Part 1's facts stand on their own either way.")
    return "\n".join(L) + "\n"


ALL_BRANCHES = {"C1-HELD", "C1-FAILED", "DIS-empty", "DIS-nonempty", "D2-nonempty", "D2-empty", "P1-HELD", "P1-FAILED", "P2-HELD", "P2-FAILED",
                "P3-HELD", "P3-FAILED", "P4-HELD", "P4-FAILED", "F1-FIRES", "F1-NOT"}


# ------------------------------------------------------------------------------------------------ modes
def self_identity():
    with open(os.path.abspath(__file__), "rb") as fh:
        p = pins_of_bytes(fh.read())
    return "script tools/analysis/recipe_edge_audit.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (
        p["blob"][:8], p["lf"][:16], p["crlf"][:16])


def load_and_check(inputs, data_roots, evidence_dir, out, n_sites=N_SITES, n_cert=N_CERT, **kw):
    got = {}
    for key in ("csv", "jsonl", "metrics", "proposals", "buildout"):
        path, raw, p = locate(inputs[key], data_roots, evidence_dir, out)
        out.write("  %-9s %s  blob:%s / sha256-lf16:%s / sha256-crlf16:%s (working file %s)\n"
                  % (key, path, p["blob"][:8], p["lf"][:16], p["crlf"][:16], "CRLF" if p["raw_crlf"] else "LF"))
        got[key] = raw
    sites = read_sites(got["csv"])
    recs = read_records(got["jsonl"])
    metrics = read_metrics(got["metrics"])
    nn, nl, fq = check_structure(recs, metrics, **kw)
    vals = check_bar(got["buildout"])
    hdr = check_header(got["proposals"])
    fails = identity_check(sites, recs[-1])
    if fails:
        raise Refusal("REFUSED (VOID): identity check failed on %d sites: %s" % (len(fails), "; ".join(fails[:10])))
    nc = sum(1 for s in sites if s["cert"])
    if (len(sites) != n_sites or nc != n_cert) and not _m("no_cert10_check"):
        raise Refusal("REFUSED: %d sites / %d certified; registered %d / %d" % (len(sites), nc, n_sites, n_cert))
    out.write("  records: %d (iterations %d..%d in order); last record %d nodes / %d leaves = iteration_metrics.csv; first quiet "
              "iteration (editsDelta 0) = %d, LATE-BORN = split iteration >= %d\n"
              % (len(recs), recs[0]["iteration"], recs[-1]["iteration"], nn, nl, fq, LATE_FROM))
    out.write("  build.out: proposalSeparationBar=%s on every occurrence (%d) and on line %d\n" % (BAR_STR, len(vals), BAR_LINE_NO))
    out.write("  proposals.csv header: %s (the registered one; no k column)\n" % hdr)
    out.write("  identity check: PASS (%d sites in the iteration-%d record, non-leaf, depth and k children match); certified: %d\n"
              % (len(sites), recs[-1]["iteration"], nc))
    return sites, recs


def dry_run(inputs, data_roots, evidence_dir, out, **kw):
    out.write(POOL_LINE + "\n")
    out.write(self_identity() + "\n")
    out.write("DRY-RUN: pins, locations and preconditions only; NO birth, split iteration or ratio on a real row.\n")
    before = STAT_CALLS[0]
    sites, recs = load_and_check(inputs, data_roots, evidence_dir, out, **kw)
    if _m("dryrun_computes") or _m("dryrun_computes_unguarded"):
        births(recs)
    if STAT_CALLS[0] != before and not _m("dryrun_computes_unguarded"):
        raise Refusal("REFUSED: the dry-run evaluated %d statistics on real rows" % (STAT_CALLS[0] - before))
    out.write("DRY-RUN done: 0 statistics evaluated on real rows; nothing written.\n")


def run(inputs, data_roots, evidence_dir, out_dir, out, late_from=LATE_FROM, **kw):
    p_txt, p_csv = os.path.join(out_dir, OUT_OUTCOME), os.path.join(out_dir, OUT_SITES)
    for p in (p_txt, p_csv):
        if os.path.exists(p) and not _m("no_write_once"):
            raise Refusal("REFUSED: %s exists; outcome files of record are write-once" % p)
    hdr = io.StringIO()
    hdr.write(POOL_LINE + "\n" + self_identity() + "\n")
    hdr.write("RECORD-RECIPE-EDGE-AUDIT outcome (Part 2; registration docs/judge_v2_program.md L20817-L20844, 6402b0a). Zero calls.\n")
    hdr.write(K_HEADER_LINE + "\n")
    hdr.write("SPLIT ITERATION of record = STABLE-FROM (ruling A6, 23f9f00); FIRST-EQUAL printed beside it, descriptive.\n")
    hdr.write("INPUTS AND PRECONDITIONS\n")
    sites, recs = load_and_check(inputs, data_roots, evidence_dir, hdr, **kw)
    rows, late_list, disagree = audit(sites, recs, late_from)
    text = render_outcome(rows, late_list, hdr.getvalue().rstrip("\n").split("\n"), disagree)
    os.makedirs(out_dir, exist_ok=True)
    mode = "w" if _m("no_write_once") else "x"
    with open(p_csv, mode, newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SITES_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(dict(node_id=r["node_id"], label=r["label"], depth=r["depth"], n=r["n"], k=r["k"], birth=r["birth"],
                            split_iter=r["split_iter"], late_born="true" if r["late_born"] else "false",
                            split_iter_first_equal=r["split_iter_first_equal"],
                            late_born_first_equal="true" if r["late_born_first_equal"] else "false",
                            observed_sep=r["observed_sep"], bar_ratio=_f(r["bar_ratio"], 6), p95_ratio=_f(r["p95_ratio"], 6),
                            cert_site_p95="true" if r["cert"] else "false"))
    with open(p_txt, mode, newline="\n", encoding="utf-8") as fh:
        fh.write(text)
    out.write(text)
    return rows, late_list, disagree


# ------------------------------------------------------------------------------------------------ selftest
def _node(i, d, leaf, parents, children, bridge=False):
    return dict(id=i, depth=d, isLeaf=leaf, isBridge=bridge, parentIds=parents, childIds=children)


def _four_records():
    """R -> A, B. Records 1-2: A, B leaves (record 2 quiet). Record 3: A splits into A1, A2 (born 3). Record 4 = 3."""
    r1 = [_node("R", 0, False, [], ["A", "B"]), _node("A", 1, True, ["R"], []), _node("B", 1, True, ["R"], [])]
    r3 = [_node("R", 0, False, [], ["A", "B"]), _node("A", 1, False, ["R"], ["A1", "A2"]), _node("B", 1, True, ["R"], []),
          _node("A1", 2, True, ["A"], []), _node("A2", 2, True, ["A"], [])]
    return [dict(iteration=1, nodes=r1), dict(iteration=2, nodes=r1), dict(iteration=3, nodes=r3), dict(iteration=4, nodes=r3)]


def _write_fixture(tmp, recs, sites_rows, metrics_rows, header=PROPOSALS_HEADER, bar_lines=None):
    base = os.path.join(tmp, B)
    os.makedirs(os.path.join(base, "seed_42", "diagnostics"), exist_ok=True)
    with open(os.path.join(base, "seed_42", "dag_snapshots.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    with open(os.path.join(tmp, INPUTS["csv"]["rel"]), "w", encoding="utf-8", newline="") as fh:
        fh.write("snapshot_id,node_id,label,depth,n,k,observed_sep,site_null_p50,site_null_p95,q_site,cert_site_p95,feasibility,reps\r\n")
        for (i, lab, d, n, k, obs, p95, q, cert) in sites_rows:
            fh.write('"S",%s,%s,%d,%d,%d,%s,0.01,%s,%s,%s,OK,300\r\n' % (i, lab, d, n, k, obs, p95, q, "true" if cert else "false"))
    with open(os.path.join(base, "seed_42", "diagnostics", "iteration_metrics.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("iter,nodes,leaves,editsDelta\n")
        for row in metrics_rows:
            fh.write("%d,%d,%d,%s\n" % row)
    with open(os.path.join(base, "seed_42", "diagnostics", "proposals.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n1,GROW,R,root,0.1,0.01,10,2,ACCEPTED,,0\n")
    if bar_lines is None:
        bar_lines = ["x"] * 14 + ["proposalSeparationBar=0.0145, other=1"] + ["Split 'A' (q=9, k=2, sep=0.046)"]
    with open(os.path.join(tmp, INPUTS["buildout"]["rel"]), "w", encoding="utf-8", newline="") as fh:
        fh.write("\r\n".join(bar_lines) + "\r\n")
    specs = {}
    for key, spec in INPUTS.items():
        with open(os.path.join(tmp, spec["rel"]), "rb") as fh:
            specs[key] = dict(spec, lf=pins_of_bytes(fh.read())["lf"])
    return specs


FIX_KW = dict(last_iter=4, last_nodes=5, last_leaves=3, quiet=2)
FIX_SITES = [("R", "root", 0, 100, 2, "0.050000", "0.030000", "0.0000", True),
             ("A", "a", 1, 50, 2, "0.015200", "0.012000", "0.0000", True)]
FIX_METRICS = [(1, 3, 2, "0.1"), (2, 3, 2, "0.0"), (3, 5, 3, "0.001"), (4, 5, 3, "0.0")]


def selftest():
    checks = []
    TMPS = []

    def check(fn):
        checks.append(fn)
        return fn

    def fixture(**kw):
        tmp = tempfile.mkdtemp()
        TMPS.append(tmp)
        return tmp, _write_fixture(tmp, kw.pop("recs", _four_records()), kw.pop("sites", FIX_SITES),
                                   kw.pop("metrics", FIX_METRICS), **kw)

    @check
    def st0_registered_pins():
        for k, v in REGISTERED_LF16.items():
            assert INPUTS[k]["lf"][:16] == v, k

    @check
    def st1_birth_and_split():
        recs = _four_records()
        sites = [dict(node_id="R"), dict(node_id="A")]
        b = births(recs)
        assert b == {"R": 1, "A": 1, "B": 1, "A1": 3, "A2": 3}, b
        sp = split_iterations(sites, recs)
        assert sp == {"R": (1, 1), "A": (3, 3)}, sp
        # a leaf split at record 3 is late-born under a quiet record 2 (late from 3)
        assert is_late(3, 3) and not is_late(2, 3) and is_late(9) and not is_late(8)
        # the two readings disagree when a set reaches its final form, leaves it and returns: NO refusal (ruling A6);
        # STABLE-FROM decides (R: first-equal 1, stable-from 3 -> late-born from 3) and R is listed as disagreeing
        r = _four_records()
        r[1] = dict(iteration=2, nodes=[_node("R", 0, False, [], ["A"]), _node("A", 1, True, ["R"], [])])
        rows, _, dis = audit([dict(node_id="R", label="r", depth=0, n=1, k=2, observed_sep="0.05", site_null_p95="0.03",
                                   q_site="0", cert=True)], r, 3)
        assert dis == ["R"], dis
        assert rows[0]["split_iter"] == 3 and rows[0]["late_born"] is True, rows[0]
        assert rows[0]["split_iter_first_equal"] == 1 and rows[0]["late_born_first_equal"] is False, rows[0]
        t = render_outcome(rows, [], [POOL_LINE], dis)
        assert "C1 FAILED" in t and "DISAGREE on 1 of 1 sites" in t and "R r stable-from 3 / first-equal 1 [certified]" in t
        # bridges are not children
        rb = _four_records()
        rb[3] = dict(iteration=4, nodes=rb[3]["nodes"] + [_node("BR", 2, True, ["A"], [], bridge=True)])
        rb[3]["nodes"][1] = dict(rb[3]["nodes"][1], childIds=["A1", "A2", "BR"])
        assert split_iterations([dict(node_id="A")], rb) == {"A": (3, 3)}

    @check
    def st1b_run_end_to_end():
        tmp, specs = fixture()
        od = os.path.join(tmp, "out")
        rows, late, dis = run(specs, [tmp], None, od, io.StringIO(), late_from=3, n_sites=2, n_cert=2, **FIX_KW)
        assert dis == []
        d = {r["node_id"]: r for r in rows}
        assert d["A"]["late_born"] and not d["R"]["late_born"] and d["A"]["split_iter"] == 3
        assert [v for _, v, _, _ in late] == ["A1", "A2"]
        with open(os.path.join(od, OUT_SITES), encoding="utf-8") as fh:
            assert fh.readline().strip().split(",") == SITES_COLUMNS
        with open(os.path.join(od, OUT_OUTCOME), encoding="utf-8") as fh:
            t = fh.read()
        assert K_HEADER_LINE in t and "DISAGREE on 0 of 2 sites" in t
        assert t.startswith(POOL_LINE) and "C1 FAILED" in t and "A: late-born (post-quiescence split, iteration 3)" in t
        try:
            run(specs, [tmp], None, od, io.StringIO(), late_from=3, n_sites=2, n_cert=2, **FIX_KW)
            raise AssertionError("second run overwrote an outcome of record")
        except Refusal:
            pass

    @check
    def st2_identity_and_counts():
        recs = _four_records()
        ok = [dict(node_id="A", depth=1, k=2)]
        assert identity_check(ok, recs[-1]) == []
        assert identity_check([dict(node_id="Z", depth=1, k=2)], recs[-1])
        assert identity_check([dict(node_id="A", depth=1, k=3)], recs[-1])
        assert identity_check([dict(node_id="B", depth=1, k=0)], recs[-1])        # a leaf
        m = {1: dict(nodes="3", leaves="2", editsDelta="0.1"), 2: dict(nodes="3", leaves="2", editsDelta="0"),
             3: dict(nodes="5", leaves="3", editsDelta="1e-3"), 4: dict(nodes="5", leaves="3", editsDelta="0")}
        check_structure(recs, m, **FIX_KW)
        for bad in ({**m, 4: dict(nodes="6", leaves="3", editsDelta="0")},
                    {**m, 4: dict(nodes="5", leaves="4", editsDelta="0")}):
            try:
                check_structure(recs, bad, **FIX_KW)
                raise AssertionError("count mismatch accepted")
            except Refusal:
                pass
        try:
            check_structure(recs, {**m, 2: dict(nodes="3", leaves="2", editsDelta="0.2")}, **FIX_KW)
            raise AssertionError("first-quiet mismatch accepted")
        except Refusal:
            pass
        try:
            read_records(("\n".join(json.dumps(r) for r in [recs[0], recs[2]]) + "\n").encode())
            raise AssertionError("non-contiguous records accepted")
        except Refusal:
            pass
        # end to end: a missing node refuses (VOID) at load
        tmp, specs = fixture(sites=FIX_SITES + [("Q", "q", 1, 5, 2, "0.03", "0.02", "0.0", False)])
        try:
            load_and_check(specs, [tmp], None, io.StringIO(), n_sites=3, n_cert=2, **FIX_KW)
            raise AssertionError("missing node accepted")
        except Refusal:
            pass
        tmp, specs = fixture()
        try:
            load_and_check(specs, [tmp], None, io.StringIO(), n_sites=2, n_cert=1, **FIX_KW)
            raise AssertionError("certified count mismatch accepted")
        except Refusal:
            pass

    @check
    def st3_bar_ratio():
        r = ratio("0.015200", BAR)
        assert r == Fraction(152, 145) and is_edge(r) and r < EDGE2               # 1.0483
        assert not is_edge(ratio("0.015225", BAR))                                # exactly 1.05: not < 1.05
        r2 = ratio("0.015900", BAR)
        assert not is_edge(r2) and r2 < EDGE2                                     # 1.0966
        assert not ratio("0.016000", BAR) < EDGE2                                # 1.1034
        assert ratio("0.0435", BAR) == 3

    @check
    def st3b_bar_string_and_header():
        tmp, specs = fixture(bar_lines=["x"] * 14 + ["proposalSeparationBar=0.0145"] + ["proposalSeparationBar=0.02"])
        try:
            load_and_check(specs, [tmp], None, io.StringIO(), n_sites=2, n_cert=2, **FIX_KW)
            raise AssertionError("a second bar accepted")
        except Refusal:
            pass
        tmp, specs = fixture(bar_lines=["x"] * 20)
        try:
            load_and_check(specs, [tmp], None, io.StringIO(), n_sites=2, n_cert=2, **FIX_KW)
            raise AssertionError("no bar string accepted")
        except Refusal:
            pass
        tmp, specs = fixture(header=PROPOSALS_HEADER + ",k")
        try:
            load_and_check(specs, [tmp], None, io.StringIO(), n_sites=2, n_cert=2, **FIX_KW)
            raise AssertionError("a different proposals header accepted")
        except Refusal:
            pass

    @check
    def st4_dryrun_and_pins():
        tmp, specs = fixture()
        buf = io.StringIO()
        before = STAT_CALLS[0]
        dry_run(specs, [tmp], None, buf, n_sites=2, n_cert=2, **FIX_KW)
        assert STAT_CALLS[0] == before, "dry-run computed statistics"
        t = buf.getvalue()
        assert t.startswith(POOL_LINE) and "bar ratio" not in t and "C1 " not in t and "late-born:" not in t
        bad = dict(specs, jsonl=dict(specs["jsonl"], lf="0" * 64))
        try:
            dry_run(bad, [tmp], None, io.StringIO(), n_sites=2, n_cert=2, **FIX_KW)
            raise AssertionError("pin mismatch accepted")
        except Refusal:
            pass
        # the evidence-dir location is accepted when the data root lacks the file
        ev = tempfile.mkdtemp()
        TMPS.append(ev)
        os.makedirs(os.path.join(ev, "diagnostics"))
        shutil.copy(os.path.join(tmp, specs["jsonl"]["rel"]), os.path.join(ev, "dag_snapshots.jsonl"))
        os.remove(os.path.join(tmp, specs["jsonl"]["rel"]))
        dry_run(specs, [tmp], ev, io.StringIO(), n_sites=2, n_cert=2, **FIX_KW)

    @check
    def st5_branches():
        BRANCH_HITS.clear()

        def row(v, late, cert, br):
            return dict(node_id=v, label=v, depth=1, n=10, k=2, birth=1, split_iter=9 if late else 1, late_born=late,
                        split_iter_first_equal=1, late_born_first_equal=False, observed_sep="0.04", bar_ratio=Fraction(br), p95_ratio=Fraction(2), cert=cert, q_site="0.0000")
        a = [row("a", False, True, "2.5"), row("b", True, False, "1.2"), row("c", True, False, "1.1")]
        b = [row("a", True, True, "1.01"), row("b", False, False, "1.2")]
        c = [row("a", False, True, "9")]
        ta = render_outcome(a, [], [POOL_LINE])
        tb = render_outcome(b, [(9, "x", ["a"], [True])], [POOL_LINE], ["a"])
        render_outcome(c, [], [POOL_LINE])
        missing = ALL_BRANCHES - BRANCH_HITS
        assert not missing, "print branches never executed: %s" % sorted(missing)
        assert "C1 HELD" in ta and "F1 does not fire" in ta and "P2 HELD" in ta and "P4 HELD" in ta
        assert "C1 FAILED" in tb and "F1 FIRES" in tb and "P3 FAILED" in tb and "UNDETERMINED BY INSTRUMENT" in tb

    results = []
    for fn in checks:
        try:
            fn()
            results.append((fn.__name__, None))
        except Exception as e:                                  # noqa: BLE001
            results.append((fn.__name__, "%s: %s" % (type(e).__name__, e)))
    for t in TMPS:
        shutil.rmtree(t, ignore_errors=True)
    return results


MUTANTS = ["no_pin_check", "no_contiguity", "id_no_count", "no_quiet_check", "no_bar_check", "no_header_check",
           "id_no_missing", "bridge_counted", "first_equal_decides", "late_strict", "edge_nonstrict", "no_cert10_check",
           "dryrun_computes", "dryrun_computes_unguarded", "no_write_once"]


def run_selftest(out):
    global MUTANT
    MUTANT = None
    base = selftest()
    nfail = sum(1 for _, e in base if e)
    for n, e in base:
        out.write("  %-32s %s\n" % (n, "PASS" if e is None else "FAIL " + e))
    out.write("SELFTEST: %d checks, %d failed\n" % (len(base), nfail))
    killed, survived = [], []
    for mu in MUTANTS:
        MUTANT = mu
        try:
            r = selftest()
        finally:
            MUTANT = None
        bad = [n for n, e in r if e]
        (killed if bad else survived).append((mu, bad))
    for mu, bad in killed:
        out.write("  mutant %-26s KILLED by %s\n" % (mu, ", ".join(bad)))
    for mu, _ in survived:
        out.write("  mutant %-26s SURVIVED\n" % mu)
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
        sys.exit(0 if run_selftest(sys.stdout) else 1)
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
            dry_run(INPUTS, roots, a.evidence_dir, buf)
            sys.stdout.write(buf.getvalue().split("\n", 1)[1])
        else:
            buf = io.StringIO()
            if not run_selftest(buf):
                sys.stdout.write(buf.getvalue())
                raise Refusal("REFUSED: selftest red (checks or mutants)")
            run(INPUTS, roots, a.evidence_dir, a.out_dir or os.path.join(repo_root(), OUT_REL), sys.stdout)
    except Refusal as e:
        if a.dry_run:
            sys.stdout.write(buf.getvalue().split("\n", 1)[-1])      # what was verified before the refusal
        print(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
