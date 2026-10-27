"""leaf_routing: the primary (maximum-weight) leaf of every reserved question, read from a routeReserved
`<tree>_reserved_leaf_assignments.csv` whose weight column is written with a DECIMAL COMMA.

QUEUE ITEM RUBRIC512-ROUTING-DECIMAL-COMMA (engineering; zero calls; no pool read; no DB opened). Recorded at
docs/judge_v2_program.md, section "## CERT-UNDER-FILTER (2026-09-23, 0 judge calls) ...", DEFECTS RECORDED, D-8
(review 605675c), verbatim: "`rubric_512.primary_routing` reads the decimal-comma weight of
bareq512_s42_reserved_leaf_assignments.csv (unquoted "0,000000") as its integer part and falls back to file order;
correct here only because the file-first leaf equals the maximum-weight leaf on all 410 multi-row qids (the cache's
anchor column agrees on 9,142 of 9,142 rows)." The queue's READY ask: routing byte-identical on bareq512_s42 before /
after; a synthetic unsorted file routed by weight, not by file order.

THE DEFECT. The routeReserved writer emits `weight` with a locale decimal comma and does not quote it, so a 6-column
header carries 7-field rows: "552,"Business",n00000219,"...",0,000000,1". csv.DictReader then puts the integer part
("0", "-0", "-1") under `weight`, the fraction under `n_leaves`, and the true n_leaves under the restkey None.
rubric_512.primary_routing compares `float("-0")` = -0.0 with `float("0")` = 0.0 (not greater), so every tie and every
negative fraction falls back to FILE ORDER. On the three promoted files the writer put the maximum-weight leaf first
(the --check below proves it), so no recorded routing moves.

WHY A NEW MODULE AND NOT AN EDIT TO rubric_512.py. rubric_512.py is BLOB-PINNED (blob 81ae1d39...) by
tools/analysis/split_exposure_child.py (ROUTE_A_SPECS["RUBRIC-512"], checked before import, refused on mismatch) and
tools/analysis/split_exposure_sensitivity.py (CONSUMERS["RUBRIC-512"]); any byte change makes those replays of record
refuse (KNOWLEDGE.md "Temp files and destructive code": pinned scripts are not edited). Whether to edit rubric_512.py
(and re-pin) or to migrate its 40+ importers to this module is the orchestrator's call; this module is the corrected
reader plus the proof that the legacy reader is right on every file that exists.

THE READING (fixed here). Header must equal HEADER exactly. A 6-field row: weight = float(field 5 with "," -> ".").
A 7-field row: weight = float(whole + "." + frac) where whole matches [+-]?digits and frac matches digits; the STRING
concatenation keeps the sign of "-0,56" (= -0.56; a numeric whole + frac / 10**k would give +0.56). Any other field
count, a non-numeric part, or a non-integer n_leaves REFUSES (ValueError naming the line). An empty body refuses.
Primary leaf = maximum weight; a TIE keeps the first row in file order (strict >), exactly the legacy tie rule.

THE COUNT CHECK (--check). Per file: rows, field-count histogram, qids, multi-row qids, how many multi-row qids have
the file-first leaf equal to the maximum-weight leaf, and whether this reader's routing equals the legacy
rubric_512.primary_routing on every qid (printed with the sha256 of each routing's canonical JSON). On bareq512_s42 the
registration expects 410 multi-row qids, 410 of 410 agreeing, routing identical.

  python tools/analysis/leaf_routing.py --check [bareq512_s42 abt2d512_s42 ...]   (default: every promoted file)
  python tools/analysis/leaf_routing.py --selftest      (sandbox files under scratch_dir; asserts printed values)

MUTANTS (run by hand against --selftest, each a temporary edit, reverted; the selftest must fail):
  M1 max -> min (w > best  ->  w < best)                                   killed (unsorted fixture routes by max)
  M2 tie rule strict > -> >=  (last tie wins)                              killed (tie fixture keeps file-first)
  M3 numeric join float(whole) + float(frac)/10**k (sign lost on "-0,x")   killed (sign fixture)
  M4 legacy reading (integer part only: weight = float(row[4]))            killed (unsorted fixture)
  M5 7-field branch drops n_leaves check (int(row[6]) skipped)             killed (bad-n_leaves refusal)
  M6 8-field row accepted (len >= 7 instead of == 7)                       killed (8-field refusal)
  M7 empty body returns {} instead of refusing                             killed (empty refusal)
  M8 --check counts agreement on ALL qids instead of multi-row qids        killed (printed "multi-row 2, first==max 1 of 2")
  M9 --check compares against itself instead of the legacy reader          killed (printed "IDENTICAL: False" on the fixture)
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PROMOTED = os.path.join(ROOT, "experiment_results", "promoted")
HEADER = ["question_id", "category", "leaf_id", "leaf_label", "weight", "n_leaves"]
_WHOLE = re.compile(r"[+-]?\d+")
_FRAC = re.compile(r"\d+")
SUFFIX = "_reserved_leaf_assignments.csv"


def path_for(tree_or_path):
    if tree_or_path.endswith(".csv") or os.sep in tree_or_path or "/" in tree_or_path:
        return tree_or_path
    return os.path.join(PROMOTED, tree_or_path + SUFFIX)


def parse_rows(path):
    """Every data row as a dict; refuses any row this reading cannot place (ValueError naming the line)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        header = next(rd, None)
        if header != HEADER:
            raise ValueError("[LEAF-ROUTING] %s: header %r != %r: REFUSED" % (path, header, HEADER))
        for line_no, r in enumerate(rd, start=2):
            if len(r) == 6:
                try:
                    w = float(r[4].replace(",", "."))
                    n = int(r[5])
                except ValueError:
                    raise ValueError("[LEAF-ROUTING] %s line %d: weight %r / n_leaves %r not numeric: REFUSED" % (path, line_no, r[4], r[5]))
            elif len(r) == 7:
                whole, frac = r[4], r[5]
                if not (_WHOLE.fullmatch(whole) and _FRAC.fullmatch(frac)):
                    raise ValueError("[LEAF-ROUTING] %s line %d: decimal-comma weight %r,%r is not <int>,<digits>: REFUSED" % (path, line_no, whole, frac))
                w = float(whole + "." + frac)
                try:
                    n = int(r[6])
                except ValueError:
                    raise ValueError("[LEAF-ROUTING] %s line %d: n_leaves %r not an integer: REFUSED" % (path, line_no, r[6]))
            else:
                raise ValueError("[LEAF-ROUTING] %s line %d: %d fields (6, or 7 with a decimal-comma weight, expected): REFUSED" % (path, line_no, len(r)))
            rows.append({"question_id": int(r[0]), "category": r[1], "leaf_id": r[2], "leaf_label": r[3], "weight": w,
                         "n_leaves": n, "fields": len(r), "line": line_no})
    if not rows:
        raise ValueError("[LEAF-ROUTING] %s: no data rows: REFUSED" % path)
    return rows


def _route(rows):
    best = {}
    for r in rows:
        q, w = r["question_id"], r["weight"]
        if q not in best or w > best[q][0]:
            best[q] = (w, r["leaf_id"])
    return {q: v[1] for q, v in best.items()}


def primary_routing(tree_or_path):
    """{question_id: leaf_id} by maximum weight, ties to the first row in file order."""
    return _route(parse_rows(path_for(tree_or_path)))


def routing_sha(route):
    return hashlib.sha256(json.dumps(sorted(route.items()), separators=(",", ":")).encode()).hexdigest()[:16]


def legacy_routing(path):
    """rubric_512.primary_routing's reading of `path`, called UNEDITED (its PROMOTED dir pointed at the file's dir)."""
    sys.path.insert(0, HERE)
    import rubric_512 as r512
    d, base = os.path.split(os.path.abspath(path))
    if not base.endswith(SUFFIX):
        raise ValueError("[LEAF-ROUTING] legacy reader needs a <tree>%s file, got %s" % (SUFFIX, base))
    saved = r512.PROMOTED
    try:
        r512.PROMOTED = d
        return r512.primary_routing(base[: -len(SUFFIX)])
    finally:
        r512.PROMOTED = saved


def routing_check(path):
    rows = parse_rows(path)
    by_q = {}
    for r in rows:
        by_q.setdefault(r["question_id"], []).append(r)
    route = _route(rows)
    multi = {q: rs for q, rs in by_q.items() if len(rs) > 1}
    first_eq = sum(1 for q, rs in multi.items() if rs[0]["leaf_id"] == route[q])
    legacy = legacy_routing(path)
    diff = sorted(q for q in set(route) | set(legacy) if route.get(q) != legacy.get(q))
    return {"rows": len(rows), "fields": dict(sorted(Counter(r["fields"] for r in rows).items())), "qids": len(by_q),
            "multi": len(multi), "first_eq_max": first_eq, "identical": not diff, "n_diff": len(diff), "diff_first": diff[:5],
            "sha_new": routing_sha(route), "sha_legacy": routing_sha(legacy)}


def print_check(path):
    r = routing_check(path)
    print("[LEAF-ROUTING] %s" % os.path.basename(path))
    print("  rows %d | field counts %s | qids %d | multi-row qids %d | file-first leaf == max-weight leaf on %d of %d"
          % (r["rows"], r["fields"], r["qids"], r["multi"], r["first_eq_max"], r["multi"]))
    print("  routing by weight vs legacy rubric_512.primary_routing: IDENTICAL: %s (differing qids %d%s) | sha16 new %s legacy %s"
          % (bool(r["identical"]), r["n_diff"], (", first %s" % r["diff_first"]) if r["n_diff"] else "", r["sha_new"], r["sha_legacy"]))
    return r


# ---------------------------------------------------------------------------------------------------- selftest
def _write(d, tree, lines):
    p = os.path.join(d, tree + SUFFIX)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines) + "\n")
    return p


H = "question_id,category,leaf_id,leaf_label,weight,n_leaves"


def selftest():
    import io
    import contextlib
    import scratch_dir
    with scratch_dir.scratch("leafrouting_") as d:
        # (1) unsorted: the max-weight leaf B is SECOND in file order; legacy routes A, this module B
        p = _write(d, "unsorted", [H, '1,"X",nA,"leaf A",-0,560441,2', '1,"X",nB,"leaf B",0,000000,2', '2,"X",nC,"leaf C",0,000000,1'])
        assert primary_routing(p) == {1: "nB", 2: "nC"}, primary_routing(p)
        assert legacy_routing(p) == {1: "nA", 2: "nC"}, legacy_routing(p)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = print_check(p)
        out = buf.getvalue()
        assert "multi-row qids 1 | file-first leaf == max-weight leaf on 0 of 1" in out, out
        assert "IDENTICAL: False (differing qids 1, first [1])" in out, out
        assert r["fields"] == {7: 3}
        # (2) sign: -0,9 vs -0,1 -> max is -0.1 (second row); a numeric whole+frac join would read +0.9 and pick the first
        p = _write(d, "sign", [H, '5,"X",n1,"a",-0,900000,2', '5,"X",n2,"b",-0,100000,2'])
        assert primary_routing(p) == {5: "n2"}, primary_routing(p)
        assert parse_rows(p)[0]["weight"] == -0.9
        # (3) tie: two equal weights -> the file-first row
        p = _write(d, "tie", [H, '7,"X",nF,"a",0,000000,2', '7,"X",nL,"b",0,000000,2'])
        assert primary_routing(p) == {7: "nF"}
        # (4) dot-decimal 6-field rows are read too; mixed with 7-field rows
        p = _write(d, "dot", [H, '8,"X",n1,"a",-0.25,2', '8,"X",n2,"b",-0,100000,2', '9,"X",n3,"c, with comma",1.5,1'])
        assert primary_routing(p) == {8: "n2", 9: "n3"}, primary_routing(p)
        assert [x["fields"] for x in parse_rows(p)] == [6, 7, 6]
        # (5) refusals, each by its message
        for tree, lines, needle in (
                ("f8", [H, '1,"X",n,"a",0,0,0,1'], "8 fields"),
                ("frac", [H, '1,"X",n,"a",0,abc,1'], "is not <int>,<digits>"),
                ("nl", [H, '1,"X",n,"a",0,500000,x'], "n_leaves 'x' not an integer"),
                ("hdr", ["question_id,category,leaf_id,leaf_label,weight", '1,"X",n,"a",0'], "header"),
                ("empty", [H], "no data rows")):
            p = _write(d, tree, lines)
            try:
                primary_routing(p)
            except ValueError as e:
                assert needle in str(e), (tree, str(e))
            else:
                raise AssertionError("no refusal for %s" % tree)
        # (6) the count check counts MULTI-ROW qids only; identical when the file is max-first
        p = _write(d, "sorted", [H, '1,"X",nA,"a",0,000000,2', '1,"X",nB,"b",-0,300000,2',
                                 '2,"X",nC,"c",-0,500000,2', '2,"X",nD,"d",0,000000,2', '3,"X",nE,"e",0,000000,1'])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_check(p)
        out = buf.getvalue()
        assert "qids 3 | multi-row qids 2 | file-first leaf == max-weight leaf on 1 of 2" in out, out
        assert "IDENTICAL: False (differing qids 1, first [2])" in out, out
        p = _write(d, "maxfirst", [H, '1,"X",nA,"a",0,000000,2', '1,"X",nB,"b",-0,300000,2', '3,"X",nE,"e",0,000000,1'])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            print_check(p)
        out = buf.getvalue()
        assert "on 1 of 1" in out and "IDENTICAL: True (differing qids 0)" in out, out
    print("selftest OK (unsorted / sign / tie / dot-decimal / 5 refusals / count check; legacy reader called unedited)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", nargs="*", metavar="TREE_OR_CSV")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.check is None:
        ap.error("--check [trees] or --selftest")
    targets = a.check or sorted(os.path.join(PROMOTED, f) for f in os.listdir(PROMOTED) if f.endswith(SUFFIX))
    for t in targets:
        print_check(path_for(t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
