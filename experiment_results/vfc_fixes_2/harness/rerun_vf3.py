"""VFC-FIXES-2 delta READY, checks (ii) and (iii) of VFC-RX-RULING section 5, under the conditions C-ii-1, C-ii-2, C-ii-3 and C-iii of the review
docs/reviews/READY_vfc_fixes_2.md (a3da968). ZERO-WRITE re-derivations in scratch, never over a file of record. PREPARED 2026-09-25 by the
engine-coder; NOT RUN (the ruling's condition (2): after the pilot and INDUCE-RUBRIC-3 close). Supersedes rerun_vf2.py.

LEGS (each refuses if --out exists):
  python rerun_vf3.py vfc --build <T>/tools/analysis --expect-lf <LF16> --repo <MAIN> --out <OUT>    (ii)  the 62 recorded caches only
  python rerun_vf3.py pia --build <T>/tools/analysis --expect-lf <LF16> --repo <MAIN> --out <OUT>    (iii) POSITION-INDEX-ALL
  python rerun_vf3.py tm  --build <T>/tools/analysis --expect-lf <LF16> --repo <MAIN> --out <OUT>    (iii) TIE-MECHANICS
SCORING (reads text files only):
  python rerun_vf3.py score-vfc --rec <record .txt> --new <OUT>/vote_frame_cert.txt [--rec-json <record .json> --new-json <OUT>/vote_frame_cert.json]
  python rerun_vf3.py score-pia --rec <record .txt> --new <OUT>/position_index_all_outcome.txt
  python rerun_vf3.py score-tm  --rec <record .txt> --new <OUT>/tie_mechanics_outcome.txt

GUARDS. C-ii-1: <T> must be `git -c core.autocrlf=false archive <build> tools/analysis src/main/kotlin experiment_configs`; the leg REFUSES unless
sha256[:16] of <T>/tools/analysis/vote_frame_cert.py equals --expect-lf and the file carries no CR byte. C-ii-3: sha256 of the four outputs of
record (vote_frame_cert.json / .txt, position_index_all_outcome.txt, x12_crossdomain/tie_mechanics_outcome.txt) before and after each leg,
REFUSED on any change. The audit hook refuses: any sqlite3.connect without mode=ro and immutable=1; any open() / os.open() inside <MAIN> with a
write mode or write flags; os.remove / os.unlink / os.rename / os.replace / os.rmdir / os.truncate / os.chmod / shutil.rmtree inside <MAIN> (the
review's row 17 holes). vfc leg: the 62 recorded caches must equal the certificate of record before and after (size, mtime_ns, sha256_16, no
non-empty -wal / -journal); the scan is restricted to them. E3: `selftest_ok=True` is PASSED, not executed; E3 of the
re-derivation rests on part (i)'s selftest of the SAME LF sha, and the leg prints so."""
import os, sys, json, argparse, hashlib, difflib

ap = argparse.ArgumentParser()
ap.add_argument("what", choices=("vfc", "pia", "tm", "score-vfc", "score-pia", "score-tm"))
ap.add_argument("--build"); ap.add_argument("--expect-lf"); ap.add_argument("--repo"); ap.add_argument("--out")
ap.add_argument("--rec"); ap.add_argument("--new"); ap.add_argument("--rec-json"); ap.add_argument("--new-json")
a = ap.parse_args()


def lines(p):
    return open(p, encoding="utf-8").read().split("\n")


def paired_diff(rec, new):
    """[(record line no or None, record text or None, new text or None)] for every line that differs, aligned by difflib."""
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, rec, new, autojunk=False).get_opcodes():
        if tag == "equal": continue
        n = max(i2 - i1, j2 - j1)
        for k in range(n):
            i = i1 + k if i1 + k < i2 else None; j = j1 + k if j1 + k < j2 else None
            out.append((i + 1 if i is not None else None, rec[i] if i is not None else None, new[j] if j is not None else None, i1))   # i1: the opcode's record start
    return out


if a.what.startswith("score"):
    rec, new = lines(a.rec), lines(a.new)
    diffs = paired_diff(rec, new); findings = []; ok = []
    if a.what == "score-vfc":
        SIX = {176: (111, 1024), 180: (187, 1048), 184: (182, 993), 188: (140, 972), 245: (29, 279), 275: (36, 288)}
        R6LAB = "(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 0"
        def expected(no, r, nw):
            if no == 1: return nw is not None and nw.startswith("=== VOTE-FRAME-CERT") and "72ceddfe" not in nw, "harness: the script sha"
            if no == 4: return nw is not None and "62 SQLite files scanned" in nw, "harness: the restricted scan"
            if no == 388: return nw is not None and "0 other scanned files" in nw, "harness: 0 other scanned"
            if no is not None and 154 <= no <= 157 or no is None: return None, "C3 block or an inserted line: judged below"
            if no in (345, 350): return nw is not None and "local imports scanned transitively" in nw and "H3 COMBINER CHECK PASS" in nw, "C3: transitive scan sentence"
            if no == 389: return nw is not None and "CERTIFIED-CONTESTANT 5" in nw and "UNCERTIFIABLE 1," in nw and "MIXED 0" in nw, "C3: classes 54/5/0/0/1/2"
            if no == 400: return nw is not None and nw.startswith("P4 HELD: 1 UNCERTIFIABLE among the 60"), "C3: P4 count 1"
            if no in SIX:
                n, m = SIX[no]
                good = nw is not None and nw.startswith("        secondary E-COMB: UNCERTIFIABLE (R6), secondary, %d resolved of %d informative" % (n, m))
                return good, "R-6 secondary (n, m) = (%d, %d); old unresolvable in record: %s; new line: %s" % (n, m, r.split("unresolvable")[-1].strip(" )"),
                                                                                                   (nw or "")[(nw or "").find("unresolvable "):][:120])
            if no == 402: return nw is not None and R6LAB in nw and nw.startswith("P4 by reason"), "R-1: six reasons"
            if no in (403, 404):       # judged on content, not on difflib's pairing of a 2-into-1 block
                carried = [l for l in new if l.startswith("P4 is carried by")]
                return (not any(l.startswith("P4 reason OUTSIDE") for l in new) and carried == ["P4 is carried by: ['E-COMB, combiner not verified']"],
                        "R-1 / R-5: the out-of-five line retired; P4 is carried by: ['E-COMB, combiner not verified'] (content check over the new text)")
            return False, "NOT an expected diff"
        c3_new = []
        for no, r, nw, i1 in diffs:
            good, why = expected(no, r, nw)
            if good is None:
                c3_new.append((no, r, nw, i1)); continue
            (ok if good else findings).append("L%s %s | record: %s | new: %s" % (no, why, (r or "")[:110], (nw or "")[:160]))
        # R2-M1 (f387d58): an inserted line belongs to the C3 block ONLY when its difflib opcode starts inside record L154-L157 (0-based 153..157);
        # every other inserted or deleted line is a FINDING, whatever its indentation
        c3_block = [x for x in c3_new if (x[0] is not None and 154 <= x[0] <= 157) or (x[0] is None and 153 <= x[3] <= 157)]
        c3_txt = " ".join(x[2] or "" for x in c3_block)
        for x in c3_new:
            if x not in c3_block: findings.append("L%s an unexpected inserted / deleted line: %s" % (x[0], (x[2] or x[1] or "")[:160]))
        if c3_block:
            (ok if "CERTIFIED-CONTESTANT" in c3_txt and "387/387" in c3_txt and "contestant 380" in c3_txt else findings).append(
                "C3 block L154-L157 (the _backup copy): %s" % c3_txt[:240])
        if any(l.startswith("P4 reason (6) R6") for l in new): findings.append("a 'P4 reason (6) R6' own line is printed: R6 > 0 on the record (a class moved)")
        print("EXPECTED DIFFS (%d):" % len(ok)); [print("  " + l) for l in ok]
        print("FINDINGS (%d): anything else that moves, above all a class, an E1-E4 or a P1-P5 line" % len(findings)); [print("  " + l) for l in findings]
        if a.rec_json and a.new_json:      # F1 (a3da968): which units' unresolvable counts rose under the ungated counter; any class move
            rj_, nj_ = json.load(open(a.rec_json, encoding="utf-8")), json.load(open(a.new_json, encoding="utf-8"))
            rc = {(c["path"], u["table"]): (c["klass"], u) for c in rj_["caches"] for u in c["units"]}
            print("F1 READOUT (record JSON, gated counter -> new JSON, ungated counter):")
            for c in nj_["caches"]:
                for u in c["units"]:
                    k0, u0 = rc.get((c["path"], u["table"]), (None, {}))
                    old_p = (u0.get("counts") or {}).get("unresolvable_labels"); new_p = (u.get("counts") or {}).get("unresolvable_labels")
                    old_s = ((u0.get("secondary") or {}).get("counts") or {}).get("unresolvable_labels")
                    new_s = ((u.get("secondary") or {}).get("counts") or {}).get("unresolvable_labels")
                    if (old_p or 0) != (new_p or 0) or (old_s or 0) != (new_s or 0) or k0 != c["klass"] or u0.get("klass") != u["klass"]:
                        print("  %s:%s | cache %s -> %s | unit %s -> %s | primary unresolvable %s -> %s | secondary unresolvable %s -> %s | labels %s"
                              % (c["path"], u["table"], k0, c["klass"], u0.get("klass"), u["klass"], old_p, new_p, old_s, new_s,
                                 u.get("unresolvable_values") or (u.get("secondary") or {}).get("unresolvable_values")))
            moved = [(c["path"], rc.get((c["path"], c["units"][0]["table"]), (None,))[0], c["klass"]) for c in nj_["caches"]
                     if rc.get((c["path"], c["units"][0]["table"]), (None,))[0] != c["klass"]]
            print("  CACHE CLASS MOVES vs the record (expected: only the _backup copy -> CERTIFIED-CONTESTANT, C3): %s" % moved)
    elif a.what == "score-pia":
        for no, r, nw, _ in diffs:
            (ok if no == 2 else findings).append("L%s | record: %s | new: %s" % (no, (r or "")[:140], (nw or "")[:140]))
        print("EXPECTED (L2, the index's own sha only): %s" % ok); print("FINDINGS: %s" % (findings or "none"))
    else:
        findings = ["L%s | record: %s | new: %s" % (no, (r or "")[:140], (nw or "")[:140]) for no, r, nw, _ in diffs]
        print("TIE-MECHANICS: %d differing lines (expected 0): %s" % (len(findings), findings or "none"))
    print("SCORE: %s" % ("PASS (only expected diffs)" if not findings else "FINDINGS PRESENT: report to the registrar before scoring (ii) / (iii)"))
    sys.exit(0 if not findings else 3)

BUILD, REPO, OUTD = (os.path.abspath(x) for x in (a.build, a.repo, a.out))
vpath = os.path.join(BUILD, "vote_frame_cert.py"); vb = open(vpath, "rb").read()
lf16 = hashlib.sha256(vb.replace(b"\r\n", b"\n")).hexdigest()[:16]; raw16 = hashlib.sha256(vb).hexdigest()[:16]
print("[BUILD] %s: sha256[:16] of the file as archived %s; of its LF rendering %s; CR bytes %d; expected LF %s" % (vpath, raw16, lf16, vb.count(b"\r"), a.expect_lf))
if raw16 != a.expect_lf or b"\r" in vb:
    raise SystemExit("[C-ii-1] REFUSED: the archived vote_frame_cert.py is not the LF build %s (archive with -c core.autocrlf=false)" % a.expect_lf)
if os.path.exists(OUTD): raise SystemExit("[RERUN] REFUSED: %s exists" % OUTD)
os.makedirs(OUTD)
RECORD_OUT = [os.path.join(REPO, *p.split("/")) for p in ("experiment_results/vote_frame_cert.json", "experiment_results/vote_frame_cert.txt",
                                                         "experiment_results/position_index_all_outcome.txt", "experiment_results/x12_crossdomain/tie_mechanics_outcome.txt")]
def rec_shas():
    return {os.path.relpath(p, REPO).replace("\\", "/"): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in RECORD_OUT}
SH0 = rec_shas(); print("[C-ii-3] before: %s" % {k: v[:16] for k, v in SH0.items()})
sys.dont_write_bytecode = True
os.environ["TAXOARENA_DATA_ROOT"] = REPO
REPO_N = os.path.normcase(REPO)
WFLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


def inside(x):
    try: return os.path.normcase(os.path.abspath(os.fsdecode(x))).startswith(REPO_N)
    except Exception: return False


def hook(event, args):
    if event == "sqlite3.connect":
        db = str(args[0])
        if not (db.startswith("file:") and "mode=ro" in db and "immutable=1" in db):
            raise RuntimeError("[AUDIT] REFUSED sqlite3.connect(%r): not mode=ro&immutable=1" % db)
    elif event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)) and inside(args[0]):
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else ""; flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
        if any(c in mode for c in "wax+") or (flags & WFLAGS):
            raise RuntimeError("[AUDIT] REFUSED write-open %s (mode %r, flags %s) inside the repository" % (args[0], mode, flags))
    elif event in ("os.remove", "os.rename", "os.rmdir", "os.truncate", "os.chmod", "shutil.rmtree") and args and inside(args[0]):
        raise RuntimeError("[AUDIT] REFUSED %s(%s) inside the repository" % (event, args[0]))


sys.addaudithook(hook)
sys.path.insert(0, BUILD)
import vote_frame_cert as vfc                                     # noqa: E402  (the build under test)

if a.what == "vfc":
    rec = json.load(open(os.path.join(REPO, "experiment_results", "vote_frame_cert.json"), encoding="utf-8"))
    paths = [os.path.join(REPO, *c["path"].split("/")) for c in rec["caches"]]
    def state(p, c):
        bad = [s for s in ("-wal", "-journal") if os.path.exists(p + s) and os.path.getsize(p + s) > 0]
        st = os.stat(p)
        return (not bad) and st.st_size == c["size"] and st.st_mtime_ns == c["mtime_ns"] and vfc.sha256_16(p) == c["sha256_16"]
    pre = [c["path"] for p, c in zip(paths, rec["caches"]) if not state(p, c)]
    if pre: raise SystemExit("[PRE] REFUSED: %d caches differ from the certificate of record: %s" % (len(pre), pre))
    print("[PRE] %d of %d recorded caches equal the certificate of record" % (len(paths), len(paths)))
    vfc.scan_sqlite_files = lambda root: list(paths)
    steward = os.path.join(OUTD, "steward_62.txt")
    with open(steward, "w", encoding="utf-8") as f: f.write("\n".join(c["path"] for c in rec["caches"]) + "\n")
    print("[E3] selftest_ok=True is PASSED, not executed here: E3 rests on part (i)'s selftest of the same LF sha %s" % lf16)
    vfc.run(steward, root=REPO, selftest_ok=True, out_txt=os.path.join(OUTD, "vote_frame_cert.txt"), out_json=os.path.join(OUTD, "vote_frame_cert.json"),
            comb_ctx=dict(repo=REPO))
    post = [c["path"] for p, c in zip(paths, rec["caches"]) if not state(p, c)]
    print("[POST] %s" % ("62 of 62 caches unchanged" if not post else "CHANGED: %s" % post))
elif a.what == "pia":
    import position_index_all as pia                            # noqa: E402
    calls = []; real = vfc.name_profile_of
    def counting(path, content_map=None):
        r = real(path, content_map); calls.append((os.path.basename(path), r[1])); return r
    vfc.name_profile_of = counting
    pia.analyze(root=REPO, out_path=os.path.join(OUTD, "position_index_all_outcome.txt"), eval_db=os.path.join(REPO, "mmlu_pro_dataset_cache_v2.db"))
    print("[WITNESS] name_profile_of called %d times, %d by content (9d3e261: 7 / 4)" % (len(calls), sum(1 for _, h in calls if h and h.startswith("content"))))
else:
    import tie_mechanics as tm                                    # noqa: E402
    tm.analyze(root=REPO, out_path=os.path.join(OUTD, "tie_mechanics_outcome.txt"))
SH1 = rec_shas()
print("[C-ii-3] after: %s -> %s" % ({k: v[:16] for k, v in SH1.items()}, "unchanged" if SH1 == SH0 else "CHANGED"))
if SH1 != SH0: raise SystemExit("[C-ii-3] REFUSED: an output of record changed during the leg")
