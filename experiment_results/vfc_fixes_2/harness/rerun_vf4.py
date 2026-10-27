"""VFC-FIXES-2 delta READY, checks (ii) and (iii) of VFC-RX-RULING section 5, under the conditions C-ii-1, C-ii-2, C-ii-3 and C-iii of the review
docs/reviews/READY_vfc_fixes_2.md (a3da968). ZERO-WRITE re-derivations in scratch, never over a file of record. PREPARED 2026-09-25 by the
engine-coder; NOT RUN (the ruling's condition (2): after the pilot and INDUCE-RUBRIC-3 close). Supersedes rerun_vf2.py.

v4 (2026-09-25, engine-coder), built from rerun_vf3.py (sha256 5b2de8a394f7ef5e..., LF, 15,177 bytes; kept byte-identical: scratchpad vf2/, the evidence disk, and rerun_vf3.py beside this file) to the
ruling docs/reviews/RULING_vfc_ii_iii_pin.md (93cc7de) section 4, fixing RP-1, RP-3 and RP-4 of its section 7:
  H1  score-tm admits exactly ONE differing line: record L14 (the CRLF parenthetical 4a18124878801487) -> the exact section-3 L14
      (d6a1a0409a0fc06e twice). The record's L14 must be the recorded text; any other L14 text or any other differing line is a FINDING (rc 3).
  H2  score-vfc takes --expect-lf and requires new L1 to be EXACTLY the section-3 string with that LF16 in both places; score-pia requires new L2 to
      be EXACTLY the section-3 constant. Each is checked by POSITION (the line must be there and read exactly so), so an unmoved line, a wrong sha
      or a CRLF half is a FINDING. Replaces v3's "starts with ... and no 72ceddfe" and "any change at L2".
  H3  every leg's C-ii-1 pre-check also pins the archived position_index_all.py (9c78d485f37f442a) and tie_mechanics.py (d6a1a0409a0fc06e) by
      sha256[:16] of the bytes as archived, with 0 CR. The vfc leg REFUSES without --e3-log <transcript>: the file must exist, open with the
      "=== VOTE-FRAME-CERT --selftest" header, carry the total line "SELFTEST PASS: 472 checks, 0 failed" exactly once and no other SELFTEST total,
      472 "[PASS]" lines and 0 "[FAIL]" lines; its sha256 is printed in place of v3's "rests on part (i)'s selftest of the same LF sha". The
      harness checks the transcript's FORM and hashes it; it cannot see which bytes produced it (binding the log to the archive is step E3's).
      pia / tm legs refuse --e3-log (it is the vfc leg's).
  prep (the ruling's section 3 steps 0a and 0c as a subcommand; added at the orchestrator's instruction, NOT one of H1-H3; REQUIRED by the
      READY review docs/reviews/READY_vfc_harness_v4.md (e256c23) section 4 (a): the build for the legs is made by prep, never by hand): `git -c core.autocrlf=false archive f76a93b tools/analysis src/main/kotlin experiment_configs` read IN MEMORY; REFUSES,
      before anything is extracted, unless f76a93b is an ancestor of the repo's HEAD, the full sha256 of the three archived instruments start with
      b45b75db7d98103e / 9c78d485f37f442a / d6a1a0409a0fc06e, the three carry 0 CR bytes, and `git diff --name-only 930ccc7 f76a93b --` over the
      15-module read closure prints exactly tools/analysis/vote_frame_cert.py. --out must not exist and must lie outside --repo.
  RV4-1 (review e256c23, MEDIUM, fixed): every leg and score-vfc REFUSE (rc 2) unless --expect-lf == PIN_LF["vote_frame_cert.py"]
      (b45b75db7d98103e): the flag is kept so the command states the pin, but the operator can no longer supply another build's sha (a b1 run of
      930ccc7 with 211112d41eed0b77 and 930ccc7's selftest log passed every pre-check, and score-vfc with 211112d41eed0b77 gave rc 0, at bf8e76c).
  RV4-2 (review e256c23, LOW, fixed): "inside --repo" (prep's --out check and the legs' audit hook) is path-component-aware (os.path.commonpath
      on normcased absolute paths), so a sibling such as ...\TaxoArena_data\... is NOT inside ...\TaxoArena.

PREP (REQUIRED; git objects only; no DB):
  python rerun_vf4.py prep --repo <MAIN> --out <S>/T
LEGS (each refuses if --out exists):
  python rerun_vf4.py vfc --build <T>/tools/analysis --expect-lf <LF16> --e3-log <E3 transcript> --repo <MAIN> --out <OUT>    (ii)  the 62 caches
  python rerun_vf4.py pia --build <T>/tools/analysis --expect-lf <LF16> --repo <MAIN> --out <OUT>    (iii) POSITION-INDEX-ALL
  python rerun_vf4.py tm  --build <T>/tools/analysis --expect-lf <LF16> --repo <MAIN> --out <OUT>    (iii) TIE-MECHANICS
SCORING (reads text files only):
  python rerun_vf4.py score-vfc --expect-lf <LF16> --rec <record .txt> --new <OUT>/vote_frame_cert.txt [--rec-json <record .json> --new-json <OUT>/vote_frame_cert.json]
  python rerun_vf4.py score-pia --rec <record .txt> --new <OUT>/position_index_all_outcome.txt
  python rerun_vf4.py score-tm  --rec <record .txt> --new <OUT>/tie_mechanics_outcome.txt

GUARDS. C-ii-1: <T> must be `git -c core.autocrlf=false archive <build> tools/analysis src/main/kotlin experiment_configs`; the leg REFUSES unless
sha256[:16] of <T>/tools/analysis/vote_frame_cert.py equals --expect-lf and the file carries no CR byte (v4 H3: the same for position_index_all.py
and tie_mechanics.py against their constants). C-ii-3: sha256 of the four outputs of
record (vote_frame_cert.json / .txt, position_index_all_outcome.txt, x12_crossdomain/tie_mechanics_outcome.txt) before and after each leg,
REFUSED on any change. The audit hook refuses: any sqlite3.connect without mode=ro and immutable=1; any open() / os.open() inside <MAIN> with a
write mode or write flags; os.remove / os.unlink / os.rename / os.replace / os.rmdir / os.truncate / os.chmod / shutil.rmtree inside <MAIN> (the
review's row 17 holes). vfc leg: the 62 recorded caches must equal the certificate of record before and after (size, mtime_ns, sha256_16, no
non-empty -wal / -journal); the scan is restricted to them. E3: `selftest_ok=True` is PASSED, not executed; E3 of the re-derivation is the
--e3-log transcript (v4 H3), whose sha256 the leg prints; the certificate's L3 "executed in-process" is NOT evidence."""
import os, sys, json, argparse, hashlib, difflib, re, io, subprocess, tarfile

# ---- v4 constants: ruling 93cc7de (docs/reviews/RULING_vfc_ii_iii_pin.md) sections 0, 3, 4; the strings are copied verbatim from section 3 ----
BUILD_COMMIT = "f76a93b"                     # (b2): the merge commit on main
BASE_COMMIT = "930ccc7"                      # the READY'd build (step 0c)
PIN_LF = {"vote_frame_cert.py": "b45b75db7d98103e", "position_index_all.py": "9c78d485f37f442a", "tie_mechanics.py": "d6a1a0409a0fc06e"}
CLOSURE = ("vote_frame_cert", "position_index_all", "tie_mechanics", "rejudge_grok", "rejudge_reasoning", "rejudge_reference", "judge_free_tests",
           "pool_guard", "split_side", "arena13", "placebo_entry", "rubric_p8", "rubric_512", "stack_judge", "prompt_v2")
VFC_L1 = ("=== VOTE-FRAME-CERT (zero calls) | registration docs/judge_v2_program.md L13032-L13109 (8adae39) | script sha256[:16] of the LF bytes %s "
          "(of the CRLF rendering %s) ===")
PIA_L2 = ("=== POSITION-INDEX-ALL (zero calls) | registration docs/judge_v2_program.md L13111-L13227 (b25bde0) | script sha256[:16] of the LF bytes "
          "9c78d485f37f442a (of the CRLF rendering 9c78d485f37f442a) ===")
TM_L14_REC = ("=== TIE-MECHANICS (zero calls) | registration docs/judge_v2_program.md L12911-L13030 (3c2fcab) | script sha256[:16] of the LF bytes "
              "d6a1a0409a0fc06e (of the CRLF rendering 4a18124878801487) ===")
TM_L14_NEW = ("=== TIE-MECHANICS (zero calls) | registration docs/judge_v2_program.md L12911-L13030 (3c2fcab) | script sha256[:16] of the LF bytes "
              "d6a1a0409a0fc06e (of the CRLF rendering d6a1a0409a0fc06e) ===")
E3_HEAD = "=== VOTE-FRAME-CERT --selftest"
E3_TOTAL = "SELFTEST PASS: 472 checks, 0 failed"
E3_N = 472

ap = argparse.ArgumentParser()
ap.add_argument("what", choices=("prep", "vfc", "pia", "tm", "score-vfc", "score-pia", "score-tm"))
ap.add_argument("--build"); ap.add_argument("--expect-lf"); ap.add_argument("--repo"); ap.add_argument("--out")
ap.add_argument("--rec"); ap.add_argument("--new"); ap.add_argument("--rec-json"); ap.add_argument("--new-json")
ap.add_argument("--e3-log")
a = ap.parse_args()
if a.what in ("vfc", "pia", "tm", "score-vfc") and not (a.expect_lf and re.fullmatch(r"[0-9a-f]{16}", a.expect_lf)):
    ap.error("%s needs --expect-lf <16 lowercase hex> (ruling 93cc7de: b45b75db7d98103e)" % a.what)
if a.what in ("vfc", "pia", "tm", "score-vfc") and a.expect_lf != PIN_LF["vote_frame_cert.py"]:      # RV4-1: the ruling's pin, not the operator's
    ap.error("%s: --expect-lf %s is not the ruling's pin of vote_frame_cert.py %s (93cc7de (b2); RV4-1)" % (a.what, a.expect_lf, PIN_LF["vote_frame_cert.py"]))


def under(path, root):
    """RV4-2: True iff `path` is `root` or lies below it, by path components (a sibling whose name merely starts with root's is NOT under it)."""
    p, r = os.path.normcase(os.path.abspath(path)), os.path.normcase(os.path.abspath(root))
    try: return os.path.commonpath([p, r]) == r
    except ValueError: return False                                   # different drives


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


def exact_line(txt, no, want, label, ok, findings):
    """v4 H1 / H2: line `no` (1-based) of `txt` must read EXACTLY `want`; judged by position, so an unmoved line is caught too."""
    got = txt[no - 1] if len(txt) >= no else None
    (ok if got == want else findings).append("L%d %s: %s | expected exactly: %s | got: %s" % (
        no, label, "EXACT" if got == want else "NOT EXACT", want, got))


if a.what.startswith("score"):
    rec, new = lines(a.rec), lines(a.new)
    diffs = paired_diff(rec, new); findings = []; ok = []
    if a.what == "score-vfc":
        SIX = {176: (111, 1024), 180: (187, 1048), 184: (182, 993), 188: (140, 972), 245: (29, 279), 275: (36, 288)}
        R6LAB = "(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 0"
        L1_WANT = VFC_L1 % (a.expect_lf, a.expect_lf)
        exact_line(new, 1, L1_WANT, "H2 (new L1, ruling 93cc7de section 3, --expect-lf %s)" % a.expect_lf, ok, findings)
        def expected(no, r, nw):
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
            if no == 1 and nw is not None: continue          # v4 H2: judged by position above (exact_line); a DELETED L1 falls through to a FINDING
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
        exact_line(new, 2, PIA_L2, "H2 (new L2, ruling 93cc7de section 3)", ok, findings)
        for no, r, nw, _ in diffs:
            if no == 2 and nw is not None: continue          # v4 H2: judged by position above
            findings.append("L%s NOT an expected diff | record: %s | new: %s" % (no, (r or "")[:140], (nw or "")[:140]))
        print("EXPECTED (L2 only, exactly the section-3 string): %s" % ok); print("FINDINGS: %s" % (findings or "none"))
    else:
        exact_line(rec, 14, TM_L14_REC, "H1 (RECORD L14: the recorded CRLF parenthetical 4a18124878801487)", ok, findings)
        exact_line(new, 14, TM_L14_NEW, "H1 (new L14, ruling 93cc7de section 3)", ok, findings)
        for no, r, nw, _ in diffs:
            if no == 14 and nw is not None: continue         # v4 H1: judged by position above
            findings.append("L%s NOT an expected diff | record: %s | new: %s" % (no, (r or "")[:140], (nw or "")[:140]))
        print("TIE-MECHANICS (v4 H1): exactly one expected differing line, L14 4a18124878801487 -> d6a1a0409a0fc06e; %d differing line(s) in all"
              % len(diffs))
        print("EXPECTED: %s" % ok); print("FINDINGS (%d): %s" % (len(findings), findings or "none"))
    print("SCORE: %s" % ("PASS (only expected diffs)" if not findings else "FINDINGS PRESENT: report to the registrar before scoring (ii) / (iii)"))
    sys.exit(0 if not findings else 3)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, check=False)


if a.what == "prep":                                  # ruling 93cc7de section 3 steps 0a and 0c; git objects only, nothing extracted before the gates
    if not (a.repo and a.out): ap.error("prep needs --repo and --out")
    REPO, OUTD = os.path.abspath(a.repo), os.path.abspath(a.out)
    if os.path.exists(OUTD): raise SystemExit("[PREP] REFUSED: %s exists" % OUTD)
    if under(OUTD, REPO): raise SystemExit("[PREP] REFUSED: --out %s lies inside --repo %s" % (OUTD, REPO))
    r = git(REPO, "rev-parse", "--verify", BUILD_COMMIT + "^{commit}")
    if r.returncode: raise SystemExit("[PREP] REFUSED: %s does not resolve in %s: %s" % (BUILD_COMMIT, REPO, r.stderr.decode(errors="replace").strip()))
    full = r.stdout.decode().strip(); print("[PREP] build commit %s = %s" % (BUILD_COMMIT, full))
    r = git(REPO, "merge-base", "--is-ancestor", full, "HEAD")
    print("[PREP] git merge-base --is-ancestor %s HEAD: rc %d" % (full, r.returncode))
    if r.returncode != 0: raise SystemExit("[PREP] REFUSED: %s is not an ancestor of HEAD in %s (the ruling's b2 builds from the merge commit on main)" % (full, REPO))
    r = subprocess.run(["git", "-C", REPO, "-c", "core.autocrlf=false", "archive", "--format=tar", full, "tools/analysis", "src/main/kotlin",
                        "experiment_configs"], capture_output=True, check=False)
    if r.returncode: raise SystemExit("[PREP] REFUSED: git archive rc %d: %s" % (r.returncode, r.stderr.decode(errors="replace").strip()))
    tf = tarfile.open(fileobj=io.BytesIO(r.stdout)); members = tf.getmembers()
    print("[PREP] git -c core.autocrlf=false archive %s tools/analysis src/main/kotlin experiment_configs: %d members, %d bytes of tar" % (
        full[:7], len(members), len(r.stdout)))
    bad, crs = [], 0
    for name, pin in PIN_LF.items():
        b = tf.extractfile("tools/analysis/" + name).read(); h = hashlib.sha256(b).hexdigest(); crs += b.count(b"\r")
        print("[0a] sha256 tools/analysis/%s = %s (%d bytes, CR %d); must start %s: %s" % (name, h, len(b), b.count(b"\r"), pin,
                                                                                            "OK" if h.startswith(pin) else "MISMATCH"))
        if not h.startswith(pin): bad.append(name)
    if bad: raise SystemExit("[0a] REFUSED: %s of the archive of %s do not carry the ruling's pins" % (bad, full[:7]))
    print("[0a] CR bytes over the three instruments: %d (must be 0)" % crs)
    if crs: raise SystemExit("[0a] REFUSED: %d CR bytes in the archived instruments" % crs)
    r = git(REPO, "diff", "--name-only", BASE_COMMIT, full, "--", *["tools/analysis/%s.py" % m for m in CLOSURE])
    changed = [l for l in r.stdout.decode().replace("\r", "").split("\n") if l]
    print("[0c] git diff --name-only %s %s -- <the %d-module read closure>: rc %d, %d line(s): %s" % (BASE_COMMIT, full[:7], len(CLOSURE),
                                                                                                    r.returncode, len(changed), changed))
    if r.returncode or changed != ["tools/analysis/vote_frame_cert.py"]:
        raise SystemExit("[0c] REFUSED: the read closure must differ between %s and %s in exactly tools/analysis/vote_frame_cert.py" % (BASE_COMMIT, full[:7]))
    os.makedirs(OUTD); tf.extractall(OUTD)
    print("[PREP] extracted %d members to %s; the build for the legs is --build %s" % (len(members), OUTD, os.path.join(OUTD, "tools", "analysis")))
    sys.exit(0)

BUILD, REPO, OUTD = (os.path.abspath(x) for x in (a.build, a.repo, a.out))
# C-ii-1 (v3) and v4 H3: every instrument of the three, as archived, is pinned by sha256[:16] of its bytes, with 0 CR, before anything else
for name, want, tag in (("vote_frame_cert.py", a.expect_lf, "C-ii-1"), ("position_index_all.py", PIN_LF["position_index_all.py"], "H3"),
                        ("tie_mechanics.py", PIN_LF["tie_mechanics.py"], "H3")):
    p = os.path.join(BUILD, name); vb = open(p, "rb").read()
    lf16 = hashlib.sha256(vb.replace(b"\r\n", b"\n")).hexdigest()[:16]; raw16 = hashlib.sha256(vb).hexdigest()[:16]
    print("[BUILD] %s: sha256[:16] of the file as archived %s; of its LF rendering %s; CR bytes %d; expected LF %s" % (p, raw16, lf16, vb.count(b"\r"), want))
    if raw16 != want:
        raise SystemExit("[%s] REFUSED: the archived %s is not the LF build %s (archive with -c core.autocrlf=false)" % (tag, name, want))
    if b"\r" in vb:
        raise SystemExit("[%s] REFUSED: the archived %s carries %d CR byte(s) (archive with -c core.autocrlf=false)" % (tag, name, vb.count(b"\r")))
VFC_LF16 = hashlib.sha256(open(os.path.join(BUILD, "vote_frame_cert.py"), "rb").read()).hexdigest()[:16]
if a.what == "vfc":                                   # v4 H3: E3 is a transcript, not a sentence
    if not a.e3_log: raise SystemExit("[E3] REFUSED: the vfc leg needs --e3-log <the transcript of vote_frame_cert.py --selftest on the archive> "
                                      "(ruling 93cc7de H3, P3)")
    if not os.path.isfile(a.e3_log): raise SystemExit("[E3] REFUSED: --e3-log %s is not a file" % a.e3_log)
    e3b = open(a.e3_log, "rb").read(); e3 = e3b.decode("utf-8", errors="replace").replace("\r\n", "\n").split("\n")
    e3_head = e3[0].startswith(E3_HEAD)
    e3_tot = [l for l in e3 if l.startswith("SELFTEST")]
    e3_pass = sum(1 for l in e3 if l.startswith("  [PASS]")); e3_fail = sum(1 for l in e3 if l.startswith("  [FAIL]"))
    print("[E3] --e3-log %s: sha256 %s (%d bytes); header %r; SELFTEST total line(s) %s; [PASS] lines %d; [FAIL] lines %d" % (
        a.e3_log, hashlib.sha256(e3b).hexdigest(), len(e3b), e3[0][:80], e3_tot, e3_pass, e3_fail))
    if not e3_head: raise SystemExit("[E3] REFUSED: the log does not open with %r (not a vote_frame_cert selftest transcript)" % E3_HEAD)
    if e3_tot != [E3_TOTAL]: raise SystemExit("[E3] REFUSED: the log's SELFTEST total line(s) %s are not exactly [%r]" % (e3_tot, E3_TOTAL))
    if e3_pass != E3_N: raise SystemExit("[E3] REFUSED: %d [PASS] lines, not %d" % (e3_pass, E3_N))
    if e3_fail != 0: raise SystemExit("[E3] REFUSED: %d [FAIL] lines" % e3_fail)
elif a.e3_log:
    raise SystemExit("[E3] REFUSED: --e3-log is the vfc leg's; the %s leg does not take it" % a.what)
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
    try: return under(os.fsdecode(x), REPO)                          # RV4-2
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
    print("[E3] selftest_ok=True is PASSED, not executed here: E3 of this leg is the transcript --e3-log %s (sha256 %s), which must be step E3's "
          "selftest of the archive whose vote_frame_cert.py is LF %s; the certificate's L3 'executed in-process' is NOT evidence"
          % (a.e3_log, hashlib.sha256(e3b).hexdigest(), VFC_LF16))
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
