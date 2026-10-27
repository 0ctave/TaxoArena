"""DATASET-SURVEY (docs/judge_v2_program.md L21774-L21788, "## Registered 2026-09-27 (before any code or call) - DATASET-SURVEY",
registered at a357ef0 before any code; plan RP10, DS-0). ZERO calls; no model-result file content is read by this tool, no key,
never the SuperGPQA Records' aggregate JSON (plan B8; SUPERGPQA-STAGE0's seal). It is precondition B2 of SUPERGPQA-STAGE0b.

WHAT IT IS (the minimal build; the orchestrator's instruction "keep it small"): the data-steward fills the admission table
(one row per candidate x column, each cell with its status and its SOURCE: URL + retrieval date + sha256 of the fetched metadata
bytes, or the count command; or an UNVERIFIED reason); this tool VALIDATES the table, scores C1 / C2 / P1-P7 / F1 exactly as
registered, and writes the outcome of record write-once. It fetches nothing and decides no cell.

TABLE (CSV, UTF-8, header exactly): candidate,column,status,value,source,reason
  legs (ADMISSION; status PASS / FAIL / UNVERIFIED): models (>= 20 complete models), support (>= 120 EVAL items per scored
    stratum at the registered 0.30 EVAL share; value = the number of strata >= 120), closure (closable under CK-CLOSE-v1 with a
    stem_key collision check), key (an answer key or an executed checker), licence (a stated licence)
  reported (status REPORTED / UNVERIFIED; never an admission leg): scoring_protocol, metric_granularity, cot_extraction,
    dominance (REPORTED only: admitting on it would select on SQ1's dependent variable)
  A cell with status UNVERIFIED needs a reason; every other cell needs a source.

CRITERIA (registered): C1 COMPLETENESS HELD iff every cell of every candidate row carries a source or an UNVERIFIED reason;
FAILED otherwise. C2 per candidate: ADMIT iff every leg PASSES; REFUSE-by-<leg> iff any leg FAILS; UNVERIFIED iff no leg fails
and one is UNVERIFIED. Readings (stated): a missing cell counts as a C1 failure and as UNVERIFIED in C2; the REFUSE label names
every failing leg in the registered leg order; P5's "at most 3 categories >= 120 EVAL" reads the support cell's value.
[DELTA 2026-09-29, the engine-coder, READY_w0_delta1 C11-2; insertion only] VALUE AGAINST STATUS on the two numeric legs: a
PASS or FAIL cell of `models` or `support` must carry an integer value, and the status must be what the value implies
(models: PASS iff value >= MIN_MODELS = 20; support: PASS iff value >= MIN_STRATA = 1, the value being the number of strata
with >= 120 EVAL items at the 0.30 EVAL share, so the registered per-stratum floor is inside the count); otherwise the TABLE
is REFUSED (nothing scored, nothing written). A candidate is admitted on values, never on a status word alone (reviewer
witness Y-DS1: models 12 and support 0 marked PASS). UNVERIFIED cells carry no value check (a reason is required).

  python tools/analysis/dataset_survey.py --selftest            # synthetic tables; every branch executed; mutants killed
  python tools/analysis/dataset_survey.py --template PATH       # an empty table skeleton for the data-steward (not a record)
  python tools/analysis/dataset_survey.py --analyze TABLE.csv   # validate + score; experiment_results/dataset_survey/
                                                                #   dataset_survey_outcome.txt and dataset_survey_table.csv, WRITE-ONCE
"""
import argparse
import csv
import hashlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TAG = "[DATASET-SURVEY]"
REGISTRATION = "docs/judge_v2_program.md L21774-L21788 (registered at a357ef0)"
LEGS = ("models", "support", "closure", "key", "licence")
REPORTED = ("scoring_protocol", "metric_granularity", "cot_extraction", "dominance")
COLUMNS = LEGS + REPORTED
HEADER = ["candidate", "column", "status", "value", "source", "reason"]
CANDIDATES = ("SuperGPQA", "HELM Capabilities v1.15.0", "RouterEval / OLL-v2", "BFCL-Result full", "BigCodeBench-perf",
              "EmbedLLM (positioning only)", "RouterBench (positioning only)", "LiveBench", "agent corpora",
              "MMLU-Pro (inventory)", "OLL-v2 union (inventory)", "LCB v6 (inventory)", "20NG (inventory)",
              "BFCL multi_turn (inventory)", "Multi-SWE (inventory)")
OUT_DIR = os.path.join(ROOT, "experiment_results", "dataset_survey")
MIN_MODELS = 20          # registered: >= 20 complete models
MIN_STRATA = 1           # registered: >= 120 EVAL items per scored stratum; value = number of such strata; >= 1 to admit
NUMERIC_BAR = {"models": MIN_MODELS, "support": MIN_STRATA}
MUTANT = None


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def read_table(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != HEADER:
        refuse("the table's header must be exactly %s" % ",".join(HEADER))
    cells = {}
    for r in rows[1:]:
        if not any(x.strip() for x in r):
            continue
        if len(r) != len(HEADER):
            refuse("a row has %d fields, not %d: %r" % (len(r), len(HEADER), r))
        d = dict(zip(HEADER, [x.strip() for x in r]))
        if d["candidate"] not in CANDIDATES:
            refuse("unknown candidate %r (the registered list only)" % d["candidate"])
        if d["column"] not in COLUMNS:
            refuse("unknown column %r" % d["column"])
        k = (d["candidate"], d["column"])
        if k in cells:
            refuse("duplicate cell %s" % (k,))
        ok = ("PASS", "FAIL", "UNVERIFIED") if d["column"] in LEGS else ("REPORTED", "UNVERIFIED")
        if d["status"] not in ok:
            refuse("cell %s status %r is not one of %s" % (k, d["status"], ok))
        if d["column"] in NUMERIC_BAR and d["status"] in ("PASS", "FAIL") and MUTANT != "status_trusted":
            v = _int(d["value"])
            if v is None or str(v) != d["value"]:
                refuse("cell %s: a %s status needs an integer value (got %r)" % (k, d["status"], d["value"]))
            implied = "PASS" if v >= NUMERIC_BAR[d["column"]] else "FAIL"
            if implied != d["status"]:
                refuse("cell %s: status %s contradicts its value %d (bar >= %d implies %s); the table is refused"
                       % (k, d["status"], v, NUMERIC_BAR[d["column"]], implied))
        cells[k] = d
    return cells


def cell_complete(d):
    if d is None:
        return False
    if d["status"] == "UNVERIFIED":
        return bool(d["reason"])
    return bool(d["source"]) if MUTANT != "source_not_required" else True


def c1(cells):
    missing = [(c, col) for c in CANDIDATES for col in COLUMNS if not cell_complete(cells.get((c, col)))]
    return (not missing), missing


def c2(cells, cand):
    st = {leg: (cells.get((cand, leg)) or {}).get("status", "UNVERIFIED") for leg in LEGS}
    failed = [leg for leg in LEGS if st[leg] == "FAIL"]
    if failed:
        return "REFUSE-by-" + "+".join(failed), st
    if any(st[leg] == "UNVERIFIED" for leg in LEGS) and MUTANT != "unverified_admits":
        return "UNVERIFIED", st
    return "ADMIT", st


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def render(cells):
    L = ["pool - (DATASET-SURVEY: no pool; a census of public metadata; zero calls; no key; no model-result content)",
         "%s | registration %s" % (TAG, REGISTRATION), ""]
    ok1, missing = c1(cells)
    L.append("ADMISSION TABLE (legs %s; reported, never admission: %s):" % (", ".join(LEGS), ", ".join(REPORTED)))
    words = {}
    for cand in CANDIDATES:
        w, st = c2(cells, cand)
        words[cand] = (w, st)
        L.append("  %-34s %-26s %s" % (cand, w, " ".join("%s=%s" % (leg, st[leg]) for leg in LEGS)))
    L.append("")
    L.append("C1 COMPLETENESS: %s (%d of %d cells carry a source or an UNVERIFIED reason)%s"
             % ("HELD" if ok1 else "FAILED", len(CANDIDATES) * len(COLUMNS) - len(missing), len(CANDIDATES) * len(COLUMNS),
                "" if ok1 else "; missing or unsourced: " + "; ".join("%s/%s" % m for m in missing[:12])))
    L.append("C2 ADMISSION per candidate: printed in the table above (recorded per row).")
    L.append("PREDICTIONS (priors as registered; HELD / FAILED):")

    def adm(c):
        return words[c][0]
    lic = lambda c: words[c][1]["licence"]
    sup_v = _int((cells.get(("BFCL-Result full", "support")) or {}).get("value"))
    preds = [
        ("P1 SuperGPQA ADMITS on every pre-key leg (0.85)", adm("SuperGPQA") == "ADMIT"),
        ("P2 BigCodeBench-perf REFUSED or UNVERIFIED on licence (0.70)", lic("BigCodeBench-perf") in ("FAIL", "UNVERIFIED")),
        ("P3 HELM UNVERIFIED on licence (0.60)", lic("HELM Capabilities v1.15.0") == "UNVERIFIED"),
        ("P4 LiveBench REFUSED on support (0.90)", words["LiveBench"][1]["support"] == "FAIL"),
        ("P5 BFCL-Result ADMITS with at most 3 categories >= 120 EVAL (0.70; value %s)" % sup_v,
         adm("BFCL-Result full") == "ADMIT" and sup_v is not None and sup_v <= 3),
        ("P6 RouterEval ADMITS (0.85)", adm("RouterEval / OLL-v2") == "ADMIT"),
        ("P7 C1 HELD (0.85)", ok1),
    ]
    for text, v in preds:
        L.append("  %s: %s" % (text, "HELD" if bool(v) else "FAILED"))
    f1 = adm("SuperGPQA").startswith("REFUSE")
    if f1 and MUTANT != "f1_never":
        L.append("F1 FIRES: SuperGPQA REFUSED (%s) -> SUPERGPQA-STAGE0(b) does not run; the second-corpus clause becomes a sourced "
                 "limit (it overturns the author-scoped plan item, not a recorded result)." % adm("SuperGPQA"))
    else:
        L.append("F1 does not fire (SuperGPQA: %s)%s." % (adm("SuperGPQA"), "" if adm("SuperGPQA") == "ADMIT" else
                                                           "; an UNVERIFIED row is not an admission (the STAGE0b precondition stays unmet)"))
    L.append("SUPPORT: (a) a census of %d candidate rows x %d columns; (b)-(e) not applicable (a census); (f) SCOREABLE; (g) a licence "
             "leg can be UNVERIFIABLE at any budget; UNVERIFIED is a registered outcome, never read as PASS." % (len(CANDIDATES), len(COLUMNS)))
    return L, dict(c1=ok1, words={k: v[0] for k, v in words.items()}, preds=[bool(v) for _, v in preds], f1=bool(f1))


def write_once(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w" if MUTANT == "write_w" else "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def analyze(table, out_dir=OUT_DIR, out=print):
    cells = read_table(table)
    with open(table, "rb") as f:
        raw = f.read()
    L, v = render(cells)
    L.insert(2, "TABLE %s sha256=%s (%d cells)" % (table, hashlib.sha256(raw).hexdigest(), len(cells)))
    txt = "\n".join(L) + "\n"
    oc, tc = os.path.join(out_dir, "dataset_survey_outcome.txt"), os.path.join(out_dir, "dataset_survey_table.csv")
    for p in (oc, tc):
        if os.path.exists(p) and MUTANT != "write_w":
            refuse("%s exists (write-once)" % p)
    write_once(tc, raw.decode("utf-8"))
    write_once(oc, txt)
    for l in L:
        out(l)
    return v


def template(path):
    if os.path.exists(path):
        refuse("%s exists" % path)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(HEADER)
        for c in CANDIDATES:
            for col in COLUMNS:
                w.writerow([c, col, "", "", "", ""])
    return 0


# ------------------------------------------------------------------------------------------------ selftest
def _table(td, name, mod=None, drop=()):
    rows = []
    for c in CANDIDATES:
        for col in COLUMNS:
            if (c, col) in drop:
                continue
            st = "PASS" if col in LEGS else "REPORTED"
            rows.append([c, col, st, {"support": "5", "models": "25"}.get(col, ""), "https://example.org/%s sha256=00 2026-09-27" % col, ""])
    for (c, col), (st, val, src, why) in (mod or {}).items():
        for r in rows:
            if r[0] == c and r[1] == col:
                r[2:] = [st, val, src, why]
    p = os.path.join(td, name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(HEADER)
        w.writerows(rows)
    return p


def selftest(quiet=False):
    n = [0]

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    with tempfile.TemporaryDirectory() as td:
        base = read_table(_table(td, "t0.csv"))
        L, v = render(base)
        t = "\n".join(L)
        ok(v["c1"] and "C1 COMPLETENESS: HELD (135 of 135 cells" in t, "C1 HELD on a complete table")
        ok(v["words"]["SuperGPQA"] == "ADMIT" and "F1 does not fire (SuperGPQA: ADMIT)." in t, "C2 ADMIT; F1 silent")
        ok(t.startswith("pool - (DATASET-SURVEY"), "the first line names the (absent) pool")
        mod = {("SuperGPQA", "licence"): ("FAIL", "", "https://hf.co/x sha256=11", ""),
               ("SuperGPQA", "closure"): ("FAIL", "", "cmd: a4.py", ""),
               ("HELM Capabilities v1.15.0", "licence"): ("UNVERIFIED", "", "", "no licence stated on the release page"),
               ("BigCodeBench-perf", "licence"): ("FAIL", "", "https://x sha256=22", ""),
               ("LiveBench", "support"): ("FAIL", "0", "cmd: count", ""),
               ("BFCL-Result full", "support"): ("PASS", "3", "cmd: count", ""),
               ("RouterEval / OLL-v2", "models"): ("UNVERIFIED", "", "", "roster file not listed"),
               ("20NG (inventory)", "dominance"): ("REPORTED", "", "", "")}
        L, v = render(read_table(_table(td, "t1.csv", mod)))
        t = "\n".join(L)
        ok(v["words"]["SuperGPQA"] == "REFUSE-by-closure+licence" and "F1 FIRES: SuperGPQA REFUSED (REFUSE-by-closure+licence)" in t,
           "C2 REFUSE names every failing leg in the registered order; F1 FIRES")
        ok(v["words"]["HELM Capabilities v1.15.0"] == "UNVERIFIED" and v["words"]["RouterEval / OLL-v2"] == "UNVERIFIED",
           "C2 UNVERIFIED when no leg fails and one is unverified")
        ok(not v["c1"] and "20NG (inventory)/dominance" in t, "C1 FAILED on a reported cell without a source")
        ok(v["preds"] == [False, True, True, True, True, False, False], "P1-P7 scored against the table (%s)" % v["preds"])
        L, v = render(read_table(_table(td, "t2.csv", {("BFCL-Result full", "support"): ("PASS", "4", "cmd: count", "")},
                                        drop={("LiveBench", "key")})))
        ok(not v["c1"] and v["words"]["LiveBench"] == "UNVERIFIED" and v["preds"][4] is False,
           "a missing cell fails C1 and reads UNVERIFIED; P5 FAILED at 4 strata")
        L, v = render(read_table(_table(td, "t3.csv", {("SuperGPQA", "key"): ("UNVERIFIED", "", "", "not checked")})))
        ok("an UNVERIFIED row is not an admission" in "\n".join(L), "F1 silent on UNVERIFIED, with the precondition words")
        for bad, why in ((["a", "b"], "header"), (None, "status")):
            p = os.path.join(td, "bad_%s.csv" % why)
            with open(p, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, lineterminator="\n")
                if bad:
                    w.writerow(bad)
                else:
                    w.writerow(HEADER)
                    w.writerow(["SuperGPQA", "licence", "MAYBE", "", "x", ""])
            try:
                read_table(p)
                ok(False, "a bad %s refuses" % why)
            except SystemExit:
                ok(True, "a bad %s refuses" % why)
        # C11-2: value against status (reviewer witness Y-DS1 and its neighbours); each REFUSES the table
        for name, cell, needle in (
                ("Y-DS1 models 12 marked PASS", {("SuperGPQA", "models"): ("PASS", "12", "cmd: count", "")}, "contradicts its value 12"),
                ("Y-DS1 support 0 marked PASS", {("SuperGPQA", "support"): ("PASS", "0", "cmd: count", "")}, "contradicts its value 0"),
                ("models 19 marked PASS (boundary)", {("SuperGPQA", "models"): ("PASS", "19", "cmd: count", "")}, "contradicts its value 19"),
                ("models 20 marked FAIL (boundary)", {("SuperGPQA", "models"): ("FAIL", "20", "cmd: count", "")}, "contradicts its value 20"),
                ("support 1 marked FAIL (boundary)", {("LiveBench", "support"): ("FAIL", "1", "cmd: count", "")}, "contradicts its value 1"),
                ("models PASS with no value", {("SuperGPQA", "models"): ("PASS", "", "cmd: count", "")}, "needs an integer value"),
                ("support PASS with value 2.5", {("SuperGPQA", "support"): ("PASS", "2.5", "cmd: count", "")}, "needs an integer value")):
            try:
                read_table(_table(td, "vs_%d.csv" % abs(hash(name)), cell))
                ok(False, "C11-2 %s REFUSES the table" % name)
            except SystemExit as e:
                ok(needle in str(e), "C11-2 %s REFUSES the table (%s)" % (name, str(e)[len(TAG) + 10:][:70]))
        ok(read_table(_table(td, "vs_ok.csv", {("SuperGPQA", "models"): ("PASS", "20", "cmd: count", ""),
                                                ("SuperGPQA", "support"): ("PASS", "1", "cmd: count", ""),
                                                ("LiveBench", "models"): ("FAIL", "19", "cmd: count", "")}))[("SuperGPQA", "models")]["value"] == "20",
           "C11-2 the boundary values admitted with their implied statuses (models 20 PASS, 19 FAIL; support 1 PASS)")
        p = _table(td, "t4.csv")
        od = os.path.join(td, "out")
        analyze(p, od, out=lambda s: None)
        try:
            analyze(p, od, out=lambda s: None)
            ok(False, "the outcome is write-once")
        except SystemExit:
            ok(True, "the outcome is write-once")
        tp = os.path.join(td, "tmpl.csv")
        template(tp)
        with open(tp, encoding="utf-8") as f:
            ok(sum(1 for _ in f) == 1 + len(CANDIDATES) * len(COLUMNS), "the template lists every cell")
    return n[0]


MUTANTS = ("source_not_required", "unverified_admits", "f1_never", "write_w", "status_trusted")


def run_mutants():
    global MUTANT
    killed = 0
    for m in MUTANTS:
        MUTANT = m
        try:
            selftest(quiet=True)
            res = "SURVIVED"
        except BaseException as e:            # noqa: B902
            res = "KILLED | %s" % str(e)[:90]
        finally:
            MUTANT = None
        killed += res.startswith("KILLED")
        print("  %-22s %s" % (m, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--template")
    g.add_argument("--analyze")
    a = ap.parse_args(argv)
    print("pool - (DATASET-SURVEY: no pool; a census of public metadata)")
    if a.selftest:
        print("SELFTEST PASSED: %d checks" % selftest())
        return 0
    if a.mutants:
        return run_mutants()
    if a.template:
        return template(a.template)
    analyze(a.analyze)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
