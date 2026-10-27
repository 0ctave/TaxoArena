"""Text-only verification driver for rerun_vf4.py (VFC-FIXES-2 checks (ii)/(iii), harness v4; ruling docs/reviews/RULING_vfc_ii_iii_pin.md,
93cc7de, section 4 "Verification before the pin"). 2026-09-25, engine-coder. ZERO CALLS; opens NO DB; runs NO leg to completion and NO selftest.

What it runs (every subprocess transcript is written, write-once, under --transcripts):
  S  the three scorers on text variants: the reviewer's rv2 variants A / C / D / H (fixtures/, LF-normalised; their CRLF renderings are checked
     against the scratchpad originals' sha256), A / C / D / H regenerated with the section-3 L1, and variants of the records of reference
     (git show 93cc7de:<path>, blob ids checked) for score-pia and score-tm.
  P  `prep` (git archive of f76a93b, read in memory; the sha256 gates, 0 CR, step 0c) into <work>/T, plus its refusals on patched constants.
  L  the legs' PRE-CHECKS only (C-ii-1 and H3 pins, --e3-log), with --repo pointing at an EMPTY scratch directory: a leg whose pre-checks all
     pass dies at the first read of an output of record (FileNotFoundError in rec_shas, before the audit hook, before any import of the build),
     so no leg can proceed to a cache. The driver refuses to pass the real repository as a leg's --repo.
  RV4 (READY review docs/reviews/READY_vfc_harness_v4.md, e256c23): RV4-1 the reviewer's b1 probes (a 930ccc7 archive + --expect-lf
     211112d41eed0b77 + 930ccc7's selftest log; score-vfc with 211112d41eed0b77) must be REFUSED; RV4-2 a scratch git repo (alternates onto the
     main object store, HEAD = main's HEAD; nothing written to the main checkout) and a sibling directory whose name starts with the repo's must
     be ACCEPTED by prep; RV4-3 the reviewer's cases (tm + L13 / + L15 changed; an E3 log with one preamble line) and mutants R1-R4 (verbatim
     from scratchpad v4r/mine/rmut.py).
  M  mutants of the v4 checks: each removes or neuters ONE check by an exact, count-asserted string replacement in a copy of rerun_vf4.py under
     <work>; a mutant is KILLED when at least one of its kill cases no longer meets its expectation.
The E3 fixture is the reviewer's round-2 transcript rv2/r2st_vote_frame_cert_py.txt (a selftest of 211112d41eed0b77, i.e. of 930ccc7): a FORMAT
fixture for --e3-log only. It is NOT the E3 of b45b75db (P3), which this driver does not run.

  python test_rerun_vf4.py --repo <MAIN> --work <scratch dir, must not exist, outside MAIN> --transcripts <dir, must not exist>
"""
import argparse, ast, hashlib, io, os, re, shutil, subprocess, sys, tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
RULING_COMMIT = "93cc7de"
REC = {"vfc": ("experiment_results/vote_frame_cert.txt", "8db4403f"), "pia": ("experiment_results/position_index_all_outcome.txt", "bb1578ca"),
       "tm": ("experiment_results/x12_crossdomain/tie_mechanics_outcome.txt", "a2df609d")}
FIX = {"A": "scor_A_expected_only.txt", "C": "scor_C_inserted_indented_note.txt", "D": "scor_D_ladder_class_move.txt",
       "H": "scor_H_inserted_cache_header.txt", "E3": "r2st_vote_frame_cert_py.txt"}
FIX_CRLF_SHA = {"A": "b43be9bbd0d758ab73ac813cf7ab2b53717e0fbe5b1c11dafaf67be05540cda6", "C": "77de39001adad9782a413756d7ed893648a67ecad31c9b331b7894ffabab444e",
                "D": "c714839e2f3705439cf87612cbc51d57f96a9ad78d294effa5b9b1ef25a93b6d", "H": "b3bb666f3e1098a382c3a9bdb9aa9fe40da272ef236af8ab963a8288457c1d79",
                "E3": "02339bfd76305c32cf7210e7a0895ea38645ea6bd52d3b6ddf33839dd49419ce"}
LF = "b45b75db7d98103e"
PINMSG = "is not the ruling's pin of vote_frame_cert.py b45b75db7d98103e"

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True); ap.add_argument("--work", required=True); ap.add_argument("--transcripts", required=True)
ap.add_argument("--harness", default=os.path.join(HERE, "rerun_vf4.py"))
a = ap.parse_args()
M, W, TR, HARN = (os.path.abspath(x) for x in (a.repo, a.work, a.transcripts, a.harness))
for d in (W, TR):
    if os.path.exists(d): raise SystemExit("[DRIVER] REFUSED: %s exists" % d)
if os.path.normcase(W).startswith(os.path.normcase(M)): raise SystemExit("[DRIVER] REFUSED: --work lies inside --repo")
os.makedirs(W); os.makedirs(os.path.join(TR, "mutants"))
LOG = []


def say(s=""):
    print(s); LOG.append(s)


def sha(b): return hashlib.sha256(b).hexdigest()


def wr(p, txt):
    with open(p, "w", encoding="utf-8", newline="") as f: f.write(txt)
    return p


def git(*args):
    r = subprocess.run(["git", "-C", M] + list(args), capture_output=True)
    if r.returncode: raise SystemExit("[DRIVER] git %s: rc %d %s" % (args, r.returncode, r.stderr.decode(errors="replace")))
    return r.stdout


def lf_text(p):
    return open(p, "rb").read().replace(b"\r\n", b"\n").decode("utf-8")


# ---- 0. identities -------------------------------------------------------------------------------------------------------------------------
hb = open(HARN, "rb").read().replace(b"\r\n", b"\n")
say("[ID] harness %s: sha256-lf %s (%d bytes LF); driver sha256-lf %s" % (HARN, sha(hb), len(hb),
                                                                       sha(open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n"))))
say("[ID] python %s; repo HEAD %s" % (sys.version.split()[0], git("rev-parse", "HEAD").decode().strip()))
fx = {}
for k, n in FIX.items():
    t = lf_text(os.path.join(HERE, "fixtures", n)); fx[k] = t
    got = sha(t.replace("\n", "\r\n").encode("utf-8"))
    say("[FIXTURE] %s: sha256 of the CRLF rendering %s (scratchpad original %s): %s" % (n, got[:16], FIX_CRLF_SHA[k][:16],
                                                                                         "OK" if got == FIX_CRLF_SHA[k] else "MISMATCH"))
    if got != FIX_CRLF_SHA[k]: raise SystemExit("[DRIVER] fixture %s is not the scratchpad original" % n)
rec = {}
for k, (p, blob) in REC.items():
    b = git("rev-parse", "%s:%s" % (RULING_COMMIT, p)).decode().strip()
    say("[RECORD] %s:%s blob %s (ruling: %s...): %s" % (RULING_COMMIT, p, b, blob, "OK" if b.startswith(blob) else "MISMATCH"))
    if not b.startswith(blob): raise SystemExit("[DRIVER] record blob mismatch")
    rec[k] = git("show", "%s:%s" % (RULING_COMMIT, p)).decode("utf-8").replace("\r\n", "\n")
# the harness's section-3 strings, read by ast (no execution), against the ruling's text at 93cc7de and the records
consts = {}
for node in ast.parse(hb.decode("utf-8")).body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant):
        consts[node.targets[0].id] = node.value.value
ruling = git("show", "%s:docs/reviews/RULING_vfc_ii_iii_pin.md" % RULING_COMMIT).decode("utf-8")
checks = [("VFC_L1 %% (%s, %s) is verbatim in the ruling" % (LF, LF), ("`%s`" % (consts["VFC_L1"] % (LF, LF))) in ruling),
          ("PIA_L2 is verbatim in the ruling", ("`%s`" % consts["PIA_L2"]) in ruling),
          ("TM_L14_NEW is verbatim in the ruling", ("`%s`" % consts["TM_L14_NEW"]) in ruling),
          ("TM_L14_REC == record tm L14", rec["tm"].split("\n")[13] == consts["TM_L14_REC"]),
          ("TM_L14_NEW == TM_L14_REC with 4a18124878801487 -> d6a1a0409a0fc06e (one substitution)",
           consts["TM_L14_REC"].count("4a18124878801487") == 1 and consts["TM_L14_REC"].replace("4a18124878801487", "d6a1a0409a0fc06e") == consts["TM_L14_NEW"]),
          ("PIA_L2 == record pia L2 with its LF16 and CRLF16 replaced by 9c78d485f37f442a",
           re.sub(r"LF bytes [0-9a-f]{16} \(of the CRLF rendering [0-9a-f]{16}\)", "LF bytes 9c78d485f37f442a (of the CRLF rendering 9c78d485f37f442a)",
                  rec["pia"].split("\n")[1]) == consts["PIA_L2"]),
          ("VFC_L1 == record vfc L1 with its LF16 and CRLF16 replaced by %%s" ,
           re.sub(r"LF bytes [0-9a-f]{16} \(of the CRLF rendering [0-9a-f]{16}\)", "LF bytes %s (of the CRLF rendering %s)",
                  rec["vfc"].split("\n")[0]) == consts["VFC_L1"]),
          ("3b44739e161d0d86 appears in no harness string constant", not any("3b44739e" in str(v) for v in consts.values()))]
for what, good in checks:
    say("[CONST] %s: %s" % (what, "OK" if good else "FAILED"))
if not all(g for _, g in checks): raise SystemExit("[DRIVER] a section-3 constant does not match the ruling / record")

# ---- 1. text variants ----------------------------------------------------------------------------------------------------------------------
V = os.path.join(W, "variants"); os.makedirs(V)
L1 = consts["VFC_L1"] % (LF, LF)


def with_line(txt, no, new):
    ls = txt.split("\n"); ls[no - 1] = new; return "\n".join(ls)


def sub1(txt, old, new):
    assert txt.count(old) == 1, (old, txt.count(old)); return txt.replace(old, new)


rp = {}
for k in "ACDH":
    rp[k + "_orig"] = wr(os.path.join(V, "vfc_%s_orig.txt" % k), fx[k])
    rp[k + "_v4"] = wr(os.path.join(V, "vfc_%s_v4.txt" % k), with_line(fx[k], 1, L1))
rp["A_b2framed"] = wr(os.path.join(V, "vfc_A_b2framed.txt"), with_line(fx["A"], 1, consts["VFC_L1"] % (LF, "3b44739e161d0d86")))
rp["A_recL1"] = wr(os.path.join(V, "vfc_A_recL1.txt"), with_line(fx["A"], 1, rec["vfc"].split("\n")[0]))
rp["A_b1"] = wr(os.path.join(V, "vfc_A_b1_211112.txt"), with_line(fx["A"], 1, consts["VFC_L1"] % ("211112d41eed0b77", "211112d41eed0b77")))
rp["A_L1del"] = wr(os.path.join(V, "vfc_A_L1deleted.txt"), "\n".join(with_line(fx["A"], 1, L1).split("\n")[1:]))
rp["rec_vfc"] = wr(os.path.join(V, "rec_vfc.txt"), rec["vfc"])
pia_ok = with_line(rec["pia"], 2, consts["PIA_L2"])
rp["rec_pia"] = wr(os.path.join(V, "rec_pia.txt"), rec["pia"])
rp["pia_expected"] = wr(os.path.join(V, "pia_expected.txt"), pia_ok)
rp["pia_unmoved"] = wr(os.path.join(V, "pia_unmoved.txt"), rec["pia"])
rp["pia_rp2"] = wr(os.path.join(V, "pia_rp2_crlf_half.txt"), with_line(rec["pia"], 2, sub1(consts["PIA_L2"], "(of the CRLF rendering 9c78d485f37f442a)",
                                                                                           "(of the CRLF rendering 50bb9285e9068f0b)")))
rp["pia_second"] = wr(os.path.join(V, "pia_second_line.txt"), with_line(pia_ok, 3, pia_ok.split("\n")[2] + " x"))
tm_ok = with_line(rec["tm"], 14, consts["TM_L14_NEW"])
rp["rec_tm"] = wr(os.path.join(V, "rec_tm.txt"), rec["tm"])
rp["tm_expected"] = wr(os.path.join(V, "tm_expected_L14.txt"), tm_ok)
rp["tm_unmoved"] = wr(os.path.join(V, "tm_unmoved_R2.6.txt"), rec["tm"])
rp["tm_wrong_3b44"] = wr(os.path.join(V, "tm_L14_sha_3b44739e.txt"), with_line(rec["tm"], 14, consts["TM_L14_NEW"].replace(
    "(of the CRLF rendering d6a1a0409a0fc06e)", "(of the CRLF rendering 3b44739e161d0d86)")))
rp["tm_wrong_lf"] = wr(os.path.join(V, "tm_L14_lf_0000.txt"), with_line(rec["tm"], 14, consts["TM_L14_NEW"].replace(
    "LF bytes d6a1a0409a0fc06e", "LF bytes 0000000000000000")))
rp["tm_second"] = wr(os.path.join(V, "tm_expected_plus_L1.txt"), with_line(tm_ok, 1, tm_ok.split("\n")[0] + " x"))
rp["tm_inserted"] = wr(os.path.join(V, "tm_expected_plus_inserted.txt"), tm_ok.rstrip("\n") + "\nan inserted line\n")
rp["tm_rec_wrong"] = wr(os.path.join(V, "rec_tm_L14_altered.txt"), tm_ok)          # a record whose L14 is NOT the recorded CRLF parenthetical
for k in sorted(rp): say("[VARIANT] %-14s %s sha256 %s" % (k, os.path.basename(rp[k]), sha(open(rp[k], "rb").read())[:16]))

# ---- 2. build dirs for the leg pre-checks --------------------------------------------------------------------------------------------------
T = os.path.join(W, "T"); BUILD = os.path.join(T, "tools", "analysis")
FAKE = os.path.join(W, "fake_repo_empty"); os.makedirs(FAKE)
SREPO = os.path.join(W, "scratch_repo")                            # RV4-2: a git repo borrowing main's objects read-only (alternates)
subprocess.run(["git", "init", "-q", SREPO], check=True)
OBJ = os.path.abspath(os.path.join(M, git("rev-parse", "--git-common-dir").decode().strip(), "objects"))
with open(os.path.join(SREPO, ".git", "objects", "info", "alternates"), "w", encoding="utf-8", newline="\n") as f: f.write(OBJ.replace("\\", "/") + "\n")
MHEAD = git("rev-parse", "HEAD").decode().strip()
subprocess.run(["git", "-C", SREPO, "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
subprocess.run(["git", "-C", SREPO, "update-ref", "refs/heads/main", MHEAD], check=True)
say("[SCRATCH-REPO] %s: alternates -> %s; HEAD = main's HEAD %s" % (SREPO, OBJ, MHEAD))
E3D = os.path.join(W, "e3"); os.makedirs(E3D)
e3 = fx["E3"]
e3p = {"ok": wr(os.path.join(E3D, "e3_ok_LF.txt"), e3),
       "crlf": wr(os.path.join(E3D, "e3_ok_CRLF.txt"), e3.replace("\n", "\r\n")),
       "head": wr(os.path.join(E3D, "e3_bad_header.txt"), with_line(e3, 1, "=== POSITION-INDEX-ALL --selftest (a wrong transcript) ===")),
       "total471": wr(os.path.join(E3D, "e3_total_471.txt"), sub1(e3, "SELFTEST PASS: 472 checks, 0 failed", "SELFTEST PASS: 471 checks, 0 failed")),
       "extratotal": wr(os.path.join(E3D, "e3_extra_total.txt"), e3.rstrip("\n") + "\nSELFTEST FAIL: 1 of 473 checks failed\n"),
       "pass471": wr(os.path.join(E3D, "e3_pass_471.txt"), "\n".join(l for i, l in enumerate(e3.split("\n")) if i != 1)),
       "fail": wr(os.path.join(E3D, "e3_one_FAIL.txt"), sub1(e3, "SELFTEST PASS: 472 checks, 0 failed", "  [FAIL] a synthetic failing check\nSELFTEST PASS: 472 checks, 0 failed")),
       "preamble": wr(os.path.join(E3D, "e3_one_preamble_line.txt"), "some preamble\n" + e3),
       "missing": os.path.join(E3D, "no_such_log.txt")}
say("[E3-FIXTURES] %s" % {k: (sha(open(v, "rb").read())[:16] if os.path.exists(v) else "absent") for k, v in e3p.items()})


def mkbuild(name, alter):
    d = os.path.join(W, "builds", name); os.makedirs(d)
    for f in ("vote_frame_cert.py", "position_index_all.py", "tie_mechanics.py"):
        b = open(os.path.join(BUILD, f), "rb").read(); b = alter.get(f, lambda x: x)(b)
        open(os.path.join(d, f), "wb").write(b)
    return d


# ---- 3. the cases --------------------------------------------------------------------------------------------------------------------------
# (id, argv with {OUT} / {OUT2} placeholders, expected rc, must contain, must not contain, harness patch list)
C = []
def case(cid, argv, rc, has=(), hasnot=(), patch=()): C.append(dict(id=cid, argv=argv, rc=rc, has=list(has), hasnot=list(hasnot), patch=list(patch)))


SV = ["score-vfc", "--expect-lf", LF, "--rec", rp["rec_vfc"], "--new"]
case("S-vfc-A-v4", SV + [rp["A_v4"]], 0, ["L1 H2", "EXACT", "FINDINGS (0)", "SCORE: PASS"], ["NOT EXACT"])
case("S-vfc-A-orig-211112", SV + [rp["A_orig"]], 3, ["FINDINGS (1)", "L1 H2", "NOT EXACT"])
case("S-vfc-A-b2framed-3b44739e", SV + [rp["A_b2framed"]], 3, ["FINDINGS (1)", "NOT EXACT", "3b44739e161d0d86"])
case("S-vfc-A-L1-unmoved", SV + [rp["A_recL1"]], 3, ["FINDINGS (1)", "NOT EXACT", "72ceddfe919a982e"])
case("S-vfc-A-L1-deleted", SV + [rp["A_L1del"]], 3, ["NOT EXACT", "L1 NOT an expected diff"])
case("S-vfc-A-v4-wrong-expect-lf", ["score-vfc", "--expect-lf", "211112d41eed0b77", "--rec", rp["rec_vfc"], "--new", rp["A_v4"]], 2, [PINMSG])
case("S-vfc-b1-211112-probe", ["score-vfc", "--expect-lf", "211112d41eed0b77", "--rec", rp["rec_vfc"], "--new", rp["A_b1"]], 2, [PINMSG], ["SCORE: PASS"])
case("S-vfc-no-expect-lf", ["score-vfc", "--rec", rp["rec_vfc"], "--new", rp["A_v4"]], 2, ["score-vfc needs --expect-lf"])
case("S-vfc-C-v4", SV + [rp["C_v4"]], 3, ["FINDINGS (1)", "LNone an unexpected inserted / deleted line:         R6 stored labels unresolvable"], ["NOT EXACT"])
case("S-vfc-D-v4", SV + [rp["D_v4"]], 3, ["FINDINGS (2)", "L341 NOT an expected diff", "L342 NOT an expected diff"], ["NOT EXACT"])
case("S-vfc-H-v4", SV + [rp["H_v4"]], 3, ["FINDINGS (1)", "LNone an unexpected inserted / deleted line:   experiment_results/new_cache.db"], ["NOT EXACT"])
case("S-vfc-C-orig", SV + [rp["C_orig"]], 3, ["FINDINGS (2)", "NOT EXACT", "R6 stored labels unresolvable"])
case("S-vfc-D-orig", SV + [rp["D_orig"]], 3, ["FINDINGS (3)", "NOT EXACT", "L341 NOT an expected diff"])
case("S-vfc-H-orig", SV + [rp["H_orig"]], 3, ["FINDINGS (2)", "NOT EXACT", "new_cache.db"])
SP = ["score-pia", "--rec", rp["rec_pia"], "--new"]
case("S-pia-expected-L2", SP + [rp["pia_expected"]], 0, ["SCORE: PASS", "FINDINGS: none"], ["NOT EXACT"])
case("S-pia-L2-unmoved", SP + [rp["pia_unmoved"]], 3, ["NOT EXACT", "8939144e5ce87636"])
case("S-pia-L2-crlf-half-50bb9285", SP + [rp["pia_rp2"]], 3, ["NOT EXACT", "50bb9285e9068f0b"])
case("S-pia-second-line", SP + [rp["pia_second"]], 3, ["L3 NOT an expected diff"], ["NOT EXACT"])
ST = ["score-tm", "--rec", rp["rec_tm"], "--new"]
case("S-tm-expected-L14", ST + [rp["tm_expected"]], 0, ["SCORE: PASS", "FINDINGS (0)", "1 differing line(s) in all"], ["NOT EXACT"])
case("S-tm-unmoved-R2.6-zero-diff", ST + [rp["tm_unmoved"]], 3, ["FINDINGS (1)", "NOT EXACT", "0 differing line(s) in all"])
case("S-tm-L14-sha-3b44739e", ST + [rp["tm_wrong_3b44"]], 3, ["FINDINGS (1)", "NOT EXACT", "3b44739e161d0d86"])
case("S-tm-L14-lf-0000", ST + [rp["tm_wrong_lf"]], 3, ["FINDINGS (1)", "NOT EXACT"])
case("S-tm-second-changed-line", ST + [rp["tm_second"]], 3, ["FINDINGS (1)", "L1 NOT an expected diff", "2 differing line(s) in all"], ["NOT EXACT"])
case("S-tm-inserted-line", ST + [rp["tm_inserted"]], 3, ["FINDINGS (1)", "LNone NOT an expected diff"], ["NOT EXACT"])
rp_l13 = wr(os.path.join(V, "tm_expected_plus_L13.txt"), with_line(tm_ok, 13, tm_ok.split("\n")[12] + " x"))
rp_l15 = wr(os.path.join(V, "tm_expected_plus_L15.txt"), with_line(tm_ok, 15, tm_ok.split("\n")[14] + " x"))
case("S-tm-L13-changed", ST + [rp_l13], 3, ["FINDINGS (1)", "L13 NOT an expected diff"], ["NOT EXACT"])
case("S-tm-L15-changed", ST + [rp_l15], 3, ["FINDINGS (1)", "L15 NOT an expected diff"], ["NOT EXACT"])
case("S-tm-record-L14-not-of-record", ["score-tm", "--rec", rp["tm_rec_wrong"], "--new", rp["tm_expected"]], 3, ["FINDINGS (1)", "RECORD L14", "NOT EXACT"])

WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))       # the worktree root holding this file (for the inside-repo refusal only)
case("P-prep-ok", ["prep", "--repo", M, "--out", T], 0, ["[0a] CR bytes over the three instruments: 0", "1 line(s): ['tools/analysis/vote_frame_cert.py']",
                                                          "rc 0", "b45b75db7d98103e", "9c78d485f37f442a", "d6a1a0409a0fc06e", "[PREP] extracted"], ["REFUSED"])
case("P-prep-out-exists", ["prep", "--repo", M, "--out", T], 1, ["[PREP] REFUSED", "exists"])
case("P-prep-out-inside-repo", ["prep", "--repo", WT, "--out", os.path.join(WT, "_prep_probe_never_created")], 1, ["lies inside --repo"])
case("P-prep-pin-mismatch", ["prep", "--repo", M, "--out", "{OUT}"], 1, ["[0a] REFUSED", "MISMATCH"],
     patch=[('"position_index_all.py": "9c78d485f37f442a"', '"position_index_all.py": "9c78d485f37f442b"')])
case("P-prep-closure-0c", ["prep", "--repo", M, "--out", "{OUT}"], 1, ["[0c] REFUSED", "0 line(s)"],
     patch=[('BASE_COMMIT = "930ccc7"', 'BASE_COMMIT = "a9d8d7d"')])
case("P-prep-not-ancestor", ["prep", "--repo", M, "--out", "{OUT}"], 1, ["is not an ancestor of HEAD"],
     patch=[('BUILD_COMMIT = "f76a93b"', 'BUILD_COMMIT = "930ccc7"')])


def leg(what, build, extra=()):
    return [what, "--build", build, "--expect-lf", LF] + list(extra) + ["--repo", FAKE, "--out", "{OUT}"]


PASSED_PRE = ["FileNotFoundError", "fake_repo_empty"]          # every pre-check passed; the leg died at rec_shas on the empty repo
for w in ("vfc", "pia", "tm"):
    ex = ["--e3-log", e3p["ok"]] if w == "vfc" else []
    case("L-%s-prechecks-pass" % w, leg(w, BUILD, ex), 1, PASSED_PRE + ["expected LF 9c78d485f37f442a", "expected LF d6a1a0409a0fc06e"], ["REFUSED"])
case("L-vfc-prechecks-pass-e3-CRLF", leg("vfc", BUILD, ["--e3-log", e3p["crlf"]]), 1, PASSED_PRE + ["[PASS] lines 472"], ["REFUSED"])
case("L-vfc-wrong-expect-lf", ["vfc", "--build", BUILD, "--expect-lf", "211112d41eed0b77", "--e3-log", e3p["ok"], "--repo", FAKE, "--out", "{OUT}"], 2,
     [PINMSG], ["FileNotFoundError"])
case("L-pia-wrong-expect-lf", ["pia", "--build", BUILD, "--expect-lf", "211112d41eed0b77", "--repo", FAKE, "--out", "{OUT}"], 2, [PINMSG], ["FileNotFoundError"])
case("L-vfc-no-expect-lf", ["vfc", "--build", BUILD, "--e3-log", e3p["ok"], "--repo", FAKE, "--out", "{OUT}"], 2, ["vfc needs --expect-lf"])
case("L-vfc-no-e3-log", leg("vfc", BUILD), 1, ["[E3] REFUSED: the vfc leg needs --e3-log"])
case("L-vfc-e3-missing", leg("vfc", BUILD, ["--e3-log", e3p["missing"]]), 1, ["[E3] REFUSED", "is not a file"])
case("L-vfc-e3-bad-header", leg("vfc", BUILD, ["--e3-log", e3p["head"]]), 1, ["[E3] REFUSED: the log does not open with"])
case("L-vfc-e3-preamble", leg("vfc", BUILD, ["--e3-log", e3p["preamble"]]), 1, ["[E3] REFUSED: the log does not open with"])
case("L-vfc-e3-total-471", leg("vfc", BUILD, ["--e3-log", e3p["total471"]]), 1, ["[E3] REFUSED: the log's SELFTEST total line(s)"])
case("L-vfc-e3-extra-total", leg("vfc", BUILD, ["--e3-log", e3p["extratotal"]]), 1, ["[E3] REFUSED: the log's SELFTEST total line(s)"])
case("L-vfc-e3-pass-471", leg("vfc", BUILD, ["--e3-log", e3p["pass471"]]), 1, ["[E3] REFUSED: 471 [PASS] lines, not 472"])
case("L-vfc-e3-one-FAIL", leg("vfc", BUILD, ["--e3-log", e3p["fail"]]), 1, ["[E3] REFUSED: 1 [FAIL] lines"])
for w in ("pia", "tm"):
    case("L-%s-e3-log-refused" % w, leg(w, BUILD, ["--e3-log", e3p["ok"]]), 1, ["[E3] REFUSED: --e3-log is the vfc leg's"])
case("L-vfc-out-exists", ["vfc", "--build", BUILD, "--expect-lf", LF, "--e3-log", e3p["ok"], "--repo", FAKE, "--out", FAKE], 1, ["[RERUN] REFUSED"])

mutated_builds = {}


def prepare_builds():
    crlf = lambda b: b.replace(b"\n", b"\r\n")
    mutated_builds["pia_mut"] = mkbuild("pia_plus_newline", {"position_index_all.py": lambda b: b + b"\n"})
    mutated_builds["tm_mut"] = mkbuild("tm_plus_newline", {"tie_mechanics.py": lambda b: b + b"\n"})
    mutated_builds["vfc_crlf"] = mkbuild("vfc_crlf", {"vote_frame_cert.py": crlf})
    mutated_builds["vfc_mut"] = mkbuild("vfc_plus_newline", {"vote_frame_cert.py": lambda b: b + b"\n"})
    b1 = os.path.join(W, "builds", "b1_930ccc7"); os.makedirs(b1)
    tf = tarfile.open(fileobj=io.BytesIO(git("-c", "core.autocrlf=false", "archive", "--format=tar", "930ccc7", *["tools/analysis/" + f for f in
                                             ("vote_frame_cert.py", "position_index_all.py", "tie_mechanics.py")])))
    for m in tf.getmembers():
        if m.isfile(): open(os.path.join(b1, os.path.basename(m.name)), "wb").write(tf.extractfile(m).read())
    mutated_builds["b1"] = b1
    mutated_builds["b1_vfc_sha16"] = sha(open(os.path.join(b1, "vote_frame_cert.py"), "rb").read())[:16]
    mutated_builds["vfc_crlf_lf16"] = sha(open(os.path.join(mutated_builds["vfc_crlf"], "vote_frame_cert.py"), "rb").read())[:16]
    say("[BUILDS] %s" % {k: v for k, v in mutated_builds.items()})
    for w in ("vfc", "pia", "tm"):
        ex = ["--e3-log", e3p["ok"]] if w == "vfc" else []
        case("L-%s-pia-file-mutated" % w, leg(w, mutated_builds["pia_mut"], ex), 1, ["[H3] REFUSED: the archived position_index_all.py is not the LF build 9c78d485f37f442a"])
        case("L-%s-tm-file-mutated" % w, leg(w, mutated_builds["tm_mut"], ex), 1, ["[H3] REFUSED: the archived tie_mechanics.py is not the LF build d6a1a0409a0fc06e"])
    case("L-vfc-CRLF-file-with-its-own-raw16", ["vfc", "--build", mutated_builds["vfc_crlf"], "--expect-lf", mutated_builds["vfc_crlf_lf16"], "--e3-log", e3p["ok"],
                                                "--repo", FAKE, "--out", "{OUT}"], 2, [PINMSG], ["FileNotFoundError"])
    case("L-vfc-vfc-file-mutated", leg("vfc", mutated_builds["vfc_mut"], ["--e3-log", e3p["ok"]]), 1,
         ["[C-ii-1] REFUSED: the archived vote_frame_cert.py is not the LF build b45b75db7d98103e"])
    # RV4-1 probe (i): the b1 build (930ccc7, LF archive of the three instruments) + its own LF16 + 930ccc7's selftest transcript
    case("L-vfc-b1-930ccc7-probe", ["vfc", "--build", mutated_builds["b1"], "--expect-lf", "211112d41eed0b77", "--e3-log", e3p["ok"],
                                    "--repo", FAKE, "--out", "{OUT}"], 2, [PINMSG], ["FileNotFoundError", "[BUILD]"])
    # RV4-2: prep against a scratch repo; a sibling whose name starts with the repo's is accepted, a subdirectory is refused
    case("P-prep-sibling-accepted", ["prep", "--repo", SREPO, "--out", SREPO + "_sibling_T"], 0,
         ["[PREP] extracted", "1 line(s): ['tools/analysis/vote_frame_cert.py']"], ["REFUSED"])
    case("P-prep-inside-scratch-repo", ["prep", "--repo", SREPO, "--out", os.path.join(SREPO, "sub_T")], 1, ["lies inside --repo"])


# ---- 4. the mutants: (id, what it removes, [(old, new)], [kill case ids]) --------------------------------------------------------------------
MUT = [
    ("MH1-new-L14", "H1: new L14 exactness (score-tm)", [("exact_line(new, 14, TM_L14_NEW,", "exact_line(new, 14, new[13] if len(new) > 13 else None,")],
     ["S-tm-L14-sha-3b44739e", "S-tm-L14-lf-0000", "S-tm-unmoved-R2.6-zero-diff"]),
    ("MH1-rec-L14", "H1: record L14 is the recorded text (score-tm)", [("exact_line(rec, 14, TM_L14_REC,", "exact_line(rec, 14, rec[13],")],
     ["S-tm-record-L14-not-of-record"]),
    ("MH1-other-lines", "H1: any other differing line is a FINDING (score-tm)",
     [("            if no == 14 and nw is not None: continue         # v4 H1", "            continue         # MUTANT")],
     ["S-tm-second-changed-line", "S-tm-inserted-line"]),
    ("MH2-vfc-L1", "H2: vfc L1 exactness", [("exact_line(new, 1, L1_WANT,", "exact_line(new, 1, new[0],")],
     ["S-vfc-A-orig-211112", "S-vfc-A-b2framed-3b44739e", "S-vfc-A-L1-unmoved", "S-vfc-A-v4-wrong-expect-lf"]),
    ("MH2-vfc-L1-skip", "H2: the positional L1 check replaces the diff-loop judgement (the skip is load-bearing)",
     [("            if no == 1 and nw is not None: continue", "            pass")], ["S-vfc-A-v4"]),
    ("MH2-vfc-expect-lf-required", "H2: score-vfc refuses without --expect-lf",
     [('if a.what in ("vfc", "pia", "tm", "score-vfc") and not (a.expect_lf', 'if a.what in ("vfc", "pia", "tm") and not (a.expect_lf')], ["S-vfc-no-expect-lf"]),
    ("MH2-pia-L2", "H2: pia L2 exactness", [("exact_line(new, 2, PIA_L2,", "exact_line(new, 2, new[1],")],
     ["S-pia-L2-unmoved", "S-pia-L2-crlf-half-50bb9285"]),
    ("MH2-pia-other-lines", "H2: pia, any other differing line is a FINDING",
     [("            if no == 2 and nw is not None: continue          # v4 H2", "            continue          # MUTANT")], ["S-pia-second-line"]),
    ("MH3-pin-pia", "H3: the leg pins position_index_all.py", [('("position_index_all.py", PIN_LF["position_index_all.py"], "H3"),', "")],
     ["L-vfc-pia-file-mutated", "L-pia-pia-file-mutated", "L-tm-pia-file-mutated"]),
    ("MH3-pin-tm", "H3: the leg pins tie_mechanics.py", [('\n                        ("tie_mechanics.py", PIN_LF["tie_mechanics.py"], "H3")):', "):")],
     ["L-vfc-tm-file-mutated", "L-pia-tm-file-mutated", "L-tm-tm-file-mutated"]),
    ("MH3-raw16", "C-ii-1 / H3: the sha comparison", [("    if raw16 != want:", "    if False:")],
     ["L-vfc-vfc-file-mutated", "L-vfc-pia-file-mutated", "L-tm-tm-file-mutated"]),
    ("MRV4-1-pin", "RV4-1: --expect-lf must equal the ruling's pin b45b75db7d98103e",
     [('and a.expect_lf != PIN_LF["vote_frame_cert.py"]:      # RV4-1', 'and False:      # RV4-1')],
     ["L-vfc-b1-930ccc7-probe", "S-vfc-b1-211112-probe", "L-vfc-wrong-expect-lf", "L-pia-wrong-expect-lf"]),
    ("MP-inside-repo", "prep: --out must lie outside --repo (run against the SCRATCH repo, so the mutant extracts only into scratch)",
     [("    if under(OUTD, REPO): raise SystemExit", "    if False: raise SystemExit")], ["P-prep-inside-scratch-repo"]),
    ("MRV4-2-commonpath", "RV4-2: path-component-aware 'inside --repo'", [("    try: return os.path.commonpath([p, r]) == r", "    try: return p.startswith(r)")],
     ["P-prep-sibling-accepted"]),
    ("R1-M1-window", "reviewer R1: R2-M1 regression, the C3 window admits any insertion",
     [("(x[0] is None and 153 <= x[3] <= 157)", "(x[0] is None and 0 <= x[3] <= 10**6)")], ["S-vfc-C-v4", "S-vfc-H-v4"]),
    ("R2-prefix", "reviewer R2: exact_line compares a 60-char prefix",
     [("(ok if got == want else findings)", "(ok if (got or '')[:60] == want[:60] else findings)")], ["S-vfc-A-orig-211112", "S-pia-L2-crlf-half-50bb9285"]),
    ("R3-tm-skip-window", "reviewer R3: the H1 positional skip widened to L13-L15",
     [("            if no == 14 and nw is not None: continue", "            if no in (13, 14, 15) and nw is not None: continue")],
     ["S-tm-L13-changed", "S-tm-L15-changed"]),
    ("R4-e3-anyheader", "reviewer R4: the E3 header may be on any line",
     [("e3_head = e3[0].startswith(E3_HEAD)", "e3_head = any(l.startswith(E3_HEAD) for l in e3)")], ["L-vfc-e3-preamble"]),
    ("MH3-e3-required", "H3: the vfc leg refuses without --e3-log", [("    if not a.e3_log: raise SystemExit", "    if False: raise SystemExit")],
     ["L-vfc-no-e3-log"]),
    ("MH3-e3-isfile", "H3: --e3-log must be a file", [("    if not os.path.isfile(a.e3_log):", "    if False:")], ["L-vfc-e3-missing"]),
    ("MH3-e3-header", "H3: the transcript opens with the vfc selftest header", [("    if not e3_head:", "    if False:")], ["L-vfc-e3-bad-header"]),
    ("MH3-e3-total", "H3: exactly the one total line 'SELFTEST PASS: 472 checks, 0 failed'", [("    if e3_tot != [E3_TOTAL]:", "    if False:")],
     ["L-vfc-e3-total-471", "L-vfc-e3-extra-total"]),
    ("MH3-e3-pass-count", "H3: 472 [PASS] lines", [("    if e3_pass != E3_N:", "    if False:")], ["L-vfc-e3-pass-471"]),
    ("MH3-e3-fail-count", "H3: 0 [FAIL] lines", [("    if e3_fail != 0:", "    if False:")], ["L-vfc-e3-one-FAIL"]),
    ("MH3-e3-vfc-only", "H3: pia / tm refuse --e3-log", [("elif a.e3_log:\n    raise", "elif False:\n    raise")], ["L-pia-e3-log-refused", "L-tm-e3-log-refused"]),
    ("MP-pin-gate", "prep 0a: the sha256 gates", [("        if not h.startswith(pin): bad.append(name)", "        pass")], ["P-prep-pin-mismatch"]),
    ("MP-closure-0c", "prep 0c: exactly vote_frame_cert.py", [('    if r.returncode or changed != ["tools/analysis/vote_frame_cert.py"]:', "    if False:")],
     ["P-prep-closure-0c"]),
    ("MP-ancestor", "prep: f76a93b is an ancestor of HEAD", [("    if r.returncode != 0: raise SystemExit(\"[PREP] REFUSED: %s is not an ancestor", "    if False: raise SystemExit(\"[PREP] REFUSED: %s is not an ancestor")],
     ["P-prep-not-ancestor"]),
    ("MP-out-exists", "prep: --out must not exist", [('    if os.path.exists(OUTD): raise SystemExit("[PREP] REFUSED: %s exists" % OUTD)', "    pass")],
     ["P-prep-out-exists"]),
]
EQUIVALENT = [("MH3-CR (legs: the 0-CR check)",
               "EQUIVALENT since RV4-1: --expect-lf must be b45b75db7d98103e (the pia / tm pins are constants) and a CR byte changes the sha256, so the "
               "sha comparison refuses first; at bf8e76c it was killed by L-vfc-CRLF-file-with-its-own-raw16, which RV4-1 now refuses at the pin (rc 2)"),
              ("MP-CR (prep 0a: 0 CR over the three instruments)",
               "EQUIVALENT under the sha gate: a CR byte in an archived instrument changes its sha256, which then cannot start with its pin; the "
               "check is kept because the ruling's step 0a prints it (a --pin-free kill would need a CR-bearing blob at f76a93b, which has none)")]

# ---- 5. run ------------------------------------------------------------------------------------------------------------------------------
NRUN = [0]


def materialise(patch, tag):
    t = hb.decode("utf-8")
    for old, new in patch:
        n = t.count(old)
        if n != 1: raise SystemExit("[DRIVER] patch %r occurs %d times in the harness (must be 1)" % (old[:80], n))
        t = t.replace(old, new)
    if not patch: return HARN
    p = os.path.join(W, "harness_variants", "rerun_vf4__%s.py" % tag); os.makedirs(os.path.dirname(p), exist_ok=True)
    wr(p, t); return p


def execute(c, harness, tpath):
    NRUN[0] += 1
    argv = [x.replace("{OUT}", os.path.join(W, "outs", "o%03d" % NRUN[0])) for x in c["argv"]]
    if c["id"].startswith("L-"):
        ri = argv.index("--repo")
        if os.path.normcase(os.path.abspath(argv[ri + 1])) != os.path.normcase(FAKE):
            raise SystemExit("[DRIVER] REFUSED: a leg case must run against the empty fake repo")
        if os.listdir(FAKE) and c["id"] != "L-vfc-out-exists": raise SystemExit("[DRIVER] REFUSED: the fake repo is not empty")
    r = subprocess.run([sys.executable, harness] + argv, capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", errors="replace").replace("\r\n", "\n")
    good = r.returncode == c["rc"] and all(h in out for h in c["has"]) and not any(h in out for h in c["hasnot"])
    with open(tpath, "x", encoding="utf-8", newline="\n") as f:
        f.write("$ python %s %s\n%s\n[rc %d] expected rc %d; must contain %s; must not contain %s -> %s\n" % (
            os.path.basename(harness), " ".join(argv), out.rstrip("\n"), r.returncode, c["rc"], c["has"], c["hasnot"], "MEETS" if good else "DOES NOT MEET"))
    return good, r.returncode


byid = {}
results = []
def run_cases(cs):
    for c in cs:
        byid[c["id"]] = c
        h = materialise(c["patch"], "patched_" + c["id"])
        good, rc = execute(c, h, os.path.join(TR, "%s.txt" % c["id"]))
        results.append((c["id"], good, rc))
        say("[CASE] %-44s rc %d (expected %d): %s" % (c["id"], rc, c["rc"], "PASS" if good else "FAIL"))


n0 = len(C)
run_cases(C[:n0])                  # S, P (P-prep-ok creates T), then the L cases that need only T
prepare_builds()
run_cases(C[n0:])
say("")
killed = []
for mid, what, repl, kills in MUT:
    outcome = []
    for kid in kills:
        c = byid[kid]
        h = materialise(c["patch"] + repl, "%s__%s" % (mid, kid))
        good, rc = execute(c, h, os.path.join(TR, "mutants", "%s__%s.txt" % (mid, kid)))
        outcome.append((kid, rc, not good))
    k = any(x[2] for x in outcome)
    killed.append((mid, k))
    say("[MUTANT] %-28s %-80s %s by %s" % (mid, what, "KILLED" if k else "SURVIVED", ["%s rc %d%s" % (i, rc, "" if kk else " (not killed)") for i, rc, kk in outcome]))
for mid, why in EQUIVALENT: say("[MUTANT] %s: %s" % (mid, why))
fails = [r for r in results if not r[1]]; surv = [m for m, k in killed if not k]
say("")
say("[SUMMARY] cases %d, meeting expectation %d, failing %d %s" % (len(results), len(results) - len(fails), len(fails), [f[0] for f in fails]))
say("[SUMMARY] mutants %d, killed %d, survived %d %s; %d listed as equivalent / not run" % (len(killed), len(killed) - len(surv), len(surv), surv, len(EQUIVALENT)))
say("[SUMMARY] harness runs %d; no leg passed its pre-checks against a real repository (every leg case used %s, empty)" % (NRUN[0], FAKE))
with open(os.path.join(TR, "SUMMARY.txt"), "x", encoding="utf-8", newline="\n") as f: f.write("\n".join(LOG) + "\n")
sys.exit(0 if not fails and not surv else 1)
