"""math_scorer_h: the per-row H table (MATH sensitivity line of D-2026-10-08-5). Zero judge calls; read-only.

REGISTRATION. docs/judge_v2_program.md, section "## Author's decision 2026-10-08 (recorded by the registrar; zero calls;
insertion only) — D-2026-10-08-1..6 ..." (L25317-L25327, _as_of bb5eb124), paragraphs "H, THE SENSITIVITY LINE" and
"DECLARED PRE-RUN DEVIATIONS" item (2). Authority: docs/agents/author_decisions/2026-10-08.md (5211616a), D-5: the
official scorer eval_results.is_correct is of record for MATH; H is reported beside, decides nothing. This script
produces the "frozen, selftested implementation of the definition above [that] produces the per-row H table
(question_id, model, H, route)"; the registrar pins its sha256 (LF of record) BEFORE any consumer's --run.

DEFINITION (copied VERBATIM below, between the COPY markers, from the pinned source; the selftest asserts each copied
object's source text equals the source's, via ast):
  E:/TaxoArena_tmp/math_audit/math_scorer_analyse.py  sha256-lf16:fe1ce919c29a5ec3 (blob:460cfbb2 LF;
      sha256-crlf16:38486ef3b7341e49 on disk): h_score, region, answer_line, unit_prefix_ok, REF_FIX, ANS_LINE,
      DOLLAR, STATED
  E:/TaxoArena_tmp/math_audit/math_scorer_audit.py    sha256-lf16:b22251009ac14ab5 (LF on disk): labelled, modes
  tools/analysis/math_fix.py                          blob:c44a2618 (10a3413f), imported (asserted at import)
H(row) = 1 iff the official verdict is 1, OR a stated answer (boxed / Minerva "final" of labelled(region), then the
answer line) matches the reference (modes str/paren/num, or a unit-only numeric prefix); region = text after the last
</think>, nothing for an unclosed <think>; corrected references 2060002/2060129/2000164 for H only, matched as
equations after whitespace removal and "1x" -> "x".

KNOWN PROPERTY OF THE PINNED DEFINITION (implemented as recorded, NOT fixed; reported to the registrar): the
".replace('1x', 'x')" step turns a correct "11x+6y+5z+86=0" into "1x+6y+5z+86=0", so H can never credit a correct
answer to 2060129 through the eqn path (selftest case S20 asserts this). The regex r"\\s|\\[,;!]" removes whitespace
only (its second alternative is the literal text "[,;!]").

OUTPUT (--run only; write-once, mode "x"; never a DB write):
  experiment_results/math_scorer_h/math_h_table.csv   header question_id,model,H,route; one row per MATH
      (question_id, model) of eval_results x corpus_questions(source='MATH'); sorted by (question_id, model); LF;
      utf-8; route = h_score's reason ("imported", "<cand>:<mode>", "none").
  experiment_results/math_scorer_h/math_h_table.meta.json  counts, routes, pins, sha256-lf of the CSV.
  The CSV's sha256 (bytes are LF, so sha256 = sha256-lf) is printed; the registrar pins it. Outputs are not
  committed: back them up to E:/TaxoArena_backup_<date>_math_scorer_h with SHA256SUMS.
Column names follow the record's "(question_id, model, H, route)" (the brief's "h_correct, reason" differ; the record wins).

INPUT. <data-root>/multicorpus_cache_v1.db opened mode=ro&immutable=1 (refused if a non-empty -wal / -journal exists).
Refusals (exit 2, nothing written): row count != 23,832, models != 18, any model != 1,324 rows, the excluded
Meta-Llama-3-70B-Instruct present, an is_correct outside {0,1}, a duplicate (question_id, model), output exists.
No pool / split is involved (all cached MATH rows; no split word claimed, S3), so no pool_guard line: the table is
an input to consumers, which apply their own R1 drops.

LAUNCH SEQUENCE (rule 7: E:/TaxoArena_tmp/busy.ps1 must exit 1 before --dry-run and before --run; one reader):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/math_scorer_h.py --selftest
  python tools/analysis/math_scorer_h.py --dry-run      # reads the DB, computes H, prints counts + sha; writes nothing
  python tools/analysis/math_scorer_h.py --run          # same, then writes the two files (mode x)
--data-root defaults to the main checkout (the DB is never copied into a worktree).

SELFTEST (--selftest; needs the E: audit files, pinned by sha256 below; fails if they are absent or changed):
  A  pins: math_fix blob; source files' sha256-lf16; ast source text of every copied object == the source's.
  B  the 150 adjudicated audit rows (full responses in E:/TaxoArena_tmp/math_scorer_h/fixtures150_full.json, built
     read-only from the DB 2026-10-08 after a busy check, each output asserted to end with the sample's stored tail;
     backup E:/TaxoArena_backup_20261009_math_scorer_h with SHA256SUMS; raw outputs, never committed, R5): h_score ==
     the sheet's hybrid on 150/150; H=1 on 90; H false credits vs strict verdict 2, H misses 5 (== summary.json
     strata hfp/hfn sums).
  C  documented synthetic cases S01-S25 (30 cases: each route, each rejected candidate, the corrected references,
     the 2060129 "11x" property S20, the leading-dot property S25).
  D  corrected references re-derived by arithmetic (2060002: plane through L and (1,1,1); 2060129: bisector through
     (-5,-1,-5)); 2000164 is the stored RHS (record).
  E  end to end through main(): a fixture DB in a scratch dir -> default count pins REFUSE it; --dry-run (exact
     printed official / H credits, route dict and sha; nothing written); --run (exact CSV bytes, sorted although the
     DB order is not; printed sha == sha of the file; meta values); second --run REFUSED (write-once, file unchanged);
     REFUSED: models, rows per model, Llama-3-70B present, is_correct=2, duplicate row, non-empty -wal.

DRY-RUN DISCRIMINATOR (2026-10-08, real DB, read-only, busy check FREE first, nothing written): rows 23,832, 18 models
x 1,324; official 2,335; H 7,126; all 13 route counts identical to the audit's summary.json hybrid_routes; table
sha256-lf16:6b010fa60dde7278 at that DB state (a dry-run figure; the pin of record is the --run's, by the registrar).

MUTANTS (temporary edits, reverted; each run against legs B-E, then leg A alone; harness in the session scratchpad).
Leg A (verbatim-copy check) kills every edit to the copied definition by construction, so the table reports B-E.
  M01 region: rfind('</think>') -> find                         B-E: C (S05)        A: killed
  M02 region: unclosed <think> returns resp                      B-E: C, E           A: killed
  M03 answer_line: last 2 non-empty lines -> last 3              B-E: C (S10)        A: killed
  M04 answer_line: ms[-1] -> ms[0]                               B-E: C (S12)        A: killed
  M05 answer_line: d[-1] -> d[0]                                 B-E: B, C (S11)     A: killed
  M06 STATED += lastnum                                          B-E: B, C, E        A: killed
  M07 h_score: official short-circuit removed                    B-E: C, E           A: killed
  M08 h_score: prefix accepted without unit_prefix_ok            B-E: B, C           A: killed
  M09 unit_prefix_ok: digits allowed in the remainder            B-E: C (S16e)       A: killed
  M10 h_score: REF_FIX ignored (stored ref used)                 B-E: B, C, E        A: killed
  M11 h_score: eqn path falls through to modes (no continue)     B-E: C (S18)        A: killed
  M12 h_score: .replace('1x','x') dropped                        B-E: C (S20, S21)   A: killed
  M13 modes: 'num' never returned                                B-E: B, C           A: killed
  M14 h_score: 'paren' not accepted                              B-E: C (S15)        A: killed
  M15 answer_line not appended                                   B-E: B, C, E        A: killed
  M16 candidates: boxed only                                     B-E: B, C           A: killed
  M17 write: rows unsorted (DB order)                            B-E: E
  M18 write: CRLF line endings                                   B-E: E
  M19 write-once removed (pre-check and mode x)                  B-E: E
  M20 refusal: excluded model check removed                      B-E: E
  M21 refusal: row-count check removed                           B-E: E
  M22 refusal: -wal check removed                                B-E: E
  M23 printed sha over CRLF bytes                                B-E: E
  M24 credits exclude the official credits                       B-E: E
  M25 duplicate (question_id, model) check removed               B-E: E
  M26 is_correct domain check removed                            B-E: E
  M27 region: + 8 -> + 7 (keeps ">")                             B-E: survived (equivalent: ">" changes no candidate);
                                                                 A: killed
  M28 answer_line: strip(" *.") -> strip(" *")                   B-E: C (S25)        A: killed
  M29 refusal: model-count check removed                         B-E: E
  M30 refusal: per-model count check removed                     B-E: E
  Total 30/30 killed (29 by B-E; M27 behaviourally equivalent, killed by A).
"""
import argparse, ast, collections, contextlib, hashlib, io, json, os, re, sqlite3, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MAIN_ROOT = "Z:/FAC/TUBerlin/THESIS/TaxoArena"
sys.path.insert(0, HERE)
import math_fix as mf  # noqa: E402

PIN_MATH_FIX_BLOB = "c44a2618d8ad07fff37b875ab81b8ecfbb94917f"
AUDIT_DIR = "E:/TaxoArena_tmp/math_audit/"
SRC_ANALYSE = (AUDIT_DIR + "math_scorer_analyse.py", "fe1ce919c29a5ec3")
SRC_AUDIT = (AUDIT_DIR + "math_scorer_audit.py", "b22251009ac14ab5")
FIXTURES = ("E:/TaxoArena_tmp/math_scorer_h/fixtures150_full.json",
            "0e711a8acc90597dcc618ed573b8b5548755e77f59d869cb8cac958a1b1aa1d4")
SHEET = (AUDIT_DIR + "adjudication_sheet.csv", "b43b7b8f4ada1bf16706276a6cba76297a1000d7e05ac1047cccf1780b008912")
SUMMARY = (AUDIT_DIR + "summary.json", "b26f3507bc58a1b91bc863eaf14642f1b7482805146c089f0833a4978371f5e1")
COPIED_FROM_ANALYSE = ("REF_FIX", "ANS_LINE", "DOLLAR", "STATED", "region", "answer_line", "unit_prefix_ok", "h_score")
COPIED_FROM_AUDIT = ("modes", "labelled")

EXPECT_ROWS, EXPECT_MODELS, EXPECT_PER_MODEL = 23832, 18, 1324
EXCLUDED_MODEL = "Meta-Llama-3-70B-Instruct"
OUT_REL = "experiment_results/math_scorer_h"
CSV_NAME, META_NAME = "math_h_table.csv", "math_h_table.meta.json"
QUERY = """select e.question_id, e.model_name, q.target, e.model_output, e.is_correct
    from eval_results e join corpus_questions q using(question_id) where q.source='MATH'"""


def git_blob(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def lf_bytes(path):
    return open(path, "rb").read().replace(b"\r\n", b"\n")


if git_blob(lf_bytes(os.path.join(HERE, "math_fix.py"))) != PIN_MATH_FIX_BLOB:
    raise SystemExit("REFUSED: tools/analysis/math_fix.py blob != %s (the H definition's helper)" % PIN_MATH_FIX_BLOB)

# ======================= COPY BEGIN (verbatim; math_scorer_audit.py) =======================
def modes(c, t):
    p, tt = mf.normalise(c), mf.normalise(t)
    if p is None or tt is None or p == "": return None
    if p == tt: return "str"
    if p.replace("(", "").replace(")", "") == tt.replace("(", "").replace(")", ""): return "paren"
    a, b = mf.as_number(p), mf.as_number(tt)
    if a is not None and b is not None: return "num" if abs(a - b) <= 1e-6 * max(1.0, abs(b)) else None
    if b is not None:
        m = mf.NUM.search(p)
        if m:
            a = mf.as_number(m.group(0))
            if a is not None and abs(a - b) <= 1e-6 * max(1.0, abs(b)): return "prefix"
    return None

def labelled(resp):
    out = []
    if not resp: return out
    b = mf.last_braced(resp, mf.BOXED)
    if b is not None and b.strip(): out.append(("boxed", b))
    m = mf.FINAL.search(resp)
    if m and m.group(1).strip(): out.append(("final", m.group(1)))
    n = mf.NUM.findall(resp[-400:])
    if n: out.append(("lastnum", n[-1]))
    return out
# ======================= COPY BEGIN (verbatim; math_scorer_analyse.py) =====================
REF_FIX = {2060002: "20x+23y+26z-69=0", 2060129: "11x+6y+5z+86=0", 2000164: "4x-5y=-50"}  # upstream RHS-only references
ANS_LINE = re.compile(r"(?:final answer|the answer is|\banswer\b\s*[:*])[^\n]*", re.I)
DOLLAR = re.compile(r"\$([^$]+)\$")
STATED = ("boxed", "final", "answer_line")

def region(resp):
    if not resp: return ""
    if "</think>" in resp: return resp[resp.rfind("</think>") + 8:]
    if "<think>" in resp: return ""          # unclosed think: nothing delivered
    return resp

def answer_line(txt):
    lines = [x for x in txt.rstrip().split(chr(10)) if x.strip()][-2:]   # answer statement must be in the last 2 non-empty lines
    ms = list(ANS_LINE.finditer(chr(10).join(lines)))
    if not ms: return None
    line = ms[-1].group(0)
    d = DOLLAR.findall(line)
    if d: return d[-1]
    tail = re.split(r"(?:\bis\b|:)", line)[-1].strip(" *.")
    return tail or None

def unit_prefix_ok(c, t):
    p = mf.normalise(c); m = mf.NUM.search(p or "")
    if not m: return False
    rest = (p[:m.start()] + p[m.end():]).replace("^\circ", "").replace("^{\circ}", "").replace("\circ", "")
    return not re.search(r"[0-9+\-*/^_=\{}()\[\]]", rest)

def h_score(resp, target, imported, qid):
    if imported: return 1, "imported"
    ref = REF_FIX.get(qid, target)
    reg = region(resp)
    cands = [(k, c) for k, c in labelled(reg) if k in STATED]
    al = answer_line(reg)
    if al: cands.append(("answer_line", al))
    for k, c in cands:
        if qid in REF_FIX:
            if re.sub(r"\s|\[,;!]", "", c).replace("1x", "x") == ref: return 1, k + ":eqn"
            continue
        md = modes(c, ref)
        if md in ("str", "paren", "num"): return 1, "%s:%s" % (k, md)
        if md == "prefix" and unit_prefix_ok(c, ref): return 1, k + ":unitprefix"
    return 0, "none"
# ======================= COPY END ==========================================================


class Refused(Exception):
    pass


def open_ro(db):
    for suf in ("-wal", "-journal"):
        p = db + suf
        if os.path.exists(p) and os.path.getsize(p) > 0:
            raise Refused("non-empty %s beside the DB (immutable=1 would hide it): a failed precondition" % p)
    if not os.path.exists(db):
        raise Refused("DB not found: %s" % db)
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % db.replace("\\", "/"), uri=True)


def build_table(rows):
    """rows: (question_id, model, target, model_output, is_correct). Returns sorted [(qid, model, H, route)]."""
    seen, out = set(), []
    for qid, m, tgt, resp, imp in rows:
        if imp not in (0, 1):
            raise Refused("is_correct %r outside {0,1} at (%s, %s)" % (imp, qid, m))
        k = (int(qid), m)
        if k in seen:
            raise Refused("duplicate (question_id, model) %r" % (k,))
        seen.add(k)
        h, why = h_score(resp, tgt, imp, int(qid))
        out.append((int(qid), m, h, why))
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def check_counts(table):
    n = len(table)
    per = collections.Counter(r[1] for r in table)
    if EXCLUDED_MODEL in per:
        raise Refused("%s present (excluded from every roster)" % EXCLUDED_MODEL)
    if n != EXPECT_ROWS:
        raise Refused("MATH rows %d != %d" % (n, EXPECT_ROWS))
    if len(per) != EXPECT_MODELS:
        raise Refused("models %d != %d" % (len(per), EXPECT_MODELS))
    bad = {m: c for m, c in per.items() if c != EXPECT_PER_MODEL}
    if bad:
        raise Refused("rows per model != %d: %s" % (EXPECT_PER_MODEL, bad))
    return per


def render_csv(table):
    s = "question_id,model,H,route\n" + "".join("%d,%s,%d,%s\n" % r for r in table)
    for r in table:
        if "," in r[1] or "," in r[3] or "\n" in r[1]:
            raise Refused("unquotable field in %r" % (r,))
    return s.encode("utf-8")


def self_pins():
    me = os.path.abspath(__file__)
    raw = open(me, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(script_blob_lf=git_blob(lf), script_sha256_lf=hashlib.sha256(lf).hexdigest(),
                script_sha256_worktree=hashlib.sha256(raw).hexdigest(), math_fix_blob=PIN_MATH_FIX_BLOB)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", default=MAIN_ROOT)
    ap.add_argument("--out-dir", default=None, help="default <worktree>/" + OUT_REL)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    pins = self_pins()
    print("math_scorer_h: H sensitivity table (D-2026-10-08-5); zero calls; read-only; no pool/split (all MATH rows)")
    print("script blob:%s sha256-lf16:%s (worktree sha256-16:%s); math_fix blob:%s" % (
        pins["script_blob_lf"][:8], pins["script_sha256_lf"][:16], pins["script_sha256_worktree"][:16],
        pins["math_fix_blob"][:8]))
    db = os.path.join(a.data_root, "multicorpus_cache_v1.db")
    out_dir = a.out_dir or os.path.join(REPO, OUT_REL)
    csv_p, meta_p = os.path.join(out_dir, CSV_NAME), os.path.join(out_dir, META_NAME)
    try:
        if a.run:
            for p in (csv_p, meta_p):
                if os.path.exists(p):
                    raise Refused("%s exists (outcome files are write-once)" % p)
        c = open_ro(db)
        rows = c.execute(QUERY).fetchall()
        c.close()
        table = build_table(rows)
        per = check_counts(table)
    except Refused as e:
        print("REFUSED: %s" % e)
        return 2
    body = render_csv(table)
    sha = hashlib.sha256(body).hexdigest()
    routes = collections.Counter(r[3] for r in table)
    credits = sum(r[2] for r in table)
    official = routes.get("imported", 0)
    print("db: %s (mode=ro&immutable=1)" % db)
    print("rows %d | models %d | per model %s" % (len(table), len(per), sorted(set(per.values()))))
    print("official credits (eval_results.is_correct) %d / %d" % (official, len(table)))
    print("H credits %d / %d | H beyond official %d" % (credits, len(table), credits - official))
    print("H routes %s" % json.dumps(dict(sorted(routes.items()))))
    print("corrected references (H only): %s" % json.dumps({str(k): v for k, v in REF_FIX.items()}))
    print("table sha256-lf %s (sha256-lf16:%s; %d bytes, LF, sorted by question_id, model)" % (sha, sha[:16], len(body)))
    if a.dry_run:
        print("DRY-RUN: nothing written (would write %s)" % csv_p)
        return 0
    os.makedirs(out_dir, exist_ok=True)
    meta = dict(table=CSV_NAME, table_sha256_lf=sha, bytes=len(body), rows=len(table), models=len(per),
                official_credits=official, h_credits=credits, routes=dict(sorted(routes.items())),
                ref_fix={str(k): v for k, v in REF_FIX.items()}, db=db, pins=pins,
                definition="docs/judge_v2_program.md L25321 (bb5eb124); D-2026-10-08-5")
    try:
        with open(csv_p, "xb") as fh:
            fh.write(body)
        with open(meta_p, "x", encoding="utf-8", newline="\n") as fh:
            json.dump(meta, fh, indent=1, sort_keys=True)
    except FileExistsError as e:
        print("REFUSED: %s exists (outcome files are write-once)" % e.filename)
        return 2
    print("WROTE %s and %s" % (csv_p, meta_p))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def _sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _leg_a():
    mine = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    my_text = open(os.path.abspath(__file__), encoding="utf-8").read()

    def segs(tree, text, names):
        out = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in names:
                out[node.name] = ast.get_source_segment(text, node)
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", None) in names:
                out[node.targets[0].id] = ast.get_source_segment(text, node)
        return out
    n = 0
    for (path, pin16), names in ((SRC_ANALYSE, COPIED_FROM_ANALYSE), (SRC_AUDIT, COPIED_FROM_AUDIT)):
        assert os.path.exists(path), "source of the definition absent: %s" % path
        got = hashlib.sha256(lf_bytes(path)).hexdigest()[:16]
        assert got == pin16, "%s sha256-lf16 %s != pinned %s" % (path, got, pin16)
        src = open(path, encoding="utf-8").read()
        a_, b_ = segs(ast.parse(src), src, names), segs(mine, my_text, names)
        assert set(a_) == set(names) == set(b_), (sorted(a_), sorted(b_))
        for k in names:
            assert a_[k] == b_[k], "copied %s differs from %s" % (k, path)
            n += 1
    assert git_blob(lf_bytes(os.path.join(HERE, "math_fix.py"))) == PIN_MATH_FIX_BLOB
    return "A pins + verbatim copy: %d objects identical to the pinned sources; math_fix blob ok" % n


def _leg_b():
    import csv
    for p, s in (FIXTURES, SHEET, SUMMARY):
        assert os.path.exists(p), "fixture absent: %s" % p
        assert _sha_file(p) == s, "fixture changed: %s" % p
    fx = json.load(open(FIXTURES[0], encoding="utf-8"))
    sheet = {r["sid"]: r for r in csv.DictReader(open(SHEET[0], encoding="utf-8"))}
    summ = json.load(open(SUMMARY[0], encoding="utf-8"))
    assert len(fx) == 150 and len(sheet) == 150
    agree = h1 = fp = fn = 0
    for r in fx:
        s = sheet[r["sid"]]
        assert (int(s["question_id"]), s["model"]) == (r["question_id"], r["model"])
        assert r["imported"] == 0
        h, why = h_score(r["model_output"], r["target"], r["imported"], r["question_id"])
        agree += int(h == int(s["hybrid"]))
        h1 += h
        fp += int(h == 1 and s["verdict_strict"] == "W")
        fn += int(h == 0 and s["verdict_strict"] == "C")
    hfp = sum(v["hfp"] for v in summ["strata"].values())
    hfn = sum(v["hfn"] for v in summ["strata"].values())
    assert agree == 150, "h_score agrees with the audit's hybrid on %d / 150" % agree
    assert h1 == 90, h1
    assert (fp, fn) == (hfp, hfn) == (2, 5), (fp, fn, hfp, hfn)
    return "B audit fixtures: 150/150 equal to the sheet's hybrid; H=1 on 90; false credits 2, misses 5 (== summary)"


# (id, response, reference, imported, question_id, expected (H, route)) -- paraphrased, no raw model output
SYN = [
    ("S01", "", "5", 1, 1, (1, "imported")),
    ("S02", None, "5", 0, 1, (0, "none")),
    ("S03", "<think>so \\boxed{5}", "5", 0, 1, (0, "none")),
    ("S04", "<think>try 4</think>\nThus \\boxed{5}", "5", 0, 1, (1, "boxed:str")),
    ("S05", "<think>a</think> The answer is \\boxed{7} </think> nothing", "7", 0, 1, (0, "none")),
    ("S06", "No tags here, \\boxed{5}", "5", 0, 1, (1, "boxed:str")),
    ("S07", "We get 12.\nThe final answer is $12$.", "12", 0, 1, (1, "final:str")),
    ("S08", "\\boxed{3} The final answer is $5$.", "5", 0, 1, (1, "final:str")),
    ("S09", "work\n**Answer:** -120", "-120", 0, 1, (1, "answer_line:str")),
    ("S10", "Answer: 5\nmore\nmore", "5", 0, 1, (0, "none")),
    ("S11", "so the answer is $4$, i.e. $3$", "3", 0, 1, (1, "answer_line:str")),
    ("S12", "Answer: 4\nThe answer is 9", "9", 0, 1, (1, "answer_line:str")),
    ("S13", "the result 5\nok\ndone", "5", 0, 1, (0, "none")),
    ("S14", "\\boxed{0.5}", "\\frac{1}{2}", 0, 1, (1, "boxed:num")),
    ("S15", "\\boxed{(1,2)}", "1,2", 0, 1, (1, "boxed:paren")),
    ("S16", "\\boxed{25 \\text{trips}}", "25", 0, 1, (1, "boxed:unitprefix")),
    ("S16b", "\\boxed{25+x}", "25", 0, 1, (0, "none")),
    ("S16c", "\\boxed{3 cm^2}", "3", 0, 1, (0, "none")),
    ("S16d", "\\boxed{47^\\circ}", "47", 0, 1, (1, "boxed:unitprefix")),
    ("S16e", "\\boxed{12 \\text{m}3}", "12", 0, 1, (0, "none")),
    ("S17","\\boxed{20x + 23y + 26z - 69 = 0}", "0", 0, 2060002, (1, "boxed:eqn")),
    ("S18", "\\boxed{0}", "0", 0, 2060002, (0, "none")),
    ("S19", "\\boxed{4x - 5y = -50}", "-50", 0, 2000164, (1, "boxed:eqn")),
    ("S19b", "\\boxed{-50}", "-50", 0, 2000164, (0, "none")),
    ("S20", "\\boxed{11x + 6y + 5z + 86 = 0}", "0", 0, 2060129, (0, "none")),
    ("S21", "\\boxed{41x-5y=-50}", "-50", 0, 2000164, (1, "boxed:eqn")),
    ("S22", "Final answer: 42.", "42", 0, 1, (1, "answer_line:str")),
    ("S23", "\\boxed{5} The final answer is $5$.", "5", 0, 1, (1, "boxed:str")),
    ("S24", "\\boxed{4}", "3", 0, 1, (0, "none")),
    ("S25", "The answer is .5", "5", 0, 1, (1, "answer_line:str")),  # strip(" *.") also strips a leading dot
]


def _leg_c():
    for sid, resp, ref, imp, qid, exp in SYN:
        got = h_score(resp, ref, imp, qid)
        assert got == exp, "%s: h_score -> %r, expected %r" % (sid, got, exp)
    return "C synthetic: %d/%d cases give the documented (H, route)" % (len(SYN), len(SYN))


def _leg_d():
    # 2060002: planes P1 = x+y+z-6, P2 = 2x+3y+4z+5; P1 + t P2 through (1,1,1): -3 + 14 t = 0 -> 14 P1 + 3 P2.
    p = [14 * a + 3 * b for a, b in zip((1, 1, 1, -6), (2, 3, 4, 5))]
    assert p == [20, 23, 26, -69] and sum(p[:3]) + p[3] == 0
    assert REF_FIX[2060002] == "%dx+%dy+%dz%d=0" % tuple(p)
    # 2060129: bisectors 13(3x-6y+2z+5) -/+ 7(4x-12y+3z-3); the one through (-5,-1,-5), A > 0, gcd 1.
    import math
    sols = []
    for s in (1, -1):
        v = [13 * a - s * 7 * b for a, b in zip((3, -6, 2, 5), (4, -12, 3, -3))]
        if v[0] < 0:
            v = [-x for x in v]
        g = math.gcd(*[abs(x) for x in v])
        v = [x // g for x in v]
        if -5 * v[0] - v[1] - 5 * v[2] + v[3] == 0:
            sols.append(v)
    assert sols == [[11, 6, 5, 86]], sols
    assert REF_FIX[2060129] == "%dx+%dy+%dz+%d=0" % tuple(sols[0])
    assert REF_FIX[2000164].split("=")[1] == "-50"  # stored target is the RHS (record)
    return "D corrected references: 2060002 and 2060129 re-derived; 2000164 RHS == stored -50"


def _fixture_db(d, rows, extra_models=()):
    db = os.path.join(d, "multicorpus_cache_v1.db")
    c = sqlite3.connect(db)
    c.execute("create table corpus_questions(question_id integer, source text, target text)")
    c.execute("create table eval_results(question_id integer, model_name text, model_output text, is_correct integer)")
    qs = sorted({(r[0], r[2], r[5]) for r in rows})
    c.executemany("insert into corpus_questions values(?,?,?)", [(q, src, t) for q, t, src in reversed(qs)])
    c.executemany("insert into eval_results values(?,?,?,?)", [(r[0], r[1], r[3], r[4]) for r in rows])
    c.commit(); c.close()
    return db


def _call(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def _leg_e():
    global EXPECT_ROWS, EXPECT_MODELS, EXPECT_PER_MODEL
    # (qid, model, target, output, is_correct, source); inserted in non-sorted order on purpose
    base = [
        (9, "mB", "5", "\\boxed{5}", 0, "MATH"),
        (9, "mA", "5", "<think>\\boxed{5}", 0, "MATH"),
        (3, "mB", "7", "x", 1, "MATH"),
        (3, "mA", "7", "Answer: 7", 0, "MATH"),
        (2060002, "mB", "0", "\\boxed{0}", 0, "MATH"),
        (2060002, "mA", "0", "\\boxed{20x+23y+26z-69=0}", 0, "MATH"),
        (500, "mA", "4", "\\boxed{4}", 0, "IFEval"),
        (500, "mB", "4", "\\boxed{4}", 0, "IFEval"),
    ]
    want = (b"question_id,model,H,route\n3,mA,1,answer_line:str\n3,mB,1,imported\n9,mA,0,none\n9,mB,1,boxed:str\n"
            b"2060002,mA,1,boxed:eqn\n2060002,mB,0,none\n")
    wsha = hashlib.sha256(want).hexdigest()
    saved = (EXPECT_ROWS, EXPECT_MODELS, EXPECT_PER_MODEL)
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, "root"); os.makedirs(root)
        _fixture_db(root, base)
        out = os.path.join(d, "out")
        rc, s = _call(["--dry-run", "--data-root", root, "--out-dir", out])  # default pins: must refuse
        assert rc == 2 and "REFUSED: MATH rows 6 != 23832" in s, s
        try:
            EXPECT_ROWS, EXPECT_MODELS, EXPECT_PER_MODEL = 6, 2, 3
            rc, s = _call(["--dry-run", "--data-root", root, "--out-dir", out])
            assert rc == 0 and not os.path.exists(out), s
            assert "official credits (eval_results.is_correct) 1 / 6" in s, s
            assert "H credits 4 / 6 | H beyond official 3" in s, s
            assert 'H routes {"answer_line:str": 1, "boxed:eqn": 1, "boxed:str": 1, "imported": 1, "none": 2}' in s, s
            assert "table sha256-lf %s " % wsha in s, s
            assert render_csv(build_table([r[:5] for r in reversed(base) if r[5] == "MATH"])) == want
            rc, s = _call(["--run", "--data-root", root, "--out-dir", out])
            assert rc == 0, s
            body = open(os.path.join(out, CSV_NAME), "rb").read()
            assert body == want, body
            assert "table sha256-lf %s " % hashlib.sha256(body).hexdigest() in s
            meta = json.load(open(os.path.join(out, META_NAME), encoding="utf-8"))
            assert meta["table_sha256_lf"] == wsha and meta["h_credits"] == 4 and meta["official_credits"] == 1
            rc, s = _call(["--run", "--data-root", root, "--out-dir", out])  # write-once
            assert rc == 2 and "REFUSED:" in s and "write-once" in s, s
            assert open(os.path.join(out, CSV_NAME), "rb").read() == want
            # refusals on bad inputs
            for tag, rows, msg in (
                    ("llama", base + [(3, EXCLUDED_MODEL, "7", "x", 0, "MATH")], "REFUSED: %s present" % EXCLUDED_MODEL),
                    ("ic2", [r if r[:2] != (9, "mB") else r[:4] + (2, "MATH") for r in base], "REFUSED: is_correct 2"),
                    ("dup", base + [(9, "mB", "5", "\\boxed{5}", 0, "MATH")], "REFUSED: duplicate")):
                r2 = os.path.join(d, tag); os.makedirs(r2)
                _fixture_db(r2, rows)
                rc, s = _call(["--dry-run", "--data-root", r2])
                assert rc == 2 and msg in s, (tag, s)
            EXPECT_MODELS = 3
            rc, s = _call(["--dry-run", "--data-root", root])
            assert rc == 2 and "REFUSED: models 2 != 3" in s, s
            EXPECT_MODELS, EXPECT_PER_MODEL = 2, 2
            rc, s = _call(["--dry-run", "--data-root", root])
            assert rc == 2 and "REFUSED: rows per model != 2" in s, s
            open(os.path.join(root, "multicorpus_cache_v1.db-wal"), "wb").write(b"x")
            rc, s = _call(["--dry-run", "--data-root", root])
            assert rc == 2 and "REFUSED: non-empty" in s and "-wal" in s, s
        finally:
            EXPECT_ROWS, EXPECT_MODELS, EXPECT_PER_MODEL = saved
    return "E end to end: dry-run values, run bytes/sha/meta, write-once, 7 refusals (rows, models, per-model, Llama, is_correct, dup, wal)"


def selftest(legs=("A", "B", "C", "D", "E")):
    fn = dict(A=_leg_a, B=_leg_b, C=_leg_c, D=_leg_d, E=_leg_e)
    for L in legs:
        print("SELFTEST " + fn[L]())
    print("SELFTEST OK (%d legs)" % len(legs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
